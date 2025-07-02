# app.py - Complete Smart Meeting Assistant with Georgian Language Support

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from transcribe import transcribe_audio
from generate_summary import generate_summary
from semantic.search_query import semantic_answer
from visuals.generate_visual import generate_visual_image
from translate_georgian import translate_georgian_transcript, is_georgian_file
import re
import os
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Ensure required directories exist
for directory in ["data", "temp", "visuals/generated", "static_data"]:
    os.makedirs(directory, exist_ok=True)


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "features": ["transcription", "summary", "search", "visuals", "georgian_translation"]
    })


@app.route("/api/transcribe", methods=["POST"])
def transcribe():
    """Enhanced transcription endpoint with Georgian language support"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400

        # Validate file type and size
        allowed_extensions = {'.mp3', '.wav', '.m4a', '.flac', '.ogg'}
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            return jsonify({"error": f"Unsupported file type: {file_ext}"}), 400

        logger.info(f"Processing audio file: {file.filename}")
        result = transcribe_audio()

        # If it's a Georgian file, check if we should auto-translate
        if hasattr(result, 'get_json') and result.get_json():
            response_data = result.get_json()
            if response_data.get('language') == 'ka':  # Georgian
                filename = response_data.get('filename')
                logger.info(f"Georgian file detected: {filename}")

                # Try auto-translation
                try:
                    translated_filename = translate_georgian_transcript(filename)
                    if translated_filename:
                        response_data['translated_filename'] = translated_filename
                        response_data['auto_translated'] = True
                        logger.info(f"Auto-translated to: {translated_filename}")
                    else:
                        response_data['auto_translated'] = False
                except Exception as e:
                    logger.warning(f"Auto-translation failed: {e}")
                    response_data['auto_translated'] = False
                    response_data['translation_error'] = str(e)

                return jsonify(response_data)

        return result

    except Exception as e:
        logger.error(f"Transcription error: {str(e)}")
        return jsonify({"error": f"Transcription failed: {str(e)}"}), 500


@app.route("/api/summary", methods=["GET", "POST"])
def summary():
    """Generate meeting summary"""
    return generate_summary()


@app.route("/api/semantic-search", methods=["POST"])
def semantic_search():
    """Semantic search across all transcripts"""
    try:
        data = request.get_json()
        query = data.get("query", "")

        if not query:
            return jsonify({"error": "Missing query"}), 400

        if len(query.strip()) < 3:
            return jsonify({"error": "Query must be at least 3 characters"}), 400

        logger.info(f"Semantic search query: {query}")
        result = semantic_answer(query)
        return jsonify(result)

    except Exception as e:
        logger.error(f"Semantic search error: {str(e)}")
        return jsonify({"error": f"Search failed: {str(e)}"}), 500


@app.route("/api/translate", methods=["POST"])
def translate_georgian():
    """Translate Georgian transcript to English"""
    try:
        data = request.get_json()
        filename = data.get('filename')

        if not filename:
            return jsonify({"error": "Filename is required"}), 400

        if not is_georgian_file(filename):
            return jsonify({"error": "File is not a Georgian transcript"}), 400

        file_path = os.path.join("data", filename)
        if not os.path.exists(file_path):
            return jsonify({"error": "Georgian transcript file not found"}), 404

        logger.info(f"Translating Georgian file: {filename}")
        translated_filename = translate_georgian_transcript(filename)

        if translated_filename:
            return jsonify({
                "status": "success",
                "original_filename": filename,
                "translated_filename": translated_filename,
                "message": "Translation completed successfully"
            })
        else:
            return jsonify({"error": "Translation failed"}), 500

    except Exception as e:
        logger.error(f"Translation error: {str(e)}")
        return jsonify({"error": f"Translation service unavailable: {str(e)}"}), 500


@app.route("/api/batch-translate", methods=["POST"])
def batch_translate():
    """Translate all Georgian files"""
    try:
        georgian_files = [f for f in os.listdir("data") if is_georgian_file(f)]

        if not georgian_files:
            return jsonify({
                "message": "No Georgian files found to translate",
                "results": []
            })

        results = []
        for filename in georgian_files:
            try:
                translated_filename = translate_georgian_transcript(filename)
                results.append({
                    "original": filename,
                    "translated": translated_filename,
                    "status": "success"
                })
                logger.info(f"Translated: {filename} -> {translated_filename}")
            except Exception as e:
                results.append({
                    "original": filename,
                    "translated": None,
                    "status": "error",
                    "error": str(e)
                })
                logger.error(f"Failed to translate {filename}: {e}")

        successful = len([r for r in results if r["status"] == "success"])

        return jsonify({
            "message": f"Batch translation completed: {successful}/{len(results)} successful",
            "results": results,
            "total_processed": len(results),
            "successful_count": successful
        })

    except Exception as e:
        logger.error(f"Batch translation error: {str(e)}")
        return jsonify({"error": f"Batch translation failed: {str(e)}"}), 500


@app.route('/api/georgian-files', methods=['GET'])
def get_georgian_files():
    """Return list of Georgian transcript files that need translation"""
    try:
        data_dir = "data"
        if not os.path.exists(data_dir):
            return jsonify([])

        georgian_files = []
        for filename in os.listdir(data_dir):
            if filename.endswith('.json') and '_ge_' in filename:
                georgian_files.append(filename)

        return jsonify(georgian_files)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/translate-georgian', methods=['POST'])
def translate_georgian_files():
    """Trigger translation of all Georgian files"""
    try:
        from translate_georgian import main as translate_main

        # Call your existing translation script
        result = translate_main()

        return jsonify({
            "message": "Georgian files translated successfully and processed for summaries/embeddings",
            "result": result
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Enhanced extract function for better visual generation
def extract_key_info_for_visual(summary_content):
    """Extract structured information from summary for visual generation"""
    content_lower = summary_content.lower()

    key_info = {
        "has_decisions": any(word in content_lower for word in [
            "decision", "decided", "approved", "agreed", "resolution", "concluded"
        ]),
        "has_actions": any(word in content_lower for word in [
            "action", "to-do", "task", "follow-up", "assigned", "responsible", "deadline"
        ]),
        "has_financial": any(word in content_lower for word in [
            "budget", "cost", "revenue", "profit", "expense", "financial", "$", "gel"
        ]),
        "has_technical": any(word in content_lower for word in [
            "technical", "development", "software", "system", "code", "api", "database"
        ]),
        "has_strategic": any(word in content_lower for word in [
            "strategy", "strategic", "roadmap", "planning", "goals", "objectives"
        ]),
        "metrics": re.findall(
            r"\d+%|\$\d[\d,]*|\d+\s+(?:gel|students|volunteers|attendees|people|sessions|weeks|days|hours|items|projects|plans|reports|percent)",
            summary_content,
            flags=re.IGNORECASE
        )[:5],
        "dates": re.findall(
            r'\d{4}-\d{2}-\d{2}|\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\b(?:January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, \d{4}',
            summary_content
        )[:3],
        "participant_count": len(set(re.findall(
            r'\b(?:assigned to|responsible for|will handle|should complete|[A-Z][a-z]+ will)\b',
            summary_content,
            flags=re.IGNORECASE
        ))),
        "topics": list(set(re.findall(
            r'\b(strategy|budget|timeline|hiring|product|report|review|deadline|client|attendance|student|initiative|session|marketing|sales|development|training)\b',
            content_lower
        )))[:6],
        "priority_level": "high" if any(word in content_lower for word in [
            "urgent", "critical", "important", "priority", "asap", "immediately"
        ]) else "normal",
        "meeting_type": "strategic" if any(word in content_lower for word in [
            "strategy", "planning", "roadmap"
        ]) else "operational" if any(word in content_lower for word in [
            "daily", "weekly", "status", "update"
        ]) else "general"
    }

    return key_info


@app.route("/api/visual-summary", methods=["POST"])
def generate_visual_summary():
    """Generate visual summaries using DALL-E 3"""
    logger.info("Visual summary endpoint called")

    try:
        # Get the most recent summary
        summary_dir = "data"
        if not os.path.exists(summary_dir):
            return jsonify({"error": "Summary directory not found"}), 404

        summary_files = [f for f in os.listdir(summary_dir) if f.startswith("summary_") and f.endswith(".txt")]
        if not summary_files:
            return jsonify({"error": "No summaries found"}), 404

        latest_file = max(summary_files, key=lambda x: os.path.getctime(os.path.join(summary_dir, x)))
        summary_path = os.path.join(summary_dir, latest_file)

        with open(summary_path, "r", encoding="utf-8") as f:
            summary_content = f.read()

        # Extract structured information
        key_info = extract_key_info_for_visual(summary_content)
        logger.info(f"Extracted key info: {key_info}")

        # Format information for prompts
        metrics_str = ", ".join(key_info["metrics"]) or "No specific metrics"
        dates_str = ", ".join(key_info["dates"]) or "No specific dates"
        topics_str = ", ".join(key_info["topics"]) or "General business topics"

        # Determine visual style based on content
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

        # Create enhanced visual prompts
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
PURPOSE: Track and manage meeting follow-ups"""
        }

        # Generate visuals
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
                        "color_scheme": color_scheme
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

        return jsonify({
            "status": "success",
            "visuals": results,
            "source_file": latest_file,
            "key_info": key_info,
            "summary_length": len(summary_content),
            "generated_count": len(results)
        })

    except Exception as e:
        logger.error(f"Visual generation error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Visual generation failed: {str(e)}"}), 500


