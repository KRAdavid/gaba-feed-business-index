#!/usr/bin/env python3
"""
GABA Feed Auto Intelligence Engine v1.0
- Zero-login scheduled collection
- PubMed, Europe PMC, Crossref
- Official policy/market/statistics page change monitoring
- Optional KOSIS / USDA integrations through GitHub Secrets
- Deterministic quality gate and deduplication
- Safe merge into docs/data/index.json

Only Python standard library is required.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "intelligence_sources.json"
STATE_PATH = ROOT / "data" / "auto_intelligence_state.json"
OUTPUT_PATH = ROOT / "docs" / "data" / "auto_intelligence.json"
INDEX_PATH = ROOT / "docs" / "data" / "index.json"
REVIEW_PATH = ROOT / "data" / "auto_review_queue.json"

USER_AGENT = "Cellpinda-GABA-Feed-Intelligence/1.0 (public research monitor)"
TIMEOUT = 35
MAX_ITEMS_PER_SOURCE = 25


@dataclass
class Item:
    item_id: str
    category: str
    source_type: str
    title: str
    summary: str
    source_name: str
    source_url: str
    published_at: str
    detected_at: str
    doi: str = ""
    pmid: str = ""
    species: str = "Multi-species"
    evidence_grade: str = "C"
    confidence: str = "medium"
    auto_publish: bool = False
    official_source: bool = False
    tags: list[str] | None = None
    metadata: dict[str, Any] | None = None


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_date(value: datetime | None = None) -> str:
    return (value or utc_now()).isoformat()


def request_bytes(url: str, headers: dict[str, str] | None = None) -> bytes:
    req_headers = {"User-Agent": USER_AGENT, "Accept": "*/*"}
    if headers:
        req_headers.update(headers)
    req = urllib.request.Request(url, headers=req_headers)
    with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
        return response.read()


def request_json(url: str) -> Any:
    return json.loads(request_bytes(url, {"Accept": "application/json"}).decode("utf-8"))


def clean_text(value: str | None) -> str:
    if not value:
        return ""
    value = html.unescape(value)
    value = re.sub(r"<[^>]+>", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def short_summary(text: str, max_chars: int = 420) -> str:
    text = clean_text(text)
    if not text:
        return "초록 또는 상세 설명이 제공되지 않았습니다."
    sentences = re.split(r"(?<=[.!?])\s+", text)
    chosen = []
    length = 0
    for sentence in sentences:
        if not sentence:
            continue
        if length + len(sentence) > max_chars and chosen:
            break
        chosen.append(sentence)
        length += len(sentence) + 1
        if len(chosen) >= 3:
            break
    result = " ".join(chosen).strip()
    return result[:max_chars].rstrip()


def stable_id(*parts: str) -> str:
    raw = "|".join(str(p or "").strip().lower() for p in parts)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:20]


SPECIES_RULES = {
    "Pig": ["pig", "swine", "porcine", "piglet", "sow", "boar"],
    "Broiler": ["broiler", "chicken", "poultry", "avian"],
    "Layer": ["laying hen", "layer hen", "egg production"],
    "Beef Cattle": ["beef cattle", "steer", "bull", "bovine"],
    "Dairy Cattle": ["dairy cow", "dairy cattle", "lactating cow", "milk yield"],
    "Aquaculture": ["fish", "shrimp", "aquaculture", "tilapia", "carp", "salmon"],
    "Sheep": ["sheep", "lamb", "ovine"],
    "Goat": ["goat", "caprine"],
}


def classify_species(text: str) -> str:
    lower = text.lower()
    matches = [name for name, terms in SPECIES_RULES.items() if any(t in lower for t in terms)]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        return "Multi-species"
    return "Multi-species"


def evidence_grade(title: str, abstract: str, publication_types: Iterable[str] = ()) -> str:
    text = f"{title} {abstract} {' '.join(publication_types)}".lower()
    if any(term in text for term in ["meta-analysis", "systematic review"]):
        return "A"
    if any(term in text for term in ["randomized controlled trial", "controlled trial", "clinical trial"]):
        return "A"
    if any(term in text for term in ["animal experiment", "feeding trial", "in vivo", "growth performance"]):
        return "B"
    if any(term in text for term in ["review", "observational", "cohort"]):
        return "B"
    if abstract:
        return "C"
    return "D"


def relevant_to_gaba_feed(title: str, abstract: str) -> bool:
    text = f"{title} {abstract}".lower()
    gaba = any(term in text for term in [
        "gamma-aminobutyric", "γ-aminobutyric", "gaba", "4-aminobutanoic"
    ])
    animal_or_feed = any(term in text for term in [
        "feed", "diet", "nutrition", "pig", "swine", "broiler", "chicken",
        "cattle", "cow", "fish", "shrimp", "sheep", "goat", "animal",
        "heat stress", "growth performance", "feed conversion"
    ])
    return gaba and animal_or_feed


def quality_gate(item: Item) -> Item:
    # Automatic publication is intentionally conservative.
    if item.category == "research":
        item.auto_publish = (
            bool(item.doi or item.pmid)
            and item.evidence_grade in {"A", "B", "C"}
            and len(item.summary) >= 80
            and item.source_type in {"pubmed", "europe_pmc", "crossref"}
        )
        item.confidence = "high" if item.evidence_grade in {"A", "B"} else "medium"
    elif item.category in {"policy", "statistics", "market"}:
        item.auto_publish = item.official_source and bool(item.source_url)
        item.confidence = "high" if item.official_source else "low"
    else:
        item.auto_publish = False
    return item


def collect_pubmed(config: dict[str, Any], since_days: int) -> list[Item]:
    queries = config.get("queries", [])
    items: list[Item] = []
    mindate = (utc_now() - timedelta(days=since_days)).strftime("%Y/%m/%d")
    maxdate = utc_now().strftime("%Y/%m/%d")

    for query in queries:
        params = urllib.parse.urlencode({
            "db": "pubmed",
            "term": query,
            "retmode": "json",
            "retmax": MAX_ITEMS_PER_SOURCE,
            "sort": "pub date",
            "mindate": mindate,
            "maxdate": maxdate,
            "datetype": "pdat",
        })
        search = request_json(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?{params}")
        ids = search.get("esearchresult", {}).get("idlist", [])
        if not ids:
            continue

        fetch_params = urllib.parse.urlencode({"db": "pubmed", "id": ",".join(ids), "retmode": "xml"})
        root = ET.fromstring(request_bytes(
            f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?{fetch_params}"
        ))

        for article in root.findall(".//PubmedArticle"):
            title = clean_text("".join(article.findtext(".//ArticleTitle") or ""))
            abstract_parts = [
                clean_text("".join(node.itertext()))
                for node in article.findall(".//Abstract/AbstractText")
            ]
            abstract = " ".join(x for x in abstract_parts if x)
            if not relevant_to_gaba_feed(title, abstract):
                continue
            pmid = clean_text(article.findtext(".//PMID"))
            doi = ""
            for node in article.findall(".//ArticleId"):
                if node.attrib.get("IdType") == "doi":
                    doi = clean_text(node.text)
            journal = clean_text(article.findtext(".//Journal/Title"))
            pub_types = [clean_text(n.text) for n in article.findall(".//PublicationType")]
            date_text = clean_text(article.findtext(".//PubDate/Year"))
            source_url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else ""
            item = Item(
                item_id=f"research-{stable_id(doi or pmid, title)}",
                category="research",
                source_type="pubmed",
                title=title,
                summary=short_summary(abstract),
                source_name=journal or "PubMed",
                source_url=source_url,
                published_at=date_text,
                detected_at=iso_date(),
                doi=doi,
                pmid=pmid,
                species=classify_species(f"{title} {abstract}"),
                evidence_grade=evidence_grade(title, abstract, pub_types),
                tags=["GABA", "animal nutrition", "research"],
                metadata={"query": query, "publication_types": pub_types},
            )
            items.append(quality_gate(item))
        time.sleep(0.35)
    return items


def collect_europe_pmc(config: dict[str, Any], since_days: int) -> list[Item]:
    items: list[Item] = []
    from_date = (utc_now() - timedelta(days=since_days)).strftime("%Y-%m-%d")
    for query in config.get("queries", []):
        full_query = f"({query}) AND FIRST_PDATE:[{from_date} TO *]"
        params = urllib.parse.urlencode({
            "query": full_query,
            "format": "json",
            "pageSize": MAX_ITEMS_PER_SOURCE,
            "sort": "FIRST_PDATE_D desc",
        })
        payload = request_json(f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?{params}")
        for row in payload.get("resultList", {}).get("result", []):
            title = clean_text(row.get("title"))
            abstract = clean_text(row.get("authorString", ""))  # result endpoint often omits abstract
            if not relevant_to_gaba_feed(title, abstract + " " + query):
                continue
            doi = clean_text(row.get("doi"))
            pmid = clean_text(row.get("pmid"))
            source_url = f"https://europepmc.org/article/MED/{pmid}" if pmid else (
                f"https://doi.org/{doi}" if doi else ""
            )
            item = Item(
                item_id=f"research-{stable_id(doi or pmid, title)}",
                category="research",
                source_type="europe_pmc",
                title=title,
                summary=short_summary(row.get("authorString", "")),
                source_name=clean_text(row.get("journalTitle")) or "Europe PMC",
                source_url=source_url,
                published_at=clean_text(row.get("firstPublicationDate") or row.get("pubYear")),
                detected_at=iso_date(),
                doi=doi,
                pmid=pmid,
                species=classify_species(title),
                evidence_grade="C" if doi or pmid else "D",
                tags=["GABA", "animal nutrition", "research"],
                metadata={"query": query, "cited_by_count": row.get("citedByCount", 0)},
            )
            items.append(quality_gate(item))
        time.sleep(0.25)
    return items


def collect_crossref(config: dict[str, Any], since_days: int) -> list[Item]:
    items: list[Item] = []
    from_date = (utc_now() - timedelta(days=since_days)).strftime("%Y-%m-%d")
    mailto = os.getenv("CROSSREF_MAILTO", "")
    for query in config.get("queries", []):
        params = {
            "query.bibliographic": query,
            "filter": f"from-pub-date:{from_date}",
            "rows": MAX_ITEMS_PER_SOURCE,
            "sort": "published",
            "order": "desc",
            "select": "DOI,title,abstract,published,URL,publisher,type,container-title",
        }
        if mailto:
            params["mailto"] = mailto
        payload = request_json("https://api.crossref.org/works?" + urllib.parse.urlencode(params))
        for row in payload.get("message", {}).get("items", []):
            title = clean_text((row.get("title") or [""])[0])
            abstract = clean_text(row.get("abstract"))
            if not relevant_to_gaba_feed(title, abstract + " " + query):
                continue
            doi = clean_text(row.get("DOI"))
            parts = ((row.get("published") or {}).get("date-parts") or [[]])[0]
            published = "-".join(str(v).zfill(2) for v in parts) if parts else ""
            journal = clean_text((row.get("container-title") or [""])[0])
            item = Item(
                item_id=f"research-{stable_id(doi, title)}",
                category="research",
                source_type="crossref",
                title=title,
                summary=short_summary(abstract),
                source_name=journal or clean_text(row.get("publisher")) or "Crossref",
                source_url=clean_text(row.get("URL")) or (f"https://doi.org/{doi}" if doi else ""),
                published_at=published,
                detected_at=iso_date(),
                doi=doi,
                species=classify_species(f"{title} {abstract}"),
                evidence_grade=evidence_grade(title, abstract),
                tags=["GABA", "animal nutrition", "research"],
                metadata={"query": query, "type": row.get("type", "")},
            )
            items.append(quality_gate(item))
        time.sleep(0.25)
    return items


def collect_official_monitors(monitors: list[dict[str, Any]], previous_state: dict[str, Any]) -> tuple[list[Item], dict[str, Any]]:
    items: list[Item] = []
    new_state = dict(previous_state)
    for source in monitors:
        url = source["url"]
        source_id = source["id"]
        try:
            body = request_bytes(url)
            digest = hashlib.sha256(body).hexdigest()
            old_digest = previous_state.get(source_id, {}).get("digest")
            changed = old_digest is not None and old_digest != digest
            first_seen = old_digest is None
            new_state[source_id] = {
                "digest": digest,
                "checked_at": iso_date(),
                "url": url,
            }
            if changed or (first_seen and source.get("publish_initial", False)):
                category = source.get("category", "policy")
                item = Item(
                    item_id=f"{category}-{stable_id(source_id, digest)}",
                    category=category,
                    source_type="official_monitor",
                    title=f"{source['name']} 공식 페이지 변경 감지",
                    summary=(
                        "공식 출처의 페이지 내용이 이전 점검본과 달라졌습니다. "
                        "변경 세부사항은 원문에서 확인해야 하며, 자동 감지는 법적 해석을 대신하지 않습니다."
                    ),
                    source_name=source["name"],
                    source_url=url,
                    published_at=utc_now().date().isoformat(),
                    detected_at=iso_date(),
                    species=source.get("species", "Multi-species"),
                    evidence_grade="A",
                    confidence="high",
                    official_source=True,
                    tags=[category, "official source", "change detection"],
                    metadata={"source_id": source_id, "content_hash": digest},
                )
                items.append(quality_gate(item))
        except Exception as exc:
            print(f"[WARN] monitor failed: {source_id}: {exc}", file=sys.stderr)
    return items, new_state


def dedupe(items: list[Item]) -> list[Item]:
    by_key: dict[str, Item] = {}
    rank = {"pubmed": 4, "europe_pmc": 3, "crossref": 2, "official_monitor": 5}
    for item in items:
        key = (item.doi.lower() if item.doi else item.pmid.lower() if item.pmid
               else stable_id(item.title, item.source_url))
        current = by_key.get(key)
        if current is None or rank.get(item.source_type, 0) > rank.get(current.source_type, 0):
            by_key[key] = item
    return sorted(by_key.values(), key=lambda x: (x.published_at, x.detected_at), reverse=True)


def load_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return default
    except json.JSONDecodeError:
        return default


def save_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(path)


def merge_public_index(public_items: list[dict[str, Any]], generated_at: str) -> None:
    index = load_json(INDEX_PATH, {})
    if not isinstance(index, dict):
        index = {"legacy_data": index}
    index["auto_intelligence"] = {
        "generated_at": generated_at,
        "count": len(public_items),
        "items": public_items,
    }
    index["auto_intelligence_updated_at"] = generated_at
    save_json(INDEX_PATH, index)


def run(since_days: int, dry_run: bool = False) -> dict[str, Any]:
    config = load_json(CONFIG_PATH, {})
    state = load_json(STATE_PATH, {"official_monitors": {}})
    all_items: list[Item] = []
    failures: list[dict[str, str]] = []

    collectors = [
        ("pubmed", collect_pubmed),
        ("europe_pmc", collect_europe_pmc),
        ("crossref", collect_crossref),
    ]
    for name, func in collectors:
        if not config.get(name, {}).get("enabled", True):
            continue
        try:
            found = func(config.get(name, {}), since_days)
            all_items.extend(found)
            print(f"[OK] {name}: {len(found)}")
        except Exception as exc:
            failures.append({"source": name, "error": str(exc)})
            print(f"[WARN] {name}: {exc}", file=sys.stderr)

    monitor_state = state.get("official_monitors", {})
    monitor_items, new_monitor_state = collect_official_monitors(
        config.get("official_monitors", []), monitor_state
    )
    all_items.extend(monitor_items)

    unique = dedupe(all_items)
    public_items = [asdict(x) for x in unique if x.auto_publish]
    review_items = [asdict(x) for x in unique if not x.auto_publish]
    generated_at = iso_date()

    output = {
        "version": "1.0.0",
        "generated_at": generated_at,
        "status": "partial" if failures else "healthy",
        "sources": {
            "pubmed": config.get("pubmed", {}).get("enabled", True),
            "europe_pmc": config.get("europe_pmc", {}).get("enabled", True),
            "crossref": config.get("crossref", {}).get("enabled", True),
            "official_monitors": len(config.get("official_monitors", [])),
        },
        "counts": {
            "collected": len(all_items),
            "deduplicated": len(unique),
            "auto_published": len(public_items),
            "review_queue": len(review_items),
        },
        "items": public_items,
        "failures": failures,
        "disclaimer": (
            "자동 수집·분류 결과이며, 규제 해석과 제품 효능 확정을 대신하지 않습니다. "
            "공식 원문과 시험조건을 함께 확인해야 합니다."
        ),
    }

    if not dry_run:
        save_json(OUTPUT_PATH, output)
        save_json(REVIEW_PATH, {
            "generated_at": generated_at,
            "count": len(review_items),
            "items": review_items,
        })
        state["official_monitors"] = new_monitor_state
        state["last_run_at"] = generated_at
        save_json(STATE_PATH, state)
        merge_public_index(public_items, generated_at)
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--since-days", type=int, default=14)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    result = run(max(1, min(args.since_days, 365)), args.dry_run)
    print(json.dumps(result["counts"], ensure_ascii=False))
    # Fail only if every network source failed.
    enabled_network_sources = 3
    return 1 if len(result["failures"]) >= enabled_network_sources else 0


if __name__ == "__main__":
    raise SystemExit(main())
