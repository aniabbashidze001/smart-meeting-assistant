# translate_georgian.py

import os
import json
import re
import requests
from openai import OpenAI
from dotenv import load_dotenv
from semantic.index_transcripts import append_single_embedding

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

DATA_DIR = "data"

def is_georgian_file(filename):
    return "_ge_" in filename and filename.endswith(".json")

def translate_text(text):
    try:
        response = client.chat.completions.create(
            model="gpt-4",  # or "gpt-3.5-turbo"
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional translator. Translate the following Georgian text into English, preserving speaker meaning and tone, and returning only the English translation."
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ Translation failed: {e}")
        return None

def translate_georgian_transcript(filename):
    input_path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(input_path):
        print(f"❌ File not found: {input_path}")
        return None

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    translated = []
    for entry in data:
        translated_text = translate_text(entry["text"])
        if not translated_text:
            print(f"⚠️ Skipping entry at {entry['start']}ms due to translation error.")
            continue
        translated.append({
            "speaker": entry["speaker"],
            "text": translated_text,
            "start": entry["start"],
            "end": entry["end"]
        })

    # 🔄 Generate translated filename by removing `_ge_`
    translated_filename = re.sub(r"_ge_", "_", filename)
    output_path = os.path.join(DATA_DIR, translated_filename)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(translated, f, indent=2, ensure_ascii=False)

    print(f"✅ Translated file saved: {translated_filename}")

    # 🚀 Trigger summary generation
    try:
        res = requests.post("http://localhost:5050/api/summary", json={ "filename": translated_filename })
        res.raise_for_status()
        print(f"🧠 Summary generated for {translated_filename}")
    except Exception as e:
        print(f"⚠️ Failed to generate summary: {e}")

    # 🧠 Trigger semantic embedding
    try:
        append_single_embedding(translated_filename)
        print(f"🔍 Embedding generated for {translated_filename}")
    except Exception as e:
        print(f"❌ Failed to embed transcript: {e}")

    return translated_filename

if __name__ == "__main__":
    # Example manual trigger
    for file in os.listdir(DATA_DIR):
        if is_georgian_file(file):
            print(f"🌐 Translating {file} ...")
            translate_georgian_transcript(file)
