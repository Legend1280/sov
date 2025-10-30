#!/usr/bin/env python3
"""
Generate realistic temporal test data for Kronos visualization (v2).

This version uses the reasoner.ingest() method to ensure objects go through
the full sovereignty loop: ontology validation, embeddings, SAGE governance,
and provenance tracking.

Usage:
    python3 generate_temporal_test_data_v2.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from datetime import datetime, timedelta
from storage import CoreStorage
from reasoner import get_reasoner
import json

def generate_temporal_evolution():
    """Generate a week of temporal events for a test object."""
    
    storage = CoreStorage()
    reasoner = get_reasoner()
    
    # Create a test transaction through the reasoner
    test_object = {
        "date": "2025-10-24",
        "description": "DexaFit Denver Financial Summary (Temporal Test)",
        "category": "Revenue",
        "amount": 15000.00,
        "vendor": "DexaFit Denver",
        "account": "Operating Revenue",
        "transaction_type": "income"
    }
    
    print("Ingesting test object through reasoner...")
    result = reasoner.ingest("Transaction", test_object, actor="TemporalTestScript")
    object_id = result["symbolic"]["id"]
    
    print(f"✓ Created test object: {object_id}")
    print(f"  Description: {test_object['description']}")
    print(f"  Amount: ${test_object['amount']:,.2f}")
    print(f"  Coherence: {result['sage']['coherence_score']:.3f}")
    print(f"  Trust: {result['sage']['trust_score']:.3f}")
    print()
    
    # Define temporal evolution pattern (7 days)
    # Each event: (days_offset, event_type, coherence, trust, reason)
    evolution_pattern = [
        (0, "baseline", 0.872, 0.60, "initial_ingest"),
        (1, "update", 0.883, 0.64, "manual_review"),
        (2, "validation", 0.891, 0.69, "financial_audit"),
        (3, "update", 0.895, 0.72, "ontology_alignment"),
        (4, "drift_detected", 0.861, 0.68, "semantic_shift"),
        (5, "recovery", 0.877, 0.74, "temporal_reconciliation"),
        (6, "validation", 0.902, 0.79, "final_confirmation"),
    ]
    
    # Base timestamp (7 days ago)
    base_time = datetime.now() - timedelta(days=7)
    
    print("Generating temporal events:")
    print("-" * 70)
    
    with storage.get_connection() as conn:
        cursor = conn.cursor()
        for days_offset, event_type, coherence, trust, reason in evolution_pattern:
            event_time = base_time + timedelta(days=days_offset)
            
            # Record event with specific timestamp
            cursor.execute("""
                INSERT INTO kronos_events 
                (object_id, event_type, coherence_score, trust_score, metadata, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                object_id,
                event_type,
                coherence,
                trust,
                json.dumps({"reason": reason, "actor": get_actor(event_type)}),
                event_time.isoformat()
            ))
            conn.commit()
            
            # Display progress
            drift_indicator = ""
            if event_type == "drift_detected":
                drift_indicator = " ⚠️  DRIFT"
            elif event_type == "recovery":
                drift_indicator = " ✓ RECOVERY"
            
            print(f"Day {days_offset}: {event_type:20s} | C:{coherence:.3f} T:{trust:.3f} | {reason:25s}{drift_indicator}")
    
    print("-" * 70)
    print()
    
    # Verify events were created
    with storage.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT event_type, coherence_score, trust_score
            FROM kronos_events
            WHERE object_id = ?
            ORDER BY timestamp ASC
        """, (object_id,))
        events = cursor.fetchall()
    
    print(f"✓ Generated {len(events)} temporal events")
    print()
    
    # Calculate drift metrics
    if len(events) >= 2:
        # events are tuples: (event_type, coherence_score, trust_score)
        baseline_coherence = events[0][1]
        baseline_trust = events[0][2]
        latest_coherence = events[-1][1]
        latest_trust = events[-1][2]
        
        coherence_drift = latest_coherence - baseline_coherence
        trust_change = latest_trust - baseline_trust
        
        print("Temporal Analysis:")
        print(f"  Coherence drift: {coherence_drift:+.3f} ({baseline_coherence:.3f} → {latest_coherence:.3f})")
        print(f"  Trust evolution: {trust_change:+.3f} ({baseline_trust:.3f} → {latest_trust:.3f})")
        print()
    
    print(f"🎯 Test object ID: {object_id}")
    print()
    print("Next steps:")
    print("  1. Open Mirror UI")
    print("  2. Refresh the Financial Dashboard")
    print(f"  3. Click on '{test_object['description']}'")
    print("  4. View temporal timeline in Viewport 2")
    print()
    
    return object_id

def get_actor(event_type):
    """Return appropriate actor for event type."""
    actor_map = {
        "baseline": "Mirror",
        "update": "SAGE",
        "validation": "Human",
        "drift_detected": "Kronos",
        "recovery": "Mirror",
    }
    return actor_map.get(event_type, "System")

if __name__ == "__main__":
    print()
    print("=" * 70)
    print("  Kronos Temporal Test Data Generator v2")
    print("  Sovereignty Stack - Milestone 5.6")
    print("=" * 70)
    print()
    
    try:
        object_id = generate_temporal_evolution()
        print("✅ Temporal test data generated successfully!")
        print()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
