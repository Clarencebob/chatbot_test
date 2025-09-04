from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class FeishuMessage(BaseModel):
    """Feishu message model"""
    message_id: str
    user_id: str
    content: str
    chat_id: Optional[str] = None
    timestamp: Optional[datetime] = None


class FeishuEvent(BaseModel):
    """Feishu event model"""
    schema: str
    header: Dict[str, Any]
    event: Dict[str, Any]


class ChatRequest(BaseModel):
    """Chat request model"""
    message: str
    user_id: str
    session_id: Optional[str] = None
    context: Optional[List[Dict[str, str]]] = None


class ChatResponse(BaseModel):
    """Chat response model"""
    message: str
    sources: Optional[List[Dict[str, Any]]] = None
    session_id: str


class PDFUploadResponse(BaseModel):
    """PDF upload response model"""
    file_id: str
    filename: str
    pages: int
    chunks: int
    message: str