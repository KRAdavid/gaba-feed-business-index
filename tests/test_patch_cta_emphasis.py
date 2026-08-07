import importlib.util
from pathlib import Path
import unittest

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "patch_cta_emphasis.py"
spec = importlib.util.spec_from_file_location("patch_cta_emphasis", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PatchCtaEmphasisTest(unittest.TestCase):
    def test_installs_after_visitor_assets(self):
        source = f"<html><head>{module.VISITOR_STYLE}</head><body>{module.VISITOR_SCRIPT}</body></html>"
        patched, changed = module.patch_text(source)
        self.assertTrue(changed)
        self.assertIn(module.VISITOR_STYLE + "\n" + module.STYLE_TAG, patched)
        self.assertIn(module.VISITOR_SCRIPT + module.SCRIPT_TAG, patched)

    def test_is_idempotent(self):
        source = (
            f"<html><head>{module.VISITOR_STYLE}\n{module.STYLE_TAG}</head>"
            f"<body>{module.VISITOR_SCRIPT}{module.SCRIPT_TAG}</body></html>"
        )
        patched, changed = module.patch_text(source)
        self.assertFalse(changed)
        self.assertEqual(source, patched)


if __name__ == "__main__":
    unittest.main()
