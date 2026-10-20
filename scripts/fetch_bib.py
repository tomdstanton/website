# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Fetch publications from OpenAlex and generate docs/bib.md grouped by year."""

from __future__ import annotations

import json
import os
import re
import urllib.request
from collections import defaultdict
from pathlib import Path

AUTHOR_ID = "https://openalex.org/A5025916428"
BIB_PATH = Path("docs/bib.md")


def strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text or "").strip()


def normalize_title(title: str) -> str:
    clean = strip_html(title).lower()
    return re.sub(r"[^a-z0-9]+", "", clean)


def format_vancouver_authors(authorships: list[dict]) -> str:
    """Format OpenAlex authorships into Vancouver style, bolding Tom Stanton."""
    formatted = []
    tom_index = None

    for idx, authorship in enumerate(authorships):
        author = authorship.get("author") or {}
        display_name = author.get("display_name", "")
        author_id = author.get("id", "")
        if not display_name:
            continue

        parts = display_name.split()
        if len(parts) > 1:
            last = parts[-1]
            firsts = parts[:-1]
            initials = "".join([f[0].upper() for f in firsts if f])
            entry = f"{last} {initials}"
        else:
            entry = display_name

        is_tom = (author_id == AUTHOR_ID) or (
            entry.lower().startswith("stanton t")
        )
        if is_tom:
            entry = f"**{entry}**"
            tom_index = idx

        formatted.append(entry)

    if len(formatted) > 8:
        if tom_index is not None and tom_index >= 7:
            return ", ".join(formatted[:6]) + f", …, {formatted[tom_index]}, et al."
        return ", ".join(formatted[:7]) + ", et al."
    return ", ".join(formatted)


def score_work(work: dict) -> tuple[int, int, int]:
    """Score a work to pick the canonical journal version when deduplicating."""
    has_doi = 1 if work.get("doi") else 0
    primary_location = work.get("primary_location") or {}
    source = primary_location.get("source") or {}
    is_journal = 1 if source.get("type") == "journal" else 0
    citations = int(work.get("cited_by_count") or 0)
    return (has_doi, is_journal, citations)


def format_pub_card(work: dict) -> str:
    """Render a publication as a clean Markdown/HTML card."""
    raw_title = (work.get("title") or "").replace("\n", " ").strip()
    authors = format_vancouver_authors(work.get("authorships", []))

    primary_location = work.get("primary_location") or {}
    source = primary_location.get("source") or {}
    journal = source.get("display_name") or ""

    year = work.get("publication_year") or ""
    biblio = work.get("biblio") or {}
    volume = biblio.get("volume") or ""
    issue = biblio.get("issue") or ""
    first_page = biblio.get("first_page") or ""
    last_page = biblio.get("last_page") or ""

    pages = ""
    if first_page:
        pages = str(first_page)
        if last_page and last_page != first_page:
            pages += f"–{last_page}"

    venue_parts = []
    if journal:
        venue_parts.append(f"*{journal}*")
    vol_str = ""
    if volume:
        vol_str += str(volume)
    if issue:
        vol_str += f"({issue})"
    if pages:
        vol_str += f":{pages}" if vol_str else pages
    if vol_str:
        venue_parts.append(vol_str)
    venue_line = " • ".join(venue_parts) if venue_parts else str(year)

    doi_url = work.get("doi") or ""
    oa = work.get("open_access") or {}
    oa_url = oa.get("oa_url") or ""
    citations = int(work.get("cited_by_count") or 0)

    badges = []
    if doi_url:
        doi_short = doi_url.replace("https://doi.org/", "")
        badges.append(
            f'<a href="{doi_url}" class="pub-badge pub-badge--doi" target="_blank" rel="noopener">DOI: {doi_short}</a>'
        )
    if oa_url and oa_url != doi_url:
        badges.append(
            f'<a href="{oa_url}" class="pub-badge pub-badge--oa" target="_blank" rel="noopener">Open Access</a>'
        )
    if citations > 0:
        label = "citation" if citations == 1 else "citations"
        badges.append(
            f'<span class="pub-badge pub-badge--cite">{citations} {label}</span>'
        )

    badges_html = " ".join(badges)
    title_html = (
        f'<a href="{doi_url}" target="_blank" rel="noopener">{raw_title}</a>'
        if doi_url
        else raw_title
    )

    return (
        f'<div class="pub-card" markdown>\n'
        f'<div class="pub-title">{title_html}</div>\n\n'
        f'<div class="pub-authors" markdown>{authors}</div>\n\n'
        f'<div class="pub-footer" markdown>\n'
        f'<span class="pub-venue">{venue_line}</span>\n'
        f'<span class="pub-badges">{badges_html}</span>\n'
        f"</div>\n"
        f"</div>\n"
    )


def main() -> None:
    url = (
        f"https://api.openalex.org/works?filter=author.id:{AUTHOR_ID},"
        "type:article|proceedings-article&per-page=100"
    )
    if api_key := os.environ.get("OPENALEX_API_KEY"):
        url += f"&api_key={api_key}"

    req = urllib.request.Request(url, headers={"User-Agent": "Zensical-Bib-Fetcher/2.0"})

    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            data = json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        print(f"Warning: Failed to fetch data from OpenAlex ({exc}). Keeping existing {BIB_PATH}.")
        return

    raw_works = data.get("results", [])
    if not raw_works:
        print(f"Warning: OpenAlex returned 0 works. Keeping existing {BIB_PATH}.")
        return

    # Deduplicate by normalized title, keeping the highest-scored record
    deduped: dict[str, dict] = {}
    for work in raw_works:
        title = work.get("title")
        if not title:
            continue
        key = normalize_title(title)
        if not key:
            continue
        if key not in deduped or score_work(work) > score_work(deduped[key]):
            deduped[key] = work

    # Sort newest first by publication_date / publication_year
    sorted_works = sorted(
        deduped.values(),
        key=lambda w: (
            int(w.get("publication_year") or 0),
            w.get("publication_date") or "",
            int(w.get("cited_by_count") or 0),
        ),
        reverse=True,
    )

    by_year: dict[int | str, list[dict]] = defaultdict(list)
    for work in sorted_works:
        year = work.get("publication_year") or "Other"
        by_year[year].append(work)

    total_pubs = len(sorted_works)
    total_citations = sum(int(w.get("cited_by_count") or 0) for w in sorted_works)

    lines = [
        "---",
        "title: Publications",
        "description: Peer-reviewed publications and preprints by Tom Stanton, automatically synced from OpenAlex.",
        "author: Tom Stanton",
        "comments: false",
        "icon: lucide/book-open-text",
        "---",
        "",
        "# Publications 📚",
        "",
        f"Peer-reviewed articles and preprints automatically synced from [OpenAlex]({AUTHOR_ID}) (**{total_pubs}** publications • **{total_citations:,}** total citations).",
        "",
    ]

    for year in by_year:
        lines.append(f"## {year}")
        lines.append("")
        for work in by_year[year]:
            lines.append(format_pub_card(work))

    BIB_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {total_pubs} deduplicated publications across {len(by_year)} years to {BIB_PATH}")


if __name__ == "__main__":
    main()
