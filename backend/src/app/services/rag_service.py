import logging
from typing import List, Dict, Any
from src.app.vector_db import vector_db
from src.app.services.llm_client import llm_client

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self):
        self.vector_db = vector_db

    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """
        Break text into overlapping character chunks for RAG indexing.
        """
        if not text:
            return []
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            start += (chunk_size - overlap)
        return chunks

    def index_user_resume(self, user_id: str, resume_text: str, metadata: Dict[str, Any] = None) -> str:
        """
        Store resume chunks into user's ChromaDB collection.
        """
        if not resume_text:
            return ""
            
        collection_name = f"user_resume_{user_id.replace('-', '_')}"
        collection = self.vector_db.get_or_create_collection(collection_name)
        
        chunks = self.chunk_text(resume_text)
        ids = [f"{user_id}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [metadata or {"user_id": user_id, "chunk_index": i} for i in range(len(chunks))]
        
        # Add to ChromaDB
        collection.upsert(
            documents=chunks,
            ids=ids,
            metadatas=metadatas
        )
        logger.info(f"Indexed {len(chunks)} RAG chunks into ChromaDB for user {user_id}")
        return collection_name

    def query_resume_context(self, user_id: str, query_text: str, top_k: int = 3) -> List[str]:
        """
        Perform RAG search against indexed resume chunks.
        """
        try:
            collection_name = f"user_resume_{user_id.replace('-', '_')}"
            collection = self.vector_db.get_or_create_collection(collection_name)
            
            results = collection.query(
                query_texts=[query_text],
                n_results=top_k
            )
            
            documents = results.get("documents", [[]])[0]
            return documents if documents else []
        except Exception as e:
            logger.error(f"Error querying RAG resume context: {e}")
            return []

    def calculate_job_match_score(self, resume_text: str, job_description: str, skills: List[str]) -> float:
        """
        Calculate match percentage score between resume and job description.
        """
        if not resume_text or not job_description:
            return 50.0 # Default baseline
            
        resume_lower = resume_text.lower()
        job_lower = job_description.lower()
        
        # 1. Skill overlap score
        skill_matches = 0
        for skill in skills:
            if skill.lower() in resume_lower:
                skill_matches += 1
                
        skill_score = (skill_matches / max(len(skills), 1)) * 100 if skills else 70.0
        
        # 2. Text keyword overlap (Jaccard similarity baseline)
        resume_words = set(resume_lower.split())
        job_words = set(job_lower.split())
        
        intersection = len(resume_words.intersection(job_words))
        union = len(resume_words.union(job_words))
        text_score = (intersection / max(union, 1)) * 300 # scale up
        
        final_score = min(max((skill_score * 0.6) + (text_score * 0.4), 40.0), 98.0)
        return round(final_score, 1)

rag_service = RAGService()
