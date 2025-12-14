import { BibleChapter } from "@/types/bible";
import metadata from "@/data/bibles/WEB/metadata.json";

export interface NextChapterRef {
  bookId: string;
  chapter: number;
  title: string;
}

export async function getChapter(bookId: string, chapter: string): Promise<BibleChapter> {
  // Simulating data fetch. In production, this imports from the generated JSONs.
  try {
    // Note: Dynamic imports in Next.js need to be somewhat static-analyzable for Webpack.
    const data = await import(`@/data/bibles/WEB/${bookId}/${chapter}.json`);
    return data.default as BibleChapter;
  } catch (error) {
    console.error(`Failed to load chapter ${bookId} ${chapter}`, error);
    throw new Error(`Chapter not found: ${bookId} ${chapter}`);
  }
}

export function getNextChapter(bookId: string, currentChapter: string): NextChapterRef | null {
  const bookIndex = metadata.findIndex((b: { id: string }) => b.id === bookId);
  if (bookIndex === -1) return null;

  const bookMeta = metadata[bookIndex];
  const chapterNum = parseInt(currentChapter);

  // If there is a next chapter in the same book
  if (chapterNum < bookMeta.chapters) {
    return {
      bookId,
      chapter: chapterNum + 1,
      title: `${bookMeta.name} ${chapterNum + 1}`
    };
  }

  // If this is the last chapter, go to next book
  if (bookIndex < metadata.length - 1) {
    const nextBook = metadata[bookIndex + 1];
    return {
      bookId: nextBook.id,
      chapter: 1,
      title: `${nextBook.name} 1`
    };
  }

  return null;
}
