from typing import List, Dict, Any, Optional, Tuple
from loguru import logger
from services.vector_db_service import vector_db_service
from services.llm_service import llm_service
from services.pdf_service import pdf_service


class RAGService:
    def __init__(self):
        self.vector_db = vector_db_service
        self.llm = llm_service
        self.pdf = pdf_service
    
    def process_pdf(self, file_content: bytes, filename: str) -> Tuple[str, Dict[str, Any]]:
        """Process PDF file and store in vector database"""
        try:
            # Save PDF
            file_id = self.pdf.save_pdf(file_content, filename)
            
            # Extract text chunks
            chunks = self.pdf.extract_text_from_pdf(file_id)
            
            # Add to vector database
            self.vector_db.add_documents(chunks, file_id, filename)
            
            # Get PDF info
            pdf_info = self.pdf.get_pdf_info(file_id)
            
            # Generate summary
            chunk_texts = [chunk["text"] for chunk in chunks[:5]]
            summary = self.llm.summarize_document(chunk_texts, filename)
            
            result = {
                "file_id": file_id,
                "filename": filename,
                "pages": pdf_info["pages"],
                "chunks": len(chunks),
                "summary": summary
            }
            
            return file_id, result
        except Exception as e:
            logger.error(f"Error processing PDF: {e}")
            raise
    
    def query(
        self,
        query: str,
        file_ids: Optional[List[str]] = None,
        chat_history: Optional[List[Dict[str, str]]] = None,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """Query the RAG system"""
        try:
            # Search for relevant documents
            search_results = self.vector_db.search(query, top_k=top_k, file_ids=file_ids)
            
            # Generate response using LLM
            response = self.llm.generate_response(query, search_results, chat_history)
            
            # Format sources
            sources = []
            seen_sources = set()
            for result in search_results:
                metadata = result.get("metadata", {})
                source_key = f"{metadata.get('filename')}_{metadata.get('page')}"
                if source_key not in seen_sources:
                    seen_sources.add(source_key)
                    sources.append({
                        "filename": metadata.get("filename"),
                        "page": metadata.get("page"),
                        "file_id": metadata.get("file_id")
                    })
            
            return {
                "response": response,
                "sources": sources,
                "context_used": len(search_results)
            }
        except Exception as e:
            logger.error(f"Error querying RAG system: {e}")
            raise
    
    def list_documents(self) -> List[Dict[str, str]]:
        """List all documents in the system"""
        return self.vector_db.get_all_files()
    
    def delete_document(self, file_id: str):
        """Delete a document from the system"""
        self.vector_db.delete_by_file_id(file_id)
        # Optionally delete the PDF file
        import os
        pdf_path = os.path.join(self.pdf.storage_path, f"{file_id}.pdf")
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
        logger.info(f"Deleted document: {file_id}")


rag_service = RAGService()