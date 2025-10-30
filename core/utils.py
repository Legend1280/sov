"""
Utility functions for Core
"""

import json
from typing import Any

def sanitize_for_json(obj: Any) -> Any:
    """
    Recursively sanitize an object to be JSON serializable
    
    Converts:
    - bytes → None (can't serialize)
    - sets → lists
    - other non-serializable → str
    """
    if obj is None:
        return None
    
    if isinstance(obj, (str, int, float, bool)):
        return obj
    
    if isinstance(obj, bytes):
        # Can't serialize bytes, return None
        return None
    
    if isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    
    if isinstance(obj, (list, tuple)):
        return [sanitize_for_json(item) for item in obj]
    
    if isinstance(obj, set):
        return [sanitize_for_json(item) for item in obj]
    
    # Try to convert to string as last resort
    try:
        json.dumps(obj)
        return obj
    except:
        return str(obj)
