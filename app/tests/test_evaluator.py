# Tests for the answer evaluator with the Gemini client mocked out.

import sys
import types

import pytest


class _FakeResponse:
    def __init__(self, text):
        self.text = text


class _FakeModel:
    """Stands in for genai.GenerativeModel; returns canned text."""

    canned = ""
    raise_error = None

    def __init__(self, *args, **kwargs):
        pass

    def generate_content(self, prompt):
        if _FakeModel.raise_error:
            raise _FakeModel.raise_error
        return _FakeResponse(_FakeModel.canned)


def _evaluator(monkeypatch):
    fake_genai = types.ModuleType("google.generativeai")
    fake_genai.configure = lambda **kw: None
    fake_genai.GenerativeModel = _FakeModel
    fake_google = types.ModuleType("google")
    fake_google.generativeai = fake_genai
    fake_google.__path__ = []
    monkeypatch.setitem(sys.modules, "google", fake_google)
    monkeypatch.setitem(sys.modules, "google.generativeai", fake_genai)
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    # Fresh import so the module binds the fake client.
    for mod in ("app.evaluator",):
        sys.modules.pop(mod, None)
    from app.evaluator import AnswerEvaluator

    return AnswerEvaluator()


@pytest.mark.asyncio
async def test_empty_answer_short_circuits(monkeypatch):
    ev = _evaluator(monkeypatch)
    scores = await ev.evaluate("Q?", "   ")
    assert scores["overall_score"] == 0.0
    assert "Empty answer" in scores["feedback"]


@pytest.mark.asyncio
async def test_parses_plain_json(monkeypatch):
    ev = _evaluator(monkeypatch)
    _FakeModel.canned = (
        '{"relevance": 8, "technical_depth": 7, "communication": 6,'
        ' "star_structure": 5, "overall_score": 6.8,'
        ' "feedback": "ok", "strengths": "clear"}'
    )
    scores = await ev.evaluate("Q?", "some answer")
    assert scores["relevance"] == 8
    assert scores["overall_score"] == 6.8


@pytest.mark.asyncio
async def test_strips_markdown_code_fence(monkeypatch):
    ev = _evaluator(monkeypatch)
    _FakeModel.canned = (
        '```json\n{"relevance": 9, "technical_depth": 9, "communication": 9,'
        ' "star_structure": 9, "overall_score": 9.0,'
        ' "feedback": "great", "strengths": "all"}\n```'
    )
    scores = await ev.evaluate("Q?", "great answer")
    assert scores["star_structure"] == 9


@pytest.mark.asyncio
async def test_bad_json_returns_zero_score(monkeypatch):
    ev = _evaluator(monkeypatch)
    _FakeModel.canned = "not json at all"
    scores = await ev.evaluate("Q?", "answer")
    assert scores["overall_score"] == 0.0
    assert "Evaluation error" in scores["feedback"]


@pytest.mark.asyncio
async def test_api_error_returns_zero_score(monkeypatch):
    ev = _evaluator(monkeypatch)
    _FakeModel.raise_error = RuntimeError("boom")
    scores = await ev.evaluate("Q?", "answer")
    assert scores["overall_score"] == 0.0
    _FakeModel.raise_error = None
