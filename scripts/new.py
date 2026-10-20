# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""CLI scaffolder for adding new blog posts, software projects, or tabs.

Examples:
  uv run scripts/new.py post "Vectorized Bioinformatics with Polars" --tags Polars,Python,Bioinformatics
  uv run scripts/new.py project "Kaptive Plot" --repo tomdstanton/kaptive-plot --lang Python
  uv run scripts/new.py tab "Talks" --icon lucide/presentation
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "untitled"


def create_post(args: argparse.Namespace) -> None:
    slug = args.slug or slugify(args.title)
    today = dt.date.today().isoformat()
    tags = [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else ["Bioinformatics"]
    categories = [c.strip() for c in args.categories.split(",") if c.strip()] if args.categories else ["Bioinformatics"]

    if args.bundle:
        target = DOCS / "posts" / slug / "index.md"
    else:
        target = DOCS / "posts" / f"{slug}.md"

    if target.exists():
        sys.exit(f"Error: {target.relative_to(ROOT)} already exists.")

    target.parent.mkdir(parents=True, exist_ok=True)
    tags_yaml = "\n".join(f"  - {t}" for t in tags)
    cats_yaml = "\n".join(f"  - {c}" for c in categories)
    draft_line = "draft: true\n" if args.draft else ""

    content = f"""---
{draft_line}date: {today}
slug: {slug}
title: "{args.title}"
description: "{args.description or args.title}"
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
    print(f"✔ Created blog post: {target.relative_to(ROOT)}")
    print("  No config changes needed — Zensical's blog plugin discovers it automatically!")


def create_project(args: argparse.Namespace) -> None:
    slug = args.slug or slugify(args.title)
    target = DOCS / "projects" / f"{slug}.md"
    if target.exists():
        sys.exit(f"Error: {target.relative_to(ROOT)} already exists.")

    tags = [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else ["Bioinformatics", "Python"]
    tags_yaml = "\n".join(f"  - {t}" for t in tags)
    github_url = f"https://github.com/{args.repo}" if args.repo and not args.repo.startswith("http") else (args.repo or "")

    extra_meta = []
    if github_url:
        extra_meta.append(f"github_url: {github_url}")
    if args.pypi:
        extra_meta.append(f"pypi: {args.pypi}")
    if args.docs_url:
        extra_meta.append(f"docs_url: {args.docs_url}")
    if args.lang:
        extra_meta.append(f"language: {args.lang}")
    extra_meta_str = "\n".join(extra_meta) + ("\n" if extra_meta else "")

    content = f"""---
title: "{args.title}"
description: "{args.description or f'{args.title} — open-source bioinformatics tool.'}"
{extra_meta_str}weight: {args.weight}
tags:
{tags_yaml}
---

# {args.title}

Describe **{args.title}**, its motivation, and key features here.
"""
    target.write_text(content, encoding="utf-8")

    nav_file = DOCS / "projects" / ".nav.yml"
    if nav_file.exists():
        nav_text = nav_file.read_text(encoding="utf-8")
        entry = f"  - {slug}.md"
        if entry not in nav_text:
            nav_file.write_text(nav_text.rstrip() + f"\n{entry}\n", encoding="utf-8")

    print(f"✔ Created project page: {target.relative_to(ROOT)}")
    print(f"✔ Registered in {(DOCS / 'projects' / '.nav.yml').relative_to(ROOT)}")


def create_tab(args: argparse.Namespace) -> None:
    slug = args.slug or slugify(args.title)
    target = DOCS / f"{slug}.md"
    if target.exists():
        sys.exit(f"Error: {target.relative_to(ROOT)} already exists.")

    icon_line = f"icon: {args.icon}\n" if args.icon else ""
    content = f"""---
title: "{args.title}"
description: "{args.description or args.title}"
{icon_line}---

# {args.title}

Content for the **{args.title}** tab goes here.
"""
    target.write_text(content, encoding="utf-8")

    nav_file = DOCS / ".nav.yml"
    if nav_file.exists():
        nav_text = nav_file.read_text(encoding="utf-8")
        entry = f"  - {slug}.md"
        if entry not in nav_text:
            nav_file.write_text(nav_text.rstrip() + f"\n{entry}\n", encoding="utf-8")

    print(f"✔ Created new top-level tab: {target.relative_to(ROOT)}")
    print(f"✔ Added '{slug}.md' to {(DOCS / '.nav.yml').relative_to(ROOT)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Scaffold a new blog post, software project, or navigation tab.")
    sub = parser.add_subparsers(dest="kind", required=True)

    p_post = sub.add_parser("post", help="Create a new blog post in docs/posts/")
    p_post.add_argument("title", help="Post title")
    p_post.add_argument("--slug", help="Custom URL slug")
    p_post.add_argument("--description", help="Short summary for cards and SEO")
    p_post.add_argument("--tags", help="Comma-separated tags (e.g. Python,Rust,Genomics)")
    p_post.add_argument("--categories", help="Comma-separated categories (e.g. Bioinformatics,Tutorials)")
    p_post.add_argument("--bundle", action="store_true", help="Create as docs/posts/<slug>/index.md folder for co-located images")
    p_post.add_argument("--draft", action="store_true", help="Mark post as draft: true")
    p_post.set_defaults(func=create_post)

    p_proj = sub.add_parser("project", help="Create a new software project card & page in docs/projects/")
    p_proj.add_argument("title", help="Project title")
    p_proj.add_argument("--slug", help="Custom filename/URL slug")
    p_proj.add_argument("--description", help="Short summary for the project card")
    p_proj.add_argument("--repo", help="GitHub repository (e.g. tomdstanton/my-tool)")
    p_proj.add_argument("--pypi", help="PyPI package name")
    p_proj.add_argument("--docs-url", help="Documentation URL")
    p_proj.add_argument("--lang", default="Python", help="Primary language badge (e.g. Python, Rust / Python)")
    p_proj.add_argument("--weight", type=int, default=10, help="Sort weight (lower appears earlier; top 3 appear on Home)")
    p_proj.add_argument("--tags", help="Comma-separated tags")
    p_proj.set_defaults(func=create_project)

    p_tab = sub.add_parser("tab", help="Create a new top-level navigation tab in docs/")
    p_tab.add_argument("title", help="Tab title")
    p_tab.add_argument("--slug", help="Custom filename/URL slug")
    p_tab.add_argument("--description", help="Page description")
    p_tab.add_argument("--icon", help="Lucide/FontAwesome icon (e.g. lucide/presentation)")
    p_tab.set_defaults(func=create_tab)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
