
export interface VisualKeyframe {
  startVerse: number;
  endVerse: number;
  focus: {
    x: number; // Percentage 0-100
    y: number; // Percentage 0-100
    scale: number; // Zoom level (1.0 = fit, 2.0 = 2x zoom)
  };
  transitionDuration: number; // seconds
}

export interface BookVisualMapping {
  bookId: string;
  imageUrl: string;
  color: string;
  keyframes: VisualKeyframe[];
  orientation: 'landscape' | 'portrait';
}

export const DEFAULT_MAPPING: BookVisualMapping = {
    bookId: "DEFAULT",
    imageUrl: "",
    color: "#0f172a",
    keyframes: [{ startVerse: 1, endVerse: 999, focus: { x: 50, y: 50, scale: 1 }, transitionDuration: 0 }],
    orientation: 'landscape'
};

export async function getVisualMapping(bookId: string): Promise<BookVisualMapping | null> {
    try {
        const data = await import(`@/data/visuals/maps/${bookId}.json`);
        return data.default || data;
    } catch {
        return null;
    }
}
