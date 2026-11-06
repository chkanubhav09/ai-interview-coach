# app/evaluator.py
# Answer scoring engine using Gemini - 4-dimension rubric

import json
import os

import google.generativeai as genai

EVAL_PROMPT_TEMPLATE = """
You are an expert technical interviewer evaluating a candidate's answer.

Question: {question}
Candidate's Answer: {answer}

Score the answer on these 4 dimensions, each from 0 to 10:
1. Relevance (0-10): Does the answer directly address the question?
2. Technical Depth (0-10): Is the content technically correct and detailed?
3. Communication (0-10): Is the answer clear, structured, and concise?
4. STAR Structure (0-10): Does the answer use Situation-Task-Action-Result structure where applicable?

Also provide:
- overall_score: weighted average (Relevance 30%, Depth 30%, Communication 20%, STAR 20%)
- feedback: 2-3 sentences of specific, actionable improvement advice
- strengths: 1-2 specific things the candidate did well

Respond ONLY with valid JSON in this exact format:
{{
  "relevance": <int>,
  "technical_depth": <int>,
  "communication": <int>,
  "star_structure": <int>,
  "overall_score": <float>,
  "feedback": "<string>",
  "strengths": "<string>"
}}
"""


class AnswerEvaluator:
    """Scores interview answers using Gemini on a 4-dimension rubric."""

    def __init__(self):
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY environment variable is not set")
        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel("gemini-1.5-flash")

    async def evaluate(self, question: str, answer: str) -> dict:
        """Return a scores dict with individual and overall scores plus feedback."""
        if not answer.strip():
            return self._zero_score("Empty answer provided.")

        prompt = EVAL_PROMPT_TEMPLATE.format(question=question, answer=answer)
        try:
            response = self._model.generate_content(prompt)
            text = response.text.strip()
            # Strip markdown code fences if present
            if text.startswith("```"):
                text = text.split("```")[1]
                text = text.removeprefix("json")
            scores = json.loads(text)
            return scores
        except json.JSONDecodeError as e:
            return self._zero_score(f"Evaluation error: could not parse model response ({e})")
        except Exception as e:  # noqa: BLE001 - any client/API failure becomes a zero score, not a crash
            return self._zero_score(f"Evaluation error: {type(e).__name__}: {e}")

    @staticmethod
    def _zero_score(reason: str) -> dict:
        return {
            "relevance": 0,
            "technical_depth": 0,
            "communication": 0,
            "star_structure": 0,
            "overall_score": 0.0,
            "feedback": reason,
            "strengths": "N/A",
        }
