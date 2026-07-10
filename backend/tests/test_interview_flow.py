GOOD_ANSWER = (
    "I would use a hash map because it gives O(1) lookups; for example, in my project I "
    "measured latency drop from 300ms to 40ms after replacing the nested loop. The trade-off "
    "is extra memory, and I added an index plus a cache with tests covering each edge case."
)


def test_full_interview_flow(client, auth_headers):
    # start
    r = client.post(
        "/api/v1/interviews",
        json={"session_type": "technical", "topic": "Java", "difficulty": "medium"},
        headers=auth_headers,
    )
    assert r.status_code == 201, r.text
    session = r.json()
    assert len(session["turns"]) == 1
    assert session["turns"][0]["question"]

    # answer twice with strong answers → difficulty should escalate
    for _ in range(2):
        r = client.post(
            f"/api/v1/interviews/{session['id']}/answer",
            json={"answer": GOOD_ANSWER},
            headers=auth_headers,
        )
        assert r.status_code == 200, r.text
        body = r.json()
        assert 0 <= body["coach"]["score"] <= 10
        assert body["next_question"]
        assert body["xp_awarded"] > 0

    assert body["difficulty"] == "hard"  # adaptive difficulty went up

    # finish → report
    r = client.post(f"/api/v1/interviews/{session['id']}/finish", headers=auth_headers)
    assert r.status_code == 200, r.text
    report = r.json()
    assert 0 <= report["overall"] <= 100
    assert report["hiring_recommendation"] in {"strong_hire", "hire", "lean_hire", "no_hire"}
    assert report["improvements"]

    # dashboard reflects the session
    dash = client.get("/api/v1/dashboard", headers=auth_headers).json()
    assert dash["sessions_completed"] == 1
    assert dash["xp"] > 0
    assert dash["readiness_percent"] > 0

    # double answer to an already-answered turn is rejected (via new session)
    detail = client.get(f"/api/v1/interviews/{session['id']}", headers=auth_headers).json()
    assert detail["status"] == "completed"


def test_answer_requires_active_session(client, auth_headers):
    r = client.post(
        "/api/v1/interviews/999/answer", json={"answer": "hi"}, headers=auth_headers
    )
    assert r.status_code == 404


def test_finish_without_answers_marks_abandoned(client, auth_headers):
    session = client.post(
        "/api/v1/interviews",
        json={"session_type": "behavioral", "topic": "Behavioral"},
        headers=auth_headers,
    ).json()
    r = client.post(f"/api/v1/interviews/{session['id']}/finish", headers=auth_headers)
    assert r.status_code == 422


def test_voice_metrics_accepted(client, auth_headers):
    session = client.post(
        "/api/v1/interviews",
        json={"session_type": "hr", "topic": "HR"},
        headers=auth_headers,
    ).json()
    r = client.post(
        f"/api/v1/interviews/{session['id']}/answer",
        json={"answer": GOOD_ANSWER, "voice_metrics": {"wpm": 140, "filler_count": 3, "duration_s": 45}},
        headers=auth_headers,
    )
    assert r.status_code == 200
