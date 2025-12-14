import { getChapter, getNextChapter } from "@/lib/bible-api";
import { ChapterView } from "@/components/Reader/ChapterView";
import { notFound } from "next/navigation";

interface PageProps {
  params: Promise<{
    book: string;
    chapter: string;
  }>;
}

// In a static export, we would need generateStaticParams.
// For now, assuming dynamic SSR or we will add generateStaticParams later.
import metadata from "@/data/bibles/WEB/metadata.json";

export async function generateStaticParams() {
  const params = [];
  for (const book of metadata) {
    for (let i = 1; i <= book.chapters; i++) {
      params.push({ book: book.id, chapter: i.toString() });
    }
  }
  return params;
}

export default async function ChapterPage({ params }: PageProps) {
  const { book, chapter } = await params;
  
  try {
    const chapterData = await getChapter(book, chapter);
    const nextChapter = getNextChapter(book, chapter);
    
    return (
      <main>
        <ChapterView chapter={chapterData} nextChapter={nextChapter} />
      </main>
    );
  } catch {
    notFound();
  }
}
