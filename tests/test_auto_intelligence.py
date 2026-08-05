import importlib.util
import sys
from pathlib import Path
import unittest

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "auto_intelligence.py"
spec = importlib.util.spec_from_file_location("auto_intelligence", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)

class TestAutoIntelligence(unittest.TestCase):
    def test_species(self):
        self.assertEqual(module.classify_species("GABA supplementation in broiler chickens"), "Broiler")
        self.assertEqual(module.classify_species("GABA in swine diets"), "Pig")

    def test_relevance(self):
        self.assertTrue(module.relevant_to_gaba_feed(
            "Effects of GABA in broilers", "dietary supplementation improved feed conversion"
        ))
        self.assertFalse(module.relevant_to_gaba_feed(
            "GABA receptor in human brain", "neuroscience study"
        ))

    def test_dedupe_prefers_pubmed(self):
        a = module.Item("1","research","crossref","A","summary text "*10,"J","u","2026","now",doi="10/x")
        b = module.Item("2","research","pubmed","A","summary text "*10,"J","u","2026","now",doi="10/x")
        result = module.dedupe([a,b])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].source_type, "pubmed")

if __name__ == "__main__":
    unittest.main()
