import os
import hashlib
from typing import List, Dict, Any
import PyPDF2
import pdfplumber
from loguru import logger
from config.settings import settings


class PDFService:
    def __init__(self):
        self.storage_path = settings.pdf_storage_path
        os.makedirs(self.storage_path, exist_ok=True)
    
    def save_pdf(self, file_content: bytes, filename: str) -> str:
        """Save PDF file and return file ID"""
        file_id = self._generate_file_id(file_content)
        file_path = os.path.join(self.storage_path, f"{file_id}.pdf")
        
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        logger.info(f"Saved PDF: {filename} with ID: {file_id}")
        return file_id
    
    def extract_text_from_pdf(self, file_id: str) -> List[Dict[str, Any]]:
        """Extract text from PDF file"""
        file_path = os.path.join(self.storage_path, f"{file_id}.pdf")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found: {file_id}")
        
        chunks = []
        
        try:
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    if text:
                        # Split text into chunks (simple approach - you can improve this)
                        chunk_size = 1000
                        for i in range(0, len(text), chunk_size):
                            chunk = text[i:i + chunk_size]
                            chunks.append({
                                "text": chunk,
                                "page": page_num,
                                "file_id": file_id,
                                "chunk_id": f"{file_id}_p{page_num}_c{i//chunk_size}"
                            })
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            # Fallback to PyPDF2
            with open(file_path, "rb") as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    if text:
                        chunk_size = 1000
                        for i in range(0, len(text), chunk_size):
                            chunk = text[i:i + chunk_size]
                            chunks.append({
                                "text": chunk,
                                "page": page_num + 1,
                                "file_id": file_id,
                                "chunk_id": f"{file_id}_p{page_num + 1}_c{i//chunk_size}"
                            })
        
        logger.info(f"Extracted {len(chunks)} chunks from PDF: {file_id}")
        return chunks
    
    def get_pdf_info(self, file_id: str) -> Dict[str, Any]:
        """Get PDF file information"""
        file_path = os.path.join(self.storage_path, f"{file_id}.pdf")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found: {file_id}")
        
        with open(file_path, "rb") as f:
            pdf_reader = PyPDF2.PdfReader(f)
            num_pages = len(pdf_reader.pages)
            
        return {
            "file_id": file_id,
            "pages": num_pages,
            "path": file_path
        }
    
    def _generate_file_id(self, content: bytes) -> str:
        """Generate unique file ID from content"""
        return hashlib.md5(content).hexdigest()


pdf_service = PDFService()