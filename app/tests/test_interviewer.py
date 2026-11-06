# Tests for the interview agent with the Gemini client mocked out.

import sys
import types

import pytest


class _FakeChat:
    def __init__(self):
        self.prompts = []

    def send_message(self, prompt):
        self.prompts.append(prompt)
        return types.SimpleNamespace(text="  Tell me about a bug you fixed.  ")


class _FakeModel:
    last_chat = None
    last_kwargs = None

    def __init__(self, *args, **kwargs):
        _FakeModel.last_kwargs = kwargs

    def start_chat(self, history=None):
        _FakeModel.last_chat = _FakeChat()
        return _FakeModel.last_chat


def _agent(monkeypatch, **kwargs):
    fake_genai = types.ModuleType("google.generativeai")
    fake_genai.configure = lambda **kw: None
    fake_genai.GenerativeModel = _FakeModel
    fake_google = types.ModuleType("google")
    fake_google.generativeai = fake_genai
    fake_google.__path__ = []
    monkeypatch.setitem(sys.modules, "google", fake_google)
    monkeypatch.setitem(sys.modules, "google.generativeai", fake_genai)
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    sys.modules.pop("app.interviewer", None)
    from app.interviewer import InterviewAgent

    return InterviewAgent(**kwargs)


def test_missing_api_key_raises_clear_error(monkeypatch):
    fake_genai = types.ModuleType("google.generativeai")
    fake_genai.configure = lambda **kw: None
    fake_genai.GenerativeModel = _FakeModel
    fake_google = types.ModuleType("google")
    fake_google.generativeai = fake_genai
    fake_google.__path__ = []
    monkeypatch.setitem(sys.modules, "google", fake_google)
    monkeypatch.setitem(sys.modules, "google.generativeai", fake_genai)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    sys.modules.pop("app.interviewer", None)
    from app.interviewer import InterviewAgent

    with pytest.raises(RuntimeError, match="GEMINI_API_KEY"):
        InterviewAgent()


def test_unknown_role_falls_back_to_software_engineer(monkeypatch):
    _agent(monkeypatch, role="Astronaut", difficulty="Easy")
    prompt = _FakeModel.last_kwargs["system_instruction"]
    assert "senior software engineer" in prompt
    assert "2-4 years" in prompt  # Mid-level fallback


@pytest.mark.asyncio
async def test_first_question_is_stripped_and_recorded(monkeypatch):
    agent = _agent(monkeypatch)
    q = await agent.get_next_question()
    assert q == "Tell me about a bug you fixed."
    assert agent.current_question == q
    assert agent.get_history()[-1]["content"] == q


@pytest.mark.asyncio
async def test_followup_prompt_includes_previous_answer(monkeypatch):
    agent = _agent(monkeypatch)
    await agent.get_next_question()
    await agent.get_next_question(prev_answer="I fixed a race condition.")
    assert "race condition" in _FakeModel.last_chat.prompts[-1]
