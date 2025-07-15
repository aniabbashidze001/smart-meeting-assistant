import requests


def test_transcription_api():
    """
        Test /api/transcribe endpoint:
        - Uploads mock audio file.
        - Verifies response contains transcript and detected language.
    """
    url = "http://localhost:5050/api/transcribe"
    files = {"file": open("tests/mock_audio.wav", "rb")}

    response = requests.post(url, files=files)
    assert response.status_code == 200, "API should return status 200"
    data = response.json()
    assert "transcript" in data, "Response should include 'transcript'"
    assert "language" in data, "Response should include 'language'"


def test_summary_api():
    """
        Test /api/summary endpoint:
        - Sends existing transcript filename.
        - Verifies response includes generated summary.
    """
    url = "http://localhost:5050/api/summary"
    payload = {"filename": "test_transcript.json"}

    response = requests.post(url, json=payload)
    assert response.status_code == 200, "API should return status 200"
    data = response.json()
    assert "summary" in data, "Response should include 'summary'"
