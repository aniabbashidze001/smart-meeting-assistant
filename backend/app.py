import json
import logging
import os
import re
from datetime import datetime

import requests
from deep_translator import GoogleTranslator, single_detection
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from backend.generate_summary import generate_summary
from backend.semantic.index_transcripts import append_single_embedding
from backend.semantic.search_query import semantic_answer
from backend.transcribe import transcribe_audio
from backend.visuals.generate_visual import generate_visual_image

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

for directory in ["data", "temp", "visuals/generated", "static_data"]:
    os.makedirs(directory, exist_ok=True)


def is_georgian_file(filename: str) -> bool:
    """Check if the filename indicates a Georgian transcript file."""
    return filename.endswith(".json") and "_ge_" in filename


def translate_text(text: str, dest="en") -> str:
    """Translate text to the specified language using Google Translator."""
    try:
        translated_text = GoogleTranslator(source="auto", target=dest).translate(text)
        return translated_text
    except Exception as e:
        logger.error(f"Translation error: {e}")
        return text


@app.route("/api/transcribe", methods=["POST"])
def transcribe():
    """Handle audio file upload, transcribe using AssemblyAI, auto-translate Georgian audio, and trigger post-processing."""
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400

        language = request.form.get("language", "auto")
        language_map = {"English": "en", "Georgian": "ka", "Auto": "auto"}
        api_language = language_map.get(language, "auto")

        allowed_extensions = {".mp3", ".wav", ".m4a", ".flac", ".ogg"}
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            return jsonify({"error": f"Unsupported file type: {file_ext}"}), 400

        logger.info(f"Transcribing file: {file.filename} (Language: {language})")

        result = transcribe_audio()
        result_data = result if isinstance(result, dict) else result.get_json()

        if not result_data.get("filename"):
            raise Exception("Missing filename in transcription result.")

        original_filename = result_data["filename"]

        if result_data.get("language") == "ka" or api_language == "ka":
            try:
                transcript_text = " ".join(
                    [
                        entry.get("text", "")
                        for entry in result_data.get("transcript", [])
                    ]
                )
                translated_text = translate_text(transcript_text)
                result_data["translated_text"] = translated_text
                result_data["auto_translated"] = True

                translated_filename = original_filename.replace("_ge_", "_en_")
                translated_path = os.path.join("data", translated_filename)

                with open(translated_path, "w", encoding="utf-8") as f:
                    json.dump(
                        {
                            "transcript": [{"text": translated_text}],
                            "original_language": "ka",
                            "translated_from": original_filename,
                        },
                        f,
                        ensure_ascii=False,
                        indent=2,
                    )

                result_data["translated_filename"] = translated_filename

                requests.post(
                    "http://localhost:5050/api/summary",
                    json={"filename": translated_filename},
                )
                append_single_embedding(translated_filename)

            except Exception as e:
                logger.warning(f"Translation failed: {e}")
                result_data["auto_translated"] = False
                result_data["translation_error"] = str(e)

        else:
            try:
                requests.post(
                    "http://localhost:5050/api/summary",
                    json={"filename": original_filename},
                )
                append_single_embedding(original_filename)
            except Exception as e:
                logger.warning(f"Post-processing failed: {e}")

        return jsonify(result_data)

    except Exception as e:
        logger.error(f"Transcription error: {e}")
        return jsonify({"error": f"Transcription failed: {str(e)}"}), 500


@app.route("/api/georgian-files", methods=["GET"])
def get_georgian_files():
    """List all Georgian transcript files that do not have English translations."""
    try:
        files = []
        for filename in os.listdir("data"):
            if is_georgian_file(filename):
                translated = filename.replace("_ge_", "_en_")
                if not os.path.exists(os.path.join("data", translated)):
                    files.append(filename)
        return jsonify(files)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/translate-georgian", methods=["POST"])
