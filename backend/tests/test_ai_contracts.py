"""Every MockAIProvider structured chain must validate against the real contracts."""
import json

from app.ai.json_utils import extract_json
from app.ai.mock_provider import MockAIProvider
from app.schemas.ai_contracts import (
    CoachEvaluation,
    CodeReview,
    InterviewRoadmap,
    ResumeAnalysis,
    ResumeDocs,
    SessionReport,
)

mock = MockAIProvider()
MSG = [{"role": "user", "content": "sample content with score: 7 and score: 8"}]


def test_coach_contract():
    raw = mock.complete(system="", messages=MSG, chain="coach")
    coach = CoachEvaluation.model_validate(json.loads(raw))
    assert len(coach.key_points) >= 4  # rubric checklist must be substantive
    assert coach.ideal_answer


def test_coach_key_points_match_question():
    msg = [{
        "role": "user",
        "content": "<question>How would you handle concurrent access to shared state?</question>\n"
        "<answer>i dont know</answer>",
    }]
    coach = CoachEvaluation.model_validate(
        json.loads(mock.complete(system="", messages=msg, chain="coach"))
    )
    assert coach.score < 6  # empty answer scores below the bar
    assert any("race" in p.lower() or "lock" in p.lower() for p in coach.key_points)


def test_resume_analysis_contract():
    raw = mock.complete(system="", messages=MSG, chain="resume_analysis")
    ResumeAnalysis.model_validate(json.loads(raw))


def test_resume_docs_contract():
    raw = mock.complete(system="", messages=MSG, chain="resume_docs")
    ResumeDocs.model_validate(json.loads(raw))


def test_plan_contract_respects_days():
    raw = mock.complete(
        system="", messages=[{"role": "user", "content": "days_available: 14"}], chain="plan"
    )
    roadmap = InterviewRoadmap.model_validate(json.loads(raw))
    assert len(roadmap.days) == 14


def test_report_contract():
    raw = mock.complete(system="", messages=MSG, chain="report")
    SessionReport.model_validate(json.loads(raw))


def test_code_review_contract():
    raw = mock.complete(system="", messages=MSG, chain="code_review")
    CodeReview.model_validate(json.loads(raw))


def test_extract_json_variants():
    obj = {"a": 1, "b": "x{y}"}
    assert extract_json(json.dumps(obj)) == obj
    assert extract_json(f"```json\n{json.dumps(obj)}\n```") == obj
    assert extract_json(f"Here you go:\n{json.dumps(obj)}\nHope that helps!") == obj
    assert extract_json('"a": 1}') == {"a": 1}  # prefill without opening brace
