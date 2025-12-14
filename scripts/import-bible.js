
const fs = require('fs');
const path = require('path');
const https = require('https');

const SOURCE_URL = 'https://raw.githubusercontent.com/thiagobodruk/bible/master/json/en_bbe.json';
const OUTPUT_DIR = path.join(__dirname, '../src/data/bibles/WEB');

const BOOK_IDS = [
  "GEN", "EXO", "LEV", "NUM", "DEU", "JOS", "JDG", "RUT", "1SA", "2SA", "1KI", "2KI", "1CH", "2CH", "EZR", "NEH", "EST", "JOB", "PSA", "PRO", "ECC", "SNG", "ISA", "JER", "LAM", "EZK", "DAN", "HOS", "JOL", "AMO", "OBA", "JON", "MIC", "NAH", "HAB", "ZEP", "HAG", "ZEC", "MAL",
  "MAT", "MRK", "LUK", "JHN", "ACT", "ROM", "1CO", "2CO", "GAL", "EPH", "PHP", "COL", "1TH", "2TH", "1TI", "2TI", "TIT", "PHM", "HEB", "JAS", "1PE", "2PE", "1JN", "2JN", "3JN", "JUD", "REV"
];

async function fetchJson(url) {
  return new Promise((resolve, reject) => {
    https.get(url, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        try {
          // Strip BOM if present
          const cleanData = data.trim().replace(/^\uFEFF/, '');
          resolve(JSON.parse(cleanData));
        } catch (e) {
          reject(e);
        }
      });
      res.on('error', reject);
    });
  });
}

function normalizeChapterData(book, bookId) {
    // The source structure is typically { name, chapters: [ [v1, v2], [v1, v2] ] }
    // Or sometimes { name, content: ... } depending on specific JSON file.
    // TehShrike structure: [ {name: "Genesis", chapters: [...]}, ... ]
    return book.chapters.map((verses, index) => {
        return {
            bookId: bookId,
            chapter: (index + 1).toString(),
            title: `${book.name} ${index + 1}`,
            verses: verses.map((text, vIndex) => ({
                verse: (vIndex + 1).toString(),
                text: text
            }))
        };
    });
}

async function main() {
  console.log(`Downloading Bible data from ${SOURCE_URL}...`);
  const data = await fetchJson(SOURCE_URL);
  
  if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  }

  const metadata = [];

  // Iterate over books
  data.forEach((book, index) => {
    const bookId = BOOK_IDS[index];
    if (!bookId) {
       // Only process books we have IDs for (66 books)
       return; 
    }

    const sections = normalizeChapterData(book, bookId);
    
    metadata.push({
      id: bookId,
      name: book.name,
      chapters: sections.length
    });

    const bookDir = path.join(OUTPUT_DIR, bookId);
    if (!fs.existsSync(bookDir)) {
      fs.mkdirSync(bookDir);
    }

    console.log(`Writing ${sections.length} chapters for ${bookId}...`);
    sections.forEach(chapter => {
        fs.writeFileSync(
            path.join(bookDir, `${chapter.chapter}.json`),
            JSON.stringify(chapter, null, 2)
        );
    });
  });

  fs.writeFileSync(
    path.join(OUTPUT_DIR, 'metadata.json'),
    JSON.stringify(metadata, null, 2)
  );

  console.log('Import complete.');
}

main().catch(console.error);