def translate_georgian_files():
    """Translate all Georgian transcript files to English and save them."""
    try:
        data_dir = "data"
        georgian_files = [f for f in os.listdir(data_dir) if is_georgian_file(f)]

        if not georgian_files:
            return jsonify({"message": "No Georgian files found to translate"}), 200

        def generate():
            """Generator to yield translation progress."""
            for idx, filename in enumerate(georgian_files, 1):
                try:
                    path = os.path.join(data_dir, filename)
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)

                    combined = " ".join(
                        [entry.get("text", "") for entry in data.get("transcript", [])]
                    )
                    translated = translate_text(combined)

                    translated_filename = filename.replace("_ge_", "_en_")
                    translated_path = os.path.join(data_dir, translated_filename)

                    with open(translated_path, "w", encoding="utf-8") as f:
                        json.dump(
                            {
                                "transcript": [{"text": translated}],
                                "original_language": "ka",
                                "translated_from": filename,
                            },
                            f,
                            ensure_ascii=False,
                            indent=2,
                        )

                    append_single_embedding(translated_filename)

                    yield json.dumps(
                        {
                            "progress": round((idx / len(georgian_files)) * 100, 2),
                            "status": f"Translated {filename}",
                        }
                    ) + "\n"

                except Exception as e:
                    logger.error(f"Failed to translate {filename}: {e}")
                    yield json.dumps(
                        {"status": f"Error translating {filename}: {str(e)}"}
                    ) + "\n"

        return app.response_class(generate(), mimetype="text/event-stream")

    except Exception as e:
        logger.error(f"Translation error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/summary", methods=["GET", "POST"])
def summary():
    """Generate a summary for the latest transcript file."""
    return generate_summary()


@app.route("/api/semantic-search", methods=["POST"])
def semantic_search():
    """Handle semantic search queries."""
    try:
        data = request.get_json()
        query = data.get("query", "")

        if not query or len(query.strip()) < 3:
            return jsonify({"error": "Invalid query"}), 400

        try:
            detected_lang = single_detection(query, api_key=None)
            if detected_lang == "ka":
                query = translate_text(query)
        except Exception as e:
            logger.warning(f"Language detection failed: {e}")

        result = semantic_answer(query)
        return jsonify(result)

    except Exception as e:
        logger.error(f"Search error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/transcripts", methods=["GET"])
def get_transcripts():
    """List all transcripts with metadata."""
    try:
        transcripts = []
        for filename in os.listdir("data"):
            if filename.endswith(".json") and not filename.endswith("_summary.json"):
                path = os.path.join("data", filename)
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                stat = os.stat(path)

                is_ge = "_ge_" in filename
                translated_filename = (
                    filename.replace("_ge_", "_en_") if is_ge else None
                )
                has_translation = translated_filename and os.path.exists(
                    os.path.join("data", translated_filename)
                )

                transcripts.append(
                    {
                        "filename": filename,
                        "language": "Georgian" if is_ge else "English",
                        "translated_filename": (
                            translated_filename if has_translation else None
                        ),
                        "has_translation": has_translation,
                        "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        "file_size": stat.st_size,
                        "word_count": sum(
                            len(entry.get("text", "").split())
                            for entry in data.get("transcript", [])
                        ),
                        "speaker_count": len(
                            set(
                                entry.get("speaker", "")
                                for entry in data.get("transcript", [])
                            )
                        ),
                    }
                )

        transcripts.sort(key=lambda x: x["created_at"], reverse=True)
        return jsonify(
            {
                "transcripts": transcripts,
                "total": len(transcripts),
                "georgian_count": len(
                    [t for t in transcripts if t["language"] == "Georgian"]
                ),
                "english_count": len(
                    [t for t in transcripts if t["language"] == "English"]
                ),
            }
        )

    except Exception as e:
        logger.error(f"Transcript listing failed: {e}")
        return jsonify({"error": str(e)}), 500


