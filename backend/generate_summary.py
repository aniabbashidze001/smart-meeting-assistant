import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from flask import request, jsonify
from calendar_utils import add_calendar_event
import re

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_summary():
    try:
        if request.method == "GET":
            filename = request.args.get("filename")
        elif request.method == "POST":
            data = request.get_json()
            filename = data.get("filename")
        else:
            return jsonify({ "error": "Unsupported method" }), 405

        if not filename:
            return jsonify({ "error": "Filename not provided" }), 400

        filepath = os.path.join("data", filename)
        if not os.path.exists(filepath):
            return jsonify({ "error": "Transcript file not found" }), 404

        # ✅ Cached summary check
        summary_filename = f"summary_{filename.replace('.json', '.txt')}"
        summary_path = os.path.join("data", summary_filename)
        if os.path.exists(summary_path):
            with open(summary_path, "r", encoding="utf-8") as f:
                saved_summary = f.read()
            return jsonify({
                "summary": saved_summary,
                "summary_file": summary_filename,
                "cached": True
            })

        with open(filepath, "r", encoding="utf-8") as f:
            transcript = json.load(f)

        speaker_text = "\n".join([f"{u['speaker']}: {u['text']}" for u in transcript])

        system_prompt = (
            "You're an expert meeting assistant. Given the diarized transcript, "
            "generate:\n1. A concise meeting summary (3–5 sentences).\n"
            "2. A list of clear action items.\n"
            "3. Assign an owner (speaker) to each action if possible.\n"
            "4. Suggest a realistic future or past date (not a placeholder) for each action using the format YYYY-MM-DD.\n"
            "5. If needed, call: functions.add_calendar_event({\"title\":..., \"date\":...})"
        )

        functions = [
            {
                "name": "add_calendar_event",
                "description": "Add a task or meeting to the calendar",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": { "type": "string" },
                        "date": { "type": "string", "format": "date" }
                    },
                    "required": ["title", "date"]
                }
            }
        ]

        response = client.chat.completions.create(
            model="gpt-4-0613",
            messages=[
                { "role": "system", "content": system_prompt },
                { "role": "user", "content": speaker_text }
            ],
            functions=functions,
            function_call="auto"
        )

        choice = response.choices[0]
        summary_text = choice.message.content or "No summary generated."

        # ✅ Save summary
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(summary_text)

        # ✅ Handle structured function call (one event)
        function_call = choice.message.function_call
        if function_call and function_call.name == "add_calendar_event":
            try:
                args = json.loads(function_call.arguments)
                add_calendar_event(args["title"], args["date"])
            except Exception as calendar_error:
                print("⚠️ Structured function call failed:", calendar_error)

        # ✅ Handle text-based fake function calls (multiple events)
        pattern = r'functions\.add_calendar_event\(\s*(\{.*?\})\s*\)'
        matches = re.findall(pattern, summary_text)
        for match in matches:
            try:
                args = json.loads(match)
                add_calendar_event(args["title"], args["date"])
            except Exception as e:
                print("⚠️ Simulated function call failed:", e)

        return jsonify({
            "summary": summary_text,
            "summary_file": summary_filename
        })

    except Exception as e:
        print("❌ Summary generation error:", e)
        return jsonify({ "error": str(e) }), 500
