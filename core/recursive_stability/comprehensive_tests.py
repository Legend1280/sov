#!/usr/bin/env python3.11
"""
Comprehensive Recursive Stability Test Suite

This module conducts extensive testing of the Mirror-Core-SAGE recursive loop
to empirically validate the recursive stability hypothesis.

Tests include:
1. Multiple convergence trials (n=50)
2. Perturbation recovery tests
3. Long-term stability tests
4. Statistical analysis of convergence properties
"""

import json
import time
from datetime import datetime
from typing import List, Dict, Tuple
import statistics

from state_vector import StateVectorGenerator
from recursive_loop import RecursiveFeedbackLoop
from semantic_coherence import SemanticCoherenceChecker


class ComprehensiveTestSuite:
    """Comprehensive test suite for recursive stability validation"""
    
    def __init__(self):
        self.results = {
            "test_date": datetime.utcnow().isoformat(),
            "trials": [],
            "perturbation_tests": [],
            "long_term_tests": [],
            "statistical_summary": {}
        }
    
    def run_convergence_trial(self, trial_id: int, max_iterations: int = 30) -> Dict:
        """Run a single convergence trial"""
        print(f"\n=== Trial {trial_id}: Convergence Test ===")
        
        feedback_loop = RecursiveFeedbackLoop()
        coherence_checker = SemanticCoherenceChecker()
        
        trial_data = {
            "trial_id": trial_id,
            "max_iterations": max_iterations,
            "iterations": [],
            "converged": False,
            "convergence_iteration": None,
            "final_similarity": None,
            "final_trust": None,
            "final_drift": None
        }
        
        for i in range(max_iterations):
            # Run iteration with mock states
            mirror_state = {"active_components": i + 1, "rendered_objects": i * 2, "viewport_state": "active", "pulse_count": i * 10}
            core_state = {"reasoning_depth": i % 5, "intent": f"test_{i}", "ontology_objects": i * 3}
            sage_state = {"constraint_state": "valid", "validation_count": i, "violations": 0}
            result = feedback_loop.iterate(mirror_state, core_state, sage_state)
            
            # Check semantic coherence
            if feedback_loop.iteration >= 2:
                prev_vec = feedback_loop.vector_gen.get_vector_at(feedback_loop.iteration - 2)
                curr_vec = feedback_loop.vector_gen.get_vector_at(feedback_loop.iteration - 1)
                coherence_result = coherence_checker.check_coherence(prev_vec, curr_vec)
            else:
                coherence_result = {"trust_coefficient": 1.0, "semantic_coherence": 1.0, "meaning_drift": 0.0}
            
            iteration_data = {
                "iteration": i + 1,
                "similarity": result["similarity"],
                "delta": result["delta"],
                "trust": coherence_result["trust_coefficient"],
                "semantic_coherence": coherence_result["semantic_coherence"],
                "meaning_drift": coherence_result["meaning_drift"]
            }
            
            trial_data["iterations"].append(iteration_data)
            
            # Check convergence
            if result["converged"]:
                trial_data["converged"] = True
                trial_data["convergence_iteration"] = i + 1
                trial_data["final_similarity"] = result["similarity"]
                trial_data["final_trust"] = coherence_result["trust_coefficient"]
                trial_data["final_drift"] = coherence_result["meaning_drift"]
                print(f"✅ Converged at iteration {i + 1}")
                print(f"   Similarity: {result['similarity']:.6f}")
                print(f"   Trust: {coherence_result['trust_coefficient']:.6f}")
                print(f"   Drift: {coherence_result['meaning_drift']:.6f}")
                break
        
        if not trial_data["converged"]:
            last_iter = trial_data["iterations"][-1]
            trial_data["final_similarity"] = last_iter["similarity"]
            trial_data["final_trust"] = last_iter["trust"]
            trial_data["final_drift"] = last_iter["meaning_drift"]
            print(f"⚠️  Did not converge within {max_iterations} iterations")
        
        return trial_data
    
    def run_perturbation_test(self, test_id: int, perturbation_magnitude: float) -> Dict:
        """Test recovery from perturbation"""
        print(f"\n=== Perturbation Test {test_id}: Magnitude {perturbation_magnitude} ===")
        
        feedback_loop = RecursiveFeedbackLoop()
        coherence_checker = SemanticCoherenceChecker()
        
        # Run until convergence
        print("Phase 1: Initial convergence...")
        for i in range(20):
            mirror_state = {"active_components": i + 1, "rendered_objects": i * 2, "viewport_state": "active", "pulse_count": i * 10}
            core_state = {"reasoning_depth": i % 5, "intent": f"test_{i}", "ontology_objects": i * 3}
            sage_state = {"constraint_state": "valid", "validation_count": i, "violations": 0}
            result = feedback_loop.iterate(mirror_state, core_state, sage_state)
            if result["converged"]:
                print(f"✅ Initial convergence at iteration {i + 1}")
                break
        
        pre_perturbation_state = feedback_loop.vector_gen.get_vector_at(feedback_loop.iteration - 1).copy()
        pre_perturbation_similarity = result["similarity"]
        
        # Inject perturbation
        print(f"Phase 2: Injecting perturbation (magnitude: {perturbation_magnitude})...")
        import numpy as np
        noise = np.random.randn(128) * perturbation_magnitude
        perturbed_state = pre_perturbation_state + noise
        perturbed_state = perturbed_state / np.linalg.norm(perturbed_state) * np.linalg.norm(pre_perturbation_state)
        
        feedback_loop.history.append(perturbed_state)
        
        # Measure immediate impact
        from numpy.linalg import norm
        immediate_similarity = np.dot(pre_perturbation_state, perturbed_state) / (
            norm(pre_perturbation_state) * norm(perturbed_state)
        )
        immediate_delta = norm(perturbed_state - pre_perturbation_state)
        
        print(f"   Immediate similarity drop: {pre_perturbation_similarity:.6f} → {immediate_similarity:.6f}")
        print(f"   Delta: {immediate_delta:.6f}")
        
        # Test recovery
        print("Phase 3: Testing recovery...")
        recovery_iterations = []
        recovered = False
        
        for i in range(20):
            mirror_state = {"active_components": i + 1, "rendered_objects": i * 2, "viewport_state": "active", "pulse_count": i * 10}
            core_state = {"reasoning_depth": i % 5, "intent": f"test_{i}", "ontology_objects": i * 3}
            sage_state = {"constraint_state": "valid", "validation_count": i, "violations": 0}
            result = feedback_loop.iterate(mirror_state, core_state, sage_state)
            prev_vec = feedback_loop.vector_gen.get_vector_at(feedback_loop.iteration - 2)
            curr_vec = feedback_loop.vector_gen.get_vector_at(feedback_loop.iteration - 1)
            coherence_result = coherence_checker.check_coherence(prev_vec, curr_vec)
            
            recovery_iterations.append({
                "iteration": i + 1,
                "similarity": result["similarity"],
                "trust": coherence_result["trust_coefficient"],
                "drift": coherence_result["meaning_drift"]
            })
            
            # Check if recovered to near-original state
            if result["similarity"] >= 0.999 and coherence_result["trust_coefficient"] >= 0.9:
                recovered = True
                print(f"✅ Recovered at iteration {i + 1}")
                print(f"   Similarity: {result['similarity']:.6f}")
                print(f"   Trust: {coherence_result['trust_coefficient']:.6f}")
                break
        
        return {
            "test_id": test_id,
            "perturbation_magnitude": perturbation_magnitude,
            "pre_perturbation_similarity": float(pre_perturbation_similarity),
            "immediate_similarity": float(immediate_similarity),
            "immediate_delta": float(immediate_delta),
            "recovered": recovered,
            "recovery_iterations": recovery_iterations
        }
    
    def run_long_term_stability_test(self, iterations: int = 100) -> Dict:
        """Test long-term stability after convergence"""
        print(f"\n=== Long-Term Stability Test: {iterations} iterations ===")
        
        feedback_loop = RecursiveFeedbackLoop()
        coherence_checker = SemanticCoherenceChecker()
        
        # Run until convergence
        print("Phase 1: Initial convergence...")
        for i in range(20):
            mirror_state = {"active_components": i + 1, "rendered_objects": i * 2, "viewport_state": "active", "pulse_count": i * 10}
            core_state = {"reasoning_depth": i % 5, "intent": f"test_{i}", "ontology_objects": i * 3}
            sage_state = {"constraint_state": "valid", "validation_count": i, "violations": 0}
            result = feedback_loop.iterate(mirror_state, core_state, sage_state)
            if result["converged"]:
                print(f"✅ Converged at iteration {i + 1}")
                convergence_iteration = i + 1
                break
        
        # Continue for long-term stability
        print(f"Phase 2: Running {iterations} additional iterations...")
        long_term_data = []
        
        for i in range(iterations):
            mirror_state = {"active_components": convergence_iteration + i + 1, "rendered_objects": (convergence_iteration + i) * 2, "viewport_state": "active", "pulse_count": (convergence_iteration + i) * 10}
            core_state = {"reasoning_depth": (convergence_iteration + i) % 5, "intent": f"test_{convergence_iteration + i}", "ontology_objects": (convergence_iteration + i) * 3}
            sage_state = {"constraint_state": "valid", "validation_count": convergence_iteration + i, "violations": 0}
            result = feedback_loop.iterate(mirror_state, core_state, sage_state)
            prev_vec = feedback_loop.vector_gen.get_vector_at(feedback_loop.iteration - 2)
            curr_vec = feedback_loop.vector_gen.get_vector_at(feedback_loop.iteration - 1)
            coherence_result = coherence_checker.check_coherence(prev_vec, curr_vec)
            
            long_term_data.append({
                "iteration": convergence_iteration + i + 1,
                "similarity": result["similarity"],
                "trust": coherence_result["trust_coefficient"],
                "drift": coherence_result["meaning_drift"]
            })
            
            if (i + 1) % 20 == 0:
                print(f"   Iteration {convergence_iteration + i + 1}: "
                      f"sim={result['similarity']:.6f}, "
                      f"trust={coherence_result['trust_coefficient']:.6f}")
        
        # Calculate stability metrics
        similarities = [d["similarity"] for d in long_term_data]
        trusts = [d["trust"] for d in long_term_data]
        drifts = [d["drift"] for d in long_term_data]
        
        stability_metrics = {
            "similarity_mean": statistics.mean(similarities),
            "similarity_stdev": statistics.stdev(similarities) if len(similarities) > 1 else 0,
            "similarity_min": min(similarities),
            "similarity_max": max(similarities),
            "trust_mean": statistics.mean(trusts),
            "trust_stdev": statistics.stdev(trusts) if len(trusts) > 1 else 0,
            "drift_mean": statistics.mean(drifts),
            "drift_stdev": statistics.stdev(drifts) if len(drifts) > 1 else 0
        }
        
        print(f"\n✅ Long-term stability metrics:")
        print(f"   Similarity: {stability_metrics['similarity_mean']:.6f} ± {stability_metrics['similarity_stdev']:.6f}")
        print(f"   Trust: {stability_metrics['trust_mean']:.6f} ± {stability_metrics['trust_stdev']:.6f}")
        print(f"   Drift: {stability_metrics['drift_mean']:.6f} ± {stability_metrics['drift_stdev']:.6f}")
        
        return {
            "convergence_iteration": convergence_iteration,
            "total_iterations": convergence_iteration + iterations,
            "long_term_data": long_term_data,
            "stability_metrics": stability_metrics
        }
    
    def run_full_suite(self, num_trials: int = 50):
        """Run complete test suite"""
        print("=" * 80)
        print("COMPREHENSIVE RECURSIVE STABILITY TEST SUITE")
        print("=" * 80)
        
        # 1. Multiple convergence trials
        print(f"\n{'=' * 80}")
        print(f"TEST 1: CONVERGENCE TRIALS (n={num_trials})")
        print(f"{'=' * 80}")
        
        for trial_id in range(1, num_trials + 1):
            trial_result = self.run_convergence_trial(trial_id)
            self.results["trials"].append(trial_result)
        
        # 2. Perturbation tests with varying magnitudes
        print(f"\n{'=' * 80}")
        print("TEST 2: PERTURBATION RECOVERY")
        print(f"{'=' * 80}")
        
        perturbation_magnitudes = [0.1, 0.2, 0.5, 1.0, 2.0]
        for test_id, magnitude in enumerate(perturbation_magnitudes, 1):
            perturb_result = self.run_perturbation_test(test_id, magnitude)
            self.results["perturbation_tests"].append(perturb_result)
        
        # 3. Long-term stability test
        print(f"\n{'=' * 80}")
        print("TEST 3: LONG-TERM STABILITY")
        print(f"{'=' * 80}")
        
        long_term_result = self.run_long_term_stability_test(iterations=100)
        self.results["long_term_tests"].append(long_term_result)
        
        # 4. Statistical analysis
        self._compute_statistical_summary()
        
        # 5. Save results
        self._save_results()
        
        return self.results
    
    def _compute_statistical_summary(self):
        """Compute statistical summary of all tests"""
        print(f"\n{'=' * 80}")
        print("STATISTICAL SUMMARY")
        print(f"{'=' * 80}")
        
        # Convergence statistics
        converged_trials = [t for t in self.results["trials"] if t["converged"]]
        convergence_rate = len(converged_trials) / len(self.results["trials"])
        
        if converged_trials:
            convergence_iterations = [t["convergence_iteration"] for t in converged_trials]
            final_similarities = [t["final_similarity"] for t in converged_trials]
            final_trusts = [t["final_trust"] for t in converged_trials]
            final_drifts = [t["final_drift"] for t in converged_trials]
            
            self.results["statistical_summary"] = {
                "convergence_rate": convergence_rate,
                "mean_convergence_iteration": statistics.mean(convergence_iterations),
                "stdev_convergence_iteration": statistics.stdev(convergence_iterations) if len(convergence_iterations) > 1 else 0,
                "mean_final_similarity": statistics.mean(final_similarities),
                "stdev_final_similarity": statistics.stdev(final_similarities) if len(final_similarities) > 1 else 0,
                "mean_final_trust": statistics.mean(final_trusts),
                "stdev_final_trust": statistics.stdev(final_trusts) if len(final_trusts) > 1 else 0,
                "mean_final_drift": statistics.mean(final_drifts),
                "stdev_final_drift": statistics.stdev(final_drifts) if len(final_drifts) > 1 else 0,
                "perturbation_recovery_rate": sum(1 for p in self.results["perturbation_tests"] if p["recovered"]) / len(self.results["perturbation_tests"]) if self.results["perturbation_tests"] else 0
            }
            
            print(f"\n✅ Convergence Rate: {convergence_rate * 100:.1f}%")
            print(f"✅ Mean Convergence Iteration: {self.results['statistical_summary']['mean_convergence_iteration']:.2f} ± {self.results['statistical_summary']['stdev_convergence_iteration']:.2f}")
            print(f"✅ Mean Final Similarity: {self.results['statistical_summary']['mean_final_similarity']:.6f} ± {self.results['statistical_summary']['stdev_final_similarity']:.6f}")
            print(f"✅ Mean Final Trust: {self.results['statistical_summary']['mean_final_trust']:.6f} ± {self.results['statistical_summary']['stdev_final_trust']:.6f}")
            print(f"✅ Mean Final Drift: {self.results['statistical_summary']['mean_final_drift']:.6f} ± {self.results['statistical_summary']['stdev_final_drift']:.6f}")
            print(f"✅ Perturbation Recovery Rate: {self.results['statistical_summary']['perturbation_recovery_rate'] * 100:.1f}%")
    
    def _save_results(self):
        """Save results to JSON file"""
        output_file = "/home/ubuntu/sov/core/recursive_stability/test_results.json"
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n✅ Results saved to: {output_file}")


if __name__ == "__main__":
    suite = ComprehensiveTestSuite()
    results = suite.run_full_suite(num_trials=50)
    
    print("\n" + "=" * 80)
    print("TEST SUITE COMPLETE")
    print("=" * 80)
