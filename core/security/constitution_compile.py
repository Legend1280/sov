"""
Sovereignty Constitution Compiler

Compiles constitution.yaml to executable JSON format with SHA3-512 hash.
Adapted to use PulseBus instead of HTTP for distribution.

Author: Brady Simmons
Copyright: © 2025 Sovereignty Foundation. All rights reserved.
"""

import yaml
import json
import hashlib
import datetime
from pathlib import Path

def compile_constitution():
    """Compile constitution.yaml to constitution.json with SHA3-512 hash"""
    
    constitution_path = Path(__file__).parent / 'constitution.yaml'
    output_path = Path(__file__).parent / 'constitution.json'
    
    print("[Constitution] Loading constitution.yaml...")
    with open(constitution_path, 'r', encoding='utf-8') as f:
        doc = yaml.safe_load(f)
    
    # Generate canonical JSON representation
    doc_json = json.dumps(doc, indent=2, ensure_ascii=False, sort_keys=True)
    
    # Calculate SHA3-512 hash
    hashval = hashlib.sha3_512(doc_json.encode('utf-8')).hexdigest()
    
    print(f"[Constitution] SHA3-512 hash: {hashval[:16]}...")
    
    # Create compiled constitution
    compiled = {
        "constitution_id": doc["constitution"]["id"],
        "version": doc["constitution"]["version"],
        "title": doc["constitution"]["title"],
        "preamble": doc["constitution"]["preamble"],
        "source_code": doc["constitution"]["source_code"],
        "rights": doc["constitution"]["rights"],
        "obligations": doc["constitution"]["obligations"],
        "enforcement": doc["constitution"]["enforcement"],
        "amendment_rules": doc["constitution"]["amendment_rules"],
        "governance": doc["constitution"]["governance"],
        "checksum": doc["constitution"]["checksum"],
        "provenance": {
            "compiled_at": datetime.datetime.utcnow().isoformat() + 'Z',
            "hash": "SHA3-512:" + hashval,
            "compiler_version": "1.0.0"
        }
    }
    
    # Write compiled constitution
    with open(output_path, 'w', encoding='utf-8') as out:
        json.dump(compiled, out, indent=2, ensure_ascii=False)
    
    print(f"[Constitution] ✅ Compiled successfully to {output_path}")
    print(f"[Constitution] Constitution ID: {compiled['constitution_id']}")
    print(f"[Constitution] Version: {compiled['version']}")
    print(f"[Constitution] Hash: SHA3-512:{hashval[:32]}...")
    
    return compiled, hashval

if __name__ == "__main__":
    constitution, hash_value = compile_constitution()
    
    # Write hash to environment file for easy access
    env_file = Path(__file__).parent / 'constitution.env'
    with open(env_file, 'w') as f:
        f.write(f"CONSTITUTION_HASH=SHA3-512:{hash_value}\n")
        f.write(f"CONSTITUTION_ID={constitution['constitution_id']}\n")
        f.write(f"CONSTITUTION_VERSION={constitution['version']}\n")
    
    print(f"[Constitution] Environment variables written to {env_file}")
    print("[Constitution] 🜂 Ready for registration across PulseMesh")
