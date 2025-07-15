import json
import os
import time
from pathlib import Path

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

DATA_FOLDER = Path(__file__).resolve().parent.parent / "data"
INDEX_FILE = Path(__file__).resolve().parent / "vector_index.json"


def load_transcripts():
    """
    Load and process transcript files from the DATA_FOLDER directory.

    Returns:
        list: A list of dictionaries containing processed transcripts.
              Each dictionary has two keys:
              - 'source': The filename of the transcript
              - 'text': The concatenated text content of all utterances

    Handles multiple transcript formats:
    - Dictionary with 'transcript' key
    - Raw list of utterances
    - Skips untranslated non-English files
    - Skips files with invalid formats or empty content
    """
    transcripts = []
    for file in DATA_FOLDER.glob("*.json"):
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)

                if isinstance(data, dict) and "transcript" in data:
                    original_lang = data.get("original_language", "en")
                    is_translated = data.get("translated", False)

                    if original_lang != "en" and not is_translated:
                        print(f"⚠️ Skipping untranslated non-English file: {file.name}")
                        continue

                    utterances = data["transcript"]

                elif isinstance(data, list):
                    utterances = data
                else:
                    print(f"⚠️ Unknown format in: {file.name}")
                    continue

                full_text = " ".join([u["text"] for u in utterances if "text" in u])
                if not full_text.strip():
                    print(f"⚠️ No text content in {file.name}")
                    continue

                transcripts.append({"source": file.name, "text": full_text})

        except Exception as e:
            print(f"❌ Error processing {file.name}: {e}")
    return transcripts


def get_embedding(text: str):
    """
        Generate an embedding vector for the given text using OpenAI's text-embedding-ada-002 model.

        Args:
            text (str): The input text for which the embedding is to be generated.

        Returns:
            list[float] | None: A list of floating point numbers representing the embedding vector,
                                or None if the embedding generation fails.
    """
    try:
        response = client.embeddings.create(model="text-embedding-ada-002", input=text)
        return response.data[0].embedding
    except Exception as e:
        print(f"❌ Failed to get embedding: {e}")
        return None


def build_vector_index():
    """
        Build a vector index from transcript files in the `DATA_FOLDER`.

        This method processes transcript files, generates embeddings for their content using OpenAI's embedding model,
        and saves the resulting index to the `INDEX_FILE`. It handles multiple transcript formats and skips files
        with untranslated non-English content or invalid formats.

        Steps:
        1. Load transcript files from the `DATA_FOLDER`.
        2. Generate embeddings for the text content of each transcript.
        3. Save the embeddings along with the source filename and text content to the `INDEX_FILE`.

        Returns:
            None
    """
    transcripts = load_transcripts()
    print(f"🔍 Found {len(transcripts)} transcript files.")

    index = []
    for t in transcripts:
        print(f"📄 Processing: {t['source']}")
        embedding = get_embedding(t["text"])
        if embedding:
            index.append(
                {"embedding": embedding, "text": t["text"], "source": t["source"]}
            )

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2)
    print(f"✅ Embeddings saved to {INDEX_FILE.name}")


