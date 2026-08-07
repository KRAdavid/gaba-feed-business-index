import importlib.util
from pathlib import Path
import unittest

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "patch_hero_banner_rotator.py"
spec = importlib.util.spec_from_file_location("patch_hero_banner_rotator", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PatchHeroBannerRotatorTest(unittest.TestCase):
    def test_installs_after_cta_assets(self):
        source = f"<html><head>{module.STYLE_ANCHOR}</head><body>{module.SCRIPT_ANCHOR}</body></html>"
        patched, changed = module.patch_text(source)
        self.assertTrue(changed)
        self.assertIn(module.STYLE_ANCHOR + "\n" + module.STYLE_TAG, patched)
        self.assertIn(module.SCRIPT_ANCHOR + module.SCRIPT_TAG, patched)

    def test_is_idempotent(self):
        source = (
            f"<html><head>{module.STYLE_ANCHOR}\n{module.STYLE_TAG}</head>"
            f"<body>{module.SCRIPT_ANCHOR}{module.SCRIPT_TAG}</body></html>"
        )
        patched, changed = module.patch_text(source)
        self.assertFalse(changed)
        self.assertEqual(source, patched)


if __name__ == "__main__":
    unittest.main()
