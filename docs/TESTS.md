# TESTS.md — Smart Meeting Assistant

## Overview

This document summarizes the automated test cases implemented for the Smart Meeting Assistant backend, outlining what is tested, why, and how. It also explains how to execute the test suite.

---

## Technologies Used

- **Pytest** — Python testing framework
- **Requests** — For integration API testing

---

## Running Tests

```bash
# Run all tests (from project root)
PYTHONPATH=. pytest backend/tests

# Run specific test file
PYTHONPATH=. pytest backend/tests/test_semantic_search.py
```

Ensure your Flask backend server is running locally on port **5050** before running integration tests.

---

## Test Cases Summary

### 1. Semantic Search Tests (`test_semantic_search.py`)

**Purpose:**
- Validate that embedding generation and semantic querying are functioning correctly.

**Tests:**
- `test_append_single_embedding()`
  - Tests that embeddings are correctly generated and appended for a dummy/mock transcript.
- `test_search_embedding()`
  - Verifies that a sample query returns a non-empty list of results, confirming search functionality.

**Covers:**
- Backend semantic search pipeline
- Vector indexing and retrieval

---

### 2. Integration Tests (`test_integration.py`)

**Purpose:**
- Ensure that backend API endpoints work as expected when accessed via HTTP requests.

**Tests:**
- `test_transcription_api()`
  - Uploads a short mock audio file via `/api/transcribe` endpoint.
  - Asserts that the API responds successfully and returns a valid transcript structure.
- `test_summary_api()`
  - Calls `/api/summary` endpoint with a known transcript filename.
  - Verifies that a summary is successfully generated and returned.

**Covers:**
- End-to-end backend service integration
- External API handling (AssemblyAI, OpenAI)
- Response format correctness

**Note:**
- Requires a real or mock audio file (e.g., `tests/mock_audio.wav`).
- Assumes backend is running locally.

---

## Test Philosophy

- **Focus:** Core backend services and APIs
- **Scope:** Minimal, functional test coverage to validate primary pipelines

---


## Conclusion

Current tests confirm that Semantic Search, Audio Transcription, and Summary Generation pipelines work reliably under normal conditions. They validate both service-level correctness and endpoint responsiveness, providing baseline test coverage for the project.

