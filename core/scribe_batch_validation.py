#!/usr/bin/env python3
"""
Scribe Batch Validation Service
Comprehensive testing of Scribe Fusion vs MiniLM baseline
Supports batch sizes: 10, 50, 100, 200
Includes statistical analysis: t-tests, effect sizes, confidence intervals
Communicates via PulseMesh
"""

import asyncio
import json
import time
import numpy as np
import websockets
from datetime import datetime
from typing import Dict, List, Any, Tuple
from sentence_transformers import SentenceTransformer
from scipy import stats
from scipy.spatial.distance import cosine

# Initialize MiniLM for baseline comparison
print("[Batch Validation] Loading MiniLM model...")
miniLM_model = SentenceTransformer('all-MiniLM-L6-v2')
print("[Batch Validation] MiniLM loaded (384 dimensions)")

# Expanded test dataset (200 samples across 4 categories)
def generate_test_samples(count: int = 200) -> List[Dict]:
    """Generate diverse test samples across all 4 categories"""
    
    personal_memory_templates = [
        "I remember {} when I {}. It was {}.",
        "Back in {}, I experienced {}. The feeling was {}.",
        "My memory of {} is vivid. I was {} and felt {}.",
        "During {}, I learned {}. That moment was {}.",
        "I'll never forget {} when {}. Everything felt {}."
    ]
    
    creative_fiction_templates = [
        "The {} {} across the {}. Its {} was {}.",
        "In a world where {}, the {} {}. Everything was {}.",
        "She {} the {} with {}. The {} was {}.",
        "The ancient {} {} in the {}. Its power was {}.",
        "Beyond the {}, {} awaited. The {} was {}."
    ]
    
    conversational_templates = [
        "Hey, did you {}? That was {}!",
        "I can't believe {}. It's so {}!",
        "Have you heard about {}? It's really {}.",
        "What do you think about {}? I find it {}.",
        "Did you see {}? That was absolutely {}!"
    ]
    
    technical_templates = [
        "The {} function implements {}. It returns {}.",
        "This {} utilizes {} to achieve {}.",
        "The {} class provides {} for {}.",
        "To configure {}, use {} with {}.",
        "The {} method processes {} and outputs {}."
    ]
    
    samples = []
    samples_per_category = count // 4
    
    # Generate personal memory samples
    for i in range(samples_per_category):
        template = personal_memory_templates[i % len(personal_memory_templates)]
        samples.append({
            "id": f"pm_{i:03d}",
            "category": "personal_memory",
            "narrative": template.format(
                ["summer 2018", "winter 2020", "spring 2019", "fall 2021"][i % 4],
                ["learned to surf", "climbed a mountain", "started painting", "wrote a novel"][i % 4],
                ["transformative", "challenging", "peaceful", "exciting"][i % 4]
            ),
            "modal": ["experiential", "reflective", "emotional", "analytical"][i % 4],
            "temporal": ["past", "recent_past", "distant_past", "childhood"][i % 4],
            "role": "first_person"
        })
    
    # Generate creative fiction samples
    for i in range(samples_per_category):
        template = creative_fiction_templates[i % len(creative_fiction_templates)]
        samples.append({
            "id": f"cf_{i:03d}",
            "category": "creative_fiction",
            "narrative": template.format(
                ["dragon", "spaceship", "wizard", "robot", "phoenix"][i % 5],
                ["soared", "glided", "materialized", "descended", "emerged"][i % 5],
                ["misty mountains", "starlit void", "ancient forest", "neon city", "crystal cavern"][i % 5],
                ["scales", "hull", "robes", "circuits", "feathers"][i % 5],
                ["glinting", "gleaming", "shimmering", "pulsing", "radiant"][i % 5]
            ),
            "modal": ["imaginative", "descriptive", "dramatic", "poetic"][i % 4],
            "temporal": ["present", "timeless", "future", "mythical"][i % 4],
            "role": ["third_person", "omniscient", "limited"][i % 3]
        })
    
    # Generate conversational samples
    for i in range(samples_per_category):
        template = conversational_templates[i % len(conversational_templates)]
        samples.append({
            "id": f"cd_{i:03d}",
            "category": "conversational_dialogue",
            "narrative": template.format(
                ["see the game last night", "hear the news", "check out that video", "try the new restaurant"][i % 4],
                ["incredible", "amazing", "unbelievable", "fantastic"][i % 4]
            ),
            "modal": ["interactive", "casual", "enthusiastic", "inquisitive"][i % 4],
            "temporal": ["immediate_past", "present", "recent"][i % 3],
            "role": "first_person"
        })
    
    # Generate technical documentation samples
    for i in range(samples_per_category):
        template = technical_templates[i % len(technical_templates)]
        samples.append({
            "id": f"td_{i:03d}",
            "category": "technical_documentation",
            "narrative": template.format(
                ["transform", "validate", "serialize", "authenticate", "optimize"][i % 5],
                ["data structures", "input parameters", "API requests", "user credentials", "algorithms"][i % 5],
                ["validated results", "boolean status", "JSON objects", "auth tokens", "performance metrics"][i % 5]
            ),
            "modal": ["instructional", "descriptive", "procedural", "explanatory"][i % 4],
            "temporal": ["present", "imperative", "conditional"][i % 3],
            "role": ["second_person", "third_person"][i % 2]
        })
    
    return samples

