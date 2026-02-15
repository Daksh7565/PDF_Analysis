import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any
import json
import sys
import os

# Add parent directory to path for config import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config


class VectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=Config.CHROMA_PERSIST_DIR,
            settings=Settings(anonymized_telemetry=False)
        )
        # Use Chroma's default embedding function (no PyTorch needed)
        from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
        self.embedding_function = DefaultEmbeddingFunction()
        
        self.collection = self._get_or_create_collection()
    
    def _get_or_create_collection(self):
        return self.client.get_or_create_collection(
            name="pdf_documents",
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "cosine"}
        )
    
    def add_documents(self, chunks: List[Any]):
        """Add document chunks to vector store"""
        if not chunks:
            return 0
        
        ids = [chunk.chunk_id for chunk in chunks]
        texts = [chunk.text for chunk in chunks]
        
        metadatas = [{
            "pdf_name": chunk.pdf_name,
            "page_number": chunk.page_number,
            "heading": chunk.heading,
            "text_preview": chunk.text[:200],
            **chunk.metadata
        } for chunk in chunks]
        
        self.collection.add(
            ids=ids,
            documents=texts,
            metadatas=metadatas
        )
        
        return len(chunks)
    
    def query(self, query_text: str, n_results: int = 5) -> Dict[str, Any]:
        """Query similar documents"""
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results,
            include=["documents", "metadatas", "distances"]
        )
        return results
    
    def get_stats(self) -> Dict:
        """Get collection statistics"""
        return {
            "total_documents": self.collection.count(),
            "collection_name": self.collection.name
        }
    
    def clear(self):
        """Clear all documents"""
        try:
            self.client.delete_collection("pdf_documents")
        except Exception:
            pass
        self.collection = self._get_or_create_collection()