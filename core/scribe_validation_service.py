#!/usr/bin/env python3
"""
Scribe Validation Service
Empirical testing of Scribe Fusion vs MiniLM baseline
Communicates via PulseMesh
"""

import asyncio
import json
import time
import numpy as np
import websockets
from datetime import datetime
from typing import Dict, List, Any
from sentence_transformers import SentenceTransformer

# Initialize MiniLM for baseline comparison
print("[Scribe Validation] Loading MiniLM model...")
miniLM_model = SentenceTransformer('all-MiniLM-L6-v2')
print("[Scribe Validation] MiniLM loaded")

# Test samples (from training dataset)
TEST_SAMPLES = [
    {
        "id": "pm_001",
        "category": "personal_memory",
        "narrative": "I remember the summer of 2018 when I learned to surf in California. The waves were perfect that day.",
        "modal": "experiential",
        "temporal": "past",
        "role": "first_person"
    },
    {
        "id": "cf_001",
        "category": "creative_fiction",
        "narrative": "The dragon soared over the misty mountains, its scales glinting in the moonlight.",
        "modal": "imaginative",
        "temporal": "present",
        "role": "third_person"
    },
    {
        "id": "cd_001",
        "category": "conversational_dialogue",
        "narrative": "Hey, did you see the game last night? That last-minute goal was incredible!",
        "modal": "interactive",
        "temporal": "past",
        "role": "first_person"
    },
    {
        "id": "td_001",
        "category": "technical_documentation",
        "narrative": "The transformer architecture uses self-attention mechanisms to process sequential data efficiently.",
        "modal": "instructional",
        "temporal": "present",
        "role": "instructional"
    }
]

