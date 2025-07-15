from typing import Any, Dict

from deep_translator import GoogleTranslator


class TranslationService:
    """
    Service class for handling translation of meeting transcripts to English.

    Methods:
        - translate_to_english(text, source_lang): Translate a single text segment to English.
        - translate_transcript(transcript_data): Translate a full speaker-separated transcript to English,
          preserving structure.

    Uses:
        - GoogleTranslator from deep_translator for machine translation.
    """

    def __init__(self):
        pass

    def translate_to_english(self, text: str, source_lang: str) -> str:
        """Translate a single text segment to English."""
        try:
            if source_lang == "en":
                return text
            return GoogleTranslator(source=source_lang, target="en").translate(text)
        except Exception as e:
            raise Exception(f"Translation failed for text: '{text[:30]}...': {str(e)}")

    def translate_transcript(self, transcript_data: Dict[str, Any]) -> Dict[str, Any]:
        """Translate a full speaker-separated transcript to English."""
        lang = transcript_data.get("language", "en")

        if lang == "en":
            return {**transcript_data, "original_language": "en"}

        translated_output = []
        for entry in transcript_data.get("transcript", []):
            try:
                translated_text = self.translate_to_english(entry.get("text", ""), lang)
                translated_output.append({**entry, "text": translated_text})
            except Exception as e:
                translated_output.append(
                    {**entry, "text": f"[Translation failed] {entry.get('text', '')}"}
                )

        return {
            **transcript_data,
            "transcript": translated_output,
            "original_language": lang,
            "language": "en",
        }