def wait_for_file_ready(file_path, max_attempts=10, initial_wait=0.5):
    """
    Wait for file to be fully written and contain valid JSON (dict or list).
    Uses exponential backoff for more reliable file reading.
    """
    for attempt in range(max_attempts):
        try:
            if not file_path.exists():
                print(f"⏳ Attempt {attempt + 1}: File doesn't exist yet, waiting...")
                time.sleep(initial_wait * (1.5**attempt))
                continue

            file_size = file_path.stat().st_size
            if file_size == 0:
                print(f"⏳ Attempt {attempt + 1}: File is empty, waiting...")
                time.sleep(initial_wait * (1.5**attempt))
                continue

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read().strip()

            if not content:
                print(f"⏳ Attempt {attempt + 1}: File content is empty, waiting...")
                time.sleep(initial_wait * (1.5**attempt))
                continue

            data = json.loads(content)

            if isinstance(data, dict):
                if "transcript" in data or "utterances" in data:
                    print(
                        f"✅ File ready with dict structure after {attempt + 1} attempts"
                    )
                    return content, data
                else:
                    print(
                        f"⏳ Attempt {attempt + 1}: Dict missing expected keys, waiting..."
                    )
                    time.sleep(initial_wait * (1.5**attempt))
                    continue

            elif isinstance(data, list):
                if any("text" in entry for entry in data):
                    print(
                        f"✅ File ready with list structure after {attempt + 1} attempts"
                    )
                    return content, data
                else:
                    print(
                        f"⏳ Attempt {attempt + 1}: List has no 'text' entries, waiting..."
                    )
                    time.sleep(initial_wait * (1.5**attempt))
                    continue

            print(f"⏳ Attempt {attempt + 1}: Unexpected structure, waiting...")
            time.sleep(initial_wait * (1.5**attempt))

        except json.JSONDecodeError as e:
            print(f"⏳ Attempt {attempt + 1}: JSON parse error ({e}), waiting...")
            time.sleep(initial_wait * (1.5**attempt))
        except Exception as e:
            print(f"⏳ Attempt {attempt + 1}: Read error ({e}), waiting...")
            time.sleep(initial_wait * (1.5**attempt))

    print(f"❌ File not ready after {max_attempts} attempts")
    return None, None


def append_single_embedding(filename):
    """
        Append a single transcript file's embedding to the vector index.

        Args:
            filename (str): The name of the transcript file to process.

        Returns:
            bool: True if the embedding was successfully added to the index,
                  False if the process failed or the file was skipped.

        This method:
        - Waits for the file to be ready and contain valid JSON content.
        - Detects the structure of the transcript (dictionary or list).
        - Skips untranslated non-English files and files with invalid formats.
        - Generates an embedding for the transcript's text content using OpenAI's embedding model.
        - Appends the embedding to the vector index file (`vector_index.json`), avoiding duplicates.
    """
    file_path = (DATA_FOLDER / filename).resolve()
    print(f"📂 Processing file: {file_path}")

    content, data = wait_for_file_ready(file_path)

    if not content or not data:
        print(
            f"❌ Failed to read valid content from {filename} after multiple attempts."
        )
        return False

    print(f"📦 Successfully loaded {len(data)} transcript entries from {filename}")

    # Detect structure
    if isinstance(data, dict) and "transcript" in data:
        original_lang = data.get("original_language", "en")
        is_translated = data.get("translated", False)

        if original_lang != "en" and not is_translated:
            print(f"⚠️ Skipping untranslated non-English file: {filename}")
            return False

        utterances = data["transcript"]

    elif isinstance(data, list):
        utterances = data
    else:
        print(f"⚠️ Unknown format in {filename}")
        return False

    full_text = " ".join([entry["text"] for entry in utterances if "text" in entry])

    if not full_text.strip():
        print(f"⚠️ No text content found in {filename}")
        return False

    embedding = get_embedding(full_text)
    if not embedding:
        print(f"❌ Failed to generate embedding for {filename}")
        return False

    try:
        if INDEX_FILE.exists():
            with open(INDEX_FILE, "r", encoding="utf-8") as f:
                index = json.load(f)
        else:
            index = []
    except Exception as e:
        print(f"⚠️ Error loading existing index: {e}, creating new one")
        index = []

    existing_sources = [item.get("source") for item in index]
    if filename in existing_sources:
        print(f"⚠️ {filename} already exists in index, skipping...")
        return True

    new_record = {"embedding": embedding, "text": full_text, "source": filename}

    index.append(new_record)

    try:
        with open(INDEX_FILE, "w", encoding="utf-8") as f:
            json.dump(index, f, indent=2)
        print(f"✅ Successfully embedded and indexed: {filename}")
        return True
    except Exception as e:
        print(f"❌ Failed to save index: {e}")
        return False


if __name__ == "__main__":
    build_vector_index()
