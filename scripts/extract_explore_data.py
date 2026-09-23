#!/usr/bin/env python3
"""Populate the Explore Food demo dataset inside the website repository.

Reads the private-reference recipe compendiums from the Perceptiosphere vault
and writes into this repo:

  src/data/explore/*.json        build-time data for static recipe pages
  public/explore-data/*.json     client-fetch data for the directory
  public/explore-images/<slug>/  exact source-mapped recipe photographs

Private reference only: do not commit or deploy until rights are cleared.
"""

from __future__ import annotations

import json
import re
import shutil
import unicodedata
from pathlib import Path

from PIL import Image, ImageOps

VAULT = Path("/home/findcongwang/work/FCWANG/Perceptiosphere")
SOURCES = VAULT / "02_Sandbox" / "Sources" / "T2_Authoritative"
SITE = Path(__file__).resolve().parents[1]

FULL_BOOKS = [
    ("Tao of Nutrition", "Mao Shing Ni and Cathy McNease", "2012"),
    ("The Five Elements Cookbook", "Zoey Xinyi Gong", "2021"),
    ("The Food Lab", "J. Kenji Lopez-Alt", "2015"),
    ("The Wisdom of the Chinese Kitchen", "Grace Young with Alan Richardson", "1999"),
    ("Vegetable Kingdom", "Bryant Terry", "2020"),
    ("The How Not to Age Cookbook", "Michael Greger", "2023"),
    ("The How Not to Die Cookbook", "Michael Greger", "2017"),
    ("The How Not to Diet Cookbook", "Michael Greger", "2019"),
    ("The Blue Zones Kitchen One Pot Meals", "Dan Buettner", "2024"),
]

INDEX_BOOKS = [
    ("A Plant-Based Revolution Cookbook", "Michele Wallace", ""),
    ("A Spoonful of Ginger", "Nina Simonds", "1999"),
    ("Forks Over Knives \u2014 The Cookbook", "Del Sroufe and others", "2012"),
    ("Mediterranean Diet Cookbook for Beginners", "Enzo Reds", "2021"),
    ("Plenty More", "Yotam Ottolenghi", "2014"),
    ("Salt Fat Acid Heat", "Samin Nosrat", "2017"),
]

IMG = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
SLUG_RE = re.compile(r"[^a-z0-9]+")

# A source illustration smaller than this is not usable as a meaningful web
# photograph. It remains in the private source package, but is excluded from
# the demo so it is never enlarged into a blurry listing-card or hero image.
MIN_DISPLAY_EDGE = 240
MAX_DISPLAY_IMAGES_PER_RECIPE = 3
MAX_WEB_IMAGE_DIMENSION = 1400
JPEG_QUALITY = 84


