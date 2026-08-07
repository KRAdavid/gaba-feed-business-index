#!/usr/bin/env python3
"""Cellpinda GABA Feed Intelligence Engine v2.

Daily collection from PubMed, Europe PMC and Crossref, conservative quality
screening, confirmed official-page change detection, curated baseline merging,
and deterministic JSON publishing for the public dashboard.

Only the Python standard library is required.
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
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "intelligence_sources_v2.json"
CURATED_PATH = ROOT / "config" / "curated_intelligence.json"
STATE_PATH = ROOT / "data" / "auto_intelligence_state.json"
REVIEW_PATH = ROOT / "data" / "auto_review_queue.json"
OUTPUT_PATH = ROOT / "docs" / "data" / "auto_intelligence.json"
KNOWLEDGE_PATH = ROOT / "docs" / "data" / "knowledge_base.json"
STATUS_PATH = ROOT / "docs" / "data" / "update_status.json"
INDEX_PATH = ROOT / "docs" / "data" / "index.json"

USER_AGENT = "Cellpinda-GABA-Feed-Intelligence/2.0 (+https://github.com/KRAdavid/gaba-feed-business-index)"
TIMEOUT = 35
RETRIES = 3


@dataclass
class Item:
    item_id: str
    category: str
    source_type: str
    title: str
    summary: str
    source_name: str
    source_url: str
    published_at: str = ""
    detected_at: str = ""
    doi: str = ""
    pmid: str = ""
    species: str = "Multi-species"
    evidence_grade: str = "C"
    confidence: str = "medium"
    auto_publish: bool = False
    official_source: bool = False
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def iso_now() -> str:
    return now_utc().replace(microsecond=0).isoformat()


def load_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def canonical_json(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=False) + "\n"


def save_if_changed(path: Path, payload: Any) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = canonical_json(payload)
    old = path.read_text(encoding="utf-8") if path.exists() else None
    if old == text:
        return False
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)
    return True


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    text = html.unescape(str(value))
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def short_summary(value: str, limit: int = 520) -> str:
    text = clean_text(value)
    if not text:
        return ""
    sentences = re.split(r"(?<=[.!?])\s+", text)
    out: list[str] = []
    for sentence in sentences:
        if out and len(" ".join(out + [sentence])) > limit:
            break
        out.append(sentence)
        if len(out) >= 3:
            break
    return " ".join(out)[:limit].rstrip()


def normalize_doi(value: str) -> str:
    value = clean_text(value).lower()
    value = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", value)
    return value.strip().rstrip(".")


def normalize_title(value: str) -> str:
    value = clean_text(value).lower()
    value = re.sub(r"[^0-9a-z가-힣α-ωγ]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def stable_id(*parts: str) -> str:
    raw = "|".join(clean_text(x).lower() for x in parts)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:20]


GABA_RE = re.compile(r"(?:\bgaba\b|가바|gamma[- ]aminobutyric|γ[- ]aminobutyric|4[- ]aminobutanoic)", re.I)
FEED_RE = re.compile(r"(?:\bfeed(?:ing)?\b|\bdiet(?:ary)?\b|nutrition|supplement(?:ation)?|ration|premix|digestibility|feed conversion|growth performance|사료|급여|영양|소화율|사료효율|증체)", re.I)
ANIMAL_RE = re.compile(r"(?:\banimal\b|livestock|piglet|\bpig\b|swine|porcine|sow|boar|broiler|chicken|poultry|hen|cattle|bovine|cow|steer|calf|fish|shrimp|aquaculture|tilapia|carp|salmon|sheep|lamb|goat|가축|동물|돼지|자돈|종모돈|종빈돈|육계|산란계|소|한우|육우|젖소|송아지|어류|새우|양|염소)", re.I)

SPECIES_RULES: list[tuple[str, re.Pattern[str]]] = [
    ("Pig", re.compile(r"piglet|\bpig\b|swine|porcine|sow|boar", re.I)),
    ("Broiler", re.compile(r"broiler|chicken|poultry|avian", re.I)),
    ("Layer", re.compile(r"laying hen|layer hen|egg production", re.I)),
    ("Dairy Cattle", re.compile(r"dairy cow|lactating cow|milk yield", re.I)),
    ("Beef Cattle", re.compile(r"beef cattle|steer|bull|hanwoo|bovine", re.I)),
    ("Calf", re.compile(r"pre[- ]?weaned calf|\bcalves\b|\bcalf\b", re.I)),
    ("Aquaculture", re.compile(r"fish|shrimp|aquaculture|tilapia|carp|salmon", re.I)),
    ("Sheep", re.compile(r"sheep|lamb|ovine", re.I)),
    ("Goat", re.compile(r"goat|caprine", re.I)),
]


def classify_species(text: str) -> str:
    matches = [name for name, pattern in SPECIES_RULES if pattern.search(text)]
    return matches[0] if len(matches) == 1 else "Multi-species"


def strict_relevance(title: str, abstract: str) -> bool:
    text = f"{title} {abstract}"
    return bool(GABA_RE.search(text) and ANIMAL_RE.search(text) and FEED_RE.search(text))


def plausible_date(value: str, future_days: int = 31) -> bool:
    value = clean_text(value)
    match = re.match(r"^(\d{4})(?:-(\d{1,2}))?(?:-(\d{1,2}))?", value)
    if not match:
        return False
    year, month, day = int(match.group(1)), int(match.group(2) or 1), int(match.group(3) or 1)
    try:
        parsed = date(year, month, day)
    except ValueError:
        return False
    return date(1990, 1, 1) <= parsed <= (now_utc().date() + timedelta(days=future_days))


def evidence_grade(title: str, abstract: str, publication_types: Iterable[str] = ()) -> str:
    text = f"{title} {abstract} {' '.join(publication_types)}".lower()
    if "meta-analysis" in text or "systematic review" in text:
        return "A"
    if any(x in text for x in ("feeding trial", "controlled trial", "randomized", "in vivo", "growth performance")):
        return "B"
    return "C" if abstract else "D"


def request_bytes(url: str, headers: dict[str, str] | None = None) -> bytes:
    req_headers = {"User-Agent": USER_AGENT, "Accept": "*/*"}
    if headers:
        req_headers.update(headers)
    last_error: Exception | None = None
    for attempt in range(RETRIES):
        try:
            req = urllib.request.Request(url, headers=req_headers)
            with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
                return response.read()
        except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
            last_error = exc
            if attempt + 1 < RETRIES:
                time.sleep(1.2 * (2**attempt))
    raise RuntimeError(f"request failed after {RETRIES} attempts: {url}: {last_error}")


def request_json(url: str) -> Any:
    return json.loads(request_bytes(url, {"Accept": "application/json"}).decode("utf-8"))


def quality_gate(item: Item, config: dict[str, Any]) -> Item:
    future_days = int(config.get("settings", {}).get("future_date_tolerance_days", 31))
    if item.source_type == "curated":
        item.auto_publish = bool(item.title and item.summary and item.source_url)
        item.confidence = "high" if item.official_source or item.evidence_grade in {"A", "B"} else "medium"
        return item
    if item.category == "research":
        relevant = strict_relevance(item.title, item.summary)
        valid_date = plausible_date(item.published_at, future_days)
        trusted_source = item.source_type in {"pubmed", "europe_pmc"}
        item.auto_publish = bool(
            trusted_source
            and relevant
            and valid_date
            and (item.doi or item.pmid)
            and len(item.summary) >= 100
            and item.evidence_grade != "D"
        )
        item.confidence = "high" if item.auto_publish and item.evidence_grade in {"A", "B"} else "medium"
    elif item.source_type == "official_monitor":
        item.auto_publish = item.official_source
        item.confidence = "high"
    else:
        item.auto_publish = False
    return item


def item_key(item: Item | dict[str, Any]) -> str:
    getter = item.get if isinstance(item, dict) else lambda k, d="": getattr(item, k, d)
    doi = normalize_doi(getter("doi", ""))
    pmid = clean_text(getter("pmid", ""))
    category = clean_text(getter("category", ""))
    if doi:
        return f"doi:{doi}"
    if pmid:
        return f"pmid:{pmid}"
    return f"{category}:{stable_id(normalize_title(getter('title', '')), getter('source_url', ''))}"


def item_rank(item: Item) -> tuple[int, int, int]:
    source_rank = {"curated": 6, "pubmed": 5, "europe_pmc": 4, "official_monitor": 4, "crossref": 2}.get(item.source_type, 1)
    return (1 if item.auto_publish else 0, source_rank, len(item.summary))


def merge_items(existing: list[Item], incoming: list[Item], limit: int) -> list[Item]:
    old_by_key = {item_key(x): x for x in existing}
    merged: dict[str, Item] = {}
    for item in existing + incoming:
        key = item_key(item)
        current = merged.get(key)
        if current is None or item_rank(item) > item_rank(current):
            if key in old_by_key and old_by_key[key].detected_at:
                item.detected_at = old_by_key[key].detected_at
            merged[key] = item
    def sort_key(x: Item) -> tuple[str, str]:
        return (x.published_at or "0000", x.detected_at or "")
    return sorted(merged.values(), key=sort_key, reverse=True)[:limit]


def curated_items(config: dict[str, Any]) -> list[Item]:
    payload = load_json(CURATED_PATH, {"items": []})
    out: list[Item] = []
    for row in payload.get("items", []):
        data = dict(row)
        data.setdefault("item_id", f"curated-{stable_id(data.get('title',''), data.get('source_url',''))}")
        data.setdefault("source_type", "curated")
        data.setdefault("detected_at", data.get("curated_at", "2026-08-06T00:00:00+00:00"))
        data.setdefault("tags", [])
        data.setdefault("metadata", {})
        data.setdefault("auto_publish", True)
        item = Item(**{k: v for k, v in data.items() if k in Item.__dataclass_fields__})
        out.append(quality_gate(item, config))
    return out


def collect_pubmed(cfg: dict[str, Any], settings: dict[str, Any], since_days: int) -> list[Item]:
    out: list[Item] = []
    retmax = int(settings.get("max_items_per_query", 20))
    mindate = (now_utc() - timedelta(days=since_days)).strftime("%Y/%m/%d")
    maxdate = now_utc().strftime("%Y/%m/%d")
    for query in cfg.get("queries", []):
        params = urllib.parse.urlencode({"db": "pubmed", "term": query, "retmode": "json", "retmax": retmax,
                                         "sort": "pub date", "mindate": mindate, "maxdate": maxdate, "datetype": "pdat"})
        ids = request_json(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?{params}").get("esearchresult", {}).get("idlist", [])
        if not ids:
            continue
        fetch_params = urllib.parse.urlencode({"db": "pubmed", "id": ",".join(ids), "retmode": "xml"})
        root = ET.fromstring(request_bytes(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?{fetch_params}"))
        for article in root.findall(".//PubmedArticle"):
            title_node = article.find(".//ArticleTitle")
            title = clean_text("".join(title_node.itertext()) if title_node is not None else "")
            abstract = " ".join(clean_text("".join(n.itertext())) for n in article.findall(".//Abstract/AbstractText"))
            if not strict_relevance(title, abstract):
                continue
            pmid = clean_text(article.findtext(".//PMID"))
            doi = ""
            for node in article.findall(".//ArticleId"):
                if node.attrib.get("IdType") == "doi":
                    doi = normalize_doi(node.text or "")
            pub_types = [clean_text(n.text) for n in article.findall(".//PublicationType")]
            year = clean_text(article.findtext(".//PubDate/Year")) or clean_text(article.findtext(".//ArticleDate/Year"))
            item = Item(
                item_id=f"research-{stable_id(doi or pmid, title)}", category="research", source_type="pubmed",
                title=title, summary=short_summary(abstract), source_name=clean_text(article.findtext(".//Journal/Title")) or "PubMed",
                source_url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else (f"https://doi.org/{doi}" if doi else ""),
                published_at=year, detected_at=iso_now(), doi=doi, pmid=pmid,
                species=classify_species(f"{title} {abstract}"), evidence_grade=evidence_grade(title, abstract, pub_types),
                tags=["GABA", "animal nutrition", "research"], metadata={"publication_types": pub_types},
            )
            out.append(quality_gate(item, {"settings": settings}))
        time.sleep(0.35)
    return out


def collect_europe_pmc(cfg: dict[str, Any], settings: dict[str, Any], since_days: int) -> list[Item]:
    out: list[Item] = []
    page_size = int(settings.get("max_items_per_query", 20))
    from_date = (now_utc() - timedelta(days=since_days)).strftime("%Y-%m-%d")
    for query in cfg.get("queries", []):
        full_query = f"({query}) AND FIRST_PDATE:[{from_date} TO {now_utc().date().isoformat()}]"
        params = urllib.parse.urlencode({"query": full_query, "format": "json", "resultType": "core", "pageSize": page_size, "sort": "FIRST_PDATE_D desc"})
        payload = request_json(f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?{params}")
        for row in payload.get("resultList", {}).get("result", []):
            title = clean_text(row.get("title"))
            abstract = clean_text(row.get("abstractText"))
            if not strict_relevance(title, abstract):
                continue
            doi, pmid = normalize_doi(row.get("doi", "")), clean_text(row.get("pmid"))
            published = clean_text(row.get("firstPublicationDate") or row.get("pubYear"))
            item = Item(
                item_id=f"research-{stable_id(doi or pmid, title)}", category="research", source_type="europe_pmc",
                title=title, summary=short_summary(abstract), source_name=clean_text(row.get("journalTitle")) or "Europe PMC",
                source_url=f"https://europepmc.org/article/MED/{pmid}" if pmid else (f"https://doi.org/{doi}" if doi else ""),
                published_at=published, detected_at=iso_now(), doi=doi, pmid=pmid,
                species=classify_species(f"{title} {abstract}"), evidence_grade=evidence_grade(title, abstract),
                tags=["GABA", "animal nutrition", "research"], metadata={"cited_by_count": row.get("citedByCount", 0)},
            )
            out.append(quality_gate(item, {"settings": settings}))
        time.sleep(0.25)
    return out


def collect_crossref(cfg: dict[str, Any], settings: dict[str, Any], since_days: int) -> list[Item]:
    out: list[Item] = []
    rows = int(settings.get("max_items_per_query", 20))
    from_date = (now_utc() - timedelta(days=since_days)).strftime("%Y-%m-%d")
    until_date = now_utc().date().isoformat()
    for query in cfg.get("queries", []):
        params: dict[str, Any] = {"query.bibliographic": query, "filter": f"from-pub-date:{from_date},until-pub-date:{until_date}",
                                  "rows": rows, "sort": "published", "order": "desc",
                                  "select": "DOI,title,abstract,published,URL,publisher,type,container-title"}
        if os.getenv("CROSSREF_MAILTO"):
            params["mailto"] = os.environ["CROSSREF_MAILTO"]
        payload = request_json("https://api.crossref.org/works?" + urllib.parse.urlencode(params))
        for row in payload.get("message", {}).get("items", []):
            title = clean_text((row.get("title") or [""])[0])
            abstract = clean_text(row.get("abstract"))
            if not strict_relevance(title, abstract):
                continue
            doi = normalize_doi(row.get("DOI", ""))
            parts = ((row.get("published") or {}).get("date-parts") or [[]])[0]
            published = "-".join(str(v).zfill(2) for v in parts) if parts else ""
            item = Item(
                item_id=f"research-{stable_id(doi, title)}", category="research", source_type="crossref",
                title=title, summary=short_summary(abstract), source_name=clean_text((row.get("container-title") or [""])[0]) or clean_text(row.get("publisher")) or "Crossref",
                source_url=clean_text(row.get("URL")) or (f"https://doi.org/{doi}" if doi else ""),
                published_at=published, detected_at=iso_now(), doi=doi,
                species=classify_species(f"{title} {abstract}"), evidence_grade=evidence_grade(title, abstract),
                auto_publish=False, tags=["GABA", "animal nutrition", "research"], metadata={"type": row.get("type", ""), "review_required": True},
            )
            out.append(quality_gate(item, {"settings": settings}))
        time.sleep(0.25)
    return out


def visible_text_digest(raw: bytes, keywords: list[str]) -> str:
    text = raw.decode("utf-8", errors="ignore")
    text = re.sub(r"<(script|style|noscript)[^>]*>.*?</\1>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.S)
    text = clean_text(text).lower()
    text = re.sub(r"\b\d{1,2}:\d{2}(?::\d{2})?\b", " ", text)
    text = re.sub(r"\b(?:19|20)\d{2}[./-]\d{1,2}[./-]\d{1,2}\b", " ", text)
    if keywords:
        windows: list[str] = []
        for keyword in keywords:
            for match in re.finditer(re.escape(keyword.lower()), text):
                windows.append(text[max(0, match.start() - 500): match.end() + 1500])
                if len(windows) >= 30:
                    break
        if windows:
            text = " ".join(windows)
    text = re.sub(r"\s+", " ", text)[:120000]
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def advance_monitor_state(old: dict[str, Any], digest: str, confirmations: int) -> tuple[dict[str, Any], bool]:
    old_digest = clean_text(old.get("digest"))
    if not old_digest:
        return {"digest": digest, "candidate_digest": "", "candidate_count": 0}, False
    if digest == old_digest:
        return {"digest": old_digest, "candidate_digest": "", "candidate_count": 0}, False
    candidate = clean_text(old.get("candidate_digest"))
    count = int(old.get("candidate_count", 0)) + 1 if candidate == digest else 1
    if count >= max(1, confirmations):
        return {"digest": digest, "candidate_digest": "", "candidate_count": 0}, True
    return {"digest": old_digest, "candidate_digest": digest, "candidate_count": count}, False


def collect_official_monitors(monitors: list[dict[str, Any]], old_state: dict[str, Any], config: dict[str, Any]) -> tuple[list[Item], dict[str, Any], list[dict[str, str]]]:
    items: list[Item] = []
    state = dict(old_state)
    failures: list[dict[str, str]] = []
    for source in monitors:
        sid = source["id"]
        urls = [url for url in (source.get("urls") or [source.get("url")]) if url]
        active_url = ""
        last_error: Exception | None = None
        try:
            raw: bytes | None = None
            for candidate_url in urls:
                try:
                    raw = request_bytes(candidate_url)
                    active_url = candidate_url
                    break
                except Exception as exc:
                    last_error = exc
            if raw is None:
                raise last_error or RuntimeError(f"no monitor URL configured for {sid}")

            digest = visible_text_digest(raw, source.get("keywords", []))
            next_state, confirmed = advance_monitor_state(state.get(sid, {}), digest, int(source.get("confirmation_runs", 2)))
            next_state["url"] = active_url
            next_state["fallback_count"] = max(0, urls.index(active_url)) if active_url in urls else 0
            state[sid] = next_state
            if confirmed or (not old_state.get(sid) and source.get("publish_initial", False)):
                category = source.get("category", "policy")
                item = Item(
                    item_id=f"{category}-{stable_id(sid, digest)}", category=category, source_type="official_monitor",
                    title=f"{source['name']} 관련 페이지 변경 확인 필요", summary="공식 출처의 관련 페이지에서 두 차례 연속 동일한 변경이 감지되었습니다. 변경 내용은 원문과 시행일을 확인한 뒤 사업 자료에 반영해야 합니다.",
                    source_name=source["name"], source_url=active_url, published_at=now_utc().date().isoformat(), detected_at=iso_now(),
                    species=source.get("species", "Multi-species"), evidence_grade="A", confidence="high", official_source=True,
                    tags=[category, "official source", "confirmed change"], metadata={"source_id": sid, "content_hash": digest, "confirmation_runs": source.get("confirmation_runs", 2), "fallback_count": next_state["fallback_count"]},
                )
                items.append(quality_gate(item, config))
        except Exception as exc:  # monitoring must not stop research collection
            failures.append({"source": sid, "error": str(exc)[:300], "attempted_urls": urls})
    return items, state, failures


def row_to_item(row: dict[str, Any], config: dict[str, Any]) -> Item | None:
    try:
        data = {k: row.get(k) for k in Item.__dataclass_fields__ if k in row}
        data.setdefault("tags", [])
        data.setdefault("metadata", {})
        item = Item(**data)
    except (TypeError, ValueError):
        return None
    if item.source_type == "official_monitor" and not item.metadata.get("confirmation_runs"):
        return None
    if item.category == "research" and not strict_relevance(item.title, item.summary):
        return None
    if item.category == "research" and not plausible_date(item.published_at, int(config.get("settings", {}).get("future_date_tolerance_days", 31))):
        return None
    return quality_gate(item, config)


def knowledge_payload(items: list[Item], generated_at: str) -> dict[str, Any]:
    type_map = {"research": "paper", "policy": "policy", "statistics": "statistics", "market": "market"}
    rows = []
    for item in items:
        rows.append({
            "id": item.item_id, "type": type_map.get(item.category, item.category),
            "category": f"{item.category} · {item.species}" if item.category == "research" else f"{item.category} · {item.source_name}",
            "date": item.published_at, "title": item.title, "summary": item.summary, "url": item.source_url,
            "source": item.source_name, "evidence_grade": item.evidence_grade, "confidence": item.confidence,
        })
    counts = {key: sum(1 for x in rows if x["type"] == key) for key in ("paper", "policy", "statistics", "market")}
    return {"schema_version": "2.0.0", "updated_at": generated_at, "count": len(rows), "counts": counts, "items": rows}


def semantic_digest(public_items: list[Item], review_items: list[Item], failures: list[dict[str, str]], monitor_state: dict[str, Any]) -> str:
    payload = {
        "public": [{k: v for k, v in asdict(x).items() if k != "detected_at"} for x in public_items],
        "review": [{k: v for k, v in asdict(x).items() if k != "detected_at"} for x in review_items],
        "failures": failures,
        "monitor_state": monitor_state,
    }
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def validate_outputs() -> None:
    output = load_json(OUTPUT_PATH, None)
    knowledge = load_json(KNOWLEDGE_PATH, None)
    review = load_json(REVIEW_PATH, None)
    status = load_json(STATUS_PATH, None)
    state = load_json(STATE_PATH, None)
    for name, payload in (("output", output), ("knowledge", knowledge), ("review", review), ("status", status), ("state", state)):
        if not isinstance(payload, dict):
            raise ValueError(f"{name} is not a JSON object")
    if output.get("counts", {}).get("auto_published") != len(output.get("items", [])):
        raise ValueError("published count mismatch")
    for row in output.get("items", []):
        if row.get("category") == "research":
            if not strict_relevance(row.get("title", ""), row.get("summary", "")):
                raise ValueError(f"irrelevant public research: {row.get('title')}")
            if not plausible_date(row.get("published_at", "")):
                raise ValueError(f"invalid public research date: {row.get('published_at')}")
    if knowledge.get("count") != len(knowledge.get("items", [])):
        raise ValueError("knowledge count mismatch")


def run(since_days: int, skip_network: bool = False) -> dict[str, Any]:
    config = load_json(CONFIG_PATH, {})
    settings = config.get("settings", {})
    max_public = int(settings.get("max_public_items", 250))
    max_review = int(settings.get("max_review_items", 500))
    old_output = load_json(OUTPUT_PATH, {})
    old_review = load_json(REVIEW_PATH, {})
    old_state = load_json(STATE_PATH, {"version": "2.0.0", "official_monitors": {}})

    existing_public = [x for row in old_output.get("items", []) if (x := row_to_item(row, config))]
    existing_review = [x for row in old_review.get("items", []) if (x := row_to_item(row, config))]
    incoming = curated_items(config)
    failures: list[dict[str, str]] = []
    monitor_state = old_state.get("official_monitors", {})

    if not skip_network:
        collectors = (("pubmed", collect_pubmed), ("europe_pmc", collect_europe_pmc), ("crossref", collect_crossref))
        for name, collector in collectors:
            if not config.get(name, {}).get("enabled", True):
                continue
            try:
                found = collector(config.get(name, {}), settings, since_days)
                incoming.extend(found)
                print(f"[OK] {name}: {len(found)}")
            except Exception as exc:
                failures.append({"source": name, "error": str(exc)[:300]})
                print(f"[WARN] {name}: {exc}", file=sys.stderr)
        monitor_items, monitor_state, monitor_failures = collect_official_monitors(config.get("official_monitors", []), monitor_state, config)
        incoming.extend(monitor_items)
        failures.extend(monitor_failures)

    new_public = [x for x in incoming if x.auto_publish]
    new_review = [x for x in incoming if not x.auto_publish]
    public_items = merge_items(existing_public, new_public, max_public)
    review_items = merge_items(existing_review, new_review, max_review)
    # A public item must not remain in the review queue.
    public_keys = {item_key(x) for x in public_items}
    review_items = [x for x in review_items if item_key(x) not in public_keys]

    digest = semantic_digest(public_items, review_items, failures, monitor_state)
    old_digest = clean_text(old_state.get("semantic_digest"))
    generated_at = clean_text(old_output.get("generated_at")) if digest == old_digest else iso_now()
    generated_at = generated_at or iso_now()

    status_name = "healthy" if not failures else "partial"
    output = {
        "version": "2.0.0", "generated_at": generated_at, "status": status_name,
        "sources": {"pubmed": config.get("pubmed", {}).get("enabled", True), "europe_pmc": config.get("europe_pmc", {}).get("enabled", True),
                    "crossref": config.get("crossref", {}).get("enabled", True), "official_monitors": len(config.get("official_monitors", [])), "curated": len(curated_items(config))},
        "counts": {"collected_this_run": len(incoming), "auto_published": len(public_items), "review_queue": len(review_items)},
        "items": [asdict(x) for x in public_items], "failures": failures,
        "disclaimer": "자동 수집·분류 결과입니다. 규제 해석, 제품 효능, 최적 급여량은 공식 원문과 시험조건을 확인한 뒤 확정해야 합니다.",
    }
    review_payload = {"version": "2.0.0", "generated_at": generated_at, "count": len(review_items), "items": [asdict(x) for x in review_items]}
    knowledge = knowledge_payload(public_items, generated_at)
    status = {"version": "2.0.0", "updated_at": generated_at, "status": status_name, "semantic_digest": digest,
              "counts": output["counts"], "failures": failures, "next_schedule": "daily 03:20 Asia/Seoul"}
    state = {"version": "2.0.0", "semantic_digest": digest, "official_monitors": monitor_state}

    save_if_changed(OUTPUT_PATH, output)
    save_if_changed(REVIEW_PATH, review_payload)
    save_if_changed(KNOWLEDGE_PATH, knowledge)
    save_if_changed(STATUS_PATH, status)
    save_if_changed(STATE_PATH, state)

    index = load_json(INDEX_PATH, {})
    if isinstance(index, dict):
        index["auto_intelligence"] = {"version": "2.0.0", "generated_at": generated_at, "count": len(public_items), "items": [asdict(x) for x in public_items]}
        index["auto_intelligence_updated_at"] = generated_at
        save_if_changed(INDEX_PATH, index)
    validate_outputs()
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--since-days", type=int, default=None)
    parser.add_argument("--skip-network", action="store_true")
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    if args.validate_only:
        validate_outputs()
        print("validated auto-intelligence outputs")
        return 0
    config = load_json(CONFIG_PATH, {})
    default_days = int(config.get("settings", {}).get("default_lookback_days", 30))
    result = run(max(1, min(args.since_days or default_days, 365)), args.skip_network)
    print(json.dumps(result["counts"], ensure_ascii=False))
    # Curated baseline keeps the public dashboard usable even if all networks fail.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
