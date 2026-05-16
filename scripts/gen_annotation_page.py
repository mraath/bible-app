#!/usr/bin/env python3
"""
Generate a two-column scripture annotation image, sync to Obsidian,
and maintain a user scripture index.

Usage:
  python3 gen_annotation_page.py MAT 1 1 17 mraath
  python3 gen_annotation_page.py PSA 23 1 6 mraath
"""

import json
import sys
import shutil
from datetime import date
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BIBLE_ROOT   = Path(__file__).parent.parent / "src/data/bibles/WEB"
OUTPUT_ROOT  = Path(__file__).parent.parent / "users"
OBSIDIAN_IMG = Path("/home/marty/projects/obsidian/Images")
OBSIDIAN_NOTE= Path("/home/marty/projects/obsidian/Personal/MR Bible")

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
W, H     = 1600, 2200
MARGIN   = 60
HEADER_H = 90
COL_GAP  = 40
LEFT_W   = 640
RIGHT_W  = W - MARGIN * 2 - LEFT_W - COL_GAP

FONT_TITLE = 30
FONT_BODY  = 21
FONT_VNUM  = 17
FONT_LABEL = 16
LINE_H     = 36

BOOK_NAMES = {
    "GEN": "Genesis",       "EXO": "Exodus",        "LEV": "Leviticus",
    "NUM": "Numbers",       "DEU": "Deuteronomy",   "JOS": "Joshua",
    "JDG": "Judges",        "RUT": "Ruth",          "1SA": "1 Samuel",
    "2SA": "2 Samuel",      "1KI": "1 Kings",       "2KI": "2 Kings",
    "1CH": "1 Chronicles",  "2CH": "2 Chronicles",  "EZR": "Ezra",
    "NEH": "Nehemiah",      "EST": "Esther",        "JOB": "Job",
    "PSA": "Psalms",        "PRO": "Proverbs",      "ECC": "Ecclesiastes",
    "SNG": "Song of Solomon","ISA": "Isaiah",       "JER": "Jeremiah",
    "LAM": "Lamentations",  "EZK": "Ezekiel",       "DAN": "Daniel",
    "HOS": "Hosea",         "JOL": "Joel",          "AMO": "Amos",
    "OBA": "Obadiah",       "JON": "Jonah",         "MIC": "Micah",
    "NAM": "Nahum",         "HAB": "Habakkuk",      "ZEP": "Zephaniah",
    "HAG": "Haggai",        "ZEC": "Zechariah",     "MAL": "Malachi",
    "MAT": "Matthew",       "MAR": "Mark",          "LUK": "Luke",
    "JHN": "John",          "ACT": "Acts",          "ROM": "Romans",
    "1CO": "1 Corinthians", "2CO": "2 Corinthians", "GAL": "Galatians",
    "EPH": "Ephesians",     "PHP": "Philippians",   "COL": "Colossians",
    "1TH": "1 Thessalonians","2TH": "2 Thessalonians","1TI": "1 Timothy",
    "2TI": "2 Timothy",     "TIT": "Titus",         "PHM": "Philemon",
    "HEB": "Hebrews",       "JAS": "James",         "1PE": "1 Peter",
    "2PE": "2 Peter",       "1JN": "1 John",        "2JN": "2 John",
    "3JN": "3 John",        "JUD": "Jude",          "REV": "Revelation",
}


def book_name(code: str) -> str:
    return BOOK_NAMES.get(code.upper(), code)


def image_filename(book_code: str, chapter: int, v_start: int, v_end: int) -> str:
    """Portable, self-describing filename readable on any system."""
    return f"Bible.{book_name(book_code)}.{chapter}.{v_start}-{v_end}.annotation.png"


def load_verses(book_code: str, chapter: int, v_start: int, v_end: int):
    path = BIBLE_ROOT / book_code / f"{chapter}.json"
    if not path.exists():
        raise FileNotFoundError(f"No WEB data for {book_code} {chapter}")
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


