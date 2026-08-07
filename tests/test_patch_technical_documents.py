import importlib.util
from pathlib import Path
import unittest

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "patch_technical_documents.py"
spec = importlib.util.spec_from_file_location("patch_technical_documents", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PatchTechnicalDocumentsTest(unittest.TestCase):
    def test_installs_after_split_assets(self):
        source = f"<html><head>{module.SPLIT_STYLE}</head><body>{module.SPLIT_SCRIPT}</body></html>"
        patched, changed = module.patch_text(source)
        self.assertTrue(changed)
        self.assertIn(module.SPLIT_STYLE + "\n" + module.STYLE_TAG, patched)
        self.assertIn(module.SPLIT_SCRIPT + module.SCRIPT_TAG, patched)

    def test_is_idempotent(self):
        source = (
            f"<html><head>{module.SPLIT_STYLE}\n{module.STYLE_TAG}</head>"
            f"<body>{module.SPLIT_SCRIPT}{module.SCRIPT_TAG}</body></html>"
        )
        patched, changed = module.patch_text(source)
        self.assertFalse(changed)
        self.assertEqual(source, patched)


if __name__ == "__main__":
    unittest.main()
