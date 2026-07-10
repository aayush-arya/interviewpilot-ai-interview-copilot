PASSING_CODE = "a, b = map(int, input().split())\nprint(a + b)\n"
FAILING_CODE = "a, b = map(int, input().split())\nprint(a - b)\n"
LOOPING_CODE = "while True:\n    pass\n"


def test_run_adhoc(client, auth_headers):
    r = client.post(
        "/api/v1/coding/run",
        json={"language": "python", "code": "print(int(input()) * 2)", "stdin": "21"},
        headers=auth_headers,
    )
    assert r.status_code == 200, r.text
    assert r.json()["stdout"].strip() == "42"


def test_submit_pass(client, auth_headers):
    problems = client.get("/api/v1/coding/problems", headers=auth_headers).json()
    pid = problems[0]["id"]
    r = client.post(
        f"/api/v1/coding/problems/{pid}/submit",
        json={"language": "python", "code": PASSING_CODE},
        headers=auth_headers,
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["status"] == "passed"
    assert body["passed_count"] == body["total_count"] == 2
    assert body["review"] is not None
    assert body["xp_awarded"] >= 70  # submit + pass XP
    # hidden test inputs are not leaked
    hidden = [t for t in body["results"] if t["hidden"]]
    assert hidden and all(t["input"] is None for t in hidden)


def test_submit_fail(client, auth_headers):
    problems = client.get("/api/v1/coding/problems", headers=auth_headers).json()
    pid = problems[0]["id"]
    body = client.post(
        f"/api/v1/coding/problems/{pid}/submit",
        json={"language": "python", "code": FAILING_CODE},
        headers=auth_headers,
    ).json()
    assert body["status"] == "failed"
    assert body["passed_count"] < body["total_count"]


def test_timeout(client, auth_headers):
    r = client.post(
        "/api/v1/coding/run",
        json={"language": "python", "code": LOOPING_CODE, "stdin": ""},
        headers=auth_headers,
    )
    assert r.status_code == 200
    assert r.json()["timed_out"] is True


def test_unknown_language_rejected(client, auth_headers):
    r = client.post(
        "/api/v1/coding/run",
        json={"language": "cobol", "code": "x", "stdin": ""},
        headers=auth_headers,
    )
    assert r.status_code == 422
