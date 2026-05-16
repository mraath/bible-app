#!/usr/bin/env python3
"""
Generate a two-column scripture annotation image.
Left column: scripture text with verse numbers.
Right column: blank lined space for handwritten or digital notes.

Usage:
  python3 gen_annotation_page.py MAT 1 1 17 mraath
  python3 gen_annotation_page.py PSA 1 1 6 mraath
"""

import json
import sys
import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BIBLE_ROOT  = Path(__file__).parent.parent / "src/data/bibles/WEB"
OUTPUT_ROOT = Path(__file__).parent.parent / "users"

FONT_REGULAR = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
FONT_BOLD    = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

# Colours
BG          = "#FAFAF8"
TEXT        = "#0D0D0D"
VERSE_NUM   = "#888880"
DIVIDER     = "#D8D8D4"
LINE_COLOUR = "#E0E0DC"
HEADER_BG   = "#1A1A2E"
HEADER_TEXT = "#FAFAF8"
ACCENT      = "#E8851F"

# Page dimensions (portrait, ~letter size at 150 dpi)
W, H   = 1600, 2200
MARGIN = 60
HEADER_H = 90

COL_GAP    = 40
LEFT_W     = 640
RIGHT_W    = W - MARGIN*2 - LEFT_W - COL_GAP   # remaining

FONT_TITLE  = 30
FONT_BODY   = 21
FONT_VNUM   = 17
FONT_LABEL  = 16
LINE_H      = 36   # annotation line spacing


def load_verses(book_code: str, chapter: int, v_start: int, v_end: int):
    path = BIBLE_ROOT / book_code / f"{chapter}.json"
    if not path.exists():
        raise FileNotFoundError(f"No data for {book_code} {chapter} at {path}")
    with open(path) as f:
        data = json.load(f)
    return [v for v in data["verses"] if v_start <= int(v["verse"]) <= v_end]


def wrap_verse(text: str, font, draw, max_width: int):
    words = text.split()
    lines, current = [], []
    for word in words:
        test = " ".join(current + [word])
        if draw.textlength(test, font=font) <= max_width:
            current.append(word)
        else:
            if current:
                lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))
    return lines


def generate(book_code: str, chapter: int, v_start: int, v_end: int, username: str):
    verses = load_verses(book_code, chapter, v_start, v_end)

    img  = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    f_title = ImageFont.truetype(FONT_BOLD,    FONT_TITLE)
    f_body  = ImageFont.truetype(FONT_REGULAR, FONT_BODY)
    f_vnum  = ImageFont.truetype(FONT_BOLD,    FONT_VNUM)
    f_label = ImageFont.truetype(FONT_BOLD,    FONT_LABEL)

    # ── Header bar ──────────────────────────────────────────────
    draw.rectangle([0, 0, W, HEADER_H], fill=HEADER_BG)
    ref = f"{book_code.capitalize()} {chapter}:{v_start}–{v_end}"
    draw.text((MARGIN, HEADER_H // 2), ref, font=f_title, fill=HEADER_TEXT, anchor="lm")
    version_label = "WEB · World English Bible"
    draw.text((W - MARGIN, HEADER_H // 2), version_label, font=f_label, fill=ACCENT, anchor="rm")

    # ── Column labels ────────────────────────────────────────────
    label_y = HEADER_H + 24
    left_x  = MARGIN
    right_x = MARGIN + LEFT_W + COL_GAP

    draw.text((left_x, label_y), "SCRIPTURE", font=f_label, fill=VERSE_NUM)
    draw.text((right_x, label_y), "NOTES", font=f_label, fill=VERSE_NUM)

    # Thin rule under labels
    rule_y = label_y + 22
    draw.line([(left_x, rule_y), (left_x + LEFT_W, rule_y)], fill=DIVIDER, width=1)
    draw.line([(right_x, rule_y), (right_x + RIGHT_W, rule_y)], fill=DIVIDER, width=1)

    # ── Vertical divider ─────────────────────────────────────────
    div_x = MARGIN + LEFT_W + COL_GAP // 2
    draw.line([(div_x, HEADER_H + 10), (div_x, H - MARGIN)], fill=DIVIDER, width=1)

    # ── Scripture (left column) ───────────────────────────────────
    y = rule_y + 18
    vnum_w = 36   # reserved width for verse number

    for v in verses:
        vnum  = str(v["verse"])
        vtext = v["text"].strip()

        # Verse number
        draw.text((left_x, y), vnum, font=f_vnum, fill=VERSE_NUM)

        # Verse text wrapped
        text_x = left_x + vnum_w
        avail_w = LEFT_W - vnum_w
        lines = wrap_verse(vtext, f_body, draw, avail_w)
        for line in lines:
            if y > H - MARGIN:
                break
            draw.text((text_x, y), line, font=f_body, fill=TEXT)
            y += FONT_BODY + 8
        y += 10   # gap between verses

    # ── Annotation lines (right column) ──────────────────────────
    line_y = rule_y + 18 + LINE_H   # start one line lower
    while line_y < H - MARGIN - LINE_H:
        draw.line([(right_x, line_y), (right_x + RIGHT_W, line_y)], fill=LINE_COLOUR, width=1)
        line_y += LINE_H

    # ── Save ─────────────────────────────────────────────────────
    slug      = f"{book_code}_{chapter}_{v_start}-{v_end}"
    out_dir   = OUTPUT_ROOT / username / "annotations" / book_code
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path  = out_dir / f"{slug}.png"
    img.save(out_path, "PNG", dpi=(150, 150))
    print(out_path)
    return out_path


if __name__ == "__main__":
    if len(sys.argv) < 6:
        print("Usage: gen_annotation_page.py BOOK CHAPTER V_START V_END USERNAME")
        sys.exit(1)
    book    = sys.argv[1].upper()
    chap    = int(sys.argv[2])
    v_start = int(sys.argv[3])
    v_end   = int(sys.argv[4])
    user    = sys.argv[5]
    generate(book, chap, v_start, v_end, user)
