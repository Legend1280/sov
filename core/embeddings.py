"""
Embeddings Module
Wrapper around embedding_service.py for Core kernel

Provides:
- Vector generation
- Semantic similarity
- Relation inference
"""

import numpy as np
from typing import List, Tuple, Optional
from sentence_transformers import SentenceTransformer, util
import os

# Model configuration
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # 384 dimensions
EMBEDDING_DIM = 384

# Initialize model (lazy loading)
_model = None

def get_model() -> SentenceTransformer:
    """Get or initialize the embedding model (singleton)"""
    global _model
    if _model is None:
        print(f"Loading embedding model: {EMBEDDING_MODEL}...")
        _model = SentenceTransformer(EMBEDDING_MODEL)
        print(f"Model loaded. Dimension: {_model.get_sentence_embedding_dimension()}")
    return _model

def generate_embedding(text: str) -> np.ndarray:
    """
    Generate embedding for text
    
    Args:
        text: Input text
        
    Returns:
        NumPy array of shape (384,)
    """
    model = get_model()
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding

def generate_embeddings_batch(texts: List[str]) -> List[np.ndarray]:
    """
    Generate embeddings for multiple texts (more efficient)
    
    Args:
        texts: List of input texts
        
    Returns:
        List of NumPy arrays
    """
    model = get_model()
    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    return [emb for emb in embeddings]

def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """
    Calculate cosine similarity between two vectors
    
    Args:
        vec1: First vector
        vec2: Second vector
        
    Returns:
        Similarity score (0.0 - 1.0)
    """
    similarity = util.cos_sim(vec1, vec2)
    return float(similarity[0][0])

def find_similar(query_vector: np.ndarray, candidate_vectors: List[Tuple[str, np.ndarray]], top_k: int = 5) -> List[Tuple[str, float]]:
    """
    Find most similar vectors to query
    
    Args:
        query_vector: Query embedding
        candidate_vectors: List of (id, vector) tuples
        top_k: Number of results to return
        
    Returns:
        List of (id, similarity_score) tuples, sorted by similarity
    """
    if not candidate_vectors:
        return []
    
    # Calculate similarities
    similarities = []
    for obj_id, vec in candidate_vectors:
        sim = cosine_similarity(query_vector, vec)
        similarities.append((obj_id, sim))
    
    # Sort by similarity (descending)
    similarities.sort(key=lambda x: x[1], reverse=True)
    
    # Return top k
    return similarities[:top_k]

def semantic_neighbors(vector: np.ndarray, all_vectors: List[Tuple[str, np.ndarray]], threshold: float = 0.75, top_k: int = 10) -> List[Tuple[str, float]]:
    """
    Find semantic neighbors above similarity threshold
    
    Args:
        vector: Query vector
        all_vectors: List of (id, vector) tuples
        threshold: Minimum similarity score
        top_k: Maximum number of neighbors
        
    Returns:
        List of (id, similarity_score) tuples
    """
    similar = find_similar(vector, all_vectors, top_k=top_k)
    
    # Filter by threshold
    neighbors = [(obj_id, score) for obj_id, score in similar if score >= threshold]
    
    return neighbors

def serialize_vector(vector: np.ndarray) -> bytes:
    """
    Serialize vector for storage
    
    Args:
        vector: NumPy array
        
    Returns:
        Bytes suitable for BLOB storage
    """
    # Convert to float32 for efficiency
    vector_f32 = vector.astype(np.float32)
    return vector_f32.tobytes()

def deserialize_vector(blob: bytes, dimension: int = EMBEDDING_DIM) -> np.ndarray:
    """
    Deserialize vector from storage
    
    Args:
        blob: Bytes from BLOB storage
        dimension: Vector dimension
        
    Returns:
        NumPy array
    """
    vector = np.frombuffer(blob, dtype=np.float32)
    return vector.reshape(dimension)

def embed_object(obj: dict) -> np.ndarray:
    """
    Generate embedding for an object
    
    Combines relevant fields into text representation
    
    Args:
        obj: Object dictionary
        
    Returns:
        Embedding vector
    """
    # Extract text fields
    text_parts = []
    
    # Add object type
    if "object_type" in obj:
        text_parts.append(f"Type: {obj['object_type']}")
    
    # Add data fields
    if "data" in obj:
        data = obj["data"]
        for key, value in data.items():
            if isinstance(value, (str, int, float, bool)):
                text_parts.append(f"{key}: {value}")
    
    # Combine into single text
    text = " | ".join(text_parts)
    
    # Generate embedding
    return generate_embedding(text)


# Export key functions
__all__ = [
    "generate_embedding",
    "generate_embeddings_batch",
    "cosine_similarity",
    "find_similar",
    "semantic_neighbors",
    "serialize_vector",
    "deserialize_vector",
    "embed_object",
    "EMBEDDING_DIM"
]
