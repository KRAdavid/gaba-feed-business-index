import importlib.util
from pathlib import Path
import unittest

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "patch_order_guide.py"
spec = importlib.util.spec_from_file_location("patch_order_guide", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PatchOrderGuideTest(unittest.TestCase):
    def test_adds_assets_after_inquiry_script(self):
        source = f"<html><head></head><body>{module.INQUIRY_SCRIPT}</body></html>"
        patched, changed = module.patch_text(source)
        self.assertTrue(changed)
        self.assertIn(module.STYLE_TAG, patched)
        self.assertIn(module.INQUIRY_SCRIPT + module.SCRIPT_TAG, patched)

    def test_is_idempotent(self):
        source = f"<html><head>{module.STYLE_TAG}</head><body>{module.INQUIRY_SCRIPT}{module.SCRIPT_TAG}</body></html>"
        patched, changed = module.patch_text(source)
        self.assertFalse(changed)
        self.assertEqual(source, patched)


if __name__ == "__main__":
    unittest.main()