def render_image(book_code: str, chapter: int, v_start: int, v_end: int, verses: list) -> Image.Image:
    img  = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    f_title = ImageFont.truetype(FONT_BOLD,    FONT_TITLE)
    f_body  = ImageFont.truetype(FONT_REGULAR, FONT_BODY)
    f_vnum  = ImageFont.truetype(FONT_BOLD,    FONT_VNUM)
    f_label = ImageFont.truetype(FONT_BOLD,    FONT_LABEL)

    # Header bar
    draw.rectangle([0, 0, W, HEADER_H], fill=HEADER_BG)
    ref = f"{book_name(book_code)} {chapter}:{v_start}–{v_end}"
    draw.text((MARGIN, HEADER_H // 2), ref, font=f_title, fill=HEADER_TEXT, anchor="lm")
    draw.text((W - MARGIN, HEADER_H // 2), "WEB · World English Bible",
              font=f_label, fill=ACCENT, anchor="rm")

    # Column labels
    label_y = HEADER_H + 24
    left_x  = MARGIN
    right_x = MARGIN + LEFT_W + COL_GAP

    draw.text((left_x, label_y),  "SCRIPTURE", font=f_label, fill=VERSE_NUM)
    draw.text((right_x, label_y), "NOTES",     font=f_label, fill=VERSE_NUM)

    rule_y = label_y + 22
    draw.line([(left_x, rule_y), (left_x + LEFT_W, rule_y)], fill=DIVIDER, width=1)
    draw.line([(right_x, rule_y), (right_x + RIGHT_W, rule_y)], fill=DIVIDER, width=1)

    # Vertical divider
    div_x = MARGIN + LEFT_W + COL_GAP // 2
    draw.line([(div_x, HEADER_H + 10), (div_x, H - MARGIN)], fill=DIVIDER, width=1)

    # Scripture
    y      = rule_y + 18
    vnum_w = 36

    for v in verses:
        draw.text((left_x, y), str(v["verse"]), font=f_vnum, fill=VERSE_NUM)
        text_x  = left_x + vnum_w
        avail_w = LEFT_W - vnum_w
        for line in wrap_verse(v["text"].strip(), f_body, draw, avail_w):
            if y > H - MARGIN:
                break
            draw.text((text_x, y), line, font=f_body, fill=TEXT)
            y += FONT_BODY + 8
        y += 10

    # Annotation lines
    line_y = rule_y + 18 + LINE_H
    while line_y < H - MARGIN - LINE_H:
        draw.line([(right_x, line_y), (right_x + RIGHT_W, line_y)], fill=LINE_COLOUR, width=1)
        line_y += LINE_H

    return img


def update_scripture_index(book_code: str, chapter: int, v_start: int, v_end: int,
                            username: str, img_filename: str, note_slug: str):
    index_path = OUTPUT_ROOT / username / "scripture-index.json"
    index = {}
    if index_path.exists():
        with open(index_path) as f:
            index = json.load(f)

    key = f"{book_code}:{chapter}:{v_start}-{v_end}"
    index[key] = {
        "book":          book_name(book_code),
        "chapter":       chapter,
        "verses":        f"{v_start}-{v_end}",
        "annotation":    f"users/{username}/annotations/{img_filename}",
        "bible_app_note":f"users/{username}/notes/{book_code}/{note_slug}.md",
        "obsidian_note": f"Personal/MR Bible/{book_name(book_code)} {chapter}v{v_start}-{v_end}.md",
        "created":       str(date.today()),
    }

    with open(index_path, "w") as f:
        json.dump(index, f, indent=2)
    return key


def create_obsidian_note(book_code: str, chapter: int, v_start: int, v_end: int,
                          img_filename: str, verses: list):
    bname    = book_name(book_code)
    note_name = f"{bname} {chapter}v{v_start}-{v_end}.md"
    note_path = OBSIDIAN_NOTE / note_name

    if note_path.exists():
        return note_path  # don't overwrite existing notes

    verse_text = "\n".join(
        f"> **{v['verse']}** {v['text'].strip()}" for v in verses
    )

    content = f"""# {bname} {chapter}:{v_start}–{v_end}

**Version:** WEB (World English Bible)
**Tags:** #bible-note #{bname.lower().replace(' ', '-')} #annotation

---

## Annotation Page

![[{img_filename}]]

---

## Scripture Text

{verse_text}

---

## Notes

<!-- Your notes here -->

---

## Prayer

<!-- Prayer from this reading -->
"""
    note_path.write_text(content)
    return note_path


def generate(book_code: str, chapter: int, v_start: int, v_end: int, username: str):
    book_code = book_code.upper()
    verses    = load_verses(book_code, chapter, v_start, v_end)
    img       = render_image(book_code, chapter, v_start, v_end, verses)

    fname     = image_filename(book_code, chapter, v_start, v_end)
    note_slug = f"{chapter}_{v_start}-{v_end}"

    # Save to bible-app annotations
    ann_dir = OUTPUT_ROOT / username / "annotations"
    ann_dir.mkdir(parents=True, exist_ok=True)
    app_img_path = ann_dir / fname
    img.save(app_img_path, "PNG", dpi=(150, 150))

    # Copy to Obsidian Images
    OBSIDIAN_IMG.mkdir(parents=True, exist_ok=True)
    obs_img_path = OBSIDIAN_IMG / fname
    shutil.copy2(app_img_path, obs_img_path)

    # Create Obsidian note
    obs_note_path = create_obsidian_note(book_code, chapter, v_start, v_end, fname, verses)

    # Update scripture index
    index_key = update_scripture_index(
        book_code, chapter, v_start, v_end, username, fname, note_slug
    )

    print(json.dumps({
        "image":         str(app_img_path),
        "obsidian_image":str(obs_img_path),
        "obsidian_note": str(obs_note_path),
        "index_key":     index_key,
        "filename":      fname,
    }))
    return app_img_path


if __name__ == "__main__":
    if len(sys.argv) < 6:
        print("Usage: gen_annotation_page.py BOOK CHAPTER V_START V_END USERNAME")
        sys.exit(1)
    generate(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5])
