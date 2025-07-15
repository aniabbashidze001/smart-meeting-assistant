# Smart Meeting Assistant 

\
**AI-powered meeting transcription, summarization, semantic search, and visual reporting platform.**

---

## 🚀 Project Overview

Smart Meeting Assistant automates post-meeting documentation using AI models. It transcribes meetings, generates structured summaries and action items, builds a searchable knowledge base, and produces stakeholder-ready visuals. It also supports Georgian language audio.

---

## 📦 Features

- 🎙️ **Audio Upload & Transcription**
- 📄 **Meeting Summarization & Action Item Extraction**
- 🔍 **Semantic Search across Meetings**
- 🎨 **DALL·E 3 Visual Summaries (3 Types)**
- 📅 **Integrated Calendar View**
- 🌐 **Multilingual Support**

---

## 🛠️ Technology Stack

| Layer         | Technologies                                             |
| ------------- | -------------------------------------------------------- |
| **Frontend**  | React, Tailwind CSS                                      |
| **Backend**   | Python (Flask), AssemblyAI, OpenAI APIs, Deep Translator |
| **Database**  | Local JSON storage (data/ folder)                        |
| **AI Models** | Whisper, GPT-4 (Function Calling), Embeddings, DALL·E 3  |
| **Testing**   | Pytest, Requests                                         |

---

## 📁 Project Structure

```plaintext
smart-meeting-assistant/
├── backend/
│   ├── app.py
│   ├── transcribe.py
│   ├── generate_summary.py
│   ├── calendar_utils.py
│   ├── services/
│   ├── semantic/
│   ├── visuals/
│   ├── tests/
│   ├── static_data/
│   └── data/
├── client/   # React Frontend
├── docs/
│   ├── ARCHITECTURE.md
│   └── TESTS.md
├── README.md
└── requirements.txt
```

---

## 🌐 API Endpoints

| Endpoint               | Method | Purpose                             |
| ---------------------- | ------ | ----------------------------------- |
| `/api/transcribe`      | POST   | Upload audio file for transcription |
| `/api/summary`         | POST   | Generate summary from transcript    |
| `/api/semantic-search` | POST   | Perform semantic search             |
| `/api/visual-summary`  | POST   | Generate visual summaries (3 types) |
| `/api/calendar`        | GET    | Fetch calendar events               |

---

## ⚙️ Installation & Setup

1. **Clone Repository:**

```bash
git clone https://github.com/aniabbashidze001/smart-meeting-assistant.git
cd smart-meeting-assistant
```

2. **Backend Setup:**

```bash
cd backend
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
python app.py
```

3. **Frontend Setup:**

```bash
cd client
npm install
npm run dev
```

4. **Access App:**

- Frontend: `http://localhost:3000`
- Backend APIs: `http://localhost:5050`

---

## 🧪 Running Tests

```bash
# From project root
PYTHONPATH=. pytest backend/tests
```

Detailed test cases are described in [`docs/TESTS.md`](docs/TESTS.md).

---

## 📊 Reports & Generated Files

- **Transcripts & Summaries:** `backend/data/`
- **Vector Index (Embeddings):** `backend/semantic/vector_index.json`


---

## 📅 Calendar Events

- Endpoint serves mock or real meeting events.
- Data file: `backend/data/calendar_events.json`
- Accessible at `/api/calendar`

---

## 📄 Documentation

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- [`docs/TESTS.md`](docs/TESTS.md)

---

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch
3. Commit and push
4. Open a pull request



