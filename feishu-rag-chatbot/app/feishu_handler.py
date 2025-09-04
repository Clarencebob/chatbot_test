import json
from typing import Dict, Any
from loguru import logger
from services.feishu_service import feishu_service
from services.rag_service import rag_service


async def handle_feishu_event(event_data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle different types of Feishu events"""
    
    event_type = event_data.get("header", {}).get("event_type")
    
    if event_type == "im.message.receive_v1":
        return await handle_message_event(event_data)
    elif event_type == "im.message.message_read_v1":
        # Handle message read event if needed
        return {"status": "ok"}
    else:
        logger.warning(f"Unhandled event type: {event_type}")
        return {"status": "ok"}


async def handle_message_event(event_data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle message events from Feishu"""
    try:
        event = event_data.get("event", {})
        message = event.get("message", {})
        
        # Extract message details
        message_id = message.get("message_id")
        chat_id = message.get("chat_id")
        message_type = message.get("message_type")
        content = json.loads(message.get("content", "{}"))
        sender = event.get("sender", {})
        user_id = sender.get("sender_id", {}).get("open_id")
        
        # Only handle text messages for now
        if message_type != "text":
            logger.info(f"Ignoring non-text message type: {message_type}")
            return {"status": "ok"}
        
        # Extract text content
        text = content.get("text", "").strip()
        
        if not text:
            return {"status": "ok"}
        
        logger.info(f"Received message from {user_id}: {text}")
        
        # Handle special commands
        if text.startswith("/"):
            response = await handle_command(text, user_id, chat_id)
        else:
            # Query RAG system
            result = rag_service.query(text)
            response = result["response"]
            
            # Add sources if available
            if result.get("sources"):
                sources_text = "\n\n📚 Sources:\n"
                for source in result["sources"]:
                    sources_text += f"- {source['filename']} (Page {source['page']})\n"
                response += sources_text
        
        # Send reply
        feishu_service.reply_message(message_id, response)
        
        return {"status": "ok"}
    
    except Exception as e:
        logger.error(f"Error handling message event: {e}")
        # Send error message to user
        try:
            feishu_service.reply_message(
                message_id,
                "Sorry, I encountered an error processing your message. Please try again later."
            )
        except:
            pass
        return {"status": "error", "message": str(e)}


async def handle_command(command: str, user_id: str, chat_id: str) -> str:
    """Handle special commands"""
    command_parts = command.split()
    cmd = command_parts[0].lower()
    
    if cmd == "/help":
        return """🤖 Feishu RAG Chatbot Commands:

/help - Show this help message
/list - List all uploaded documents
/info <filename> - Get information about a specific document
/search <query> - Search across all documents

To ask questions about the documents, just type your question naturally!

For uploading PDFs, please use the web interface or API endpoint."""
    
    elif cmd == "/list":
        documents = rag_service.list_documents()
        if not documents:
            return "📄 No documents uploaded yet."
        
        doc_list = "📄 Available documents:\n"
        for doc in documents:
            doc_list += f"- {doc['filename']} (ID: {doc['file_id'][:8]}...)\n"
        return doc_list
    
    elif cmd == "/info" and len(command_parts) > 1:
        filename = " ".join(command_parts[1:])
        documents = rag_service.list_documents()
        
        for doc in documents:
            if doc['filename'].lower() == filename.lower():
                # Get more info about the document
                return f"📄 Document: {doc['filename']}\nID: {doc['file_id']}\n\nUse this document by asking questions about its content!"
        
        return f"Document '{filename}' not found. Use /list to see available documents."
    
    elif cmd == "/search" and len(command_parts) > 1:
        query = " ".join(command_parts[1:])
        result = rag_service.query(query)
        return result["response"]
    
    else:
        return "Unknown command. Type /help for available commands."