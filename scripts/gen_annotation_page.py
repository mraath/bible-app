#!/usr/bin/env python3
"""
Generate a two-column scripture annotation image, sync to Obsidian,
and maintain a user scripture index.

Usage — pass the raw plan reference string + username:
  python3 gen_annotation_page.py "MATTHEW 1:1-17" mraath
  python3 gen_annotation_page.py "PSALMS 1" mraath
  python3 gen_annotation_page.py "GENESIS 1-2" mraath
  python3 gen_annotation_page.py "ACTS 3" mraath

Or explicit args (legacy):
  python3 gen_annotation_page.py MAT 1 1 17 mraath
"""

import json
import re
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


BOOK_ALIASES = {
    "MATTHEW": "MAT", "MARK": "MAR", "LUKE": "LUK", "JOHN": "JHN",
    "ACTS": "ACT", "ROMANS": "ROM",
    "1 CORINTHIANS": "1CO", "1COR": "1CO", "1 COR.": "1CO",
    "2 CORINTHIANS": "2CO", "2COR": "2CO", "2 COR.": "2CO",
    "GALATIANS": "GAL", "EPHESIANS": "EPH", "PHILIPPIANS": "PHP",
    "COLOSSIANS": "COL", "OLOSSIANS": "COL",
    "1 THESSALONIANS": "1TH", "2 THESSALONIANS": "2TH",
    "1 TIMOTHY": "1TI", "2 TIMOTHY": "2TI",
    "TITUS": "TIT", "PHILEMON": "PHM", "HEBREWS": "HEB",
    "JAMES": "JAS", "1 PETER": "1PE", "2 PETER": "2PE",
    "1 JOHN": "1JN", "2 JOHN": "2JN", "3 JOHN": "3JN",
    "JUDE": "JUD", "REVELATION": "REV",
    "GENESIS": "GEN", "EXODUS": "EXO", "LEVITICUS": "LEV",
    "NUMBERS": "NUM", "DEUTERONOMY": "DEU", "JOSHUA": "JOS",
    "JUDGES": "JDG", "RUTH": "RUT",
    "1 SAMUEL": "1SA", "2 SAMUEL": "2SA",
    "1 KINGS": "1KI", "2 KINGS": "2KI",
    "1 CHRONICLES": "1CH", "2 CHRONICLES": "2CH",
    "EZRA": "EZR", "NEHEMIAH": "NEH", "ESTHER": "EST",
    "JOB": "JOB", "PSALMS": "PSA", "PSALM": "PSA",
    "PROVERBS": "PRO", "ECCLESIASTES": "ECC",
    "SONG OF SONGS": "SNG", "SONG OF SOLOMON": "SNG",
    "ISAIAH": "ISA", "JEREMIAH": "JER", "LAMENTATIONS": "LAM",
    "LAMENTATIANS": "LAM",
    "EZEKIEL": "EZK", "DANIEL": "DAN", "HOSEA": "HOS",
    "JOEL": "JOL", "AMOS": "AMO", "OBADIAH": "OBA",
    "JONAH": "JON", "MICAH": "MIC", "NAHUM": "NAM",
    "HABAKKUK": "HAB", "ZEPHANIAH": "ZEP", "HAGGAI": "HAG",
    "ZECHARIAH": "ZEC", "MALACHI": "MAL",
}


def resolve_book_code(raw: str) -> str:
    """Convert any book name/abbreviation to a 3-letter WEB code."""
    up = raw.strip().upper()
    if up in BOOK_ALIASES:
        return BOOK_ALIASES[up]
    if up in BOOK_NAMES:
        return up
    # Try prefix match
    for alias, code in BOOK_ALIASES.items():
        if up.startswith(alias[:4]):
            return code
    return up   # hope it's already a valid code


