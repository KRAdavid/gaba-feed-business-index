import importlib.util
from pathlib import Path
import unittest

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "patch_inquiry_apps_script.py"
spec = importlib.util.spec_from_file_location("patch_inquiry_apps_script", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PatchInquiryAppsScriptTest(unittest.TestCase):
    def test_replaces_old_delivery_client(self):
        source = f"<html><body>{module.INQUIRY_SCRIPT}{module.DELIVERY_SCRIPT}</body></html>"
        patched, changed = module.patch_text(source)
        self.assertTrue(changed)
        self.assertNotIn(module.DELIVERY_SCRIPT, patched)
        self.assertIn(module.SCRIPT_TAG, patched)

    def test_is_idempotent(self):
        source = f"<html><body>{module.INQUIRY_SCRIPT}{module.SCRIPT_TAG}</body></html>"
        patched, changed = module.patch_text(source)
        self.assertFalse(changed)
        self.assertEqual(source, patched)


if __name__ == "__main__":
    unittest.main()
