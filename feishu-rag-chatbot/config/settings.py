from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Feishu Configuration
    feishu_app_id: str
    feishu_app_secret: str
    feishu_verification_token: str
    feishu_encrypt_key: Optional[str] = None
    
    # OpenAI Configuration
    openai_api_key: str
    openai_model: str = "gpt-3.5-turbo"
    
    # Server Configuration
    server_host: str = "0.0.0.0"
    server_port: int = 8000
    debug: bool = False
    
    # Vector Database Configuration
    chroma_persist_directory: str = "./storage/vectordb"
    embedding_model: str = "all-MiniLM-L6-v2"
    
    # Storage Configuration
    pdf_storage_path: str = "./storage/pdfs"
    max_file_size_mb: int = 50
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()