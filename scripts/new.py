# /// script
# requires-python = ">=3.14"
# dependencies = []
# ///

"""Scaffold a new blog post, software project, or navigation tab with clio.

Examples:
  clio scripts/new.py post "Vectorized Bioinformatics with Polars" --tags Polars Python Bioinformatics
  clio scripts/new.py project "Kaptive Plot" --repo tomdstanton/kaptive-plot --lang Python
  clio scripts/new.py tab "Talks" --icon lucide/presentation
"""

import datetime as dt
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "untitled"


def _split_items(items: list[str] | None, default: list[str]) -> list[str]:
    if not items:
        return default
    parsed = [part.strip() for raw in items for part in raw.split(",") if part.strip()]
    return parsed or default


def post(
    title: str,
    *,
    slug: str | None = None,
    description: str | None = None,
    tags: list[str] | None = None,
    categories: list[str] | None = None,
    bundle: bool = False,
    draft: bool = False,
) -> dict[str, str]:
    """Create a new blog post in docs/posts/."""
    resolved_slug = slug or _slugify(title)
    today = dt.date.today().isoformat()
    resolved_tags = _split_items(tags, ["Bioinformatics"])
    resolved_cats = _split_items(categories, ["Bioinformatics"])

    target = (
        DOCS / "posts" / resolved_slug / "index.md"
        if bundle
        else DOCS / "posts" / f"{resolved_slug}.md"
    )
    if target.exists():
        raise FileExistsError(f"{target.relative_to(ROOT)} already exists.")

    target.parent.mkdir(parents=True, exist_ok=True)
    tags_yaml = "\n".join(f"  - {t}" for t in resolved_tags)
    cats_yaml = "\n".join(f"  - {c}" for c in resolved_cats)
    draft_line = "draft: true\n" if draft else ""

    content = f"""---
{draft_line}date: {today}
slug: {resolved_slug}
title: "{title}"
description: "{description or title}"
categories:
{cats_yaml}
tags:
{tags_yaml}
---

Write your opening summary paragraph here. It will appear as the preview card on the home page.

<!-- more -->

## Introduction

Start writing your post here!
"""
    target.write_text(content, encoding="utf-8")
    rel = str(target.relative_to(ROOT))
    print(f"✔ Created blog post: {rel}")
    return {"path": rel, "slug": resolved_slug}


def project(
    title: str,
    *,
    slug: str | None = None,
    description: str | None = None,
    repo: str | None = None,
    pypi: str | None = None,
    docs_url: str | None = None,
    lang: str = "Python",
    weight: int = 10,
    tags: list[str] | None = None,
) -> dict[str, str]:
    """Create a new software project card and page in docs/projects/."""
    resolved_slug = slug or _slugify(title)
    target = DOCS / "projects" / f"{resolved_slug}.md"
    if target.exists():
        raise FileExistsError(f"{target.relative_to(ROOT)} already exists.")

    resolved_tags = _split_items(tags, ["Bioinformatics", "Python"])
    tags_yaml = "\n".join(f"  - {t}" for t in resolved_tags)
    github_url = (
        f"https://github.com/{repo}"
        if repo and not repo.startswith("http")
        else (repo or "")
    )

    extra_meta: list[str] = []
    if github_url:
        extra_meta.append(f"github_url: {github_url}")
    if pypi:
        extra_meta.append(f"pypi: {pypi}")
    if docs_url:
        extra_meta.append(f"docs_url: {docs_url}")
    if lang:
        extra_meta.append(f"language: {lang}")
    extra_meta_str = "\n".join(extra_meta) + ("\n" if extra_meta else "")

    content = f"""---
title: "{title}"
description: "{description or f'{title} — open-source bioinformatics tool.'}"
{extra_meta_str}weight: {weight}
tags:
{tags_yaml}
---

# {title}

Describe **{title}**, its motivation, and key features here.

[← Back to all Software](index.md)
"""
    target.write_text(content, encoding="utf-8")

    rel = str(target.relative_to(ROOT))
    print(f"✔ Created project page: {rel} (auto-ordered by weight={weight})")
    return {"path": rel, "slug": resolved_slug}


def tab(
    title: str,
    *,
    slug: str | None = None,
    description: str | None = None,
    icon: str | None = None,
) -> dict[str, str]:
    """Create a new top-level navigation tab in docs/."""
    resolved_slug = slug or _slugify(title)
    target = DOCS / f"{resolved_slug}.md"
    if target.exists():
        raise FileExistsError(f"{target.relative_to(ROOT)} already exists.")

    icon_line = f"icon: {icon}\n" if icon else ""
    content = f"""---
title: "{title}"
description: "{description or title}"
{icon_line}---

# {title}

Content for the **{title}** tab goes here.
"""
    target.write_text(content, encoding="utf-8")

    nav_file = DOCS / ".nav.yml"
    if nav_file.exists():
        nav_text = nav_file.read_text(encoding="utf-8")
        entry = f"  - {resolved_slug}.md"
        if entry not in nav_text:
            nav_file.write_text(nav_text.rstrip() + f"\n{entry}\n", encoding="utf-8")

    rel = str(target.relative_to(ROOT))
    print(f"✔ Created new top-level tab: {rel}")
    return {"path": rel, "slug": resolved_slug}


if __name__ == "__main__":
    from clio import Cli

    Cli(prog="new", commands=[post, project, tab]).run()
