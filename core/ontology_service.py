#!/usr/bin/env python3
"""
Ontology Service - PulseMesh-based Ontology Transport
Listens for ontology_request Pulses, loads YAML ontologies, emits ontology_response Pulses
Enables true semantic transport where ontologies flow through PulseMesh
"""

import asyncio
import json
import yaml
import websockets
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

class OntologyService:
    def __init__(self):
        self.ws = None
        self.ontology_paths = [
            Path('/home/ubuntu/sov/ontology'),
            Path('/home/ubuntu/sov/core/ontology')
        ]
        self.ontology_registry = {}
        
    async def connect_pulsemesh(self):
        """Connect to PulseMesh"""
        try:
            self.ws = await websockets.connect('ws://localhost:8088/ws/mesh/ontology_service')
            print("[Ontology Service] Connected to PulseMesh")
            return True
        except Exception as e:
            print(f"[Ontology Service] Failed to connect: {e}")
            return False
    
    def scan_ontologies(self):
        """Scan ontology directories and build registry"""
        print("[Ontology Service] Scanning for ontologies...")
        
        for base_path in self.ontology_paths:
            if not base_path.exists():
                print(f"[Ontology Service] Path does not exist: {base_path}")
                continue
            
            # Find all YAML files
            for yaml_file in base_path.glob('*.yaml'):
                try:
                    with open(yaml_file, 'r') as f:
                        ontology = yaml.safe_load(f)
                    
                    # Extract ontology ID
                    ontology_id = None
                    if 'id' in ontology:
                        ontology_id = ontology['id']
                    elif 'metadata' in ontology and 'name' in ontology['metadata']:
                        ontology_id = ontology['metadata']['name'].lower().replace(' ', '_')
                    else:
                        ontology_id = yaml_file.stem
                    
                    self.ontology_registry[ontology_id] = {
                        'path': str(yaml_file),
                        'id': ontology_id,
                        'name': ontology.get('metadata', {}).get('name', ontology_id),
                        'version': ontology.get('version', ontology.get('metadata', {}).get('version', '1.0.0'))
                    }
                    
                    print(f"[Ontology Service] Registered: {ontology_id} ({yaml_file.name})")
                    
                except Exception as e:
                    print(f"[Ontology Service] Error loading {yaml_file}: {e}")
        
        print(f"[Ontology Service] Registry complete: {len(self.ontology_registry)} ontologies")
    
    def load_ontology(self, ontology_id: str) -> Optional[Dict]:
        """Load ontology by ID"""
        if ontology_id not in self.ontology_registry:
            print(f"[Ontology Service] Ontology not found: {ontology_id}")
            return None
        
        registry_entry = self.ontology_registry[ontology_id]
        ontology_path = Path(registry_entry['path'])
        
        try:
            with open(ontology_path, 'r') as f:
                ontology = yaml.safe_load(f)
            
            print(f"[Ontology Service] Loaded ontology: {ontology_id}")
            return ontology
            
        except Exception as e:
            print(f"[Ontology Service] Error loading ontology {ontology_id}: {e}")
            return None
    
    async def handle_ontology_request(self, request: Dict):
        """Handle ontology_request Pulse"""
        object_id = request.get('object_id')
        source = request.get('source', 'unknown')
        
        print(f"[Ontology Service] Request from {source}: {object_id}")
        
        # Load ontology
        ontology = self.load_ontology(object_id)
        
        if ontology:
            # Emit ontology_response Pulse
            response = {
                'type': 'ontology_response',
                'source': 'ontology_service',
                'target': source,
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'object_id': object_id,
                'ontology': ontology,
                'success': True
            }
            
            await self.ws.send(json.dumps(response))
            print(f"[Ontology Service] Sent ontology: {object_id} to {source}")
        else:
            # Emit error response
            response = {
                'type': 'ontology_response',
                'source': 'ontology_service',
                'target': source,
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'object_id': object_id,
                'success': False,
                'error': f"Ontology not found: {object_id}"
            }
            
            await self.ws.send(json.dumps(response))
            print(f"[Ontology Service] Ontology not found: {object_id}")
    
    async def handle_ontology_list_request(self, request: Dict):
        """Handle ontology_list_request Pulse"""
        source = request.get('source', 'unknown')
        
        print(f"[Ontology Service] List request from {source}")
        
        # Build ontology list
        ontology_list = [
            {
                'id': entry['id'],
                'name': entry['name'],
                'version': entry['version']
            }
            for entry in self.ontology_registry.values()
        ]
        
        # Emit response
        response = {
            'type': 'ontology_list_response',
            'source': 'ontology_service',
            'target': source,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'ontologies': ontology_list,
            'count': len(ontology_list)
        }
        
        await self.ws.send(json.dumps(response))
        print(f"[Ontology Service] Sent list of {len(ontology_list)} ontologies to {source}")
    
    async def listen(self):
        """Listen for ontology requests"""
        while True:
            try:
                message_raw = await self.ws.recv()
                message = json.loads(message_raw)
                
                message_type = message.get('type')
                
                if message_type == 'ontology_request':
                    await self.handle_ontology_request(message)
                elif message_type == 'ontology_list_request':
                    await self.handle_ontology_list_request(message)
                
            except Exception as e:
                print(f"[Ontology Service] Error: {e}")
                await asyncio.sleep(1)

async def main():
    service = OntologyService()
    
    # Scan for ontologies
    service.scan_ontologies()
    
    # Connect to PulseMesh
    if not await service.connect_pulsemesh():
        return
    
    print("[Ontology Service] Ready to serve ontologies")
    
    # Listen for requests
    await service.listen()

if __name__ == "__main__":
    asyncio.run(main())