@app.route("/api/transcripts", methods=["GET"])
def get_transcripts():
    """Get list of all transcripts with metadata"""
    try:
        transcripts = []

        for filename in os.listdir("data"):
            if filename.endswith('.json') and not filename.endswith('_summary.json'):
                file_path = os.path.join("data", filename)

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    # Get file metadata
                    stat = os.stat(file_path)

                    # Determine language and translation status
                    is_georgian = '_ge_' in filename
                    language = 'Georgian' if is_georgian else 'English'

                    # Check for translated version if Georgian
                    has_translation = False
                    translated_filename = None
                    if is_georgian:
                        translated_name = filename.replace('_ge_', '_')
                        translated_path = os.path.join("data", translated_name)
                        has_translation = os.path.exists(translated_path)
                        if has_translation:
                            translated_filename = translated_name

                    # Check for summary
                    summary_path = os.path.join("data", filename.replace('.json', '_summary.json'))
                    has_summary = os.path.exists(summary_path)

                    transcripts.append({
                        "filename": filename,
                        "language": language,
                        "is_georgian": is_georgian,
                        "has_translation": has_translation,
                        "translated_filename": translated_filename,
                        "has_summary": has_summary,
                        "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        "file_size": stat.st_size,
                        "word_count": sum(len(entry.get("text", "").split()) for entry in data),
                        "speaker_count": len(set(entry.get("speaker", "") for entry in data))
                    })

                except Exception as e:
                    logger.warning(f"Error reading transcript {filename}: {e}")
                    continue

        # Sort by creation date (newest first)
        transcripts.sort(key=lambda x: x['created_at'], reverse=True)

        return jsonify({
            "transcripts": transcripts,
            "total": len(transcripts),
            "georgian_count": len([t for t in transcripts if t["is_georgian"]]),
            "english_count": len([t for t in transcripts if not t["is_georgian"]])
        })

    except Exception as e:
        logger.error(f"Error fetching transcripts: {e}")
        return jsonify({"error": "Failed to fetch transcripts"}), 500


