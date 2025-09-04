import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional
import uuid
from loguru import logger
from config.settings import settings


class VectorDBService:
    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=settings.chroma_persist_directory,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        self.embedding_model = SentenceTransformer(settings.embedding_model)
        self.collection_name = "pdf_documents"
        self._init_collection()
    
    def _init_collection(self):
        """Initialize or get collection"""
        try:
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"Created new collection: {self.collection_name}")
        except:
            self.collection = self.client.get_collection(name=self.collection_name)
            logger.info(f"Using existing collection: {self.collection_name}")
    
    def add_documents(self, documents: List[Dict[str, Any]], file_id: str, filename: str):
        """Add documents to vector database"""
        if not documents:
            return
        
        # Prepare data for insertion
        ids = []
        embeddings = []
        metadatas = []
        documents_text = []
        
        for doc in documents:
            doc_id = str(uuid.uuid4())
            ids.append(doc_id)
            
            # Generate embedding
            embedding = self.embedding_model.encode(doc["text"])
            embeddings.append(embedding.tolist())
            
            # Prepare metadata
            metadata = {
                "file_id": file_id,
                "filename": filename,
                "page": doc["page"],
                "chunk_id": doc["chunk_id"]
            }
            metadatas.append(metadata)
            documents_text.append(doc["text"])
        
        # Add to collection
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=documents_text
        )
        
        logger.info(f"Added {len(documents)} documents to vector database for file: {filename}")
    
    def search(self, query: str, top_k: int = 5, file_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        # Generate query embedding
        query_embedding = self.embedding_model.encode(query)
        
        # Prepare where clause for filtering
        where = None
        if file_ids:
            where = {"file_id": {"$in": file_ids}}
        
        # Search in collection
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k,
            where=where
        )
        
        # Format results
        formatted_results = []
        if results["ids"] and results["ids"][0]:
            for i in range(len(results["ids"][0])):
                formatted_results.append({
                    "id": results["ids"][0][i],
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i] if "distances" in results else None
                })
        
        return formatted_results
    
    def delete_by_file_id(self, file_id: str):
        """Delete all documents for a specific file"""
        self.collection.delete(where={"file_id": file_id})
        logger.info(f"Deleted all documents for file: {file_id}")
    
    def get_all_files(self) -> List[Dict[str, str]]:
        """Get all unique files in the database"""
        # Get all documents
        all_docs = self.collection.get()
        
        # Extract unique files
        files = {}
        if all_docs["metadatas"]:
            for metadata in all_docs["metadatas"]:
                file_id = metadata.get("file_id")
                filename = metadata.get("filename")
                if file_id and filename and file_id not in files:
                    files[file_id] = filename
        
        return [{"file_id": k, "filename": v} for k, v in files.items()]


vector_db_service = VectorDBService()