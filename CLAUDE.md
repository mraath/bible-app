# bible-app — Claude Context

Personal Bible reading and study app. Built incrementally — start simple, add depth over time.
Owner: mraath. Repo: `github.com/mraath/bible-app`.

---

## Tech Stack

- **Framework:** Next.js (App Router, TypeScript)
- **Bible data:** WEB (World English Bible) stored as JSON under `src/data/bibles/WEB/`
- **Annotation images:** Generated with Python + Pillow (`scripts/gen_annotation_page.py`)
- **Dev server:** `npm run dev` → http://localhost:3000

---

## Folder Structure

```
bible-app/
├── src/
│   ├── app/
│   │   └── [book]/[chapter]/page.tsx   ← chapter reader route
│   ├── components/
│   │   ├── Layout/Header
│   │   ├── Navigation/PullToNext       ← swipe/pull to next chapter
│   │   ├── Reader/ChapterView, Verse   ← core reading UI
│   │   ├── Timeline/                   ← biblical timeline
│   │   └── Visuals/BackgroundLayer     ← map/visual overlays
│   ├── data/
│   │   ├── bibles/WEB/<BOOKCODE>/<chapter>.json   ← scripture text
│   │   ├── timeline.json
│   │   └── visuals/maps/<BOOKCODE>.json
│   ├── lib/bible-api.ts
│   └── types/bible.ts
├── scripts/
│   └── gen_annotation_page.py          ← generates annotation images (see below)
├── knowledge/
│   └── books.md                        ← all 66 books: OT/NT, chapters, authors
├── plans/
│   └── discipleship-journal.md         ← master Discipleship Journal plan (25/month, 300 days)
└── users/
    └── mraath/
        ├── plans/
        │   └── discipleship-journal.md ← mraath's personal progress (checkboxes)
        ├── annotations/
        │   └── Bible.Matthew.1.1-17.annotation.png  ← annotation images
        ├── notes/
        │   └── MAT/1_1-17.md           ← study notes per passage
        └── scripture-index.json        ← passage → note/image lookup
```

---

## Bible Data Format

Each chapter is a JSON file at `src/data/bibles/WEB/<BOOKCODE>/<chapter>.json`:

```json
{
  "book": "MAT",
  "chapter": 1,
  "verses": [
    { "verse": 1, "text": "The book of the generations..." },
    ...
  ]
}
```

**Book codes** (3-letter, uppercase) — full list in `knowledge/books.md`:

| Code | Book | Code | Book | Code | Book |
|------|------|------|------|------|------|
| GEN | Genesis | MAT | Matthew | ROM | Romans |
| EXO | Exodus | MAR | Mark | 1CO | 1 Corinthians |
| PSA | Psalms | LUK | Luke | EPH | Ephesians |
| PRO | Proverbs | JHN | John | REV | Revelation |
| ... | (see knowledge/books.md) | ACT | Acts | ... | |

---

## Reading Plans

### Master plan
`plans/discipleship-journal.md` — the template. Never modify directly.

Discipleship Journal plan structure:
- 4 readings per day (Gospel · Epistle · Psalms/Proverbs · OT)
- 25 days per month (built-in catch-up days)
- 300 total entries across 12 months
- No fixed dates — purely sequential

### User progress
`users/<username>/plans/discipleship-journal.md` — personal checkbox copy:

```markdown
- [ ] **Jan 1** — MATTHEW 1:1-17 · ACTS 1:1-11 · PSALMS 1 · GENESIS 1-2
- [x] **Jan 2** — ...   (completed)
- [s] **Jan 3** — ...   (skipped)
```

When a reading has an annotation note, the first passage gets a wiki link:
```markdown
- [x] **Jan 1** — [[notes/MAT/1_1-17|Matthew 1:1-17]] · ACTS 1:1-11 · PSALMS 1 · GENESIS 1-2
```

---

## Annotation System

### Generating an annotation page

```bash
python3 scripts/gen_annotation_page.py <BOOKCODE> <CHAPTER> <V_START> <V_END> <USERNAME>
# e.g.
python3 scripts/gen_annotation_page.py MAT 1 1 17 mraath
```

