"use client";

import { useReadingPosition } from "@/components/Reader/useReadingPosition";
import { BookVisualMapping, getVisualMapping } from "@/lib/visuals";
import styles from "./BackgroundLayer.module.css";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

export default function BackgroundLayer() {
  const params = useParams();
  const bookId = params?.book as string;
  const activeVerseStr = useReadingPosition();
  const activeVerse = parseInt(activeVerseStr, 10);
  const [mapping, setMapping] = useState<BookVisualMapping | null>(null);

  useEffect(() => {
    if (bookId) {
       getVisualMapping(bookId).then(map => {
           if (map) setMapping(map);
           else setMapping(null);
       });
    }
  }, [bookId]);

  const style: React.CSSProperties = {
      backgroundColor: mapping?.color || "#0f172a",
      transition: 'background-color 1s ease'
  };

  let imageStyle: React.CSSProperties = {};

  if (mapping) {
      // Find matching keyframe or interpolate
      // Simple lookup for MVP
      const currentKeyframe = mapping.keyframes.find(k => activeVerse >= k.startVerse && activeVerse <= k.endVerse) 
                              || mapping.keyframes[0];
                              
      const focus = currentKeyframe?.focus || { x: 50, y: 50, scale: 1 };
      
      imageStyle = {
          backgroundImage: `url(${mapping.imageUrl})`,
          transformOrigin: `${focus.x}% ${focus.y}%`,
          transform: `scale(${focus.scale})`,
          opacity: 1
      };
  } else {
      imageStyle = { opacity: 0 };
  }

  return (
    <div className={styles.fixedContainer} style={style}>
       <div 
         className={styles.imageLayer}
         style={imageStyle}
       />
       <div className={styles.overlay} />
    </div>
  );
}
