import os

import requests
from flask import jsonify, request

from backend.config import DATA_DIR, TEMP_DIR
from backend.services.transcription_service import TranscriptionService
from backend.services.translation_service import TranslationService

transcription_service = TranscriptionService()
translation_service = TranslationService()


def transcribe_audio():
    """Handle the /api/transcribe request: saves uploaded audio, performs transcription using AssemblyAI,
    triggers translation (if Georgian), generates summaries, and returns structured transcript data."""
    try:
        file = request.files["file"]
        language = request.form.get("language", "en")
        print(f"INFO: Transcribing file: {file.filename} (Language: {language})")

        os.makedirs(TEMP_DIR, exist_ok=True)
        file_path = os.path.join(TEMP_DIR, file.filename)
        file.save(file_path)

        transcript_data = transcription_service.transcribe(file_path, language)

        output_filename = transcription_service.save_transcript(
            transcript_data, file.filename
        )
        output_path = os.path.abspath(os.path.join(DATA_DIR, output_filename))

        if not os.path.exists(output_path):
            raise Exception(f"❌ Output JSON file missing after save: {output_path}")

        if transcript_data["language"] == "ka":
            translated_data = translation_service.translate_transcript(transcript_data)
            translated_filename = transcription_service.save_transcript(
                translated_data, file.filename.replace("_ge_", "_en_")
            )

            try:
                requests.post(
                    "http://localhost:5050/api/summary",
                    json={"filename": translated_filename},
                ).raise_for_status()
            except Exception as e:
                print(f"⚠️ Post-processing error (summary): {e}")

            response_data = {
                **translated_data,
                "original_filename": output_filename,
                "translated_filename": translated_filename,
            }

        else:
            try:
                requests.post(
                    "http://localhost:5050/api/summary",
                    json={"filename": output_filename},
                ).raise_for_status()
            except Exception as e:
                print(f"⚠️ Post-processing error (summary): {e}")

            response_data = {**transcript_data, "filename": output_filename}

        try:
            os.remove(file_path)
        except Exception as cleanup_error:
            print(f"⚠️ Temp cleanup failed: {cleanup_error}")

        return jsonify(response_data)

    except Exception as e:
        print(f"❌ Transcription error: {str(e)}")
        return jsonify({"error": f"Transcription failed: {str(e)}"}), 500
