"""
Test Core reasoning engine directly
"""

import json
from reasoner import get_reasoner

# Initialize reasoner
reasoner = get_reasoner("./test_core.db", "./ontology")

# Test transaction
transaction_data = {
    "amount": 2500.00,
    "date": "2025-10-29",
    "description": "Equipment Lease - DexaFit Denver",
    "transaction_type": "expense",
    "category": "Equipment",
    "vendor": "FitEquip Pro"
}

print("Ingesting transaction...")
try:
    reasoned = reasoner.ingest("Transaction", transaction_data, "test_script")
    print("\n✅ Transaction ingested successfully!")
    print(f"\nObject ID: {reasoned['symbolic']['id']}")
    print(f"Object Type: {reasoned['object']}")
    print(f"SAGE Validated: {reasoned['sage']['validated']}")
    print(f"Coherence Score: {reasoned['sage']['coherence_score']}")
    print(f"Trust Score: {reasoned['sage']['trust_score']}")
    print(f"Has Embedding: {reasoned['vector']['has_embedding']}")
    print(f"Relations: {len(reasoned['vector']['relations'])}")
    print(f"Provenance Events: {len(reasoned['provenance'])}")
    
    # Try to JSON serialize
    print("\nTesting JSON serialization...")
    json_str = json.dumps(reasoned, indent=2)
    print("✅ JSON serialization successful!")
    print(f"\nJSON length: {len(json_str)} bytes")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
