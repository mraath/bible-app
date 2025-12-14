"use client";

import styles from "./Timeline.module.css";
import { useParams } from "next/navigation";
import events from "@/data/timeline.json";

export function Timeline() {
  const params = useParams();
  const currentBook = typeof params?.book === 'string' ? params.book : "GEN";
  
  // Find crude progress estimate (0-100%)
  // In a real app, calculate true canonical progress
  const currentEventIndex = events.findIndex(e => e.bookId === currentBook);
  const activeEvent = currentEventIndex !== -1 ? events[currentEventIndex] : events[0];

  return (
    <aside className={styles.container}>
      <div className={styles.line} />
      {events.map((event) => {
        const isActive = event.bookId === currentBook;
        const isPast = events.findIndex(e => e.id === event.id) < events.findIndex(e => e.id === activeEvent.id);
        const isMajor = (event as any).type === "major";
        
        return (
          <div 
            key={event.id} 
            className={`
              ${styles.marker} 
              ${isActive ? styles.active : ''} 
              ${isPast ? styles.past : ''}
              ${isMajor ? styles.major : ''}
            `}
            // Use standard styling for top position (percentage of scroll container height)
            // But since we want "Scrolling", we need to map 0-1 to [0px - containerHeight] or similar?
            // For now, let's map 0-1 to 0-150vh (scrollable area)
            style={{ top: `${event.progress * 150}%` }}
          >
            <div className={styles.dot} />
            <div className={styles.label}>{event.title}</div>
          </div>
        );
      })}
    </aside>
  );
}
