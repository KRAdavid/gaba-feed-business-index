from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class InquiryE2EStaticTests(unittest.TestCase):
    def setUp(self):
        self.apps_script = (ROOT / "apps-script" / "Inquiry_v2.gs").read_text(encoding="utf-8")
        self.route = (ROOT / "docs" / "assets" / "inquiry-apps-script.js").read_text(encoding="utf-8")

    def test_runtime_route_is_single_apps_script_receiver(self):
        self.assertEqual(self.apps_script.count("function doPost("), 1)
        self.assertIn("feed@cellpinda.com", self.apps_script)
        self.assertIn("script.google.com/macros/s/", self.route)
        self.assertIn("form.method = 'POST'", self.route)
        self.assertIn("form.target = IFRAME_NAME", self.route)

    def test_inquiry_creates_and_links_lead(self):
        self.assertIn("LEAD_SHEET_NAME: 'Lead_Pipeline'", self.apps_script)
        self.assertIn("function gabaCreateLeadV2_", self.apps_script)
        self.assertIn("LEAD-", self.apps_script)
        self.assertIn("gabaInquiryUpdateLeadV2_", self.apps_script)
        self.assertIn("Lead_Status", self.apps_script)
        self.assertIn("lead_id: leadResult.leadId", self.apps_script)

    def test_lead_creation_is_best_effort_and_reports_failure(self):
        self.assertIn("Lead creation is deliberately best-effort", self.apps_script)
        self.assertIn("status: 'FAILED'", self.apps_script)
        self.assertIn("lead_error: leadResult.error || ''", self.apps_script)


if __name__ == "__main__":
    unittest.main()
