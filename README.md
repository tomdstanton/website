# Bytes & Bacteria

[![Deploy Blog](https://github.com/tomdstanton/website/actions/workflows/deploy.yml/badge.svg)](https://github.com/tomdstanton/website/actions/workflows/deploy.yml)

Personal website, blog, and software portfolio for **Tom Stanton** ([tomdstanton.com](https://tomdstanton.com)), built with [Zensical](https://zensical.org/).

## Local Development

```bash
# Install dependencies & git hooks
uv sync
uv run prek install

# Refresh OpenAlex publications
uv run python scripts/fetch_bib.py

# Serve locally with live reload
uv run zensical serve

# Run all pre-commit checks (builtin hygiene + strict Zensical build)
uv run prek run --all-files
```

## Adding Content

### 1. New Blog Post
Blog posts inside `docs/posts/` are discovered automatically by Zensical's `blog` plugin — no config edits needed!

```bash
# Create a single-file post (docs/posts/<slug>.md)
clio scripts/new.py post "Vectorized Bioinformatics with Polars" --tags Polars Python Bioinformatics

# Or create a folder bundle for co-located images (docs/posts/<slug>/index.md)
clio scripts/new.py post "Deep Dive into Kaptive 3" --bundle --tags Kaptive Genomics
```

### 2. New Software Project
Project pages live in `docs/projects/*.md`. The top 3 projects (lowest `weight` in front matter) are automatically featured on the Home page, and all projects appear on the **Software** tab with live GitHub star counts.

```bash
clio scripts/new.py project "Kaptive Plot" \
  --repo tomdstanton/kaptive-plot \
  --lang Python \
  --weight 7 \
  --tags Kaptive Plotting Python
```

### 3. New Top-Level Navigation Tab
Navigation is managed via `docs/.nav.yml` (powered by `awesome-nav`).

```bash
clio scripts/new.py tab "Talks" --icon lucide/presentation
```
