"use client";

import { useState, useEffect } from "react";

export function useReadingPosition() {
  const [activeVerse, setActiveVerse] = useState<string>("1");

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        // Find the verse that is most visible or crossing the center
        const visible = entries.filter((e) => e.isIntersecting);
        if (visible.length > 0) {
          // Sort by intersection ratio or closeness to center?
          // Simple heuristic: Take the first intersecting one.
          // Better: The one closest to the top-center (reading line).
          const sorted = visible.sort((a, b) => {
             const aRect = a.boundingClientRect;
             const bRect = b.boundingClientRect;
             return aRect.top - bRect.top;
          });
          
          if (sorted[0]?.target.id) {
            const verseId = sorted[0].target.id.replace("verse-", "");
            setActiveVerse(verseId);
          }
        }
      },
      {
        rootMargin: "-20% 0px -60% 0px", // Focus area is roughly top part of screen
        threshold: 0,
      }
    );

    // Observe all verse elements
    const verses = document.querySelectorAll("[id^='verse-']");
    verses.forEach((v) => observer.observe(v));

    return () => observer.disconnect();
  }, []);

  return activeVerse;
}
