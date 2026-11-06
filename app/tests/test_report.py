# Tests for the report generator (JSON + HTML).

import os

from app.report import ReportGenerator


def _scores():
    return [
        {
            "question": "What is a closure?",
            "answer": "A function capturing its lexical scope.",
            "scores": {
                "relevance": 9,
                "technical_depth": 8,
                "communication": 7,
                "star_structure": 5,
                "overall_score": 7.5,
                "feedback": "Good definition, add an example.",
                "strengths": "Accurate core concept.",
            },
        },
        {
            "question": "Explain event loop.",
            "answer": "It schedules async tasks.",
            "scores": {
                "relevance": 6,
                "technical_depth": 5,
                "communication": 6,
                "star_structure": 4,
                "overall_score": 5.3,
                "feedback": "Go deeper into the call stack.",
                "strengths": "Concise.",
            },
        },
    ]


def test_to_dict_shape_and_average():
    gen = ReportGenerator("sess1", _scores())
    report = gen.to_dict()
    assert report["session_id"] == "sess1"
    assert report["total_questions"] == 2
    assert report["average_score"] == round((7.5 + 5.3) / 2, 2)
    assert len(report["results"]) == 2
    assert report["generated_at"].endswith("Z")


def test_to_dict_empty_scores():
    report = ReportGenerator("empty", []).to_dict()
    assert report["average_score"] == 0.0
    assert report["total_questions"] == 0


def test_to_html_writes_real_file():
    gen = ReportGenerator("sess1", _scores())
    path = gen.to_html()
    try:
        assert os.path.exists(path)
        with open(path, encoding="utf-8") as f:
            content = f.read()
        assert "Session Report" in content
        assert "6.4" in content  # rounded average appears in the badge
    finally:
        os.unlink(path)
