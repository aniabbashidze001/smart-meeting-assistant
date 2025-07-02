# transcribe.py

import os
import json
from datetime import datetime
import assemblyai as aai
from flask import request, jsonify
from dotenv import load_dotenv
import requests
from semantic.index_transcripts import append_single_embedding

load_dotenv()

aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")


def transcribe_audio():
    try:
        file = request.files['file']
        filename = file.filename
        file_path = os.path.join("temp", filename)
        os.makedirs("temp", exist_ok=True)
        file.save(file_path)

        # ✅ Enable language detection + speaker diarization
        config = aai.TranscriptionConfig(
            speech_model=aai.SpeechModel.best,
            speaker_labels=True,
            language_detection=True
        )

        transcriber = aai.Transcriber(config=config)
        transcript = transcriber.transcribe(file_path)

        # ✅ Check if transcription was successful
        if transcript.status == aai.TranscriptStatus.error:
            return jsonify({"error": f"Transcription failed: {transcript.error}"}), 500

        # ✅ Properly access detected language with fallback
        detected_lang = getattr(transcript, 'language_code', 'en') or 'en'
        is_georgian = detected_lang == "ka"

        # 🎙️ Format speaker output with null checks
        speaker_output = []

        # Check if utterances exist and is not None
        if hasattr(transcript, 'utterances') and transcript.utterances is not None:
            speaker_output = [
                {
                    "speaker": utterance.speaker,
                    "text": utterance.text,
                    "start": utterance.start,
                    "end": utterance.end
                }
                for utterance in transcript.utterances
            ]
        else:
            # Fallback: use the main transcript text without speaker separation
            print("⚠️ No speaker utterances found, using full transcript")
            speaker_output = [
                {
                    "speaker": "Speaker A",
                    "text": transcript.text or "",
                    "start": 0,
                    "end": 0
                }
            ]

        # Additional validation
        if not speaker_output or not any(entry.get("text", "").strip() for entry in speaker_output):
            return jsonify({"error": "No transcribable content found in audio"}), 400

        # 💾 Save transcript to /backend/data/
        save_dir = os.path.join("data")
        os.makedirs(save_dir, exist_ok=True)

        base_name = os.path.splitext(filename)[0]
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        lang_suffix = "ge" if is_georgian else "en"
        output_filename = f"{base_name}_{lang_suffix}_{timestamp}.json"
        json_path = os.path.join(save_dir, output_filename)

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(speaker_output, f, indent=2, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())

        import time
        time.sleep(0.2)

        # 🔁 Conditional post-processing
        if is_georgian:
            print(f"🌍 Detected Georgian language — saved as {output_filename}")
            print("🚫 Skipping summary and embedding for now. Will handle after translation.")

            # Optional: Trigger translation immediately
            try:
                from translate_georgian import translate_georgian_transcript
                translated_filename = translate_georgian_transcript(output_filename)
                print(f"🔄 Auto-translated to: {translated_filename}")
            except Exception as translation_error:
                print(f"⚠️ Auto-translation failed: {translation_error}")

        else:
            # ✨ Trigger summary generation
            try:
                summary_res = requests.post("http://localhost:5050/api/summary", json={"filename": output_filename})
                summary_res.raise_for_status()
                print(f"📝 Summary generated for {output_filename}")
            except Exception as summary_error:
                print("⚠️ Failed to generate summary:", summary_error)

            # 🧠 Trigger semantic embedding
            try:
                if os.path.exists(json_path) and os.path.getsize(json_path) > 0:
                    append_single_embedding(output_filename)
                    print(f"🔍 Embedding generated for {output_filename}")
                else:
                    print(f"⚠️ Cannot embed: File not ready or empty - {output_filename}")
            except Exception as embed_error:
                print(f"❌ Error embedding {output_filename}: {embed_error}")

        # Clean up temp file
        try:
            os.remove(file_path)
        except:
            pass

        # ✅ Return result
        return jsonify({
            "transcript": speaker_output,
            "filename": output_filename,
            "language": detected_lang,
            "word_count": sum(len(entry["text"].split()) for entry in speaker_output),
            "speaker_count": len(set(entry["speaker"] for entry in speaker_output))
        })

    except Exception as e:
        print(f"❌ Transcription error: {str(e)}")
        return jsonify({"error": f"Transcription failed: {str(e)}"}), 500