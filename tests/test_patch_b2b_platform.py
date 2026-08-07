import importlib.util
from pathlib import Path
import unittest

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "patch_b2b_platform.py"
spec = importlib.util.spec_from_file_location("patch_b2b_platform", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PatchB2BPlatformTest(unittest.TestCase):
    def test_index_patch_is_idempotent(self):
        source = (
            '<head><link rel="stylesheet" href="assets/technical-documents.css" data-technical-documents="v1"></head>'
            '<body><script src="assets/technical-documents.js" defer data-technical-documents="v1"></script></body>'
        )
        patched, changed = module.patch_index(source)
        self.assertTrue(changed)
        self.assertIn(module.STYLE_TAG, patched)
        self.assertIn(module.SCRIPT_TAG, patched)
        repatched, changed_again = module.patch_index(patched)
        self.assertFalse(changed_again)
        self.assertEqual(patched, repatched)

    def test_inquiry_removes_formsubmit_and_legacy_recipient(self):
        source = (
            "const RECIPIENT = 'dubaissday@cellpinda.com';\n"
            "const FORM_ENDPOINT = `https://formsubmit.co/${RECIPIENT}`;\n"
        )
        patched, changed = module.patch_inquiry_ui(source)
        self.assertTrue(changed)
        self.assertIn("feed@cellpinda.com", patched)
        self.assertNotIn("formsubmit.co", patched)
        self.assertNotIn("dubaissday@cellpinda.com", patched)

    def test_source_config_updates_current_urls(self):
        payload = {
            "official_monitors": [
                {"id": "us-fda-animal-food", "url": "old"},
                {"id": "au-apvma-animal-feed", "url": "old"},
                {"id": "oecd-fao-agricultural-outlook", "url": "old"},
            ]
        }
        patched, changed = module.patch_source_config(payload)
        self.assertTrue(changed)
        rows = {row["id"]: row for row in patched["official_monitors"]}
        self.assertEqual(rows["us-fda-animal-food"]["url"], "https://www.fda.gov/animal-food-feeds")
        self.assertGreaterEqual(len(rows["au-apvma-animal-feed"]["urls"]), 2)
        self.assertIn("2026-2035", rows["oecd-fao-agricultural-outlook"]["url"])

    def test_collector_adds_fallback_support(self):
        source = "prefix\n" + module.OLD_MONITOR_BLOCK + "\nsuffix"
        patched, changed = module.patch_collector(source)
        self.assertTrue(changed)
        self.assertIn('source.get("urls")', patched)
        self.assertIn('source_url=active_url', patched)
        repatched, changed_again = module.patch_collector(patched)
        self.assertFalse(changed_again)
        self.assertEqual(patched, repatched)


if __name__ == "__main__":
    unittest.main()
