import openai
from typing import List, Dict, Any, Optional
from loguru import logger
from config.settings import settings


class LLMService:
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
    
    def generate_response(
        self,
        query: str,
        context: List[Dict[str, Any]],
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Generate response using LLM with context"""
        
        # Prepare context from search results
        context_text = self._prepare_context(context)
        
        # Prepare messages
        messages = [
            {
                "role": "system",
                "content": """You are a helpful assistant that answers questions based on the provided context.
                If the context contains relevant information, use it to answer the question.
                If the context doesn't contain enough information, say so.
                Always cite the source (filename and page number) when using information from the context."""
            }
        ]
        
        # Add chat history if available
        if chat_history:
            for msg in chat_history[-5:]:  # Last 5 messages for context
                messages.append(msg)
        
        # Add current query with context
        user_message = f"Context:\n{context_text}\n\nQuestion: {query}"
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            return "I'm sorry, I encountered an error while processing your request. Please try again."
    
    def _prepare_context(self, context: List[Dict[str, Any]]) -> str:
        """Prepare context text from search results"""
        if not context:
            return "No relevant context found."
        
        context_parts = []
        for i, item in enumerate(context):
            metadata = item.get("metadata", {})
            text = item.get("text", "")
            filename = metadata.get("filename", "Unknown")
            page = metadata.get("page", "Unknown")
            
            context_parts.append(
                f"[Source {i+1}: {filename}, Page {page}]\n{text}\n"
            )
        
        return "\n".join(context_parts)
    
    def summarize_document(self, chunks: List[str], filename: str) -> str:
        """Generate a summary of the document"""
        # Combine chunks (limit to avoid token limits)
        text = " ".join(chunks[:10])  # First 10 chunks
        
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant that creates concise summaries of documents."
            },
            {
                "role": "user",
                "content": f"Please provide a brief summary of the following document '{filename}':\n\n{text[:3000]}"
            }
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.5,
                max_tokens=200
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return "Unable to generate summary."


llm_service = LLMService()