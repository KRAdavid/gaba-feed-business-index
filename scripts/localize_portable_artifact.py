#!/usr/bin/env python3
"""Localize the canonical portable artifact's fixed UI labels into Korean."""

from __future__ import annotations

import argparse
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path


FIXED_REPLACEMENTS = {
    '<html lang="en"': '<html lang="ko"',
    'Data Analytics dashboard': 'GABA 사업 대시보드',
    'Source for ': '근거: ',
    'Source: ': '출처: ',
    'File: ': '파일: ',
    'Table: ': '테이블: ',
    '>Sources</h2>': '>출처</h2>',
    ' data</caption>': ' 자료</caption>',
}


def localize_time(match: re.Match[str]) -> str:
    raw = match.group(1)
    try:
        utc_time = datetime.fromisoformat(raw.replace('Z', '+00:00'))
    except ValueError:
        return match.group(0)
    korea_time = utc_time.astimezone(timezone(timedelta(hours=9)))
    label = f'{korea_time.year}년 {korea_time.month}월 {korea_time.day}일 {korea_time:%H:%M} (한국 시간)'
    return f'<time datetime="{raw}">{label}</time>'


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('html', nargs='?', default='GABA_Business_Model_Index.html')
    args = parser.parse_args()

    path = Path(args.html).resolve()
    content = path.read_text(encoding='utf-8-sig')
    for source, target in FIXED_REPLACEMENTS.items():
        content = content.replace(source, target)
    content = re.sub(r'<time datetime="([^"]+)">.*?</time>', localize_time, content, count=1)
    path.write_text(content, encoding='utf-8')
    print(f'localized {path}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
