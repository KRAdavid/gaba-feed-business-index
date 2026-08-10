import json
from pathlib import Path
import importlib.util
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "validate_evidence_qa.py"
spec = importlib.util.spec_from_file_location("validate_evidence_qa", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class EvidenceQATests(unittest.TestCase):
    def test_current_matrix_has_three_review_documents_and_no_red_claims(self):
        payload = json.loads((ROOT / "data" / "evidence_claim_matrix.json").read_text(encoding="utf-8"))
        self.assertEqual(module.validate(payload), [])
        self.assertEqual(len(payload["documents"]), 3)
        self.assertFalse(any(row.get("public") for row in payload["claims"]))

    def test_public_claim_requires_green_qa(self):
        payload = {"documents": [], "claims": [{"claim_id": "x", "source": "source", "public": True, "qa_status": "AMBER"}]}
        self.assertTrue(module.validate(payload))


if __name__ == "__main__":
    unittest.main()
