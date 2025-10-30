Vector Utilities for LoomLite v5.2

Provides functions for:
- Vector serialization/deserialization (SQLite BLOB storage)
- Vector fingerprinting (provenance tracking)
- Vector comparison and similarity

"""

import numpy as np
import zlib
import hashlib
from datetime import datetime
from typing import Optional, Dict, Any

# ==================== SERIALIZATION ====================

def serialize_vector(vector: np.ndarray) -> bytes:
    """
    Serialize vector for SQLite BLOB storage (compressed)
    
    Args:
        vector: NumPy array of floats
        
    Returns:
        Compressed bytes suitable for SQLite BLOB
        
    Example:
        >>> vec = np.array([0.1, 0.2, 0.3])
        >>> blob = serialize_vector(vec)
        >>> len(blob)  # Much smaller than 384 * 4 bytes
        50
    """
    # Convert to float32 for efficiency
    vector_f32 = vector.astype(np.float32)
    
    # Compress with zlib (60-70% reduction)
    compressed = zlib.compress(vector_f32.tobytes())
    