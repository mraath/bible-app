
const fs = require('fs');
const path = require('path');
const https = require('https');

const URL = 'https://bibleproject.com/downloads/';
const OUTPUT_DIR = path.join(__dirname, '../public/images/books');

// Mapping simple names or patterns to our IDs
const BOOK_MAP = {
  "Genesis": "GEN", "Exodus": "EXO", "Leviticus": "LEV", "Numbers": "NUM", "Deuteronomy": "DEU",
  "Joshua": "JOS", "Judges": "JDG", "Ruth": "RUT", "1-Samuel": "1SA", "2-Samuel": "2SA",
  "1-Kings": "1KI", "2-Kings": "2KI", "1-Chronicles": "1CH", "2-Chronicles": "2CH",
  "Ezra": "EZR", "Nehemiah": "NEH", "Esther": "EST", "Job": "JOB", "Psalms": "PSA",
  "Proverbs": "PRO", "Ecclesiastes": "ECC", "Song-of-Songs": "SNG", "Isaiah": "ISA",
  "Jeremiah": "JER", "Lamentations": "LAM", "Ezekiel": "EZK", "Daniel": "DAN",
  "Hosea": "HOS", "Joel": "JOL", "Amos": "AMO", "Obadiah": "OBA", "Jonah": "JON",
  "Micah": "MIC", "Nahum": "NAH", "Habakkuk": "HAB", "Zephaniah": "ZEP", "Haggai": "HAG",
  "Zechariah": "ZEC", "Malachi": "MAL",
  "Matthew": "MAT", "Mark": "MRK", "Luke": "LUK", "John": "JHN", "Acts": "ACT",
  "Romans": "ROM", "1-Corinthians": "1CO", "2-Corinthians": "2CO", "Galatians": "GAL",
  "Ephesians": "EPH", "Philippians": "PHP", "Colossians": "COL",
  "1-Thessalonians": "1TH", "2-Thessalonians": "2TH", "1-Timothy": "1TI", "2-Timothy": "2TI",
  "Titus": "TIT", "Philemon": "PHM", "Hebrews": "HEB", "James": "JAS",
  "1-Peter": "1PE", "2-Peter": "2PE", "1-John": "1JN", "2-John": "2JN", "3-John": "3JN",
  "Jude": "JUD", "Revelation": "REV"
};

async function fetchHtml(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Failed to fetch ${url}: ${res.status}`);
  return await res.text();
}

async function downloadImage(url, dest) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Failed to fetch image ${url}: ${res.status}`);
  const buffer = await res.arrayBuffer();
  fs.writeFileSync(dest, Buffer.from(buffer));
}

async function main() {
  if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  }

  console.log('Fetching BibleProject downloads page...');
  const html = await fetchHtml(URL);

  // Regex to find poster links (usually cloudfront and .jpg)
  // They look like: href="https://d1bsmz3sdihplr.cloudfront.net/media/Posters%20Download/01-02%20Genesis_FNL.jpg"
  const regex = /href="([^"]+cloudfront[^"]+Posters[^"]+\.jpg)"/g;
  let match;
  const links = new Set();
  
  while ((match = regex.exec(html)) !== null) {
    links.add(match[1]);
  }

  console.log(`Found ${links.size} poster links.`);

  for (const link of links) {
    const filename = decodeURIComponent(link.split('/').pop()); // e.g., "01-02 Genesis_FNL.jpg"
    
    // Attempt to match filename to book ID
    let bookId = null;
    
    // Normalize filename for matching
    const norm = filename.replace(/[0-9-]+/, '').replace(/_FNL|FNL|_art|_hq|\.jpg/gi, '').trim().replace(/ /g, '-');
    // e.g. "Genesis", "1-Samuel", "Song-of-Songs"
    
    // Check direct map
    // We might need fuzzy matching or iterating map keys
    for (const [key, id] of Object.entries(BOOK_MAP)) {
      if (filename.toLowerCase().includes(key.toLowerCase())) {
        bookId = id;
        break;
      }
    }

    if (bookId) {
      const dest = path.join(OUTPUT_DIR, `${bookId}.jpg`);
      if (fs.existsSync(dest)) {
        console.log(`Skipping ${bookId} (exists)`);
        continue;
      }
      console.log(`Downloading ${bookId} from ${filename}...`);
      try {
        await downloadImage(link, dest);
      } catch (e) {
        console.error(`Failed to download ${bookId}:`, e);
      }
    } else {
      console.warn(`Could not identify book for ${filename}`);
    }
  }

  console.log('Download complete.');
}

main().catch(console.error);
