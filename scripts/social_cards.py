# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pillow>=11.0.0",
#     "pyyaml>=6.0.0",
# ]
# ///

"""Generate 1200x630 Open Graph social preview cards for every page in docs/.

Runs before `zensical build`. Each card renders the Bytes and Bacteria logo,
page title, and description in the site's dark-slate + bio-cyan theme, saving
to `docs/assets/social/<page_url>.png` (which `overrides/main.html` links in `og:image`).
"""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

import yaml
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
OUT = DOCS / "assets" / "social"

WIDTH, HEIGHT = 1200, 630
BG_DARK = (15, 23, 42)        # #0f172a
BG_CARD = (30, 41, 59)        # #1e293b
BORDER_CYAN = (14, 165, 233)  # #0ea5e9
TEXT_PALE = (224, 242, 254)   # #e0f2fe
TEXT_MUTED = (148, 163, 184)  # #94a3b8
ACCENT_CYAN = (56, 189, 248)  # #38bdf8

LOGO_SIZE = 280
TEXT_X = 430
TEXT_WIDTH = WIDTH - TEXT_X - 80

CONFIG = tomllib.loads((ROOT / "zensical.toml").read_text(encoding="utf-8"))["project"]
SITE_NAME = CONFIG["site_name"]
POST_URL_FORMAT = (
    CONFIG.get("plugins", {}).get("blog", {}).get("post_url_format", "blog/{slug}")
)

FONT_CANDIDATES_BOLD = [
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
]
FONT_CANDIDATES_REGULAR = [
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
]
FONT_CANDIDATES_MONO = [
    "/System/Library/Fonts/Menlo.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
]


def load_font(candidates: list[str], size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in candidates:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default(size=size)


def strip_emojis_and_shortcodes(text: str) -> str:
    text = re.sub(r":[a-z0-9_-]+:", "", text)
    # Strip supplemental emoji codepoints that basic system TTFs may not render
    text = re.sub(r"[\U00010000-\U0010ffff]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def front_matter(path: Path) -> tuple[dict, str | None]:
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    meta = yaml.safe_load(m.group(1)) if m else {}
    body = text[m.end() if m else 0 :]
    h1 = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
    return (meta or {}), (h1.group(1).strip() if h1 else None)


def page_url(path: Path, meta: dict) -> str:
    rel = path.relative_to(DOCS)
    if rel.parts[0] == "posts":
        slug = meta.get("slug") or (
            rel.parent.name if rel.stem == "index" else rel.stem
        )
        return POST_URL_FORMAT.format(slug=slug).strip("/") + "/"
    parts = list(rel.with_suffix("").parts)
    if parts and parts[-1] == "index":
        parts = parts[:-1]
    return "/".join(parts) + "/" if parts else ""


def wrap(
    draw: ImageDraw.ImageDraw,
    text: str,
    candidates: list[str],
    size: int,
    min_size: int,
    max_lines: int,
) -> tuple[ImageFont.FreeTypeFont | ImageFont.ImageFont, list[str]]:
    while True:
        f = load_font(candidates, size)
        lines: list[str] = []
        for word in text.split():
            if lines and draw.textlength(f"{lines[-1]} {word}", font=f) <= TEXT_WIDTH:
                lines[-1] += f" {word}"
            else:
                lines.append(word)
        if len(lines) <= max_lines or size <= min_size:
            if len(lines) > max_lines:
                lines = lines[:max_lines]
                lines[-1] = lines[-1].rstrip(" .,;:") + "…"
            return f, lines
        size -= 4


def prepare_tinted_logo(logo_path: Path, size: int) -> Image.Image:
    """Tint the black-on-transparent bacterium logo into glowing bio-cyan."""
    raw = Image.open(logo_path).convert("RGBA").resize((size, size), Image.LANCZOS)
    _, _, _, alpha = raw.split()
    tinted = Image.new("RGBA", (size, size), (*ACCENT_CYAN, 255))
    tinted.putalpha(alpha)
    return tinted


def render(title: str, description: str, logo: Image.Image) -> Image.Image:
    card = Image.new("RGB", (WIDTH, HEIGHT), BG_DARK)
    draw = ImageDraw.Draw(card)

    # Outer glass card frame
    draw.rounded_rectangle(
        (36, 36, WIDTH - 36, HEIGHT - 36),
        radius=28,
        fill=BG_CARD,
        outline=BORDER_CYAN,
        width=2,
    )
    # Left accent bar
    draw.rounded_rectangle(
        (36, 120, 44, HEIGHT - 120),
        radius=4,
        fill=ACCENT_CYAN,
    )

    # Paste tinted logo on the left
    logo_x = 95
    logo_y = (HEIGHT - LOGO_SIZE) // 2
    card.paste(logo, (logo_x, logo_y), logo)

    clean_title = strip_emojis_and_shortcodes(title) or SITE_NAME
    clean_desc = strip_emojis_and_shortcodes(description)

    site_font = load_font(FONT_CANDIDATES_MONO, 26)
    title_font, title_lines = wrap(draw, clean_title, FONT_CANDIDATES_BOLD, 56, 38, 3)
    desc_font, desc_lines = wrap(draw, clean_desc, FONT_CANDIDATES_REGULAR, 30, 24, 4)

    title_step = int(getattr(title_font, "size", 48) * 1.2)
    desc_step = int(getattr(desc_font, "size", 28) * 1.4)
    block_height = (
        30 + 28 + title_step * len(title_lines) + 24 + desc_step * len(desc_lines)
    )
    y = (HEIGHT - block_height) // 2

    draw.text((TEXT_X, y), f"~/tomdstanton • {SITE_NAME}", font=site_font, fill=ACCENT_CYAN)
    y += 30 + 28
    for line in title_lines:
        draw.text((TEXT_X, y), line, font=title_font, fill=TEXT_PALE)
        y += title_step
    y += 24
    for line in desc_lines:
        draw.text((TEXT_X, y), line, font=desc_font, fill=TEXT_MUTED)
        y += desc_step

    return card


def main() -> None:
    logo_path = DOCS / "assets" / "logo.png"
    logo = prepare_tinted_logo(logo_path, LOGO_SIZE)
    count = 0
    for path in sorted(DOCS.rglob("*.md")):
        meta, h1 = front_matter(path)
        if meta.get("draft") or not meta.get("description"):
            continue
        url = page_url(path, meta)
        out = OUT / f"{url.strip('/') or 'index'}.png"
        out.parent.mkdir(parents=True, exist_ok=True)
        title = meta.get("title") or h1 or SITE_NAME
        if url == "":
            title = SITE_NAME
        render(str(title), str(meta["description"]), logo).save(out, optimize=True)
        count += 1
    print(f"Generated {count} Open Graph social cards in {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