def extract_key_info_for_visual(summary_content):
    """Extract structured information from summary for visual generation"""
    content_lower = summary_content.lower()

    key_info = {
        "has_decisions": any(
            word in content_lower
            for word in [
                "decision",
                "decided",
                "approved",
                "agreed",
                "resolution",
                "concluded",
            ]
        ),
        "has_actions": any(
            word in content_lower
            for word in [
                "action",
                "to-do",
                "task",
                "follow-up",
                "assigned",
                "responsible",
                "deadline",
            ]
        ),
        "has_financial": any(
            word in content_lower
            for word in [
                "budget",
                "cost",
                "revenue",
                "profit",
                "expense",
                "financial",
                "$",
                "gel",
            ]
        ),
        "has_technical": any(
            word in content_lower
            for word in [
                "technical",
                "development",
                "software",
                "system",
                "code",
                "api",
                "database",
            ]
        ),
        "has_strategic": any(
            word in content_lower
            for word in [
                "strategy",
                "strategic",
                "roadmap",
                "planning",
                "goals",
                "objectives",
            ]
        ),
        "metrics": re.findall(
            r"\d+%|\$\d[\d,]*|\d+\s+(?:gel|students|volunteers|attendees|people|sessions|weeks|days|hours|items|projects|plans|reports|percent)",
            summary_content,
            flags=re.IGNORECASE,
        )[:5],
        "dates": re.findall(
            r"\d{4}-\d{2}-\d{2}|\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\b(?:January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, \d{4}",
            summary_content,
        )[:3],
        "participant_count": len(
            set(
                re.findall(
                    r"\b(?:assigned to|responsible for|will handle|should complete|[A-Z][a-z]+ will)\b",
                    summary_content,
                    flags=re.IGNORECASE,
                )
            )
        ),
        "topics": list(
            set(
                re.findall(
                    r"\b(strategy|budget|timeline|hiring|product|report|review|deadline|client|attendance|student|initiative|session|marketing|sales|development|training)\b",
                    content_lower,
                )
            )
        )[:6],
        "priority_level": (
            "high"
            if any(
                word in content_lower
                for word in [
                    "urgent",
                    "critical",
                    "important",
                    "priority",
                    "asap",
                    "immediately",
                ]
            )
            else "normal"
        ),
        "meeting_type": (
            "strategic"
            if any(
                word in content_lower for word in ["strategy", "planning", "roadmap"]
            )
            else (
                "operational"
                if any(
                    word in content_lower
                    for word in ["daily", "weekly", "status", "update"]
                )
                else "general"
            )
        ),
    }

    return key_info


