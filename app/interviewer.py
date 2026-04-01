# app/interviewer.py
# Gemini multi-turn interview agent

import os
import google.generativeai as genai
from typing import Optional

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

ROLE_PROMPTS = {
    "Software Engineer": "You are a senior software engineer interviewing a candidate for an SDE role. Focus on DSA, system design, OOP, and coding best practices.",
    "Data Scientist": "You are a lead data scientist interviewing a candidate. Focus on ML algorithms, statistics, Python, model evaluation, and real-world ML projects.",
    "Cloud Engineer": "You are an AWS Solutions Architect interviewing a candidate. Focus on cloud services, networking, security, IaC, and cost optimization.",
    "ECE Engineer": "You are a senior ECE engineer interviewing a candidate. Focus on embedded systems, microcontrollers, signal processing, IoT, and hardware-software co-design.",
    "Product Manager": "You are a senior product manager conducting a PM interview. Focus on product sense, metrics, prioritization, stakeholder management, and case studies.",
}

DIFFICULTY_NOTES = {
    "Fresher":    "The candidate is a fresh graduate. Ask foundational questions.",
    "Mid-level":  "The candidate has 2-4 years of experience. Ask practical, scenario-based questions.",
    "Senior":     "The candidate has 5+ years. Ask deep system design and leadership questions.",
    "FAANG":      "This is a FAANG-level interview. Ask highly challenging algorithmic and system design questions.",
}


class InterviewAgent:
    """Multi-turn Gemini interview agent."""

    def __init__(self, role: str = "Software Engineer", difficulty: str = "Mid-level"):
        self.role = role
        self.difficulty = difficulty
        self.current_question: Optional[str] = None
        self._history: list[dict] = []

        system_prompt = (
            f"{ROLE_PROMPTS.get(role, ROLE_PROMPTS['Software Engineer'])} "
            f"{DIFFICULTY_NOTES.get(difficulty, DIFFICULTY_NOTES['Mid-level'])} "
            "Ask ONE question at a time. After receiving an answer, ask a relevant follow-up "
            "or the next question. Keep questions concise and clear. Do NOT evaluate the answer yourself "
            "(the evaluation module handles that). Just continue the interview naturally."
        )

        self._model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=system_prompt,
        )
        self._chat = self._model.start_chat(history=[])

    async def get_next_question(self, prev_answer: Optional[str] = None) -> str:
        """Generate the next interview question."""
        if prev_answer:
            prompt = f"Candidate answered: '{prev_answer}'. Ask the next interview question."
        else:
            prompt = f"Start the {self.role} interview at {self.difficulty} level. Ask your first question."

        response = self._chat.send_message(prompt)
        question = response.text.strip()
        self.current_question = question
        self._history.append({"role": "model", "content": question})
        return question

    def get_history(self) -> list:
        return self._history
