"""Contract tests for the question bank, company profiles and problem bank."""
from app.ai.companies import COMPANIES, company_blurb, signature_questions
from app.ai.mock_provider import MockAIProvider
from app.ai.prompts import interviewer_system
from app.ai.question_bank import TOPIC_CONCEPTS, get_question, questions_per_topic_difficulty
from app.problem_bank import bank_problems

REQUIRED_LANGS = {"python", "javascript", "java", "cpp"}


# ---- Interview question bank -------------------------------------------------
def test_every_topic_has_50_plus_questions_per_difficulty():
    for topic in TOPIC_CONCEPTS:
        assert questions_per_topic_difficulty(topic) >= 50, topic


def test_questions_are_topic_specific_and_vary():
    java_questions = {get_question("Java", "medium", i) for i in range(20)}
    assert len(java_questions) >= 15  # no early repetition
    assert any("HashMap" in q or "JVM" in q or "String" in q for q in java_questions)
    react_question = get_question("React", "easy", 0)
    assert "Java" not in react_question


def test_difficulty_changes_the_question():
    easy = get_question("SQL", "easy", 0)
    hard = get_question("SQL", "hard", 0)
    assert easy != hard


def test_mock_interviewer_uses_topic_and_difficulty():
    mock = MockAIProvider()
    system = interviewer_system("technical", "Java", None, "hard", "")
    q1 = mock.complete(system=system, messages=[{"role": "user", "content": "ready"}],
                       chain="interviewer")
    system_easy = interviewer_system("technical", "Java", None, "easy", "")
    q2 = mock.complete(system=system_easy, messages=[{"role": "user", "content": "ready"}],
                       chain="interviewer")
    assert q1 != q2  # difficulty tier changes the question


def test_mock_interviewer_ignores_resume_digest_when_classifying():
    # Regression: a resume digest mentioning "system design" must not flip a
    # technical session into the system-design question bank.
    mock = MockAIProvider()
    digest = "Mid-level engineer. Gaps: limited system design exposure, behavioral stories weak."
    system = interviewer_system("technical", "Java", None, "hard", digest)
    question = mock.complete(system=system, messages=[{"role": "user", "content": "ready"}],
                             chain="interviewer")
    assert "Let's design" not in question
    assert "clarifying questions" not in question


def test_mock_interviewer_asks_company_signature_questions():
    mock = MockAIProvider()
    system = interviewer_system("technical", "Java", "Stripe", "medium", "")
    # asked index 1 (one assistant message already) → company signature slot
    messages = [
        {"role": "user", "content": "ready"},
        {"role": "assistant", "content": "q1"},
        {"role": "user", "content": "answer"},
    ]
    question = mock.complete(system=system, messages=messages, chain="interviewer")
    assert question in signature_questions("Stripe")


# ---- Company profiles ---------------------------------------------------------
def test_company_bank_size_and_shape():
    assert len(COMPANIES) >= 60
    for name, profile in COMPANIES.items():
        assert profile["style"], name
        assert profile["focus"], name
        assert len(profile["questions"]) >= 2, name
        assert company_blurb(name)
        assert "." not in name, f"'{name}' would break mock company parsing"


# ---- Problem bank ---------------------------------------------------------------
def test_problem_bank_generates_valid_problems():
    problems = bank_problems()
    assert len(problems) >= 50
    slugs = [p["slug"] for p in problems]
    assert len(slugs) == len(set(slugs))
    for p in problems:
        assert set(p["starter"].keys()) == REQUIRED_LANGS, p["slug"]
        assert len(p["visible"]) == 2, p["slug"]
        assert len(p["hidden"]) >= 1, p["slug"]
        for case in p["visible"] + p["hidden"]:
            assert case["expected"] != "", p["slug"]
        assert p["difficulty"] in {"easy", "medium", "hard"}, p["slug"]


def test_problem_bank_reference_solutions_spot_checks():
    by_slug = {p["slug"]: p for p in bank_problems()}
    assert by_slug["trapping-rain-water"]["visible"][0]["expected"] == "6"
    assert by_slug["n-queens-count"]["hidden"][0]["expected"] == "92"  # n=8
    assert by_slug["median-two-sorted"]["visible"][1]["expected"] == "2.5"
    assert by_slug["sliding-window-maximum"]["visible"][0]["expected"] == "3 3 5 5 6 7"
    assert by_slug["burst-balloons"]["visible"][0]["expected"] == "167"
    assert by_slug["decode-ways"]["visible"][0]["expected"] == "3"
    assert by_slug["unique-paths"]["visible"][0]["expected"] == "28"
