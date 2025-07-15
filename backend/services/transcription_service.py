import json
import os
from datetime import datetime
from typing import Any, Dict

import assemblyai as aai

from ..config import ASSEMBLYAI_API_KEY, ASSEMBLYAI_CONFIG, DATA_DIR
from ..semantic.index_transcripts import append_single_embedding


class TranscriptionService:
    """
        A service for handling audio transcription and saving transcript data.

        This class integrates with AssemblyAI to transcribe audio files and provides
        functionality to save the resulting transcript data to a file. It also supports
        embedding logic for English or translated transcripts.

        Methods:
            - __init__: Initializes the service with the AssemblyAI API key.
            - transcribe: Transcribes an audio file and returns structured transcript data.
            - save_transcript: Saves transcript data to a JSON file and triggers embedding logic.
    """
    def __init__(self):
        aai.settings.api_key = ASSEMBLYAI_API_KEY

    def transcribe(self, file_path: str, language: str = "en") -> Dict[str, Any]:
        """
           Transcribe an audio file using AssemblyAI and return a structured transcript.

           Args:
               file_path (str): Absolute path to the audio file to be transcribed.
               language (str, optional): Language code for transcription
                   (default is 'en'; 'ka' disables speaker labels).

           Returns:
               Dict[str, Any]: A dictionary containing:
                   - 'transcript' (List[Dict[str, Any]]): List of utterances with speaker, text, start, end.
                   - 'language' (str): Detected or specified language code.
                   - 'duration' (float or None): Duration of the audio in seconds.

           Raises:
               Exception: If AssemblyAI returns an error or transcription fails.
        """
        try:
            use_speaker_labels = (
                ASSEMBLYAI_CONFIG["speaker_labels"] if language != "ka" else False
            )

            config = aai.TranscriptionConfig(
                speech_model=ASSEMBLYAI_CONFIG["model"],
                speaker_labels=use_speaker_labels,
                language_code=language,
                language_detection=False,
            )

            transcriber = aai.Transcriber(config=config)
            transcript = transcriber.transcribe(file_path)

            if transcript.status == aai.TranscriptStatus.error:
                raise Exception(transcript.error)

            speaker_output = []
            if hasattr(transcript, "utterances") and transcript.utterances:
                for utterance in transcript.utterances:
                    speaker_output.append(
                        {
                            "speaker": utterance.speaker,
                            "text": utterance.text,
                            "start": utterance.start,
                            "end": utterance.end,
                        }
                    )
            else:
                speaker_output.append(
                    {
                        "speaker": "Speaker A",
                        "text": transcript.text or "",
                        "start": 0,
                        "end": 0,
                    }
                )

            return {
                "transcript": speaker_output,
                "language": getattr(transcript, "language_code", "en"),
                "duration": getattr(transcript, "audio_duration", None),
            }

        except Exception as e:
            raise Exception(f"AssemblyAI transcription failed: {str(e)}")

    def save_transcript(self, transcript_data: Dict[str, Any], filename: str) -> str:
        """
        Save the transcript data as a JSON file and trigger embedding generation if applicable.

        Args:
            transcript_data (dict): Transcript data, including language and transcript content.
            filename (str): Original filename of the uploaded audio file.

        Returns:
            str: Name of the saved transcript JSON file.
        """
        try:
            os.makedirs(DATA_DIR, exist_ok=True)

            base_name = os.path.splitext(filename)[0]
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            lang_suffix = "ge" if transcript_data["language"] == "ka" else "en"
            output_filename = f"{base_name}_{lang_suffix}_{timestamp}.json"

            output_path = os.path.abspath(os.path.join(DATA_DIR, output_filename))

            print(f"💾 Saving transcript to: {output_path}")

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(transcript_data, f, indent=2, ensure_ascii=False)
                f.flush()
                os.fsync(f.fileno())

            if os.path.exists(output_path):
                print(f"✅ Transcript saved successfully at: {output_path}")
            else:
                raise Exception(
                    "❌ Transcript file save failed: File not found after writing."
                )

            is_translated = transcript_data.get("translated", False)
            language_code = transcript_data.get("language", "en")

            if language_code == "en" or is_translated:
                print(f"🧠 Triggering embedding for: {output_filename}")
                append_single_embedding(output_filename)
            else:
                print(
                    f"🌍 Skipping embedding for untranslated non-English file: {output_filename}"
                )

            return output_filename

        except Exception as e:
            raise Exception(f"Failed to save transcript: {str(e)}")
