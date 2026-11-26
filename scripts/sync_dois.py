# /// script
# requires-python = ">=3.14"
# dependencies = []
# ///

"""Sync minted Rogue Scholar (InvenioRDM) DOIs into docs/posts/ YAML front matter."""

import json
import re
import tomllib
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
POSTS_DIR = DOCS / "posts"

CONFIG = tomllib.loads((ROOT / "zensical.toml").read_text(encoding="utf-8"))["project"]
SITE_URL = CONFIG["site_url"].rstrip("/")
POST_URL_FORMAT = (
    CONFIG.get("plugins", {}).get("blog", {}).get("post_url_format", "blog/{slug}")
)


def _normalize_url(url: str) -> str:
    return re.sub(r"^https?://", "", (url or "").strip()).rstrip("/").lower()


def _clean_doi(doi: str) -> str:
    return re.sub(
        r"^https?://(dx\.)?doi\.org/", "", (doi or "").strip(), flags=re.IGNORECASE
    )


def _extract_record_urls(rec: dict) -> list[str]:
    urls: list[str] = []
    meta = rec.get("metadata") or {}
    for item in meta.get("identifiers") or []:
        ident = item.get("identifier") or ""
        if item.get("scheme") == "url" or ident.startswith(("http://", "https://")):
            urls.append(ident)
    for item in meta.get("related_identifiers") or []:
        ident = item.get("identifier") or ""
        if item.get("scheme") == "url" or ident.startswith(("http://", "https://")):
            urls.append(ident)
    return urls


def _post_canonical_url(path: Path, frontmatter: str) -> str:
    m_slug = re.search(
        r"^slug:\s*['\"]?([^'\"\n]+)['\"]?\s*$", frontmatter, re.MULTILINE
    )
    slug = (
        m_slug.group(1).strip()
        if m_slug
        else (path.parent.name if path.stem == "index" else path.stem)
    )
    rel_url = POST_URL_FORMAT.format(slug=slug).strip("/")
    return f"{SITE_URL}/{rel_url}"


def sync() -> dict[str, int]:
    """Fetch Rogue Scholar records for tomdstanton.com and stamp missing `doi:` keys."""
    api_url = "https://rogue-scholar.org/api/records?q=tomdstanton.com&size=100"
    req = urllib.request.Request(
        api_url,
        headers={
            "Accept": "application/json",
            "User-Agent": "BytesAndBacteria-DOISync/1.0",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as exc:
        print(f"Note: Rogue Scholar API unreachable ({exc}); skipping DOI sync.")
        return {"matched": 0, "updated": 0}

    hits_wrapper = data.get("hits") or {}
    records = (
        hits_wrapper.get("hits", [])
        if isinstance(hits_wrapper, dict)
        else (hits_wrapper if isinstance(hits_wrapper, list) else [])
    )

    doi_by_url: dict[str, str] = {}
    for rec in records:
        if not isinstance(rec, dict):
            continue
        doi = _clean_doi(((rec.get("pids") or {}).get("doi") or {}).get("identifier") or "")
        if not doi:
            continue
        for raw_url in _extract_record_urls(rec):
            url_key = _normalize_url(raw_url)
            if "tomdstanton.com/" in url_key:
                doi_by_url[url_key] = doi

    if not doi_by_url:
        print("Rogue Scholar returned 0 indexed posts for tomdstanton.com so far.")
        return {"matched": 0, "updated": 0}

    updated = 0
    for md_path in sorted(POSTS_DIR.rglob("*.md")):
        text = md_path.read_text(encoding="utf-8")
        m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
        if not m:
            continue
        fm = m.group(1)
        if re.search(r"^doi\s*:", fm, re.MULTILINE):
            continue
        canonical = _normalize_url(_post_canonical_url(md_path, fm))
        doi = doi_by_url.get(canonical)
        if not doi:
            continue
        new_fm = f"{fm}\ndoi: {doi}"
        new_text = f"---\n{new_fm}\n---\n{text[m.end():]}"
        md_path.write_text(new_text, encoding="utf-8")
        updated += 1
        print(f"✔ Stamped doi: {doi} -> {md_path.relative_to(ROOT)}")

    return {"matched": len(doi_by_url), "updated": updated}


if __name__ == "__main__":
    sync()
