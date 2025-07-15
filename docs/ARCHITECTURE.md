# Smart Meeting Assistant — System Architecture

## Overview

Smart Meeting Assistant is a full-stack web application designed to automate meeting transcription, summarization, semantic search, and visual reporting using OpenAI APIs. The system processes recorded meeting audio and outputs structured summaries, visual assets, and a searchable knowledge base of transcripts.

---

## Technology Stack

| Layer | **Technologies**                                        |
| ------------- |---------------------------------------------------------|
| **Frontend**  | React, Tailwind CSS                                     |
| **Backend**   | Python (Flask), AssemblyAI, OpenAI API, Deep Translator |
| **Database**  | JSON file storage (local data/ folder)                  |
| **APIs Used** | Whisper, GPT-4 (Function Calling), Embeddings, DALL·E 3 |
| **Testing**   | Pytest, Requests                                        |

---

## System Architecture

### 1. Audio Processing Layer

- **Service:** `backend/transcribe.py`
- **Workflow:**
  - Receives uploaded audio file via `/api/transcribe`.
  - Calls AssemblyAI API for transcription and speaker diarization.
  - Automatically detects Georgian audio and translates it.
  - Saves transcript in JSON format inside `backend/data/`.
  - Triggers semantic embedding indexing after saving.

### 2. Content Analysis Layer

- **Service:** `backend/generate_summary.py`
- **Workflow:**
  - Generates meeting summary from transcript using GPT-4.
  - Extracts action items, owners, and optional calendar events.
  - Saves structured summaries in `backend/data/`.

### 3. Semantic Search Layer

- **Components:**
  - `backend/semantic/index_transcripts.py` — Embedding generation and indexing.
  - `backend/semantic/search_query.py` — Query embedding and similarity search.
- **Workflow:**
  - All transcripts are converted into OpenAI Embeddings vectors.
  - Stored in `vector_index.json`.
  - Queries are matched against stored vectors to retrieve relevant meetings.

### 4. Visual Synthesis Layer

- **Service:** `backend/visuals/generate_visual.py`
- **Workflow:**
  - Extracts structured summary data.
  - Generates 3 visual types using DALL·E 3:
    - Executive dashboard visual
    - Stakeholder presentation visual
    - Action items task board visual

### 5. Frontend Interface

- **Main Pages:**
  - Upload Meeting (Audio Upload & Transcription)
  - Meeting Summary & Action Items
  - Visual Summary Page
  - Semantic Search Interface
  - Calendar View 

### 6. Multilingual Handling

- Georgian language support.
- Auto-translated using Deep Translator.
- Semantic search and summary generation operate on translated transcripts.

---

## Data Storage Structure

- `/backend/data/` — Stores all meeting JSON transcripts and summaries.
- `/backend/semantic/vector_index.json` — Vector database for embeddings.

---

## API Endpoints Overview

| Endpoint               | Method | Description                         |
|------------------------|--------|-------------------------------------|
| `/api/transcribe`      | POST   | Upload audio and transcribe meeting |
| `/api/summary`         | POST   | Generate summary from transcript    |
| `/api/semantic-search` | POST   | Query semantic search               |
| `/api/visual-summary`  | POST   | Generate visual summaries           |
| `/api/calendar`             | GET      | Calendar view with events           |

---

## Project Structure

```plaintext
smart-meeting-assistant/
├── backend/
│   ├── app.py
│   ├── transcribe.py
│   ├── generate_summary.py
│   ├── calendar_utils.py
│   ├── config.py
│   ├── services/
│   ├── semantic/
│   ├── visuals/
│   ├── tests/
│   ├── static_data/
│   └── data/
├── client/
│   └── src/
├── docs/
│   ├── TESTS.md
│   └── ARCHITECTURE.md
├── README.md
└── requirements.txt
```

---

## Conclusion

Smart Meeting Assistant combines AI transcription, summarization, semantic search, and visual generation within a modular, extensible Python backend and modern React frontend. This architecture ensures scalability for future features such as fine-tuning, real-time processing, or advanced analytics.

