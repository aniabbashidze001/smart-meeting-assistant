import os
import json
import openai
import time
from pathlib import Path
from dotenv import load_dotenv

# Load your API key from .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Paths
DATA_FOLDER = Path(__file__).resolve().parent.parent / "data"
INDEX_FILE = Path(__file__).resolve().parent / "vector_index.json"


# 🔁 Load all transcripts (for full rebuild)
def load_transcripts():
    transcripts = []
    for file in DATA_FOLDER.glob("*.json"):
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    full_text = " ".join([entry["text"] for entry in data if "text" in entry])
                    transcripts.append({
                        "source": file.name,
                        "text": full_text
                    })
        except Exception as e:
            print(f"❌ Error reading {file.name}: {e}")
    return transcripts


# 🔗 Get embedding from OpenAI
def get_embedding(text: str):
    try:
        response = openai.embeddings.create(
            model="text-embedding-ada-002",
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"❌ Failed to get embedding: {e}")
        return None


# 🧱 Full index rebuild
def build_vector_index():
    transcripts = load_transcripts()
    print(f"🔍 Found {len(transcripts)} transcript files.")

    index = []
    for t in transcripts:
        print(f"📄 Processing: {t['source']}")
        embedding = get_embedding(t["text"])
        if embedding:
            index.append({
                "embedding": embedding,
                "text": t["text"],
                "source": t["source"]
            })

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2)
    print(f"✅ Embeddings saved to {INDEX_FILE.name}")


# 🔍 Wait for file to be fully written and readable
def wait_for_file_ready(file_path, max_attempts=10, initial_wait=0.5):
    """
    Wait for file to be fully written and contain valid JSON.
    Uses exponential backoff for more reliable file reading.
    """
    for attempt in range(max_attempts):
        try:
            # Check if file exists and has content
            if not file_path.exists():
                print(f"⏳ Attempt {attempt + 1}: File doesn't exist yet, waiting...")
                time.sleep(initial_wait * (1.5 ** attempt))  # Exponential backoff
                continue

            # Check file size (should be > 0)
            file_size = file_path.stat().st_size
            if file_size == 0:
                print(f"⏳ Attempt {attempt + 1}: File is empty ({file_size} bytes), waiting...")
                time.sleep(initial_wait * (1.5 ** attempt))
                continue

            # Try to read and parse the file
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read().strip()

            if not content:
                print(f"⏳ Attempt {attempt + 1}: File content is empty, waiting...")
                time.sleep(initial_wait * (1.5 ** attempt))
                continue

            # Try to parse JSON
            data = json.loads(content)

            # Verify it's the expected format (list with text content)
            if not isinstance(data, list):
                print(f"⏳ Attempt {attempt + 1}: Invalid format (not a list), waiting...")
                time.sleep(initial_wait * (1.5 ** attempt))
                continue

            # Check if there's at least one entry with text
            has_text = any("text" in entry for entry in data)
            if not has_text:
                print(f"⏳ Attempt {attempt + 1}: No text entries found, waiting...")
                time.sleep(initial_wait * (1.5 ** attempt))
                continue

            print(f"✅ File ready after {attempt + 1} attempts")
            return content, data

        except json.JSONDecodeError as e:
            print(f"⏳ Attempt {attempt + 1}: JSON parse error ({e}), waiting...")
            time.sleep(initial_wait * (1.5 ** attempt))
        except Exception as e:
            print(f"⏳ Attempt {attempt + 1}: Read error ({e}), waiting...")
            time.sleep(initial_wait * (1.5 ** attempt))

    print(f"❌ File not ready after {max_attempts} attempts")
    return None, None


# ✨ Append single transcript embedding (used by transcribe.py)
def append_single_embedding(filename):
    file_path = (DATA_FOLDER / filename).resolve()
    print(f"📂 Processing file: {file_path}")

    # Wait for file to be ready with better retry logic
    content, data = wait_for_file_ready(file_path)

    if not content or not data:
        print(f"❌ Failed to read valid content from {filename} after multiple attempts.")
        return False

    print(f"📦 Successfully loaded {len(data)} transcript entries from {filename}")

    # Extract text and create embedding
    full_text = " ".join([entry["text"] for entry in data if "text" in entry])

    if not full_text.strip():
        print(f"⚠️ No text content found in {filename}")
        return False

    # Get embedding
    embedding = get_embedding(full_text)
    if not embedding:
        print(f"❌ Failed to generate embedding for {filename}")
        return False

    # Load existing index or create new one
    try:
        if INDEX_FILE.exists():
            with open(INDEX_FILE, "r", encoding="utf-8") as f:
                index = json.load(f)
        else:
            index = []
    except Exception as e:
        print(f"⚠️ Error loading existing index: {e}, creating new one")
        index = []

    # Check if this file is already indexed (avoid duplicates)
    existing_sources = [item.get("source") for item in index]
    if filename in existing_sources:
        print(f"⚠️ {filename} already exists in index, skipping...")
        return True

    # Add new record
    new_record = {
        "embedding": embedding,
        "text": full_text,
        "source": filename
    }

    index.append(new_record)

    # Save updated index
    try:
        with open(INDEX_FILE, "w", encoding="utf-8") as f:
            json.dump(index, f, indent=2)
        print(f"✅ Successfully embedded and indexed: {filename}")
        return True
    except Exception as e:
        print(f"❌ Failed to save index: {e}")
        return False


# 🔃 Allow both modes: full + single
if __name__ == "__main__":
    build_vector_index()