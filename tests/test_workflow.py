from pathlib import Path
import json
import unittest

from content_ai_solution_lab.governance import evaluate_content_item
from content_ai_solution_lab.platform import ContentPlatformMock
from content_ai_solution_lab.catalog import load_content_items
from content_ai_solution_lab.web import DemoApplication
from content_ai_solution_lab.workflow import run_workflow


ROOT = Path(__file__).resolve().parents[1]


class WorkflowContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.items = load_content_items(ROOT / "data" / "sample_content.json")

    def test_safe_internal_item_is_eligible_for_automatic_processing(self):
        item = next(item for item in self.items if item.item_id == "CNT-1002")
        decision = evaluate_content_item(item)

        self.assertEqual(decision["classification"], "finance-automation")
        self.assertEqual(decision["disposition"], "auto_process")
        self.assertEqual(decision["link_policy"], "internal_only")
        self.assertIn("finance-content", decision["detected_signals"])

    def test_sensitive_content_requires_a_human_checkpoint(self):
        item = next(item for item in self.items if item.item_id == "CNT-1001")
        decision = evaluate_content_item(item)

        self.assertEqual(decision["classification"], "legal-review")
        self.assertEqual(decision["disposition"], "needs_review")
        self.assertEqual(decision["approver"], "legal-ops@example.com")
        self.assertIn("confidential-content", decision["policy_flags"])

    def test_unsafe_exception_is_blocked_and_never_gets_a_link(self):
        item = next(item for item in self.items if item.item_id == "CNT-1006")
        decision = evaluate_content_item(item)

        self.assertEqual(decision["classification"], "security-escalation")
        self.assertEqual(decision["disposition"], "blocked")
        self.assertEqual(decision["link_policy"], "no_link")
        self.assertIn("credential-exposure", decision["policy_flags"])
        self.assertIn("approval-bypass", decision["policy_flags"])

        run = run_workflow(self.items, ["CNT-1006"])
        result = run["results"][0]
        self.assertNotIn("shared_link", result["actions"])
        self.assertEqual(result["actions"]["approval"]["status"], "blocked_pending_review")

    def test_partial_processing_keeps_success_and_failure_visible(self):
        run = run_workflow(self.items, ["CNT-1002", "CNT-NOT-FOUND"])

        self.assertEqual(run["status"], "partial")
        self.assertEqual(run["summary"]["processed"], 1)
        self.assertEqual(run["summary"]["failed"], 1)
        self.assertEqual(run["results"][1]["status"], "failed")
        self.assertTrue(run["evaluation"]["controls"][-1]["passed"])

    def test_dry_run_projects_actions_without_provider_side_effects(self):
        run = run_workflow(self.items, ["CNT-1002"], mode="dry_run")
        result = run["results"][0]

        self.assertEqual(run["mode"], "dry_run")
        self.assertEqual(run["audit_log"], [])
        self.assertEqual(result["actions"]["metadata_update"]["status"], "projected")
        self.assertEqual(result["actions"]["shared_link"]["status"], "projected")
        self.assertNotIn("metadata_updated", result["actions"])

    def test_web_api_preserves_contract_and_rejects_invalid_input(self):
        application = DemoApplication()
        status, _, scenario = application.handle("GET", "/api/scenario")
        self.assertEqual(status, 200)
        self.assertEqual(scenario["customer"], "Northstar Manufacturing")
        self.assertEqual(scenario["catalog"]["total"], 6)

        status, _, payload = application.handle("POST", "/api/run", json.dumps({"item_ids": []}).encode())
        self.assertEqual(status, 422)
        self.assertIn("item_ids", payload["error"])

        status, _, payload = application.handle(
            "POST",
            "/api/run",
            json.dumps({"item_ids": ["CNT-1002", "CNT-NOT-FOUND"], "mode": "simulation"}).encode(),
        )
        self.assertEqual(status, 200)
        self.assertEqual(payload["status"], "partial")

        status, _, payload = application.handle("GET", "/api/content/CNT-1006/evaluation")
        self.assertEqual(status, 200)
        self.assertEqual(payload["decision"]["disposition"], "blocked")

        status, _, payload = application.handle("POST", "/api/run", b"not-json")
        self.assertEqual(status, 400)
        self.assertIn("valid JSON", payload["error"])

    def test_platform_route_contract_supports_reasoned_status(self):
        platform = ContentPlatformMock(self.items)
        packet = platform.route_for_approval(
            "CNT-1006",
            "security-ops@example.com",
            status="blocked_pending_review",
            reason="credential exposure",
        )

        self.assertEqual(packet["status"], "blocked_pending_review")
        self.assertEqual(packet["reason"], "credential exposure")
        self.assertIn("Status=blocked_pending_review", platform.audit_log()[0]["detail"])


if __name__ == "__main__":
    unittest.main()
