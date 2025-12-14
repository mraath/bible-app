export interface BibleVerse {
  verse: string; // The verse number (e.g., "1", "1a", "2-3")
  text: string;
  isPoetry?: boolean;
  isRedLetter?: boolean;
}

export interface BibleChapter {
  bookId: string;       // e.g., "GEN" (USFM code)
  chapter: string;      // e.g., "1"
  title: string;        // e.g., "The Creation"
  verses: BibleVerse[];
  previous?: { bookId: string; chapter: string };
  next?: { bookId: string; chapter: string };
}
