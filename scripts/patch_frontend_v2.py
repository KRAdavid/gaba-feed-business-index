#!/usr/bin/env python3
"""Idempotently make the public dashboard merge GitHub static intelligence with Apps Script data."""
from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "docs" / "index.html"
MARKER = "GABA_INTELLIGENCE_V2_STATIC_MERGE"

START_NEEDLE = "  let type='all', items=[];\n"
TRY_NEEDLE = "  try{\n    const [papers,regulations,statistics,market]=await Promise.all([\n"
ASSIGN_NEEDLE = """    items=normalizeKnowledge({
      papers:papers.data,regulations:regulations.data,statistics:statistics.data,market:market.data
    });
"""
STATUS_NEEDLE = "    document.getElementById('knowledgeUpdated').textContent=`API 갱신 ${new Date().toLocaleString('ko-KR')}`;\n"
API_STATUS_NEEDLE = "    if(!apiStatus.classList.contains('online'))setApiStatus('online',`Master DB 연결됨 · 공개자료 ${items.length}건`);\n"
WEEKLY_NEEDLE = "논문은 GitHub Actions가 매주 자동 검색해 후보를 갱신합니다."

HELPERS = f"""  /* {MARKER} */
  async function loadStaticKnowledge(){{
    try{{
      const r=await fetch('data/knowledge_base.json',{{cache:'no-store'}});
      if(!r.ok)throw new Error(`HTTP ${{r.status}}`);
      const db=await r.json();
      return {{items:Array.isArray(db.items)?db.items:[],updated_at:db.updated_at||''}};
    }}catch(_e){{
      return {{items:[],updated_at:''}};
    }}
  }}
  function mergeKnowledge(...groups){{
    const merged=new Map();
    groups.flat().filter(Boolean).forEach(x=>{{
      const key=(x.url&&x.url!=='#')?x.url:`${{x.type||''}}|${{x.title||''}}|${{x.date||''}}`;
      merged.set(key,merged.has(key)?{{...merged.get(key),...x}}:x);
    }});
    return [...merged.values()];
  }}
"""


def patch_text(text: str) -> tuple[str, bool]:
    if MARKER in text:
        return text, False
    required = [START_NEEDLE, TRY_NEEDLE, ASSIGN_NEEDLE, STATUS_NEEDLE, API_STATUS_NEEDLE]
    missing = [needle[:80] for needle in required if needle not in text]
    if missing:
        raise RuntimeError(f"docs/index.html structure changed; patch needles missing: {missing}")

    text = text.replace(START_NEEDLE, START_NEEDLE + HELPERS, 1)
    text = text.replace(
        TRY_NEEDLE,
        "  const staticData=await loadStaticKnowledge();\n  items=staticData.items;\n" + TRY_NEEDLE,
        1,
    )
    text = text.replace(
        ASSIGN_NEEDLE,
        """    const apiItems=normalizeKnowledge({
      papers:papers.data,regulations:regulations.data,statistics:statistics.data,market:market.data
    });
    items=mergeKnowledge(staticData.items,apiItems);
""",
        1,
    )
    text = text.replace(
        STATUS_NEEDLE,
        "    document.getElementById('knowledgeUpdated').textContent=`GitHub 자동데이터 ${staticData.updated_at||'-'} · API ${new Date().toLocaleString('ko-KR')}`;\n",
        1,
    )
    text = text.replace(
        API_STATUS_NEEDLE,
        "    if(!apiStatus.classList.contains('online'))setApiStatus('online',`GitHub 자동데이터 ${staticData.items.length}건 · Master DB ${apiItems.length}건`);\n",
        1,
    )
    text = text.replace(
        WEEKLY_NEEDLE,
        "논문과 공식기관 정보는 GitHub Actions가 매일 자동 점검하고, 공개 기준을 통과한 자료만 갱신합니다.",
        1,
    )
    return text, True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="verify that the file is already patched or patchable")
    args = parser.parse_args()
    text = TARGET.read_text(encoding="utf-8")
    patched, changed = patch_text(text)
    if args.check:
        print("frontend already patched" if not changed else "frontend patch applicable")
        return 0
    if changed:
        TARGET.write_text(patched, encoding="utf-8")
        print("patched docs/index.html to merge static and Apps Script intelligence")
    else:
        print("docs/index.html already contains v2 static merge")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