class ScribeValidationService:
    def __init__(self):
        self.ws = None
        self.test_results = []
        self.scribe_ws = None  # Connection to Scribe service
        
    async def connect_pulsemesh(self):
        """Connect to PulseMesh"""
        uri = "ws://localhost:8088/ws/mesh/scribe_validation"
        print(f"[Scribe Validation] Connecting to PulseMesh: {uri}")
        self.ws = await websockets.connect(uri)
        print("[Scribe Validation] ✅ Connected to PulseMesh")
        
    async def connect_scribe(self):
        """Connect to Scribe service"""
        uri = "ws://localhost:8088/ws/mesh/scribe"
        print(f"[Scribe Validation] Connecting to Scribe service: {uri}")
        self.scribe_ws = await websockets.connect(uri)
        print("[Scribe Validation] ✅ Connected to Scribe")
        
    async def send_pulse(self, pulse: Dict[str, Any]):
        """Send pulse to PulseMesh"""
        await self.ws.send(json.dumps(pulse))
        
    async def compose_wisp_via_scribe(self, embeddings: Dict[str, List[float]]) -> Dict[str, Any]:
        """Request Wisp composition from Scribe service"""
        request = {
            "type": "scribe.compose",
            "source": "scribe_validation",
            "target": "scribe",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "payload": {
                "narrative": embeddings["narrative"],
                "modal": embeddings["modal"],
                "temporal": embeddings["temporal"],
                "role": embeddings["role"]
            }
        }
        
        # Send to Scribe
        await self.scribe_ws.send(json.dumps(request))
        
        # Wait for response
        response_str = await self.scribe_ws.recv()
        response = json.loads(response_str)
        
        return response
        
    def generate_embeddings(self, sample: Dict[str, str]) -> Dict[str, List[float]]:
        """Generate embeddings for all modalities using MiniLM"""
        # Narrative embedding
        narrative_emb = miniLM_model.encode(sample["narrative"]).tolist()
        
        # Modal embedding (encode the modal type)
        modal_emb = miniLM_model.encode(f"modality: {sample['modal']}").tolist()
        
        # Temporal embedding
        temporal_emb = miniLM_model.encode(f"temporal: {sample['temporal']}").tolist()
        
        # Role embedding
        role_emb = miniLM_model.encode(f"role: {sample['role']}").tolist()
        
        return {
            "narrative": narrative_emb,
            "modal": modal_emb,
            "temporal": temporal_emb,
            "role": role_emb
        }
        
    def miniLM_baseline(self, sample: Dict[str, str]) -> tuple:
        """Baseline: MiniLM encoding concatenated text"""
        # Concatenate all modalities
        text = f"{sample['narrative']} [Modal: {sample['modal']}, Temporal: {sample['temporal']}, Role: {sample['role']}]"
        
        # Measure latency
        start = time.time()
        embedding = miniLM_model.encode(text)
        latency_ms = (time.time() - start) * 1000
        
        return embedding.tolist(), latency_ms
        
    def cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity"""
        a_np = np.array(a)
        b_np = np.array(b)
        return float(np.dot(a_np, b_np) / (np.linalg.norm(a_np) * np.linalg.norm(b_np)))
        
    def l2_distance(self, a: List[float], b: List[float]) -> float:
        """Calculate L2 distance"""
        a_np = np.array(a)
        b_np = np.array(b)
        return float(np.linalg.norm(a_np - b_np))
        
    async def run_single_test(self, sample: Dict[str, str]) -> Dict[str, Any]:
        """Run a single validation test"""
        print(f"[Scribe Validation] Testing sample: {sample['id']} ({sample['category']})")
        
        # Generate embeddings
        embeddings = self.generate_embeddings(sample)
        
        # Test Scribe composition
        start = time.time()
        scribe_response = await self.compose_wisp_via_scribe(embeddings)
        scribe_latency_ms = (time.time() - start) * 1000
        
        # Extract Wisp from response
        if scribe_response.get("type") == "scribe.composed":
            wisp = scribe_response["payload"]["wisp"]
            scribe_coherence = scribe_response["payload"]["coherence"]
        else:
            print(f"[Scribe Validation] Error: {scribe_response}")
            return None
            
        # Test MiniLM baseline
        baseline_emb, miniLM_latency_ms = self.miniLM_baseline(sample)
        
        # Calculate metrics
        coherence = self.cosine_similarity(wisp, embeddings["narrative"])
        semantic_drift = self.l2_distance(wisp, embeddings["narrative"])
        
        # Determine pass/fail
        passed = (
            coherence >= 0.90 and
            scribe_latency_ms < 100 and
            semantic_drift < 0.1
        )
        
        result = {
            "test_id": sample["id"],
            "category": sample["category"],
            "scribe_latency_ms": round(scribe_latency_ms, 2),
            "miniLM_latency_ms": round(miniLM_latency_ms, 2),
            "coherence": round(coherence, 4),
            "scribe_coherence": round(scribe_coherence, 4),
            "semantic_drift": round(semantic_drift, 4),
            "status": "pass" if passed else "fail",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        print(f"[Scribe Validation] Result: {result['status']} (coherence: {result['coherence']}, latency: {result['scribe_latency_ms']}ms)")
        
        return result
        
    async def run_test_suite(self, test_type: str, category: str = None):
        """Run a suite of tests"""
        print(f"[Scribe Validation] Running test suite: {test_type}")
        
        # Filter samples by category if specified
        samples = TEST_SAMPLES
        if category:
            samples = [s for s in TEST_SAMPLES if s["category"] == category]
            
        results = []
        for sample in samples:
            result = await self.run_single_test(sample)
            if result:
                results.append(result)
                self.test_results.append(result)
                
                # Send result pulse
                await self.send_pulse({
                    "type": "scribe_validation.test_result",
                    "source": "scribe_validation",
                    "target": "mirror",
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "payload": result
                })
                
        # Calculate summary statistics
        passed = len([r for r in results if r["status"] == "pass"])
        failed = len(results) - passed
        mean_latency = np.mean([r["scribe_latency_ms"] for r in results])
        mean_coherence = np.mean([r["coherence"] for r in results])
        
        summary = {
            "total_tests": len(results),
            "passed": passed,
            "failed": failed,
            "success_rate": passed / len(results) if results else 0,
            "mean_scribe_latency_ms": round(mean_latency, 2),
            "mean_coherence": round(mean_coherence, 4),
            "mean_miniLM_latency_ms": round(np.mean([r["miniLM_latency_ms"] for r in results]), 2)
        }
        
        # Send completion pulse
        await self.send_pulse({
            "type": "scribe_validation.test_complete",
            "source": "scribe_validation",
            "target": "mirror",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "payload": summary
        })
        
        print(f"[Scribe Validation] Test suite complete: {summary}")
        
    async def handle_message(self, message: Dict[str, Any]):
        """Handle incoming Pulse messages"""
        msg_type = message.get("type")
        
        if msg_type == "scribe_validation.run_test":
            payload = message.get("payload", {})
            test_type = payload.get("test_type", "single")
            category = payload.get("category")
            
            await self.run_test_suite(test_type, category)
            
    async def listen(self):
        """Listen for Pulse messages"""
        print("[Scribe Validation] Listening for test requests...")
        async for message_str in self.ws:
            try:
                message = json.loads(message_str)
                await self.handle_message(message)
            except Exception as e:
                print(f"[Scribe Validation] Error handling message: {e}")
                
    async def run(self):
        """Main service loop"""
        await self.connect_pulsemesh()
        await self.connect_scribe()
        await self.listen()

if __name__ == "__main__":
    service = ScribeValidationService()
    asyncio.run(service.run())
