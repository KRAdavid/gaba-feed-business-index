import importlib.util
from pathlib import Path
import unittest

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "patch_calculator_scenarios.py"
spec = importlib.util.spec_from_file_location("patch_calculator_scenarios", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PatchCalculatorScenariosTest(unittest.TestCase):
    def test_installs_style_and_script(self):
        source = f"<html><head></head><body>{module.INQUIRY_SCRIPT}</body></html>"
        patched, changed = module.patch_text(source)
        self.assertTrue(changed)
        self.assertIn(module.STYLE_TAG, patched)
        self.assertIn(module.SCRIPT_TAG + module.INQUIRY_SCRIPT, patched)

    def test_is_idempotent(self):
        source = f"<html><head>{module.STYLE_TAG}</head><body>{module.SCRIPT_TAG}{module.INQUIRY_SCRIPT}</body></html>"
        patched, changed = module.patch_text(source)
        self.assertFalse(changed)
        self.assertEqual(source, patched)


if __name__ == "__main__":
    unittest.main()
