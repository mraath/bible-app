import { BibleVerse } from "@/types/bible";
import styles from "./Verse.module.css";

interface VerseProps {
  verse: BibleVerse;
}

export function Verse({ verse }: VerseProps) {
  return (
    <span className={styles.container} id={`verse-${verse.verse}`}>
      <sup className={styles.number}>{verse.verse}</sup>
      <span className={styles.text}>{verse.text} </span>
    </span>
  );
}
