"""
Core Reasoner - Semantic Reasoning Engine
The heart of the Core kernel

Combines:
- Symbolic reasoning (ontology)
- Subsymbolic reasoning (embeddings)
- Governance (SAGE)
- Provenance (audit trail)

Returns: ReasonedObject (symbolic + vector + governance + provenance)
"""

import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from storage import get_storage
from ontology import get_ontology
from embeddings import embed_object, semantic_neighbors, serialize_vector, deserialize_vector, EMBEDDING_DIM
from sage import get_sage
from utils import sanitize_for_json
from kronos import TemporalIndexer

class Reasoner:
    """Main reasoning engine for Core kernel"""
    
    def __init__(self, db_path: str = "./core.db", ontology_dir: str = "./ontology"):
        self.storage = get_storage(db_path)
        self.ontology = get_ontology(ontology_dir)
        self.sage = get_sage()
        self.kronos = TemporalIndexer(self.storage)
    
    def ingest(self, object_type: str, data: Dict[str, Any], actor: str = "system") -> Dict[str, Any]:
        """
        Ingest a new object into Core
        
        Pipeline:
        1. Validate against ontology
        2. Generate embedding
        3. Run SAGE validation
        4. Store object + vector + metadata
        5. Log provenance
        6. Return ReasonedObject
        
        Args:
            object_type: Type of object
            data: Object data
            actor: Who is ingesting this
            
        Returns:
            ReasonedObject
        """
        # 1. Validate against ontology
        is_valid, normalized_data, errors = self.ontology.validate_and_normalize(data, object_type)
        
        if not is_valid:
            raise ValueError(f"Ontology validation failed: {errors}")
        
        # 2. Save object
        object_id = self.storage.save_object(object_type, normalized_data)
        
        # 3. Generate embedding
        obj_for_embedding = {
            "object_type": object_type,
            "data": normalized_data
        }
        embedding = embed_object(obj_for_embedding)
        
        # 4. Store vector
        embedding_bytes = serialize_vector(embedding)
        self.storage.save_vector(object_id, embedding_bytes, "all-MiniLM-L6-v2", EMBEDDING_DIM)
        
        # 5. Run SAGE validation (BEFORE storing)
        provenance_chain = []  # New object, no provenance yet
        sage_metadata = self.sage.validate_object(
            {"id": object_id, "object_type": object_type, "data": normalized_data},
            embedding,
            provenance_chain
        )
        
        # 6. Enforce SAGE decision (Milestone 2)
        decision = sage_metadata["decision"]
        
        if decision == "deny":
            # Do NOT store object, but log the denial
            self.storage.log_provenance(
                object_id,
                "denied",
                actor,
                {
                    "object_type": object_type,
                    "reason": sage_metadata["rationale"],
                    "coherence_score": sage_metadata["coherence_score"],
                    "trust_score": sage_metadata["trust_score"]
                }
            )
            raise ValueError(f"SAGE denied object: {sage_metadata['rationale']}")
        
        # 7. Store SAGE metadata (for allow/flag)
        self.storage.save_sage_metadata(
            object_id,
            sage_metadata["coherence_score"],
            sage_metadata["trust_score"],
            sage_metadata["validated"]
        )
        
        # 8. Log provenance with decision
        action = "ingested" if decision == "allow" else "flagged"
        self.storage.log_provenance(
            object_id,
            action,
            actor,
            {
                "object_type": object_type,
                "validated": sage_metadata["validated"],
                "decision": decision,
                "rationale": sage_metadata["rationale"]
            }
        )
        
        # 9. Record Kronos baseline event (Milestone 5: Temporal Intelligence)
        self.kronos.record_event(
            object_id=object_id,
            event_type="baseline",
            vector=embedding,
            coherence_score=sage_metadata["coherence_score"],
            trust_score=sage_metadata["trust_score"],
            metadata={
                "actor": actor,
                "decision": decision,
                "object_type": object_type
            }
        )
        
        # 8. Find semantic relations
        relations = self._find_relations(object_id, embedding, object_type)
        
        # 9. Return ReasonedObject
        return self.reason(object_id)
    
    def reason(self, object_id: str) -> Dict[str, Any]:
        """
        Perform reasoning on an object
        
        Returns a ReasonedObject with:
        - symbolic (ontology data)
        - vector (embedding + relations)
        - provenance (audit trail)
        - sage (governance metadata)
        
        Args:
            object_id: ID of object to reason about
            
        Returns:
            ReasonedObject
        """
        # Get object
        obj = self.storage.get_object(object_id)
        if not obj:
            raise ValueError(f"Object not found: {object_id}")
        
        # Get vector
        vector_data = self.storage.get_vector(object_id)
        embedding = None
        if vector_data:
            embedding = deserialize_vector(vector_data["embedding"], EMBEDDING_DIM)
        
        # Get SAGE metadata
        sage_metadata = self.storage.get_sage_metadata(object_id)
        
        # Get provenance
        provenance = self.storage.get_provenance(object_id)
        
        # Get relations
        relations = self.storage.get_relations(object_id, limit=10)
        
        # Build ReasonedObject
        reasoned = {
            "object": obj["object_type"],
            "symbolic": {
                "id": obj["id"],
                **obj["data"],
                "created_at": obj["created_at"],
                "updated_at": obj["updated_at"]
            },
            "vector": {
                "has_embedding": embedding is not None,
                "dimension": EMBEDDING_DIM if embedding is not None else None,
                "coherence": sage_metadata["coherence_score"] if sage_metadata else None,
                "relations": [
                    {
                        "id": rel["target_id"] if rel["source_id"] == object_id else rel["source_id"],
                        "type": rel["relation_type"],
                        "similarity": rel["similarity_score"]
                    }
                    for rel in relations
                ]
            },
            "provenance": provenance,
            "sage": sage_metadata if sage_metadata else {
                "coherence_score": None,
                "trust_score": None,
                "validated": False
            }
        }
        
        # Sanitize for JSON serialization
        return sanitize_for_json(reasoned)
    
    def infer_relations(self, object_id: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Infer semantic relations for an object
        
        Args:
            object_id: Object to find relations for
            top_k: Number of relations to return
            
        Returns:
            List of related objects with similarity scores
        """
        # Get object and vector
        obj = self.storage.get_object(object_id)
        if not obj:
            raise ValueError(f"Object not found: {object_id}")
        
        vector_data = self.storage.get_vector(object_id)
        if not vector_data:
            raise ValueError(f"No vector found for object: {object_id}")
        
        query_vector = deserialize_vector(vector_data["embedding"], EMBEDDING_DIM)
        
        # Get all objects of the same type
        candidates = self.storage.query_objects(obj["object_type"], limit=1000)
        
        # Get their vectors
        candidate_vectors = []
        for candidate in candidates:
            if candidate["id"] == object_id:
                continue  # Skip self
            
            cand_vector_data = self.storage.get_vector(candidate["id"])
            if cand_vector_data:
                cand_vector = deserialize_vector(cand_vector_data["embedding"], EMBEDDING_DIM)
                candidate_vectors.append((candidate["id"], cand_vector))
        
        # Find similar
        neighbors = semantic_neighbors(query_vector, candidate_vectors, threshold=0.75, top_k=top_k)
        
        # Build result
        relations = []
        for neighbor_id, similarity in neighbors:
            neighbor_obj = self.storage.get_object(neighbor_id)
            if neighbor_obj:
                relations.append({
                    "id": neighbor_id,
                    "object_type": neighbor_obj["object_type"],
                    "similarity": similarity,
                    "data": neighbor_obj["data"]
                })
        
        return relations
    
    def _find_relations(self, object_id: str, embedding: np.ndarray, object_type: str) -> List[str]:
        """
        Find and store semantic relations
        
        Returns: List of related object IDs
        """
        # Get all objects of compatible types
        candidates = self.storage.query_objects(object_type, limit=1000)
        
        # Get their vectors
        candidate_vectors = []
        for candidate in candidates:
            if candidate["id"] == object_id:
                continue  # Skip self
            
            cand_vector_data = self.storage.get_vector(candidate["id"])
            if cand_vector_data:
                cand_vector = deserialize_vector(cand_vector_data["embedding"], EMBEDDING_DIM)
                candidate_vectors.append((candidate["id"], cand_vector))
        
        # Find similar
        neighbors = semantic_neighbors(embedding, candidate_vectors, threshold=0.80, top_k=10)
        
        # Store relations
        related_ids = []
        for neighbor_id, similarity in neighbors:
            # Validate relation with SAGE
            is_valid, reason = self.sage.validate_relation(object_type, object_type, similarity)
            
            if is_valid:
                self.storage.save_relation(
                    object_id,
                    neighbor_id,
                    "semantic_similarity",
                    similarity
                )
                related_ids.append(neighbor_id)
        
        return related_ids
    
    def query(self, object_type: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Query objects from Core
        
        Args:
            object_type: Filter by type (optional)
            limit: Maximum results
            
        Returns:
            List of ReasonedObjects
        """
        objects = self.storage.query_objects(object_type, limit)
        
        # Return reasoned versions
        return [self.reason(obj["id"]) for obj in objects]


# Singleton instance
_reasoner = None

def get_reasoner(db_path: str = "./core.db", ontology_dir: str = "./ontology") -> Reasoner:
    """Get the global reasoner instance"""
    global _reasoner
    if _reasoner is None:
        _reasoner = Reasoner(db_path, ontology_dir)
    return _reasoner
