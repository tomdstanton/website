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
Blog posts inside `docs/posts/` are discovered automatically by Zensical's `blog` plugin — no config edits needed! Posts support:
- **GitHub/Obsidian callouts:** `> [!NOTE]`, `> [!IMPORTANT]`, `> [!WARNING]`
- **Direct CSV/TSV tables:** `{{ read_csv('path/to/benchmarks.csv') }}`
- **Instant hover previews:** Internal links between posts and software pages render hover preview cards automatically.

```bash
# Create a single-file post (docs/posts/<slug>.md)
clio scripts/new.py post "Vectorized Bioinformatics with Polars" --tags Polars Python Bioinformatics

# Or create a folder bundle for co-located images/CSVs (docs/posts/<slug>/index.md)
clio scripts/new.py post "Deep Dive into Kaptive 3" --bundle --tags Kaptive Genomics
```

### 2. New Software Project
Project pages live in `docs/projects/*.md` and sort automatically by `weight` via `mkdocs-nav-weight` (no `.nav.yml` maintenance needed). The top 3 projects (lowest `weight`) are featured on the Home page, and all projects appear on the **Software** tab with live GitHub star counts.

```bash
clio scripts/new.py project "Kaptive Plot" \
  --repo tomdstanton/kaptive-plot \
  --lang Python \
  --weight 7 \
  --tags Kaptive Plotting Python
```

### 3. New Top-Level Navigation Tab
Top-level navigation is managed via `docs/.nav.yml` (`awesome-nav`).

```bash
clio scripts/new.py tab "Talks" --icon lucide/presentation
```

## Generated Outputs & Scholarly Archiving (Rogue Scholar DOIs)
- **Full-Text Syndication Feeds:** `/feed_json_created.json` (JSON Feed 1.1) and `/feed_rss_created.xml` (RSS 2.0) include full-text HTML (`abstract_chars_count = -1`) and `CC BY 4.0` licensing for automatic DOI minting via **[Rogue Scholar](https://rogue-scholar.org/)**.
- **One-Time Rogue Scholar Activation:**
  1. Sign in at [rogue-scholar.org](https://rogue-scholar.org/) with your ORCID (`0000-0002-8898-4432`).
  2. Submit your blog feed URL: `https://tomdstanton.com/feed_json_created.json` (or `https://tomdstanton.com/feed_rss_created.xml`).
  3. Every new post pushed to `main` automatically receives a Crossref DOI — resolved live on the site via `javascripts/rogue-scholar.js` and stamped into static builds via `scripts/sync_dois.py` (or override manually with `doi: ...` in front matter).
- **AI / LLM Discovery:** `/llms.txt` and `/llms-full.txt`
- **Self-Hosted Assets:** Fonts and external assets are cached & self-hosted under `assets/external/` at build time (`privacy` + `optimize` + `minify`).
