from pathlib import Path
import unittest

from content_ai_solution_lab.agents import ContentAIAgent
from content_ai_solution_lab.catalog import load_content_items, search_content, summarize_catalog
from content_ai_solution_lab.cli import build_scenario
from content_ai_solution_lab.discovery import extract_solution_themes, load_discovery_signals
from content_ai_solution_lab.platform import ContentPlatformMock


ROOT = Path(__file__).resolve().parents[1]


class SolutionLabTests(unittest.TestCase):
    def test_catalog_search_and_summary(self):
        items = load_content_items(ROOT / "data" / "sample_content.json")
        finance = search_content(items, department="Finance")
        summary = summarize_catalog(items)

        self.assertEqual(len(finance), 1)
        self.assertEqual(finance[0].content_type, "invoice")
        self.assertEqual(summary["Legal:contract:confidential"], 1)

    def test_discovery_theme_extraction_prioritizes_governance_and_automation(self):
        signals = load_discovery_signals(ROOT / "data" / "discovery_notes.json")
        themes = extract_solution_themes(signals)

        self.assertGreaterEqual(themes["governance"], 2)
        self.assertGreaterEqual(themes["automation"], 2)

    def test_agent_creates_reviewable_approval_packet_and_audit_log(self):
        items = load_content_items(ROOT / "data" / "sample_content.json")
        platform = ContentPlatformMock(items)
        agent = ContentAIAgent(platform)
        packet = agent.prepare_approval_packet("CNT-1001")

        self.assertEqual(packet["classification"]["classification"], "legal-review")
        self.assertEqual(packet["approval"]["approver"], "legal-ops@example.com")
        self.assertEqual(len(platform.audit_log()), 2)

    def test_scenario_builds_customer_facing_recommendations(self):
        scenario = build_scenario(ROOT / "data" / "sample_content.json", ROOT / "data" / "discovery_notes.json")

        self.assertEqual(scenario.customer, "Northstar Manufacturing")
        self.assertEqual(len(scenario.recommendations), 2)
        self.assertIn("AI", scenario.recommendations[0].workflow_name)


if __name__ == "__main__":
    unittest.main()
