# app/main.py
# FastAPI application - REST + WebSocket routes for AI Interview Coach

import os
import uuid
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional

from app.interviewer import InterviewAgent
from app.evaluator import AnswerEvaluator
from app.tts import TextToSpeech
from app.session import SessionStore
from app.report import ReportGenerator

app = FastAPI(
    title="AI Interview Coach",
    description="AI-powered mock interview coach using Google Gemini",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount frontend static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

sessions = SessionStore()
evaluator = AnswerEvaluator()
tts = TextToSpeech()


# ---------- Models ----------
class SessionStartRequest(BaseModel):
    role: str = "Software Engineer"
    difficulty: str = "Mid-level"   # Fresher | Mid-level | Senior | FAANG
    num_questions: int = 5

class AnswerRequest(BaseModel):
    answer: str
    question_index: Optional[int] = None


# ---------- Routes ----------
@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    with open("frontend/index.html") as f:
        return f.read()


@app.post("/session/start")
async def start_session(req: SessionStartRequest):
    """Create a new interview session and return the first question."""
    session_id = str(uuid.uuid4())[:8]
    agent = InterviewAgent(role=req.role, difficulty=req.difficulty)
    first_question = await agent.get_next_question()
    sessions.create(session_id, agent, req.num_questions)
    audio_b64 = await tts.synthesize_b64(first_question)
    return {
        "session_id": session_id,
        "question_index": 0,
        "question": first_question,
        "audio_b64": audio_b64,
        "total_questions": req.num_questions,
    }


@app.post("/session/{session_id}/answer")
async def submit_answer(session_id: str, req: AnswerRequest):
    """Submit an answer, get evaluation and next question."""
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    current_q = session["agent"].current_question
    scores = await evaluator.evaluate(question=current_q, answer=req.answer)
    session["scores"].append({"question": current_q, "answer": req.answer, "scores": scores})

    next_idx = session["current_idx"] + 1
    sessions.update_idx(session_id, next_idx)

    if next_idx >= session["total_questions"]:
        return {"done": True, "scores": scores, "next_question": None}

    next_q = await session["agent"].get_next_question(prev_answer=req.answer)
    audio_b64 = await tts.synthesize_b64(next_q)
    return {
        "done": False,
        "scores": scores,
        "question_index": next_idx,
        "next_question": next_q,
        "audio_b64": audio_b64,
    }


@app.get("/session/{session_id}/report")
async def get_report(session_id: str, fmt: str = "json"):
    """Download session report as JSON or HTML."""
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    gen = ReportGenerator(session_id, session["scores"])
    if fmt == "html":
        path = gen.to_html()
        return FileResponse(path, media_type="text/html", filename=f"report_{session_id}.html")
    return gen.to_dict()


@app.get("/tts/{text}")
async def get_tts_audio(text: str):
    """Return TTS audio for arbitrary text."""
    path = await tts.synthesize_file(text)
    return FileResponse(path, media_type="audio/mpeg")


# ---------- WebSocket ----------
@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """Real-time WebSocket for streaming question + score events."""
    await websocket.accept()
    session = sessions.get(session_id)
    if not session:
        await websocket.send_json({"error": "Session not found"})
        await websocket.close()
        return
    try:
        while True:
            data = await websocket.receive_json()
            answer = data.get("answer", "")
            current_q = session["agent"].current_question
            scores = await evaluator.evaluate(question=current_q, answer=answer)
            next_q = await session["agent"].get_next_question(prev_answer=answer)
            await websocket.send_json({
                "scores": scores,
                "next_question": next_q,
            })
    except WebSocketDisconnect:
        pass
