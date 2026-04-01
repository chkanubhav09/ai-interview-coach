# app/report.py
# Session report generator - JSON and HTML export

import json
import tempfile
from pathlib import Path
from datetime import datetime


class ReportGenerator:
    """Generates JSON and HTML session reports from scored Q&A pairs."""

    def __init__(self, session_id: str, scores: list):
        self.session_id = session_id
        self.scores = scores
        self.generated_at = datetime.utcnow().isoformat() + "Z"

    def _overall_avg(self) -> float:
        if not self.scores:
            return 0.0
        total = sum(s["scores"].get("overall_score", 0) for s in self.scores)
        return round(total / len(self.scores), 2)

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "generated_at": self.generated_at,
            "total_questions": len(self.scores),
            "average_score": self._overall_avg(),
            "results": self.scores,
        }

    def to_html(self) -> str:
        """Render an HTML report and return the temp file path."""
        avg = self._overall_avg()
        rows = ""
        for i, item in enumerate(self.scores, 1):
            s = item["scores"]
            rows += f"""
            <tr>
              <td>{i}</td>
              <td>{item['question'][:80]}...</td>
              <td>{s.get('relevance', 0)}/10</td>
              <td>{s.get('technical_depth', 0)}/10</td>
              <td>{s.get('communication', 0)}/10</td>
              <td>{s.get('star_structure', 0)}/10</td>
              <td><strong>{s.get('overall_score', 0)}/10</strong></td>
              <td>{s.get('feedback', '')}</td>
            </tr>"""

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Interview Report - {self.session_id}</title>
  <style>
    body {{ font-family: Arial, sans-serif; max-width: 1100px; margin: 40px auto; padding: 20px; }}
    h1 {{ color: #2c3e50; }} h2 {{ color: #34495e; }}
    .score-badge {{ background: #27ae60; color: white; padding: 10px 20px;
                   border-radius: 8px; font-size: 1.5em; display: inline-block; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
    th {{ background: #2c3e50; color: white; padding: 10px; text-align: left; }}
    td {{ padding: 8px 10px; border-bottom: 1px solid #ecf0f1; vertical-align: top; }}
    tr:nth-child(even) {{ background: #f8f9fa; }}
  </style>
</head>
<body>
  <h1>AI Interview Coach &mdash; Session Report</h1>
  <p>Session ID: <code>{self.session_id}</code> &nbsp;|&nbsp; Generated: {self.generated_at}</p>
  <h2>Overall Score: <span class="score-badge">{avg} / 10</span></h2>
  <table>
    <thead>
      <tr>
        <th>#</th><th>Question</th><th>Relevance</th><th>Depth</th>
        <th>Communication</th><th>STAR</th><th>Overall</th><th>Feedback</th>
      </tr>
    </thead>
    <tbody>{rows}</tbody>
  </table>
</body>
</html>"""
        tmp = Path(tempfile.mktemp(suffix=".html"))
        tmp.write_text(html, encoding="utf-8")
        return str(tmp)
