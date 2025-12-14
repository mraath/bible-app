export interface VisualKeyframe {
  startVerse: number;
  endVerse: number;
  focus: {
    x: number; // 0-100%
    y: number; // 0-100%
    scale: number; // 1.0 = fit, >1 = zoom
  };
  transitionDuration?: number; // seconds
}

export interface BookVisualMapping {
  bookId: string;
  imageUrl: string;
  color: string; // Dominant color
  keyframes: VisualKeyframe[];
}