def slug(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    return SLUG_RE.sub("-", text.lower()).strip("-")[:80] or "x"


def parse_compendium(book_dir: Path):
    comp = next(book_dir.glob("*Complete Recipe List*.md"))
    text = comp.read_text(encoding="utf-8")
    body = text.split("---", 2)[2]
    recipes = []
    family = ""
    current = None
    for line in body.splitlines():
        if line.startswith("## "):
            if current:
                recipes.append(current)
                current = None
            family = line[3:].strip()
        elif line.startswith("### "):
            if current:
                recipes.append(current)
            current = {"title": line[4:].strip(), "family": family, "lines": [], "images": []}
        elif current is not None:
            m = IMG.search(line)
            if m:
                current["images"].append(m.group(1))
                line = IMG.sub("", line).strip()
                if not line:
                    continue
            current["lines"].append(line)
    if current:
        recipes.append(current)
    return recipes


def first_prose(lines):
    for line in lines:
        s = line.strip()
        if not s or s.startswith(("#", "!", "[[", ">", "|")):
            continue
        if len(s) < 24:
            continue
        return s
    return ""


def write_json(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")


def select_and_copy_display_images(book_dir: Path, rel_paths: list[str], image_root: Path, book_slug: str):
    """Return only display-quality images, ranked cover-first by usable area.

    Source order is not suitable for presentation because several EPUBs place
    tiny category graphics before their dish photograph. The source files stay
    untouched; this generates bounded JPEG derivatives for the private demo.
    """
    candidates = []
    for rel in rel_paths:
        if Path(rel).name.lower() in {"none", "null"}:
            continue
        src = book_dir / rel
        if not src.exists():
            raise FileNotFoundError(f"{book_dir.name}: missing image {rel}")
        with Image.open(src) as image:
            width, height = image.size
        if min(width, height) < MIN_DISPLAY_EDGE:
            continue
        candidates.append((width * height, width, height, src))

    candidates.sort(key=lambda item: item[0], reverse=True)
    selected = candidates[:MAX_DISPLAY_IMAGES_PER_RECIPE]
    urls = []
    for _, _, _, src in selected:
        dst = image_root / book_slug / f"{src.stem}.jpg"
        dst.parent.mkdir(parents=True, exist_ok=True)
        with Image.open(src) as image:
            image = ImageOps.exif_transpose(image)
            if image.mode != "RGB":
                image = image.convert("RGB")
            image.thumbnail((MAX_WEB_IMAGE_DIMENSION, MAX_WEB_IMAGE_DIMENSION), Image.Resampling.LANCZOS)
            image.save(dst, "JPEG", quality=JPEG_QUALITY, optimize=True, progressive=True)
        urls.append(f"/explore-images/{book_slug}/{dst.name}")
    return urls


def main():
    src_data = SITE / "src" / "data" / "explore"
    pub_data = SITE / "public" / "explore-data"
    images = SITE / "public" / "explore-images"
    for d in (src_data, pub_data):
        if d.exists():
            shutil.rmtree(d)
    if images.exists():
        shutil.rmtree(images)
    images.mkdir(parents=True)

    books_out = []
    recipes_out = []

    for name, author, year in FULL_BOOKS:
        book_dir = SOURCES / name
        recipes = parse_compendium(book_dir)
        book_slug = slug(name)
        copied = 0
        for n, r in enumerate(recipes, 1):
            imgs = select_and_copy_display_images(book_dir, r["images"], images, book_slug)
            copied += len(imgs)
            body = "\n".join(r["lines"]).strip()
            recipes_out.append(
                {
                    "id": f"{book_slug}-{n:03d}",
                    "title": r["title"],
                    "book": name,
                    "b": book_slug,
                    "family": r["family"],
                    "author": author,
                    "year": year,
                    "desc": first_prose(r["lines"])[:240],
                    "body": body,
                    "imgs": imgs,
                }
            )
        books_out.append(
            {"slug": book_slug, "title": name, "author": author, "year": year,
             "count": len(recipes), "images": copied, "full": True}
        )
        print(f"{name}: {len(recipes)} recipes, {copied} images")

    for name, author, year in INDEX_BOOKS:
        book_dir = SOURCES / name
        if not book_dir.exists():
            print(f"skip missing {name}")
            continue
        recipes = parse_compendium(book_dir)
        book_slug = slug(name)
        for n, r in enumerate(recipes, 1):
            recipes_out.append(
                {"id": f"{book_slug}-{n:03d}", "title": r["title"], "book": name,
                 "b": book_slug, "family": r["family"], "author": author,
                 "year": year, "desc": "", "io": True}
            )
        books_out.append(
            {"slug": book_slug, "title": name, "author": author, "year": year,
             "count": len(recipes), "full": False}
        )
        print(f"{name}: {len(recipes)} indexed titles")

    china_dir = SOURCES / "China The Cookbook"
    if china_dir.exists():
        entries = []
        for atom in sorted(china_dir.glob("* (Source).md")):
            if atom.name.startswith("China The Cookbook (Source)"):
                continue
            family = atom.stem.replace("China The Cookbook - ", "").replace(" (Source)", "")
            text = atom.read_text(encoding="utf-8")
            in_recipes = False
            for line in text.splitlines():
                if line.startswith("## "):
                    in_recipes = line[3:].strip() == "Recipes"
                elif in_recipes and line.startswith("### "):
                    entries.append((family, line[4:].strip()))
        book_slug = "china-the-cookbook"
        for n, (family, title) in enumerate(entries, 1):
            recipes_out.append(
                {"id": f"{book_slug}-{n:03d}", "title": title, "book": "China The Cookbook",
                 "b": book_slug, "family": family,
                 "author": "Kei Lum Chan and Diora Fong Chan", "year": "2016",
                 "desc": "", "io": True}
            )
        books_out.append(
            {"slug": book_slug, "title": "China The Cookbook",
             "author": "Kei Lum Chan and Diora Fong Chan", "year": "2016",
             "count": len(entries), "full": False, "partial": True}
        )
        print(f"China The Cookbook: {len(entries)} indexed titles")

    ysy = SOURCES / "\u836f\u98df\u540c\u6e90\u7968\u767e\u75c5\u4e2d\u533b\u6c11\u95f4\u836f\u81b3\u98df\u7597\u9632\u6cbb\u75c5\u65b91600\u4f8b"
    if ysy.exists():
        comp = next(ysy.glob("*Complete Recipe List*.md"))
        text = comp.read_text(encoding="utf-8")
        body = text.split("---", 2)[2]
        family = ""
        entries = []
        for line in body.splitlines():
            if line.startswith("## "):
                family = line[3:].strip()
            elif line.startswith("### "):
                entries.append((family, line[4:].strip()))
        book_slug = "yao-shi-tong-yuan-1600"
        for n, (family, title) in enumerate(entries, 1):
            recipes_out.append(
                {"id": f"{book_slug}-{n:03d}", "title": title,
                 "book": "\u836f\u98df\u540c\u6e90\u7968\u767e\u75c5 (1600 food-therapy formulas)",
                 "b": book_slug, "family": family, "author": "\u7531\u80fd\u529b",
                 "year": "", "desc": "", "io": True}
            )
        books_out.append(
            {"slug": book_slug,
             "title": "\u836f\u98df\u540c\u6e90\u7968\u767e\u75c5 (1600 food-therapy formulas)",
             "author": "\u7531\u80fd\u529b", "year": "", "count": len(entries),
             "full": False}
        )
        print(f"yao-shi-tong-yuan: {len(entries)} indexed titles")

    write_json(src_data / "recipes.json", recipes_out)
    write_json(src_data / "books.json", books_out)
    write_json(pub_data / "recipes.json", recipes_out)
    write_json(pub_data / "books.json", books_out)
    print(f"total recipes emitted: {len(recipes_out)}")


if __name__ == "__main__":
    main()
