from fastapi import FastAPI, Request, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import json
import os
from typing import Optional, Dict, Any
from loguru import logger

from config.settings import settings
from models.chat_models import FeishuEvent, ChatRequest, ChatResponse, PDFUploadResponse
from services.feishu_service import feishu_service
from services.rag_service import rag_service
from app.feishu_handler import handle_feishu_event


# Configure logger
logger.add("logs/app.log", rotation="500 MB", level="INFO")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Feishu RAG Chatbot...")
    yield
    # Shutdown
    logger.info("Shutting down Feishu RAG Chatbot...")


app = FastAPI(
    title="Feishu RAG Chatbot",
    description="A chatbot for Feishu with RAG capabilities",
    version="1.0.0",
    lifespan=lifespan
)

# Mount static files
static_path = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")


@app.get("/")
async def root():
    # Serve the test interface
    index_path = os.path.join(static_path, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Feishu RAG Chatbot is running!"}


@app.post("/webhook/feishu")
async def feishu_webhook(request: Request):
    """Handle Feishu webhook events"""
    try:
        # Get request body
        body = await request.body()
        
        # Get headers for verification
        timestamp = request.headers.get("X-Lark-Request-Timestamp", "")
        nonce = request.headers.get("X-Lark-Request-Nonce", "")
        signature = request.headers.get("X-Lark-Signature", "")
        
        # Verify request (optional but recommended)
        # if not feishu_service.verify_request(timestamp, nonce, signature, body):
        #     raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Parse event
        event_data = json.loads(body)
        
        # Handle URL verification challenge
        if event_data.get("type") == "url_verification":
            return JSONResponse(content={"challenge": event_data.get("challenge")})
        
        # Handle event
        response = await handle_feishu_event(event_data)
        
        return JSONResponse(content=response)
    
    except Exception as e:
        logger.error(f"Error handling Feishu webhook: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat endpoint for direct API access"""
    try:
        # Query RAG system
        result = rag_service.query(
            query=request.message,
            chat_history=request.context
        )
        
        return ChatResponse(
            message=result["response"],
            sources=result["sources"],
            session_id=request.session_id or "default"
        )
    
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/upload_pdf", response_model=PDFUploadResponse)
async def upload_pdf(
    file: UploadFile = File(...),
    description: Optional[str] = Form(None)
):
    """Upload and process PDF file"""
    try:
        # Validate file
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # Check file size
        content = await file.read()
        file_size_mb = len(content) / (1024 * 1024)
        if file_size_mb > settings.max_file_size_mb:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds {settings.max_file_size_mb}MB limit"
            )
        
        # Process PDF
        file_id, result = rag_service.process_pdf(content, file.filename)
        
        return PDFUploadResponse(
            file_id=file_id,
            filename=file.filename,
            pages=result["pages"],
            chunks=result["chunks"],
            message=f"Successfully processed PDF: {file.filename}"
        )
    
    except Exception as e:
        logger.error(f"Error uploading PDF: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/documents")
async def list_documents():
    """List all documents in the system"""
    try:
        documents = rag_service.list_documents()
        return {"documents": documents}
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/documents/{file_id}")
async def delete_document(file_id: str):
    """Delete a document from the system"""
    try:
        rag_service.delete_document(file_id)
        return {"message": f"Document {file_id} deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "feishu-rag-chatbot"}