@app.route("/api/visual-summary", methods=["POST"])
def generate_visual_summary():
    """Generate 3 visual summaries using DALL-E 3"""
    logger.info("Visual summary endpoint called")

    try:
        summary_dir = "backend/data"
        if not os.path.exists(summary_dir):
            return jsonify({"error": "Summary directory not found"}), 404

        summary_files = [
            f
            for f in os.listdir(summary_dir)
            if f.startswith("summary_") and f.endswith(".txt")
        ]
        if not summary_files:
            return jsonify({"error": "No summaries found"}), 404

        latest_file = max(
            summary_files, key=lambda x: os.path.getctime(os.path.join(summary_dir, x))
        )
        summary_path = os.path.join(summary_dir, latest_file)

        with open(summary_path, "r", encoding="utf-8") as f:
            summary_content = f.read()

        key_info = extract_key_info_for_visual(summary_content)
        logger.info(f"Extracted key info: {key_info}")

        metrics_str = ", ".join(key_info["metrics"]) or "No specific metrics"
        dates_str = ", ".join(key_info["dates"]) or "No specific dates"
        topics_str = ", ".join(key_info["topics"]) or "General business topics"

        if key_info["has_financial"]:
            visual_theme = "financial dashboard"
            color_scheme = "blue and green with gold accents"
        elif key_info["has_technical"]:
            visual_theme = "technical system diagram"
            color_scheme = "blue and purple with modern tech aesthetics"
        elif key_info["has_strategic"]:
            visual_theme = "strategic roadmap"
            color_scheme = "professional blues and grays"
        else:
            visual_theme = "business meeting summary"
            color_scheme = "corporate blue and green"

        visual_prompts = {
            "executive": f"""Create a professional executive dashboard visual representing a business meeting summary.

STYLE: Clean, modern, C-suite appropriate {visual_theme}
ELEMENTS:
- Title: "Executive Meeting Summary"
- Key metrics prominently displayed: {metrics_str}
- Important dates: {dates_str}
- Focus areas: {topics_str}
- Priority level: {key_info['priority_level']}
- Meeting type: {key_info['meeting_type']}

DESIGN: Use {color_scheme}, professional icons, clean typography, dashboard layout
MOOD: Professional, confident, results-oriented

AVOID: Cluttered design, too much text, unprofessional elements""",
            "stakeholder": f"""Design a stakeholder presentation slide for meeting outcomes.

STYLE: Professional presentation slide with clear hierarchy
ELEMENTS:
- Title: "Meeting Outcomes & Next Steps"
- Decision indicators: {"✓ Decisions Made" if key_info['has_decisions'] else "Discussion Points"}
- Action items: {"✓ Action Items Assigned" if key_info['has_actions'] else "Follow-up Items"}
- Key topics: {topics_str}
- Timeline elements: {dates_str}

DESIGN: Modern slide layout, {color_scheme}, professional icons
PURPOSE: Brief stakeholders who couldn't attend

CONTEXT: {summary_content[:500]}...""",
            "action_board": f"""Create a task management board visualization for meeting action items.

STYLE: Kanban-style task board with visual clarity
ELEMENTS:
- Title: "Action Items Dashboard"
- Task categories based on: {topics_str}
- Priority indicators: {key_info['priority_level']} priority items
- Timeline markers: {dates_str}
- Progress visualization
- Team assignment indicators

DESIGN: Modern task board aesthetic, {color_scheme}, clear visual hierarchy
PURPOSE: Track and manage meeting follow-ups""",
        }

        results = {}
        for visual_type, prompt in visual_prompts.items():
            try:
                logger.info(f"Generating {visual_type} visual...")
                image_url = generate_visual_image(prompt)
                if image_url:
                    results[visual_type] = {
                        "url": image_url,
                        "title": f"{visual_type.replace('_', ' ').title()} Summary",
                        "description": f"AI-generated {visual_type} visual for meeting stakeholders",
                        "theme": visual_theme,
                        "color_scheme": color_scheme,
                    }
                    logger.info(f"Successfully generated {visual_type} visual")
                else:
                    logger.warning(f"Failed to generate {visual_type} visual")
            except Exception as e:
                logger.error(f"Error generating {visual_type} visual: {e}")
                continue

        if not results:
            return jsonify({"error": "No visuals were generated successfully"}), 500

        logger.info(f"Generated {len(results)} visual(s) successfully")

        return jsonify(
            {
                "status": "success",
                "visuals": results,
                "source_file": latest_file,
                "key_info": key_info,
                "summary_length": len(summary_content),
                "generated_count": len(results),
            }
        )

    except Exception as e:
        logger.error(f"Visual generation error: {e}")
        import traceback

        traceback.print_exc()
        return jsonify({"error": f"Visual generation failed: {str(e)}"}), 500


@app.route("/api/calendar", methods=["GET"])
def get_calendar_events():
    """Fetch calendar events from JSON file"""
    try:
        events_file = os.path.join("backend/static_data", "calendar_events.json")
        if not os.path.exists(events_file):
            default_events = [
                {
                    "id": 1,
                    "title": "Weekly Team Meeting",
                    "date": "2024-01-15",
                    "time": "10:00 AM",
                    "duration": "1 hour",
                    "attendees": ["Team Lead", "Developers", "PM"],
                }
            ]
            os.makedirs(os.path.dirname(events_file), exist_ok=True)
            with open(events_file, "w", encoding="utf-8") as f:
                json.dump(default_events, f, indent=2)
            return jsonify(default_events)

        with open(events_file, "r", encoding="utf-8") as f:
            events = json.load(f)
        return jsonify(events)

    except Exception as e:
        logger.error(f"Calendar events error: {e}")
        return jsonify([])


@app.route("/data/calendar_events.json")
def serve_calendar_json():
    """Serve calendar events JSON file"""
    return send_from_directory("static_data", "calendar_events.json")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    debug = os.environ.get("FLASK_DEBUG", "True").lower() == "true"
    logger.info(f"🚀 Starting Smart Meeting Assistant on port {port}")
    app.run(host="0.0.0.0", port=port, debug=debug)
