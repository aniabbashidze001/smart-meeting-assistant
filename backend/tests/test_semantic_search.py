import json
import os

import pytest
from semantic.index_transcripts import append_single_embedding
from semantic.search_query import get_query_embedding

DATA_DIR = os.path.abspath("data")


@pytest.fixture
def mock_transcript_file(tmp_path):
    """Creates a temporary valid transcript JSON file inside /data folder."""
    test_filename = "test_transcript.json"
    file_path = tmp_path / test_filename

    content = {
        "transcript": [{"speaker": "Speaker 1", "text": "This is a test sentence."}],
        "original_language": "en",
    }

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(content, f, indent=2)

    os.makedirs(DATA_DIR, exist_ok=True)
    dest_path = os.path.join(DATA_DIR, test_filename)
    os.replace(file_path, dest_path)

    return test_filename


def test_append_single_embedding(mock_transcript_file):
    """Test that embedding generation and indexing works properly."""
    result = append_single_embedding(mock_transcript_file)
    assert result is True, "Embedding should be appended successfully"


def test_get_query_embedding():
    """Test that a query returns a valid embedding vector."""
    query = "This is a test sentence"
    embedding = get_query_embedding(query)
    assert isinstance(embedding, list), "Embedding should be a list"
    assert len(embedding) > 0, "Embedding vector should not be empty"
