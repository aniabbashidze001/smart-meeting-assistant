import json
import os
import re
import time

from dotenv import load_dotenv
from flask import jsonify, request
from openai import OpenAI

from backend.calendar_utils import add_calendar_event
from backend.config import DATA_DIR

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def load_transcript_safely(filepath, max_attempts=10, wait_time=2):
    """Safely load a transcript JSON file with retry logic. Supports both utterances and transcript formats."""
    for attempt in range(1, max_attempts + 1):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            if isinstance(data, dict):
                if "utterances" in data:
                    print(f"✅ Loaded transcript from 'utterances' (Attempt {attempt})")
                    return data["utterances"], data.get("language", "en")
                elif "transcript" in data:
                    print(f"✅ Loaded transcript from 'transcript' (Attempt {attempt})")
                    return data["transcript"], data.get("language", "en")

            if isinstance(data, list):
                print(f"✅ Loaded transcript from raw list (Attempt {attempt})")
                return data, "en"

            time.sleep(wait_time)

        except Exception as e:
            print(f"⏳ Attempt {attempt}: JSON error ({e}), retrying...")
            time.sleep(wait_time)

    print(f"❌ File not ready after {max_attempts} attempts")
    return None, None


def generate_summary():
    """Generate a structured meeting summary and action items using GPT-4. Supports function calling for adding calendar events."""
    try:
        if request.method == "GET":
            filename = request.args.get("filename")
        elif request.method == "POST":
            data = request.get_json()
            filename = data.get("filename")
        else:
            return jsonify({"error": "Unsupported method"}), 405

        if not filename:
            return jsonify({"error": "Filename not provided"}), 400

        filepath = os.path.join(DATA_DIR, filename)
        if not os.path.exists(filepath):
            return jsonify({"error": "Transcript file not found"}), 404

        summary_filename = f"summary_{filename.replace('.json', '.txt')}"
        summary_path = os.path.join(DATA_DIR, summary_filename)
        if os.path.exists(summary_path):
            with open(summary_path, "r", encoding="utf-8") as f:
                saved_summary = f.read()
            return jsonify(
                {
                    "summary": saved_summary,
                    "summary_file": summary_filename,
                    "cached": True,
                }
            )

        utterances, original_language = load_transcript_safely(filepath)
        if not utterances:
            return jsonify({"error": "Transcript could not be loaded."}), 500

        speaker_text = "\n".join([f"{u['speaker']}: {u['text']}" for u in utterances])

        note = ""
        if original_language != "en":
            note = f"(Note: Transcript was originally in {original_language.upper()} and translated to English)\n\n"

        system_prompt = (
            note
            + "You're an expert meeting assistant. Given the diarized transcript, generate:\n"
            "1. A concise meeting summary (3–5 sentences).\n"
            "2. A list of clear action items.\n"
            "3. Assign an owner (speaker) to each action if possible.\n"
            "4. Suggest a realistic future or past date (not a placeholder) for each action using the format YYYY-MM-DD.\n"
            '5. If needed, call: functions.add_calendar_event({"title":..., "date":...})'
        )

        functions = [
            {
                "name": "add_calendar_event",
                "description": "Add a task or meeting to the calendar",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "date": {"type": "string", "format": "date"},
                    },
                    "required": ["title", "date"],
                },
            }
        ]

        response = client.chat.completions.create(
            model="gpt-4-0613",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": speaker_text},
            ],
            functions=functions,
            function_call="auto",
        )

        choice = response.choices[0]
        summary_text = choice.message.content or "No summary generated."

        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(summary_text)

        if (
            choice.message.function_call
            and choice.message.function_call.name == "add_calendar_event"
        ):
            try:
                args = json.loads(choice.message.function_call.arguments)
                add_calendar_event(args["title"], args["date"])
            except Exception as calendar_error:
                print("⚠️ Structured function call failed:", calendar_error)

        pattern = r"functions\.add_calendar_event\(\s*(\{.*?\})\s*\)"
        matches = re.findall(pattern, summary_text)
        for match in matches:
            try:
                args = json.loads(match)
                add_calendar_event(args["title"], args["date"])
            except Exception as e:
                print("⚠️ Simulated function call failed:", e)

        return jsonify({"summary": summary_text, "summary_file": summary_filename})

    except Exception as e:
        print("❌ Summary generation error:", e)
        return jsonify({"error": str(e)}), 500
