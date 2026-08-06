import importlib.util
import sys
from pathlib import Path
import unittest

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "patch_inquiry_form.py"
spec = importlib.util.spec_from_file_location("patch_inquiry_form", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class TestPatchInquiryForm(unittest.TestCase):
    def test_inserts_assets_once(self):
        source = "<html><head></head><body><main></main></body></html>"
        patched, changed = module.patch_text(source)
        self.assertTrue(changed)
        self.assertIn(module.STYLE_TAG, patched)
        self.assertIn(module.SCRIPT_TAG, patched)

        second, changed_again = module.patch_text(patched)
        self.assertFalse(changed_again)
        self.assertEqual(second.count(module.STYLE_TAG), 1)
        self.assertEqual(second.count(module.SCRIPT_TAG), 1)

    def test_requires_document_boundaries(self):
        with self.assertRaises(RuntimeError):
            module.patch_text("<html><body></body></html>")
        with self.assertRaises(RuntimeError):
            module.patch_text("<html><head></head></html>")


if __name__ == "__main__":
    unittest.main()
