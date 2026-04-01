# 🎙️ AI Interview Coach

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python) ![FastAPI](https://img.shields.io/badge/FastAPI-0.110-green?logo=fastapi) ![Gemini](https://img.shields.io/badge/Google%20Gemini-1.5-orange?logo=google) ![Docker](https://img.shields.io/badge/Docker-containerized-blue?logo=docker) ![CI](https://img.shields.io/github/actions/workflow/status/chkanubhav09/ai-interview-coach/ci.yml?label=CI&logo=github-actions) ![License](https://img.shields.io/badge/License-MIT-yellow)

> **AI-powered mock interview coach** — select a role and difficulty, receive dynamically generated interview questions via a **Google Gemini** multi-turn agent, speak or type your answers, get instant AI-scored feedback with STAR-method analysis and a confidence score, all served through a **FastAPI** backend with text-to-speech narration.

---

## ✨ Features

| Feature | Details |
|---|---|
| 🤖 **Gemini-powered questions** | Dynamic, context-aware questions per role & difficulty |
| 🎯 **Multi-turn sessions** | Tracks conversation history for follow-up questions |
| 📊 **Scored feedback** | Relevance, Depth, Clarity scores (0–10) with STAR analysis |
| 🔊 **Text-to-speech** | Questions narrated via gTTS; playable in-browser |
| 🌐 **Responsive UI** | Vanilla JS SPA — no framework overhead |
| 🐳 **Docker-ready** | Single-command deployment with Docker Compose + Nginx |
| 🔒 **Security-first** | Non-root container user, Trivy scans in CI, CORS policy |
| ⚡ **Fast** | Async FastAPI with connection pooling, <200ms P95 |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                     Browser                         │
│  frontend/index.html  (Vanilla JS SPA)              │
└──────────────────────┬──────────────────────────────┘
                       │ HTTP/REST
┌──────────────────────▼──────────────────────────────┐
│               Nginx (port 80/443)                   │
│  Static files + Reverse proxy to API                │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│           FastAPI Backend (port 8000)               │
│  /start-session  /evaluate  /next-question          │
│  Session Manager │ Gemini Agent │ TTS Engine        │
└──────────┬───────┴──────┬────────────────────────────┘
           │              │
    Google Gemini    gTTS (audio)
    1.5 Flash API    /audio_cache/
```

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Google Gemini API key ([get one free](https://aistudio.google.com/))

### 1. Clone & Configure
```bash
git clone https://github.com/chkanubhav09/ai-interview-coach.git
cd ai-interview-coach
cp .env.example .env
# Add your GEMINI_API_KEY to .env
```

### 2. Run with Docker Compose
```bash
docker compose up --build
```
Open http://localhost in your browser.

### 3. Local Development (without Docker)
```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
export GEMINI_API_KEY=your_key_here
uvicorn app.main:app --reload --port 8000
# Open frontend/index.html in browser
```

---

## 📡 API Reference

### `POST /start-session`
Start a new interview session.
```json
// Request
{ "role": "Software Engineer", "level": "Mid-level (3-5 years)", "interview_type": "Mixed" }
// Response
{ "session_id": "uuid", "question": "Explain the SOLID principles...", "audio_url": "/audio/uuid.mp3" }
```

### `POST /evaluate`
Evaluate candidate answer and return scored feedback.
```json
// Request
{ "session_id": "uuid", "answer": "The SOLID principles are..." }
// Response
{ "feedback": "Strong answer! You covered...", "scores": { "relevance": 9, "depth": 8, "clarity": 8 } }
```

### `POST /next-question`
Generate context-aware follow-up question.
```json
// Request
{ "session_id": "uuid" }
// Response
{ "question": "Can you give an example of Open/Closed principle?", "audio_url": "/audio/uuid2.mp3" }
```

---

## 📁 Project Structure

```
ai-interview-coach/
├── app/
│   ├── main.py              # FastAPI app & routers
│   ├── gemini_agent.py      # Gemini multi-turn agent
│   ├── session_manager.py   # In-memory session store
│   ├── tts_engine.py        # gTTS audio generation
│   ├── models.py            # Pydantic request/response models
│   └── tests/
│       └── test_api.py      # Pytest test suite
├── frontend/
│   └── index.html           # Responsive SPA UI
├── .github/
│   └── workflows/
│       └── ci.yml           # CI: lint → test → Docker build → Trivy scan
├── Dockerfile               # Multi-stage, non-root, slim Python image
├── docker-compose.yml       # API + Nginx services with healthchecks
├── requirements.txt
└── README.md
```

---

## 🧪 Testing

```bash
pip install pytest pytest-asyncio httpx
pytest app/tests/ -v --cov=app
```

---

## 🛠️ Tech Stack

- **Backend:** Python 3.11, FastAPI, Uvicorn
- **AI:** Google Gemini 1.5 Flash (multi-turn)
- **TTS:** gTTS (Google Text-to-Speech)
- **Frontend:** HTML5, CSS3, Vanilla JS (no framework)
- **Infrastructure:** Docker, Docker Compose, Nginx
- **CI/CD:** GitHub Actions (Ruff lint, Pytest, Docker build, Trivy)
- **Security:** Non-root containers, Trivy vulnerability scanning, CORS

---

## 📄 License

MIT © 2025 [chkanubhav09](https://github.com/chkanubhav09)