# Generate full test dataset
ALL_SAMPLES = generate_test_samples(200)
print(f"[Batch Validation] Generated {len(ALL_SAMPLES)} test samples")

class BatchValidationService:
    def __init__(self):
        self.ws = None
        self.scribe_ws = None
        self.current_batch = None
        self.batch_results = []
        
    async def connect_pulsemesh(self):
        """Connect to PulseMesh"""
        try:
            self.ws = await websockets.connect('ws://localhost:8088/ws/mesh/scribe_batch_validation')
            print("[Batch Validation] Connected to PulseMesh")
            return True
        except Exception as e:
            print(f"[Batch Validation] Failed to connect: {e}")
            return False
    
    async def connect_scribe(self):
        """Connect to Scribe topic for composition"""
        try:
            self.scribe_ws = await websockets.connect('ws://localhost:8088/ws/mesh/scribe')
            print("[Batch Validation] Connected to Scribe topic")
            return True
        except Exception as e:
            print(f"[Batch Validation] Failed to connect to Scribe: {e}")
            return False
    
    def generate_embeddings(self, sample: Dict) -> Dict[str, np.ndarray]:
        """Generate embeddings for all 4 modalities"""
        embeddings = {}
        
        # Narrative embedding
        embeddings['narrative'] = miniLM_model.encode(sample['narrative'])
        
        # Modal embedding (encode modal + narrative for context)
        modal_text = f"{sample['modal']}: {sample['narrative']}"
        embeddings['modal'] = miniLM_model.encode(modal_text)
        
        # Temporal embedding (encode temporal + narrative)
        temporal_text = f"{sample['temporal']}: {sample['narrative']}"
        embeddings['temporal'] = miniLM_model.encode(temporal_text)
        
        # Role embedding (encode role + narrative)
        role_text = f"{sample['role']}: {sample['narrative']}"
        embeddings['role'] = miniLM_model.encode(role_text)
        
        return embeddings
    
    def generate_baseline_embedding(self, sample: Dict) -> np.ndarray:
        """Generate MiniLM baseline embedding (concatenated text)"""
        concatenated = f"{sample['narrative']} {sample['modal']} {sample['temporal']} {sample['role']}"
        return miniLM_model.encode(concatenated)
    
    async def compose_wisp(self, embeddings: Dict[str, np.ndarray]) -> Tuple[np.ndarray, float, Dict]:
        """Send embeddings to Scribe for Wisp composition"""
        start_time = time.time()
        
        # Send composition request to Scribe
        request = {
            "type": "scribe.compose",
            "source": "scribe_batch_validation",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "payload": {
                "embeddings": {
                    "narrative": embeddings['narrative'].tolist(),
                    "modal": embeddings['modal'].tolist(),
                    "temporal": embeddings['temporal'].tolist(),
                    "role": embeddings['role'].tolist()
                }
            }
        }
        
        await self.scribe_ws.send(json.dumps(request))
        
        # Wait for response
        response_raw = await self.scribe_ws.recv()
        response = json.loads(response_raw)
        
        latency = (time.time() - start_time) * 1000  # ms
        
        if response.get('type') == 'scribe.composed':
            wisp = np.array(response['payload']['wisp'])
            coherence = response['payload']['coherence']
            attention_weights = response['payload'].get('attention_weights', None)
            return wisp, latency, {"coherence": coherence, "attention_weights": attention_weights}
        else:
            raise Exception(f"Scribe composition failed: {response}")
    
    def calculate_coherence(self, wisp: np.ndarray, embeddings: Dict[str, np.ndarray]) -> Dict[str, float]:
        """Calculate coherence between Wisp and each modality"""
        coherences = {}
        for modality, embedding in embeddings.items():
            similarity = 1 - cosine(wisp, embedding)
            coherences[modality] = similarity
        return coherences
    
    def calculate_semantic_drift(self, wisp: np.ndarray, narrative_embedding: np.ndarray) -> float:
        """Calculate L2 distance between Wisp and narrative (semantic drift)"""
        return np.linalg.norm(wisp - narrative_embedding)
    
    async def test_single_sample(self, sample: Dict) -> Dict:
        """Test a single sample with Scribe vs MiniLM baseline"""
        
        # Generate embeddings
        embeddings = self.generate_embeddings(sample)
        baseline_embedding = self.generate_baseline_embedding(sample)
        
        # Scribe composition
        try:
            wisp, scribe_latency, scribe_meta = await self.compose_wisp(embeddings)
            scribe_coherences = self.calculate_coherence(wisp, embeddings)
            scribe_drift = self.calculate_semantic_drift(wisp, embeddings['narrative'])
            scribe_success = True
        except Exception as e:
            print(f"[Batch Validation] Scribe composition failed: {e}")
            scribe_success = False
            scribe_latency = None
            scribe_coherences = None
            scribe_drift = None
            scribe_meta = None
        
        # MiniLM baseline
        baseline_start = time.time()
        baseline_coherences = self.calculate_coherence(baseline_embedding, embeddings)
        baseline_drift = self.calculate_semantic_drift(baseline_embedding, embeddings['narrative'])
        baseline_latency = (time.time() - baseline_start) * 1000
        
        return {
            "sample_id": sample['id'],
            "category": sample['category'],
            "scribe": {
                "success": scribe_success,
                "latency_ms": scribe_latency,
                "coherences": scribe_coherences,
                "mean_coherence": np.mean(list(scribe_coherences.values())) if scribe_coherences else None,
                "semantic_drift": scribe_drift,
                "attention_weights": scribe_meta.get('attention_weights') if scribe_meta else None
            },
            "baseline": {
                "latency_ms": baseline_latency,
                "coherences": baseline_coherences,
                "mean_coherence": np.mean(list(baseline_coherences.values())),
                "semantic_drift": baseline_drift
            }
        }
    
    def calculate_statistics(self, results: List[Dict]) -> Dict:
        """Calculate comprehensive statistics from batch results"""
        
        # Extract metrics
        scribe_coherences = [r['scribe']['mean_coherence'] for r in results if r['scribe']['success']]
        baseline_coherences = [r['baseline']['mean_coherence'] for r in results]
        
        scribe_drifts = [r['scribe']['semantic_drift'] for r in results if r['scribe']['success']]
        baseline_drifts = [r['baseline']['semantic_drift'] for r in results]
        
        scribe_latencies = [r['scribe']['latency_ms'] for r in results if r['scribe']['success']]
        baseline_latencies = [r['baseline']['latency_ms'] for r in results]
        
        # Descriptive statistics
        stats_summary = {
            "sample_count": len(results),
            "scribe_success_rate": len(scribe_coherences) / len(results),
            
            "coherence": {
                "scribe": {
                    "mean": np.mean(scribe_coherences),
                    "std": np.std(scribe_coherences),
                    "min": np.min(scribe_coherences),
                    "max": np.max(scribe_coherences),
                    "ci_95": stats.t.interval(0.95, len(scribe_coherences)-1, 
                                              loc=np.mean(scribe_coherences), 
                                              scale=stats.sem(scribe_coherences))
                },
                "baseline": {
                    "mean": np.mean(baseline_coherences),
                    "std": np.std(baseline_coherences),
                    "min": np.min(baseline_coherences),
                    "max": np.max(baseline_coherences),
                    "ci_95": stats.t.interval(0.95, len(baseline_coherences)-1,
                                              loc=np.mean(baseline_coherences),
                                              scale=stats.sem(baseline_coherences))
                }
            },
            
            "semantic_drift": {
                "scribe": {
                    "mean": np.mean(scribe_drifts),
                    "std": np.std(scribe_drifts),
                    "ci_95": stats.t.interval(0.95, len(scribe_drifts)-1,
                                              loc=np.mean(scribe_drifts),
                                              scale=stats.sem(scribe_drifts))
                },
                "baseline": {
                    "mean": np.mean(baseline_drifts),
                    "std": np.std(baseline_drifts),
                    "ci_95": stats.t.interval(0.95, len(baseline_drifts)-1,
                                              loc=np.mean(baseline_drifts),
                                              scale=stats.sem(baseline_drifts))
                }
            },
            
            "latency": {
                "scribe": {
                    "mean": np.mean(scribe_latencies),
                    "std": np.std(scribe_latencies),
                    "ci_95": stats.t.interval(0.95, len(scribe_latencies)-1,
                                              loc=np.mean(scribe_latencies),
                                              scale=stats.sem(scribe_latencies))
                },
                "baseline": {
                    "mean": np.mean(baseline_latencies),
                    "std": np.std(baseline_latencies),
                    "ci_95": stats.t.interval(0.95, len(baseline_latencies)-1,
                                              loc=np.mean(baseline_latencies),
                                              scale=stats.sem(baseline_latencies))
                }
            }
        }
        
        # Hypothesis testing (Scribe vs Baseline)
        # Coherence: Scribe should have higher coherence
        coherence_ttest = stats.ttest_ind(scribe_coherences, baseline_coherences)
        coherence_effect_size = (np.mean(scribe_coherences) - np.mean(baseline_coherences)) / np.sqrt(
            (np.std(scribe_coherences)**2 + np.std(baseline_coherences)**2) / 2
        )
        
        # Semantic drift: Scribe should have lower drift
        drift_ttest = stats.ttest_ind(scribe_drifts, baseline_drifts)
        drift_effect_size = (np.mean(baseline_drifts) - np.mean(scribe_drifts)) / np.sqrt(
            (np.std(scribe_drifts)**2 + np.std(baseline_drifts)**2) / 2
        )
        
        stats_summary["hypothesis_tests"] = {
            "coherence": {
                "t_statistic": coherence_ttest.statistic,
                "p_value": coherence_ttest.pvalue,
                "effect_size_cohens_d": coherence_effect_size,
                "significant": coherence_ttest.pvalue < 0.05,
                "interpretation": "Scribe has significantly higher coherence" if coherence_ttest.pvalue < 0.05 else "No significant difference"
            },
            "semantic_drift": {
                "t_statistic": drift_ttest.statistic,
                "p_value": drift_ttest.pvalue,
                "effect_size_cohens_d": drift_effect_size,
                "significant": drift_ttest.pvalue < 0.05,
                "interpretation": "Scribe has significantly lower drift" if drift_ttest.pvalue < 0.05 else "No significant difference"
            }
        }
        
        # Category breakdown
        categories = set(r['category'] for r in results)
        stats_summary["by_category"] = {}
        for category in categories:
            category_results = [r for r in results if r['category'] == category]
            cat_scribe_coherences = [r['scribe']['mean_coherence'] for r in category_results if r['scribe']['success']]
            cat_baseline_coherences = [r['baseline']['mean_coherence'] for r in category_results]
            
            stats_summary["by_category"][category] = {
                "count": len(category_results),
                "scribe_mean_coherence": np.mean(cat_scribe_coherences) if cat_scribe_coherences else None,
                "baseline_mean_coherence": np.mean(cat_baseline_coherences)
            }
        
        return stats_summary
    
    async def run_batch_test(self, batch_size: int, category: str = None):
        """Run batch test with specified size and optional category filter"""
        print(f"[Batch Validation] Starting batch test: size={batch_size}, category={category}")
        
        # Select samples
        if category:
            samples = [s for s in ALL_SAMPLES if s['category'] == category][:batch_size]
        else:
            samples = ALL_SAMPLES[:batch_size]
        
        print(f"[Batch Validation] Testing {len(samples)} samples")
        
        # Test each sample
        results = []
        for i, sample in enumerate(samples):
            print(f"[Batch Validation] Testing sample {i+1}/{len(samples)}: {sample['id']}")
            
            result = await self.test_single_sample(sample)
            results.append(result)
            
            # Send progress update
            await self.send_progress_update(i + 1, len(samples), result)
            
            # Small delay to avoid overwhelming the system
            await asyncio.sleep(0.1)
        
        # Calculate statistics
        print("[Batch Validation] Calculating statistics...")
        statistics = self.calculate_statistics(results)
        
        # Send completion message
        await self.send_completion(batch_size, category, results, statistics)
        
        print(f"[Batch Validation] Batch test complete!")
        print(f"  Scribe mean coherence: {statistics['coherence']['scribe']['mean']:.4f}")
        print(f"  Baseline mean coherence: {statistics['coherence']['baseline']['mean']:.4f}")
        print(f"  p-value: {statistics['hypothesis_tests']['coherence']['p_value']:.4f}")
        print(f"  Effect size (Cohen's d): {statistics['hypothesis_tests']['coherence']['effect_size_cohens_d']:.4f}")
    
    async def send_progress_update(self, current: int, total: int, result: Dict):
        """Send progress update as ontological Pulse (scribe.result.sample)"""
        # Transform result into ontological fusion_result object
        fusion_result = {
            "sample_id": result['sample_id'],
            "category": result['category'],
            "coherence": {
                "mean": result['scribe']['mean_coherence'],
                "per_modality": [
                    result['scribe']['coherences']['narrative'],
                    result['scribe']['coherences']['modal'],
                    result['scribe']['coherences']['temporal'],
                    result['scribe']['coherences']['role']
                ] if result['scribe']['coherences'] else None
            },
            "semantic_drift": result['scribe']['semantic_drift'],
            "attention_weights": result['scribe']['attention_weights'],
            "latency_ms": result['scribe']['latency_ms']
        }
        
        baseline_result = {
            "coherence": result['baseline']['mean_coherence'],
            "semantic_drift": result['baseline']['semantic_drift'],
            "latency_ms": result['baseline']['latency_ms']
        }
        
        message = {
            "type": "scribe.result.sample",
            "source": "scribe_batch_validation",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "ontology": "scribe_results",
            "payload": {
                "fusion_result": fusion_result,
                "baseline_result": baseline_result,
                "progress": {
                    "current": current,
                    "total": total
                }
            }
        }
        await self.ws.send(json.dumps(message))
    
    async def send_completion(self, batch_size: int, category: str, results: List[Dict], statistics: Dict):
        """Send batch completion as ontological Pulse (scribe.result.batch)"""
        
        # Transform results into ontological objects
        fusion_results = []
        baseline_results = []
        
        for r in results:
            if r['scribe']['success']:
                fusion_results.append({
                    "sample_id": r['sample_id'],
                    "category": r['category'],
                    "coherence": {
                        "mean": r['scribe']['mean_coherence'],
                        "per_modality": [
                            r['scribe']['coherences']['narrative'],
                            r['scribe']['coherences']['modal'],
                            r['scribe']['coherences']['temporal'],
                            r['scribe']['coherences']['role']
                        ]
                    },
                    "semantic_drift": r['scribe']['semantic_drift'],
                    "attention_weights": r['scribe']['attention_weights'],
                    "latency_ms": r['scribe']['latency_ms']
                })
            
            baseline_results.append({
                "coherence": r['baseline']['mean_coherence'],
                "semantic_drift": r['baseline']['semantic_drift'],
                "latency_ms": r['baseline']['latency_ms']
            })
        
        # Transform statistics into ontological statistical_summary
        statistical_summary = {
            "sample_count": statistics['sample_count'],
            "coherence": {
                "scribe": {
                    "mean": float(statistics['coherence']['scribe']['mean']),
                    "std": float(statistics['coherence']['scribe']['std']),
                    "min": float(statistics['coherence']['scribe']['min']),
                    "max": float(statistics['coherence']['scribe']['max']),
                    "confidence_interval_95": [float(x) for x in statistics['coherence']['scribe']['ci_95']]
                },
                "baseline": {
                    "mean": float(statistics['coherence']['baseline']['mean']),
                    "std": float(statistics['coherence']['baseline']['std']),
                    "min": float(statistics['coherence']['baseline']['min']),
                    "max": float(statistics['coherence']['baseline']['max']),
                    "confidence_interval_95": [float(x) for x in statistics['coherence']['baseline']['ci_95']]
                }
            },
            "semantic_drift": {
                "scribe": {
                    "mean": float(statistics['semantic_drift']['scribe']['mean']),
                    "std": float(statistics['semantic_drift']['scribe']['std']),
                    "confidence_interval_95": [float(x) for x in statistics['semantic_drift']['scribe']['ci_95']]
                },
                "baseline": {
                    "mean": float(statistics['semantic_drift']['baseline']['mean']),
                    "std": float(statistics['semantic_drift']['baseline']['std']),
                    "confidence_interval_95": [float(x) for x in statistics['semantic_drift']['baseline']['ci_95']]
                }
            },
            "latency": {
                "scribe": {
                    "mean": float(statistics['latency']['scribe']['mean']),
                    "std": float(statistics['latency']['scribe']['std']),
                    "confidence_interval_95": [float(x) for x in statistics['latency']['scribe']['ci_95']]
                },
                "baseline": {
                    "mean": float(statistics['latency']['baseline']['mean']),
                    "std": float(statistics['latency']['baseline']['std']),
                    "confidence_interval_95": [float(x) for x in statistics['latency']['baseline']['ci_95']]
                }
            },
            "hypothesis_tests": {
                "coherence": {
                    "t_statistic": float(statistics['hypothesis_tests']['coherence']['t_statistic']),
                    "p_value": float(statistics['hypothesis_tests']['coherence']['p_value']),
                    "effect_size_cohens_d": float(statistics['hypothesis_tests']['coherence']['effect_size_cohens_d']),
                    "interpretation": statistics['hypothesis_tests']['coherence']['interpretation']
                },
                "semantic_drift": {
                    "t_statistic": float(statistics['hypothesis_tests']['semantic_drift']['t_statistic']),
                    "p_value": float(statistics['hypothesis_tests']['semantic_drift']['p_value']),
                    "effect_size_cohens_d": float(statistics['hypothesis_tests']['semantic_drift']['effect_size_cohens_d']),
                    "interpretation": statistics['hypothesis_tests']['semantic_drift']['interpretation']
                }
            },
            "by_category": statistics['by_category']
        }
        
        # Batch metadata
        batch_metadata = {
            "batch_size": batch_size,
            "category_filter": category,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "duration_seconds": None  # Could track this if needed
        }
        
        message = {
            "type": "scribe.result.batch",
            "source": "scribe_batch_validation",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "ontology": "scribe_results",
            "payload": {
                "batch_metadata": batch_metadata,
                "results": fusion_results,
                "baselines": baseline_results,
                "statistics": statistical_summary
            }
        }
        await self.ws.send(json.dumps(message))
    
    async def listen(self):
        """Listen for batch test requests"""
        while True:
            try:
                message_raw = await self.ws.recv()
                message = json.loads(message_raw)
                
                if message.get('type') == 'scribe_batch_validation.run':
                    batch_size = message['payload'].get('batch_size', 10)
                    category = message['payload'].get('category', None)
                    
                    # Run batch test
                    await self.run_batch_test(batch_size, category)
                    
            except Exception as e:
                print(f"[Batch Validation] Error: {e}")
                await asyncio.sleep(1)

async def main():
    service = BatchValidationService()
    
    # Connect to PulseMesh
    if not await service.connect_pulsemesh():
        return
    
    # Connect to Scribe topic
    if not await service.connect_scribe():
        return
    
    print("[Batch Validation] Ready to process batch tests")
    
    # Listen for requests
    await service.listen()

if __name__ == "__main__":
    asyncio.run(main())
