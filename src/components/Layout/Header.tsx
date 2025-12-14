"use client";

import Link from "next/link";
import styles from "./Header.module.css";
import { useParams } from "next/navigation";

export function Header() {
  const params = useParams();
  const book = typeof params?.book === 'string' ? params.book : "GEN";
  const chapter = typeof params?.chapter === 'string' ? params.chapter : "1";

  return (
    <header className={styles.header}>
      <nav className={styles.nav}>
        <div className={styles.logo}>
          <Link href="/">Bible</Link>
        </div>
        
        <button className={styles.locationTrigger}>
          {book} {chapter}
        </button>
        
        <div className={styles.actions}>
          {/* Settings toggle will go here */}
          <button className={styles.iconButton} aria-label="Settings">
            Aa
          </button>
        </div>
      </nav>
    </header>
  );
}