def parse_plan_ref(ref_str: str):
    """
    Parse a plan reference string into (book_code, chapters_verses) tuples.

    Examples:
      "MATTHEW 1:1-17"  → [("MAT", 1, 1, 17)]
      "PSALMS 1"         → [("PSA", 1, 1, last_verse)]
      "GENESIS 1-2"      → [("GEN", 1, 1, last), ("GEN", 2, 1, last)]
      "ACTS 3"           → [("ACT", 3, 1, last_verse)]
    """
    ref_str = ref_str.strip()

    # Split book name from reference numbers
    m = re.match(r'^((?:\d\s+)?[A-Z][A-Z .]+?)\s+([\d:,\-–]+)$', ref_str, re.IGNORECASE)
    if not m:
        # Single word like "JOB"
        book_raw, ref_part = ref_str, "1"
    else:
        book_raw, ref_part = m.group(1).strip(), m.group(2).strip()

    code = resolve_book_code(book_raw)

    # Normalise en-dash
    ref_part = ref_part.replace('–', '-')

    # Case 1: chapter:vstart-vend  e.g. "1:1-17"
    m1 = re.match(r'^(\d+):(\d+)-(\d+)$', ref_part)
    if m1:
        ch, vs, ve = int(m1.group(1)), int(m1.group(2)), int(m1.group(3))
        return [(code, ch, vs, ve)]

    # Case 2: chapter:verse  e.g. "1:1"
    m2 = re.match(r'^(\d+):(\d+)$', ref_part)
    if m2:
        ch, vs = int(m2.group(1)), int(m2.group(2))
        return [(code, ch, vs, vs)]

    # Case 3: chapter-chapter  e.g. "1-2" (whole chapters)
    m3 = re.match(r'^(\d+)-(\d+)$', ref_part)
    if m3:
        ch_start, ch_end = int(m3.group(1)), int(m3.group(2))
        result = []
        for ch in range(ch_start, ch_end + 1):
            last = last_verse(code, ch)
            result.append((code, ch, 1, last))
        return result

    # Case 4: single chapter  e.g. "1"
    m4 = re.match(r'^(\d+)$', ref_part)
    if m4:
        ch = int(m4.group(1))
        last = last_verse(code, ch)
        return [(code, ch, 1, last)]

    raise ValueError(f"Cannot parse reference: {ref_str!r}")


def last_verse(book_code: str, chapter: int) -> int:
    path = BIBLE_ROOT / book_code / f"{chapter}.json"
    if not path.exists():
        return 999
    with open(path) as f:
        data = json.load(f)
    return max(int(v["verse"]) for v in data["verses"])


def book_name(code: str) -> str:
    return BOOK_NAMES.get(code.upper(), code)


def image_filename(book_code: str, chap_start: int, v_start: int,
                   chap_end: int, v_end: int) -> str:
    """Portable, self-describing filename."""
    bname = book_name(book_code)
    if chap_start == chap_end:
        return f"Bible.{bname}.{chap_start}.{v_start}-{v_end}.annotation.png"
    return f"Bible.{bname}.{chap_start}-{chap_end}.annotation.png"


def load_verses(book_code: str, chapter: int, v_start: int, v_end: int):
    path = BIBLE_ROOT / book_code / f"{chapter}.json"
    if not path.exists():
        raise FileNotFoundError(f"No WEB data for {book_code} {chapter}")
    with open(path) as f:
        data = json.load(f)
    return [v for v in data["verses"] if v_start <= int(v["verse"]) <= v_end]


def load_verses_multi(segments):
    """Load verses across multiple chapter segments."""
    all_verses = []
    for (code, ch, vs, ve) in segments:
        verses = load_verses(code, ch, vs, ve)
        # prefix verse numbers with chapter for multi-chapter readings
        if len(segments) > 1:
            for v in verses:
                v = dict(v)
                v["verse"] = f"{ch}:{v['verse']}"
                all_verses.append(v)
        else:
            all_verses.extend(verses)
    return all_verses


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


