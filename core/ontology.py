"""
Ontology Module
Wrapper around ontology_validator.py for Core kernel

Provides:
- Schema validation
- Object type management
- Inheritance handling
"""

from typing import Dict, Any, List, Optional, Tuple
from ontology_validator import get_validator

class Ontology:
    """Ontology management for Core kernel"""
    
    def __init__(self, ontology_dir: str = "./ontology"):
        self.validator = get_validator(ontology_dir)
    
    def validate(self, obj: Dict[str, Any], object_type: str) -> Tuple[bool, List[str]]:
        """
        Validate an object against its schema
        
        Args:
            obj: Object data
            object_type: Type of object
            
        Returns:
            (is_valid, errors)
        """
        return self.validator.validate(obj, object_type)
    
    def get_schema(self, object_type: str) -> Optional[Dict]:
        """Get schema for an object type"""
        return self.validator.get_schema(object_type)
    
    def list_types(self) -> List[str]:
        """List all available object types"""
        return self.validator.list_object_types()
    
    def validate_and_normalize(self, obj: Dict[str, Any], object_type: str) -> Tuple[bool, Dict[str, Any], List[str]]:
        """
        Validate and normalize an object
        
        Args:
            obj: Object data
            object_type: Type of object
            
        Returns:
            (is_valid, normalized_obj, errors)
        """
        # Validate
        is_valid, errors = self.validate(obj, object_type)
        
        # Normalize (add defaults, clean up)
        normalized = obj.copy()
        
        # Add object_type if not present
        if "object_type" not in normalized:
            normalized["object_type"] = object_type
        
        return is_valid, normalized, errors
    
    def get_required_fields(self, object_type: str) -> List[str]:
        """Get required fields for an object type"""
        schema = self.get_schema(object_type)
        if not schema:
            return []
        
        required = []
        if "properties" in schema:
            for prop_name, prop_def in schema["properties"].items():
                if isinstance(prop_def, dict) and prop_def.get("required", False):
                    required.append(prop_name)
        
        return required
    
    def is_type_compatible(self, type1: str, type2: str) -> bool:
        """
        Check if two types are compatible for relations
        
        Args:
            type1: First type
            type2: Second type
            
        Returns:
            True if compatible
        """
        # Same type is always compatible
        if type1 == type2:
            return True
        
        # Check inheritance
        schema1 = self.get_schema(type1)
        schema2 = self.get_schema(type2)
        
        if schema1 and "inherits" in schema1:
            if schema1["inherits"] == type2:
                return True
        
        if schema2 and "inherits" in schema2:
            if schema2["inherits"] == type1:
                return True
        
        # Predefined compatible pairs
        compatible_pairs = [
            ("Transaction", "Account"),
            ("Forecast", "Transaction"),
            ("Document", "Concept"),
        ]
        
        pair = (type1, type2)
        reverse_pair = (type2, type1)
        
        return pair in compatible_pairs or reverse_pair in compatible_pairs


# Singleton instance
_ontology = None

def get_ontology(ontology_dir: str = "./ontology") -> Ontology:
    """Get the global ontology instance"""
    global _ontology
    if _ontology is None:
        _ontology = Ontology(ontology_dir)
    return _ontology