@app.route("/api/calendar", methods=["GET"])
def get_calendar_events():
    """Get calendar events"""
    try:
        events_file = os.path.join("data", "calendar_events.json")
        if not os.path.exists(events_file):
            # Create default events file
            default_events = [
                {
                    "id": 1,
                    "title": "Weekly Team Meeting",
                    "date": "2024-01-15",
                    "time": "10:00 AM",
                    "duration": "1 hour",
                    "attendees": ["Team Lead", "Developers", "PM"]
                }
            ]
            with open(events_file, "w", encoding="utf-8") as f:
                json.dump(default_events, f, indent=2)
            return jsonify(default_events)

        with open(events_file, "r", encoding="utf-8") as f:
            events = json.load(f)
        return jsonify(events)

    except Exception as e:
        logger.error(f"Calendar events error: {e}")
        return jsonify([])  # Return empty array on error


@app.route("/data/calendar_events.json")
def serve_calendar_json():
    """Serve calendar events JSON file"""
    return send_from_directory("static_data", "calendar_events.json")


# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5050))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'

    logger.info(f"🚀 Starting Smart Meeting Assistant on port {port}")
    logger.info(f"🔧 Debug mode: {debug}")
    logger.info("📋 Available features:")
    logger.info("  - Audio transcription (English/Georgian)")
    logger.info("  - Automatic Georgian translation")
    logger.info("  - AI-powered summaries")
    logger.info("  - Semantic search")
    logger.info("  - Visual summary generation")
    logger.info("  - Calendar integration")

    app.run(host='0.0.0.0', port=port, debug=debug)