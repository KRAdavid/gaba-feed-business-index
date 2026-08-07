import importlib.util
from pathlib import Path
import unittest

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "patch_product_split_selector.py"
spec = importlib.util.spec_from_file_location("patch_product_split_selector", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PatchProductSplitSelectorTest(unittest.TestCase):
    def test_installs_after_cta_assets(self):
        source = f"<html><head>{module.CTA_STYLE}</head><body>{module.CTA_SCRIPT}</body></html>"
        patched, changed = module.patch_text(source)
        self.assertTrue(changed)
        self.assertIn(module.CTA_STYLE + "\n" + module.STYLE_TAG, patched)
        self.assertIn(module.CTA_SCRIPT + module.SCRIPT_TAG, patched)

    def test_is_idempotent(self):
        source = (
            f"<html><head>{module.CTA_STYLE}\n{module.STYLE_TAG}</head>"
            f"<body>{module.CTA_SCRIPT}{module.SCRIPT_TAG}</body></html>"
        )
        patched, changed = module.patch_text(source)
        self.assertFalse(changed)
        self.assertEqual(source, patched)


if __name__ == "__main__":
    unittest.main()
