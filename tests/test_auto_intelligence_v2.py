import importlib.util
import sys
from pathlib import Path
import unittest

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "auto_intelligence_v2.py"
spec = importlib.util.spec_from_file_location("auto_intelligence_v2", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class TestAutoIntelligenceV2(unittest.TestCase):
    def test_status_contract_includes_heartbeat_fields(self):
        source = MODULE_PATH.read_text(encoding="utf-8")
        for field in (
            "last_run_at", "last_success_at", "last_content_change_at",
            "workflow_run_id", "workflow_attempt", "sources_success",
            "sources_failed", "items_collected_this_run",
            "items_published_current", "review_queue_current",
        ):
            self.assertIn(field, source)

    def test_content_digest_ignores_runtime_failures(self):
        self.assertEqual(
            module.semantic_digest([], [], [{"source": "a", "error": "timeout"}], {}),
            module.semantic_digest([], [], [], {"a": {"consecutive_failures": 3}}),
        )

    def test_official_monitor_state_tracks_route_health(self):
        source = MODULE_PATH.read_text(encoding="utf-8")
        for field in (
            "last_success_at", "last_failure_at", "consecutive_failures",
            "selected_url", "fallback_used", "response_status",
        ):
            self.assertIn(field, source)
    def test_strict_relevance_requires_gaba_animal_and_feed_context(self):
        self.assertTrue(module.strict_relevance(
            "Effects of GABA in broiler chickens",
            "Dietary supplementation improved feed conversion under heat stress.",
        ))
        self.assertTrue(module.strict_relevance(
            "이유자돈 GABA 급여 연구",
            "가바를 사료에 첨가하여 돼지의 성장과 스트레스 지표를 평가했다.",
        ))
        self.assertFalse(module.strict_relevance(
            "Effect of drought stress on diesel biodegradation",
            "The study evaluated drought stress, soil salinity and diesel biodegradation.",
        ))
        self.assertFalse(module.strict_relevance(
            "GABA receptor expression in the human brain",
            "A neuroscience imaging study in human volunteers.",
        ))

    def test_future_and_malformed_dates_are_rejected(self):
        self.assertTrue(module.plausible_date("2025-07-01"))
        self.assertTrue(module.plausible_date("2019"))
        self.assertFalse(module.plausible_date("2121-10-01"))
        self.assertFalse(module.plausible_date("not-a-date"))

    def test_crossref_never_auto_publishes_by_default(self):
        item = module.Item(
            item_id="x",
            category="research",
            source_type="crossref",
            title="Dietary GABA supplementation in broiler chickens",
            summary="Dietary GABA supplementation was evaluated in broiler chickens for growth performance and feed conversion. " * 2,
            source_name="Journal",
            source_url="https://doi.org/10.1/example",
            published_at="2025",
            doi="10.1/example",
            species="Broiler",
            evidence_grade="B",
        )
        checked = module.quality_gate(item, {"settings": {"future_date_tolerance_days": 31}})
        self.assertFalse(checked.auto_publish)

    def test_pubmed_item_can_pass_conservative_gate(self):
        item = module.Item(
            item_id="x",
            category="research",
            source_type="pubmed",
            title="Dietary GABA supplementation in broiler chickens",
            summary="Dietary GABA supplementation was evaluated in broiler chickens for growth performance and feed conversion. " * 2,
            source_name="Journal",
            source_url="https://pubmed.ncbi.nlm.nih.gov/1/",
            published_at="2025",
            pmid="1",
            species="Broiler",
            evidence_grade="B",
        )
        checked = module.quality_gate(item, {"settings": {"future_date_tolerance_days": 31}})
        self.assertTrue(checked.auto_publish)

    def test_monitor_change_requires_two_identical_observations(self):
        baseline, changed = module.advance_monitor_state({}, "aaa", 2)
        self.assertFalse(changed)
        first, changed = module.advance_monitor_state(baseline, "bbb", 2)
        self.assertFalse(changed)
        self.assertEqual(first["candidate_count"], 1)
        second, changed = module.advance_monitor_state(first, "bbb", 2)
        self.assertTrue(changed)
        self.assertEqual(second["digest"], "bbb")
        self.assertEqual(second["candidate_count"], 0)

    def test_merge_preserves_first_detection_timestamp(self):
        old = module.Item(
            item_id="old", category="research", source_type="pubmed",
            title="Dietary GABA supplementation in pigs", summary="GABA feed study in pigs " * 10,
            source_name="J", source_url="u", published_at="2025", detected_at="2025-01-01T00:00:00+00:00", pmid="1",
            auto_publish=True,
        )
        new = module.Item(
            item_id="new", category="research", source_type="pubmed",
            title="Dietary GABA supplementation in pigs", summary="GABA feed study in pigs " * 12,
            source_name="J", source_url="u", published_at="2025", detected_at="2026-01-01T00:00:00+00:00", pmid="1",
            auto_publish=True,
        )
        merged = module.merge_items([old], [new], 10)
        self.assertEqual(merged[0].detected_at, old.detected_at)

    def test_curated_research_items_are_relevant_and_public(self):
        config = module.load_json(module.CONFIG_PATH, {})
        items = module.curated_items(config)
        research = [x for x in items if x.category == "research"]
        self.assertGreaterEqual(len(research), 5)
        self.assertTrue(all(module.strict_relevance(x.title, x.summary) for x in research))
        self.assertTrue(all(x.auto_publish for x in items))


if __name__ == "__main__":
    unittest.main()
