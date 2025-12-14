import { BibleChapter } from "@/types/bible";
import { Verse } from "./Verse";
import styles from "./ChapterView.module.css";
import PullToNext from "../Navigation/PullToNext";
import { NextChapterRef } from "@/lib/bible-api";

interface ChapterViewProps {
  chapter: BibleChapter;
  nextChapter: NextChapterRef | null;
}

export function ChapterView({ chapter, nextChapter }: ChapterViewProps) {
  return (
    <article className={styles.article}>
      <header className={styles.header}>
        <h1 className={styles.title}>{chapter.title}</h1>
        <div className={styles.reference}>{chapter.bookId} {chapter.chapter}</div>
      </header>
      
      <div className={styles.content}>
        {chapter.verses.map((verse) => (
          <Verse key={verse.verse} verse={verse} />
        ))}
      </div>

       {nextChapter && (
        <PullToNext 
          nextChapterUrl={`/${nextChapter.bookId}/${nextChapter.chapter}`}
          nextChapterTitle={`Continue to ${nextChapter.title}`}
        />
      )}
    </article>
  );
}
