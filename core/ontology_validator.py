"""
Ontology Validator
Validates objects against the Core ontology definitions
"""

import yaml
import os
from datetime import datetime
from typing import Dict, Any, List, Optional

class OntologyValidator:
    """Validates objects against ontology schemas"""
    
    def __init__(self, ontology_dir: str = "./ontology"):
        self.ontology_dir = ontology_dir
        self.base_ontology = self._load_ontology("base_ontology.yaml")
        self.financial_ontology = self._load_ontology("financial_ontology.yaml")
        
        # Merge ontologies
        self.ontology = self._merge_ontologies(
            self.base_ontology,
            self.financial_ontology
        )
    
    def _load_ontology(self, filename: str) -> Dict:
        """Load an ontology YAML file"""
        path = os.path.join(self.ontology_dir, filename)
        if not os.path.exists(path):
            return {}
        
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    
    def _merge_ontologies(self, base: Dict, extension: Dict) -> Dict:
        """Merge base and extension ontologies"""
        merged = base.copy()
        
        if 'objects' in extension:
            if 'objects' not in merged:
                merged['objects'] = {}
            merged['objects'].update(extension['objects'])
        
        if 'relation_types' in extension:
            if 'relation_types' not in merged:
                merged['relation_types'] = {}
            merged['relation_types'].update(extension['relation_types'])
        
        return merged
    
    def validate(self, obj: Dict[str, Any], object_type: str) -> tuple[bool, List[str]]:
        """
        Validate an object against its ontology definition
        
        Returns:
            (is_valid, errors)
        """
        errors = []
        
        # Check if object type exists
        if object_type not in self.ontology.get('objects', {}):
            errors.append(f"Unknown object type: {object_type}")
            return False, errors
        
        schema = self.ontology['objects'][object_type]
        
        # Validate required properties
        required_props = self._get_required_properties(schema)
        for prop in required_props:
            if prop not in obj:
                errors.append(f"Missing required property: {prop}")
        
        # Validate property types
        if 'properties' in schema:
            for prop_name, prop_def in schema['properties'].items():
                if prop_name in obj:
                    is_valid, error = self._validate_property(
                        obj[prop_name],
                        prop_def
                    )
                    if not is_valid:
                        errors.append(f"Property '{prop_name}': {error}")
        
        return len(errors) == 0, errors
    
    def _get_required_properties(self, schema: Dict) -> List[str]:
        """Get list of required properties from schema"""
        required = []
        
        # Check if this schema inherits from another
        if 'inherits' in schema:
            parent_name = schema['inherits']
            if parent_name in self.ontology.get('objects', {}):
                parent_schema = self.ontology['objects'][parent_name]
                required.extend(self._get_required_properties(parent_schema))
        
        # Add this schema's required properties
        if 'properties' in schema:
            for prop_name, prop_def in schema['properties'].items():
                if isinstance(prop_def, dict) and prop_def.get('required', False):
                    required.append(prop_name)
        
        return required
    
    def _validate_property(self, value: Any, prop_def: Dict) -> tuple[bool, Optional[str]]:
        """Validate a property value against its definition"""
        prop_type = prop_def.get('type', 'String')
        
        # Type validation
        if prop_type == 'String':
            if not isinstance(value, str):
                return False, f"Expected String, got {type(value).__name__}"
        
        elif prop_type == 'Number':
            if not isinstance(value, (int, float)):
                return False, f"Expected Number, got {type(value).__name__}"
        
        elif prop_type == 'Integer':
            if not isinstance(value, int):
                return False, f"Expected Integer, got {type(value).__name__}"
        
        elif prop_type == 'Float':
            if not isinstance(value, float):
                return False, f"Expected Float, got {type(value).__name__}"
        
        elif prop_type == 'Boolean':
            if not isinstance(value, bool):
                return False, f"Expected Boolean, got {type(value).__name__}"
        
        elif prop_type == 'Date':
            # Validate ISO date format
            try:
                datetime.fromisoformat(str(value))
            except:
                return False, f"Invalid date format (expected YYYY-MM-DD)"
        
        elif prop_type == 'DateTime':
            # Validate ISO datetime format
            try:
                datetime.fromisoformat(str(value))
            except:
                return False, f"Invalid datetime format (expected ISO 8601)"
        
        # Enum validation
        if 'enum' in prop_def:
            if value not in prop_def['enum']:
                return False, f"Value must be one of {prop_def['enum']}"
        
        return True, None
    
    def get_schema(self, object_type: str) -> Optional[Dict]:
        """Get the full schema for an object type"""
        return self.ontology.get('objects', {}).get(object_type)
    
    def list_object_types(self) -> List[str]:
        """List all available object types"""
        return list(self.ontology.get('objects', {}).keys())


# Singleton instance
_validator = None

def get_validator(ontology_dir: str = "./ontology") -> OntologyValidator:
    """Get the global ontology validator instance"""
    global _validator
    if _validator is None:
        _validator = OntologyValidator(ontology_dir)
    return _validator
