import logging
from typing import List
try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None
from src.app.vector_db import vector_db
from src.app.config import settings

logger = logging.getLogger(__name__)

# Lazy loaded embedding model
_model_instance = None

def get_embedding_model():
    global _model_instance
    if _model_instance is None:
        if SentenceTransformer is None:
            logger.warning("SentenceTransformer is not installed (ImportError). Using fallback mock embeddings.")
            _model_instance = "fallback"
            return _model_instance
        try:
            logger.info(f"Loading SentenceTransformer model: {settings.EMBEDDING_MODEL}")
            _model_instance = SentenceTransformer(settings.EMBEDDING_MODEL)
        except Exception as e:
            logger.warning(f"Failed to load SentenceTransformer model '{settings.EMBEDDING_MODEL}': {e}. Using fallback mock embeddings.")
            # We will use None to signify fallback mode
            _model_instance = "fallback"
    return _model_instance


def generate_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Generates high-dimensional embeddings for list of texts.
    Falls back to dummy embeddings if SentenceTransformer fails to load.
    """
    model = get_embedding_model()
    if model == "fallback" or model is None:
        # Return dummy 384-dimensional vectors (standard MiniLM size)
        logger.debug("Generating mock embeddings for testing/fallback.")
        return [[0.1] * 384 for _ in texts]
    
    try:
        return model.encode(texts).tolist()
    except Exception as e:
        logger.error(f"Error encoding texts with SentenceTransformer: {e}")
        return [[0.1] * 384 for _ in texts]

def generate_and_store_resume_embeddings(user_id: str, profile_data: dict):
    """
    Chunks the resume profile details, generates semantic embeddings,
    and indexes them in ChromaDB.
    """
    texts = []
    metadatas = []
    ids = []
    
    # 1. Skills chunk
    skills = profile_data.get("skills", [])
    if skills:
        skills_text = f"Skills: {', '.join(skills)}"
        texts.append(skills_text)
        metadatas.append({"user_id": user_id, "type": "skills"})
        ids.append(f"{user_id}_skills")
        
    # 2. Experience chunks
    for i, exp in enumerate(profile_data.get("experience", [])):
        title = exp.get("title", "N/A")
        company = exp.get("company", "N/A")
        desc = exp.get("description", "")
        exp_text = f"Work Experience: {title} at {company}. Details: {desc}"
        texts.append(exp_text)
        metadatas.append({"user_id": user_id, "type": "experience", "index": i})
        ids.append(f"{user_id}_exp_{i}")
        
    # 3. Project chunks
    for i, proj in enumerate(profile_data.get("projects", [])):
        title = proj.get("title", "N/A")
        desc = proj.get("description", "")
        proj_text = f"Project: {title}. Details: {desc}"
        texts.append(proj_text)
        metadatas.append({"user_id": user_id, "type": "project", "index": i})
        ids.append(f"{user_id}_proj_{i}")
        
    # 4. Education chunks
    for i, edu in enumerate(profile_data.get("education", [])):
        degree = edu.get("degree", "N/A")
        inst = edu.get("institution", "N/A")
        edu_text = f"Education: {degree} from {inst}."
        texts.append(edu_text)
        metadatas.append({"user_id": user_id, "type": "education", "index": i})
        ids.append(f"{user_id}_edu_{i}")

    if not texts:
        logger.warning(f"No contents found to embed for user: {user_id}")
        return

    # Store in ChromaDB
    try:
        collection = vector_db.get_or_create_collection("resumes")
        
        # Clear existing embeddings for this user to avoid duplicating or leaving stale chunks
        try:
            collection.delete(where={"user_id": user_id})
        except Exception as e:
            logger.debug(f"No old records to delete or deletion issue: {e}")
            
        # Generate vectors
        embeddings = generate_embeddings(texts)
        
        # Add to collection
        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )
        logger.info(f"Successfully generated and stored {len(texts)} embeddings in ChromaDB for user: {user_id}")
    except Exception as e:
        logger.error(f"Failed to store resume embeddings in ChromaDB: {e}")
        # Non-fatal error; don't raise so the main user upload doesn't break
