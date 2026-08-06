import importlib.util
import sys
from pathlib import Path
import unittest

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "patch_frontend_v2.py"
spec = importlib.util.spec_from_file_location("patch_frontend_v2", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class TestPatchFrontendV2(unittest.TestCase):
    def sample(self):
        return """<section>논문은 GitHub Actions가 매주 자동 검색해 후보를 갱신합니다.</section>
async function loadKnowledge(){
  const grid=document.getElementById('knowledgeGrid');
  const buttons=[...document.querySelectorAll('#knowledgeToolbar button')];
  let type='all', items=[];
  function draw(){}
  try{
    const [papers,regulations,statistics,market]=await Promise.all([
      apiGet('papers'),apiGet('regulations'),apiGet('statistics'),apiGet('market')
    ]);
    items=normalizeKnowledge({
      papers:papers.data,regulations:regulations.data,statistics:statistics.data,market:market.data
    });
    document.getElementById('knowledgeUpdated').textContent=`API 갱신 ${new Date().toLocaleString('ko-KR')}`;
    if(!apiStatus.classList.contains('online'))setApiStatus('online',`Master DB 연결됨 · 공개자료 ${items.length}건`);
    draw();
  }catch(e){}
}
"""

    def test_patch_is_idempotent_and_merges_sources(self):
        patched, changed = module.patch_text(self.sample())
        self.assertTrue(changed)
        self.assertIn(module.MARKER, patched)
        self.assertIn("items=mergeKnowledge(staticData.items,apiItems);", patched)
        self.assertIn("GitHub Actions가 매일 자동 점검", patched)
        second, changed_again = module.patch_text(patched)
        self.assertFalse(changed_again)
        self.assertEqual(second, patched)

    def test_missing_structure_fails_loudly(self):
        with self.assertRaises(RuntimeError):
            module.patch_text("<html></html>")


if __name__ == "__main__":
    unittest.main()
