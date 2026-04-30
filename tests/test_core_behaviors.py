from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.ab_test.simulate_experiment import build_balanced_assignments, choose_recommendation
from src.drift.psi import calculate_psi, classify_psi
from src.governance.audit_trail import verify_audit_log, write_audit_log


class ABExperimentTests(unittest.TestCase):
    def test_balanced_assignments_reach_powered_sample_size(self) -> None:
        assignments = build_balanced_assignments(25, "unit_test_experiment")

        self.assertEqual(len(assignments["control"]), 25)
        self.assertEqual(len(assignments["treatment"]), 25)
        self.assertEqual(
            set(assignments["control"]).intersection(assignments["treatment"]),
            set(),
        )

    def test_recommendation_uses_stats_and_guardrails(self) -> None:
        positive_stats = {"significant": True, "absolute_lift": 0.04}
        passing_guardrails = {
            "latency_pass": True,
            "error_pass": True,
            "cost_pass": True,
            "retrieval_score_pass": True,
            "empty_retrieval_pass": True,
            "groundedness_pass": True,
        }

        self.assertEqual(choose_recommendation(positive_stats, passing_guardrails), "SHIP_B")

        failed_latency = dict(passing_guardrails)
        failed_latency["latency_pass"] = False
        self.assertEqual(choose_recommendation(positive_stats, failed_latency), "RUN_MORE_DATA")

        non_significant = {"significant": False, "absolute_lift": 0.04}
        self.assertEqual(choose_recommendation(non_significant, passing_guardrails), "KEEP_A")


class DriftTests(unittest.TestCase):
    def test_psi_classifies_stable_and_shifted_distributions(self) -> None:
        reference = [0.0] * 50 + [1.0] * 50
        stable = reference.copy()
        shifted = [0.0] * 10 + [1.0] * 90

        stable_psi = calculate_psi(reference, stable, bins=2)
        shifted_psi = calculate_psi(reference, shifted, bins=2)

        self.assertEqual(classify_psi(stable_psi, 0.10, 0.20), "stable")
        self.assertEqual(classify_psi(shifted_psi, 0.10, 0.20), "significant")


class AuditTrailTests(unittest.TestCase):
    def test_audit_trail_hash_chain_verifies(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            audit_path = Path(directory) / "audit-trail.json"
            write_audit_log(audit_path)

            self.assertTrue(verify_audit_log(audit_path))


if __name__ == "__main__":
    unittest.main()
