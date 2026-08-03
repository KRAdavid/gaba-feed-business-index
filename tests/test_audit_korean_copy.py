from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import audit_korean_copy  # noqa: E402


class KoreanCopyAuditTests(unittest.TestCase):
    def test_ignored_work_files_are_optional(self) -> None:
        missing = (
            ROOT / "__definitely_missing__" / "deck-builder.mjs",
            ROOT / "__definitely_missing__" / "workbook-builder.mjs",
        )
        with patch.object(audit_korean_copy, "OPTIONAL_TEXT_FILES", missing):
            errors = audit_korean_copy.audit_copy()
        self.assertFalse(errors, "\n".join(errors))


if __name__ == "__main__":
    unittest.main()
