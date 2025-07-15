export interface TranscriptEntry {
  speaker: string;
  text: string;
  start?: number; // optional timestamp start
  end?: number;   // optional timestamp end
}

export interface TranscriptionResponse {
  transcript: TranscriptEntry[];              // Final transcript (translated if applicable)
  original_transcript?: TranscriptEntry[];    // Original language transcript (e.g., Georgian)
  filename: string;                           // Stored filename (translated or original)
  translated_filename?: string;               // If translated, filename of translated file
  language: string;                           // Language detected or selected (e.g., 'en', 'ka')
  word_count: number;                         // Total word count
  speaker_count: number;                      // Number of unique speakers
  error?: string;                             // Error message (if any)
}

export interface LanguageOption {
  code: string;        // e.g., 'en', 'ka', 'auto'
  name: string;        // e.g., 'English', 'Georgian'
  nativeName?: string; // e.g., 'ქართული'
}