def generate_from_ref(plan_ref: str, username: str):
    """Main entry point. plan_ref is raw plan text e.g. 'MATTHEW 1:1-17'."""
    segments  = parse_plan_ref(plan_ref)
    book_code = segments[0][0]
    ch_start, vs_start = segments[0][1], segments[0][2]
    ch_end,   vs_end   = segments[-1][1], segments[-1][3]

    verses = load_verses_multi(segments)
    img    = render_image(book_code, ch_start, vs_start, vs_end, verses,
                          ch_end=ch_end)

    fname     = image_filename(book_code, ch_start, vs_start, ch_end, vs_end)
    note_slug = (f"{ch_start}_{vs_start}-{vs_end}" if ch_start == ch_end
                 else f"{ch_start}-{ch_end}")

    # Save to bible-app annotations
    ann_dir = OUTPUT_ROOT / username / "annotations"
    ann_dir.mkdir(parents=True, exist_ok=True)
    app_img_path = ann_dir / fname
    img.save(app_img_path, "PNG", dpi=(150, 150))

    # Copy to Obsidian Images
    OBSIDIAN_IMG.mkdir(parents=True, exist_ok=True)
    shutil.copy2(app_img_path, OBSIDIAN_IMG / fname)

    # Create Obsidian note
    obs_note_path = create_obsidian_note(book_code, ch_start, vs_start, vs_end, fname, verses)

    # Build index key
    index_key = (f"{book_code}:{ch_start}:{vs_start}-{vs_end}" if ch_start == ch_end
                 else f"{book_code}:{ch_start}-{ch_end}")
    update_scripture_index(book_code, ch_start, vs_start, ch_end, vs_end,
                           username, fname, note_slug, index_key)

    # Note path for wiki link
    note_rel = f"notes/{book_code}/{note_slug}"

    result = {
        "image":          str(app_img_path),
        "obsidian_image": str(OBSIDIAN_IMG / fname),
        "obsidian_note":  str(obs_note_path),
        "index_key":      index_key,
        "filename":       fname,
        "note_path":      note_rel,
        "wiki_link":      f"[[{note_rel}|{book_name(book_code)} {plan_ref.split()[-1]}]]",
    }
    print(json.dumps(result))
    return result


def render_image(book_code: str, chapter: int, v_start: int, v_end: int,
                 verses: list, ch_end: int = None) -> Image.Image:
    img  = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    f_title = ImageFont.truetype(FONT_BOLD,    FONT_TITLE)
    f_body  = ImageFont.truetype(FONT_REGULAR, FONT_BODY)
    f_vnum  = ImageFont.truetype(FONT_BOLD,    FONT_VNUM)
    f_label = ImageFont.truetype(FONT_BOLD,    FONT_LABEL)

    # Header bar
    draw.rectangle([0, 0, W, HEADER_H], fill=HEADER_BG)
    if ch_end and ch_end != chapter:
        ref = f"{book_name(book_code)} {chapter}–{ch_end}"
    else:
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

    div_x = MARGIN + LEFT_W + COL_GAP // 2
    draw.line([(div_x, HEADER_H + 10), (div_x, H - MARGIN)], fill=DIVIDER, width=1)

    # Scripture
    y      = rule_y + 18
    vnum_w = 46   # wider to fit "3:1" style labels

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


def update_scripture_index(book_code, ch_start, vs_start, ch_end, vs_end,
                            username, fname, note_slug, index_key):
    index_path = OUTPUT_ROOT / username / "scripture-index.json"
    index = {}
    if index_path.exists():
        with open(index_path) as f:
            index = json.load(f)
    bname = book_name(book_code)
    index[index_key] = {
        "book":           bname,
        "chapter_start":  ch_start,
        "chapter_end":    ch_end,
        "verses":         f"{vs_start}-{vs_end}",
        "annotation":     f"users/{username}/annotations/{fname}",
        "bible_app_note": f"users/{username}/notes/{book_code}/{note_slug}.md",
        "obsidian_note":  f"Personal/MR Bible/{bname} {ch_start}v{vs_start}-{vs_end}.md",
        "created":        str(date.today()),
    }
    with open(index_path, "w") as f:
        json.dump(index, f, indent=2)


if __name__ == "__main__":
    # New usage: "MATTHEW 1:1-17" mraath
    # Legacy:    MAT 1 1 17 mraath
    if len(sys.argv) == 3:
        generate_from_ref(sys.argv[1], sys.argv[2])
    elif len(sys.argv) == 6:
        # legacy explicit args
        code = sys.argv[1].upper()
        ref  = f"{code} {sys.argv[3]}:{sys.argv[4]}" if sys.argv[3] != sys.argv[4] else f"{code} {sys.argv[2]}"
        generate_from_ref(f"{sys.argv[1]} {sys.argv[2]}:{sys.argv[3]}-{sys.argv[4]}", sys.argv[5])
    else:
        print('Usage: gen_annotation_page.py "MATTHEW 1:1-17" mraath')
        sys.exit(1)
