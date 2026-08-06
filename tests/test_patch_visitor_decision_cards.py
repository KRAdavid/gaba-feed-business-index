import importlib.util
from pathlib import Path
import unittest

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "patch_visitor_decision_cards.py"
spec = importlib.util.spec_from_file_location("patch_visitor_decision_cards", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PatchVisitorDecisionCardsTest(unittest.TestCase):
    def test_installs_after_order_assets(self):
        source = f"<html><head>{module.ORDER_STYLE}</head><body>{module.ORDER_SCRIPT}</body></html>"
        patched, changed = module.patch_text(source)
        self.assertTrue(changed)
        self.assertIn(module.ORDER_STYLE + "\n" + module.STYLE_TAG, patched)
        self.assertIn(module.ORDER_SCRIPT + module.SCRIPT_TAG, patched)

    def test_is_idempotent(self):
        source = (
            f"<html><head>{module.ORDER_STYLE}\n{module.STYLE_TAG}</head>"
            f"<body>{module.ORDER_SCRIPT}{module.SCRIPT_TAG}</body></html>"
        )
        patched, changed = module.patch_text(source)
        self.assertFalse(changed)
        self.assertEqual(source, patched)


if __name__ == "__main__":
    unittest.main()
