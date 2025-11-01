#!/usr/bin/env python3.11
"""
Simplified Comprehensive Recursive Stability Test

Runs multiple trials with proper state generation.
"""

import json
import statistics
from datetime import datetime
from state_vector import StateVectorGenerator
from recursive_loop import RecursiveFeedbackLoop
from semantic_coherence import SemanticCoherenceChecker


def generate_mock_state(iteration: int):
    """Generate mock state for testing"""
    return (
        {
            "active_components": [f"comp_{j}" for j in range(min(iteration + 1, 10))],
            "rendered_objects": [f"obj_{j}" for j in range(min(iteration * 2, 20))],
            "viewport_state": "active",
            "pulse_count": iteration * 10
        },
        {
            "reasoning_depth": iteration % 5,
            "intent": f"observe_self_{iteration}",
            "ontology_objects": [f"onto_{j}" for j in range(min(iteration * 3, 30))]
        },
        {
            "constraint_state": "valid",
            "validation_count": iteration,
            "violations": 0
        }
    )


def run_convergence_trial(trial_id: int, max_iterations: int = 30):
    """Run single convergence trial"""
    print(f"\n=== Trial {trial_id} ===")
    
    feedback_loop = RecursiveFeedbackLoop()
    coherence_checker = SemanticCoherenceChecker()
    
    for i in range(max_iterations):
        mirror_state, core_state, sage_state = generate_mock_state(i)
        result = feedback_loop.iterate(mirror_state, core_state, sage_state)
        
        if feedback_loop.iteration >= 2:
            # Set baseline to first iteration
            if coherence_checker.baseline_vector is None:
                coherence_checker.set_baseline(feedback_loop.vector_gen.get_vector_at(0))
            curr_vec = feedback_loop.vector_gen.get_vector_at(feedback_loop.iteration - 1)
            coherence_result = coherence_checker.check_coherence(curr_vec)
        else:
            coherence_result = {"trust_coefficient": 1.0, "meaning_drift": 0.0}
        
        if result["converged"]:
            print(f"✅ Converged at iteration {i + 1}")
            print(f"   Similarity: {result['similarity']:.6f}")
            print(f"   Trust: {coherence_result['trust_coefficient']:.6f}")
            return {
                "trial_id": trial_id,
                "converged": True,
                "convergence_iteration": i + 1,
                "final_similarity": float(result["similarity"]) if result["similarity"] is not None else None,
                "final_trust": float(coherence_result["trust_coefficient"]),
                "final_drift": float(coherence_result["meaning_drift"])
            }
    
    print(f"⚠️  Did not converge within {max_iterations} iterations")
    return {
        "trial_id": trial_id,
        "converged": False,
        "convergence_iteration": None,
        "final_similarity": None,
        "final_trust": None,
        "final_drift": None
    }


def main():
    print("=" * 80)
    print("COMPREHENSIVE RECURSIVE STABILITY TEST SUITE")
    print("=" * 80)
    
    # Run 10 convergence trials
    print("\nTEST 1: CONVERGENCE TRIALS (n=10)")
    print("=" * 80)
    
    trials = []
    for trial_id in range(1, 11):
        result = run_convergence_trial(trial_id)
        trials.append(result)
    
    # Statistical analysis
    print("\n" + "=" * 80)
    print("STATISTICAL SUMMARY")
    print("=" * 80)
    
    converged_trials = [t for t in trials if t["converged"]]
    convergence_rate = len(converged_trials) / len(trials)
    
    print(f"\n✅ Convergence Rate: {convergence_rate * 100:.1f}%")
    print(f"✅ Converged Trials: {len(converged_trials)}/{len(trials)}")
    
    if converged_trials:
        convergence_iterations = [t["convergence_iteration"] for t in converged_trials]
        final_similarities = [t["final_similarity"] for t in converged_trials]
        final_trusts = [t["final_trust"] for t in converged_trials]
        final_drifts = [t["final_drift"] for t in converged_trials]
        
        print(f"\nConvergence Metrics:")
        print(f"  Mean Convergence Iteration: {statistics.mean(convergence_iterations):.2f} ± {statistics.stdev(convergence_iterations) if len(convergence_iterations) > 1 else 0:.2f}")
        print(f"  Mean Final Similarity: {statistics.mean(final_similarities):.6f} ± {statistics.stdev(final_similarities) if len(final_similarities) > 1 else 0:.6f}")
        print(f"  Mean Final Trust: {statistics.mean(final_trusts):.6f} ± {statistics.stdev(final_trusts) if len(final_trusts) > 1 else 0:.6f}")
        print(f"  Mean Final Drift: {statistics.mean(final_drifts):.6f} ± {statistics.stdev(final_drifts) if len(final_drifts) > 1 else 0:.6f}")
        
        # Save results
        results = {
            "test_date": datetime.utcnow().isoformat(),
            "trials": trials,
            "summary": {
                "convergence_rate": convergence_rate,
                "mean_convergence_iteration": statistics.mean(convergence_iterations),
                "mean_final_similarity": statistics.mean(final_similarities),
                "mean_final_trust": statistics.mean(final_trusts),
                "mean_final_drift": statistics.mean(final_drifts)
            }
        }
        
        with open("/home/ubuntu/sov/core/recursive_stability/test_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"\n✅ Results saved to: test_results.json")
    
    print("\n" + "=" * 80)
    print("TEST SUITE COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
