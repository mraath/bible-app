"use client";

import { useEffect, useRef, useState } from 'react';
import { useRouter } from 'next/navigation';
import styles from './PullToNext.module.css';

interface PullToNextProps {
  nextChapterUrl: string | null;
  nextChapterTitle: string;
}

export default function PullToNext({ nextChapterUrl, nextChapterTitle }: PullToNextProps) {
  const router = useRouter();
  const containerRef = useRef<HTMLDivElement>(null);
  const [progress, setProgress] = useState(0);
  const [triggered, setTriggered] = useState(false);

  useEffect(() => {
    if (!nextChapterUrl || triggered) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          // Calculate progress based on how much of the footer is visible
          // or use ratio. simpler: use intersectionRatio
          const ratio = entry.intersectionRatio;
          
          // Map ratio 0->1 to progress 0->100
          // effectively, when full footer is visible, you are ready
          let cleanRatio = Math.min(Math.max(ratio, 0), 1);
          
          setProgress(cleanRatio * 100);

          if (cleanRatio >= 0.95 && !triggered) {
             setTriggered(true);
             setTimeout(() => {
               router.push(nextChapterUrl);
             }, 500); // Visual delay for "fill" completion
          }
        });
      },
      {
        threshold: Array.from({ length: 21 }, (_, i) => i * 0.05), // 0, 0.05 ... 1.0
        root: null // viewport
      }
    );

    if (containerRef.current) {
      observer.observe(containerRef.current);
    }

    return () => observer.disconnect();
  }, [nextChapterUrl, triggered, router]);

  if (!nextChapterUrl) return null;

  return (
    <div className={styles.container} ref={containerRef}>
      <div className={styles.instruction}>
        {triggered ? "Loading..." : "Keep scrolling for next chapter"}
      </div>
      <div className={styles.circleContainer}>
        <svg viewBox="0 0 36 36" className={styles.chart}>
          <path
            className={styles.circleBg}
            d="M18 2.0845
              a 15.9155 15.9155 0 0 1 0 31.831
              a 15.9155 15.9155 0 0 1 0 -31.831"
          />
          <path
            className={styles.circle}
            strokeDasharray={`${progress}, 100`}
            d="M18 2.0845
              a 15.9155 15.9155 0 0 1 0 31.831
              a 15.9155 15.9155 0 0 1 0 -31.831"
          />
        </svg>
        <div className={styles.arrow}>↓</div>
      </div>
      <div className={styles.nextTitle}>{nextChapterTitle}</div>
    </div>
  );
}