**Output (JSON printed to stdout):**
```json
{
  "image":          "users/mraath/annotations/Bible.Matthew.1.1-17.annotation.png",
  "obsidian_image": "/home/marty/projects/obsidian/Images/Bible.Matthew.1.1-17.annotation.png",
  "obsidian_note":  "/home/marty/projects/obsidian/Personal/MR Bible/Matthew 1v1-17.md",
  "index_key":      "MAT:1:1-17",
  "filename":       "Bible.Matthew.1.1-17.annotation.png"
}
```

**What it does:**
1. Reads verses from `src/data/bibles/WEB/`
2. Renders a two-column PNG (left = scripture with verse numbers, right = blank lined space for annotations)
3. Saves to `users/<username>/annotations/`
4. Copies to `obsidian/Images/` automatically
5. Creates an Obsidian note at `obsidian/Personal/MR Bible/<Book> <ch>v<v>.md`
6. Updates `users/<username>/scripture-index.json`

### Image naming convention
`Bible.<BookName>.<Chapter>.<VStart>-<VEnd>.annotation.png`

Examples:
- `Bible.Matthew.1.1-17.annotation.png`
- `Bible.Psalms.23.1-6.annotation.png`
- `Bible.Genesis.1.1-31.annotation.png`

Self-describing — the filename alone identifies the passage regardless of which system it's on.

### Scripture index
`users/mraath/scripture-index.json` — lookup by passage key (`BOOKCODE:CHAPTER:VSTART-VEND`):

```json
{
  "MAT:1:1-17": {
    "book": "Matthew",
    "chapter": 1,
    "verses": "1-17",
    "annotation": "users/mraath/annotations/Bible.Matthew.1.1-17.annotation.png",
    "bible_app_note": "users/mraath/notes/MAT/1_1-17.md",
    "obsidian_note": "Personal/MR Bible/Matthew 1v1-17.md",
    "created": "2026-05-16"
  }
}
```

Use this to show "you have a note on this passage" anywhere in the app.

---

## Obsidian Integration

Obsidian vault: `/home/marty/projects/obsidian/`

| What | Where in Obsidian |
|------|--------------------|
| Annotation images | `Images/Bible.<Book>.<ch>.<v>.annotation.png` |
| Study notes | `Personal/MR Bible/<Book> <ch>v<v>.md` |
| Reading plan notes | `Personal/MR Bible/` (existing notes) |

Obsidian notes use `![[filename]]` to embed images. The scripture index in the bible-app and the Obsidian notes stay in sync because `gen_annotation_page.py` writes to both on every run.

---

## Claude Skills (in `~/.claude/skills/`)

| Skill | Invoke | What it does |
|-------|--------|--------------|
| `bible-reading` | `/bible-reading` | Shows next unchecked plan entry, marks it done, checks index for existing notes |
| `bible-annotate` | `/bible-annotate MAT 1:1-17` | Generates annotation image + note, syncs to Obsidian, updates index |

---

## Git & Deployment

```bash
# Dev
npm run dev

# Commit progress (reading, annotations, notes)
git add users/
git commit -m "reading: mark Jan 2 complete (2/300)"

# Push (token in AU .env.local)
GITHUB_TOKEN=$(grep ^GITHUB_TOKEN /home/marty/projects/AU/marketing/web/.env.local | cut -d= -f2)
git push https://mraath:${GITHUB_TOKEN}@github.com/mraath/bible-app.git main

# Obsidian is a separate repo — commit it separately after annotation generation
git -C /home/marty/projects/obsidian add Images/ "Personal/MR Bible/"
git -C /home/marty/projects/obsidian commit -m "bible annotation: <passage>"
git -C /home/marty/projects/obsidian push
```

---

## Vision / Roadmap

This is a personal study app being built incrementally. Planned directions:
- **Annotation viewer** — tap a verse in the Next.js app to see the annotation image inline
- **Note indicator** — when viewing a chapter, highlight verses that have notes in `scripture-index.json`
- **Multi-user** — `users/<username>/` structure already supports multiple users
- **Additional plans** — `users/<username>/plans/` can hold any plan, not just discipleship
- **Multi-translation** — `src/data/bibles/` structure supports adding ESV, NIV etc alongside WEB

Keep it simple. Add one feature at a time.
