import json

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.ai.prompts import CODE_REVIEW_SYSTEM
from app.ai.provider import AIProvider, call_structured
from app.models import CodingProblem, CodingSubmission, User
from app.repositories.content import CodingRepository
from app.schemas.ai_contracts import CodeReview
from app.schemas.coding import (
    RunCodeRequest,
    RunCodeResponse,
    SubmitCodeRequest,
    SubmissionOut,
    TestResult,
)
from app.services.gamification_service import GamificationService
from app.services.runner import CodeRunner


class CodingService:
    def __init__(self, db: Session, ai: AIProvider):
        self.db = db
        self.ai = ai
        self.repo = CodingRepository(db)
        self.runner = CodeRunner()

    def run_adhoc(self, payload: RunCodeRequest) -> RunCodeResponse:
        result = self.runner.run(payload.language, payload.code, payload.stdin)
        return RunCodeResponse(
            stdout=result.stdout, stderr=result.stderr, exit_code=result.exit_code,
            timed_out=result.timed_out, runtime_ms=result.runtime_ms,
        )

    def submit(self, user: User, problem_id: int, payload: SubmitCodeRequest) -> SubmissionOut:
        problem = self.repo.get_problem(problem_id)
        if not problem:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Problem not found")

        results, max_runtime = self._run_tests(problem, payload)
        passed_count = sum(1 for r in results if r.passed)
        total = len(results)
        if any(r.error == "Time limit exceeded" for r in results):
            submission_status = "timeout"
        elif passed_count == total:
            submission_status = "passed"
        elif any(r.error for r in results):
            submission_status = "error"
        else:
            submission_status = "failed"

        review = self._review(problem, payload, results)

        submission = self.repo.create_submission(
            user_id=user.id,
            problem_id=problem.id,
            language=payload.language,
            code=payload.code,
            status=submission_status,
            passed_count=passed_count,
            total_count=total,
            results_json=json.dumps([r.model_dump() for r in results]),
            review_json=review.model_dump_json() if review else "{}",
            runtime_ms=max_runtime,
        )
        gamification = GamificationService(self.db)
        xp = gamification.award(user, "coding_submitted", {"problem_id": problem.id})
        if submission_status == "passed":
            xp += gamification.award(user, "coding_passed", {"problem_id": problem.id})

        return self._to_out(submission, results, review, xp)

    # --- internals ----------------------------------------------------------
    def _run_tests(
        self, problem: CodingProblem, payload: SubmitCodeRequest
    ) -> tuple[list[TestResult], int]:
        visible = json.loads(problem.visible_tests_json)
        hidden = json.loads(problem.hidden_tests_json)
        results: list[TestResult] = []
        max_runtime = 0
        for i, (test, is_hidden) in enumerate(
            [(t, False) for t in visible] + [(t, True) for t in hidden]
        ):
            run = self.runner.run(payload.language, payload.code, test["input"])
            max_runtime = max(max_runtime, run.runtime_ms)
            actual = run.stdout.strip()
            expected = str(test["expected"]).strip()
            error = None
            if run.timed_out:
                error = "Time limit exceeded"
            elif run.exit_code != 0:
                error = (run.stderr or "Runtime error").strip()[:500]
            passed = error is None and actual == expected
            results.append(
                TestResult(
                    index=i,
                    hidden=is_hidden,
                    passed=passed,
                    input=None if is_hidden else test["input"],
                    expected=None if is_hidden else expected,
                    actual=None if is_hidden else actual[:500],
                    error=error if not is_hidden else ("hidden test failed" if error else None),
                )
            )
        return results, max_runtime

    def _review(self, problem, payload, results) -> CodeReview | None:
        try:
            results_summary = json.dumps(
                [{"index": r.index, "passed": r.passed, "error": r.error} for r in results]
            )
            return call_structured(
                self.ai,
                CodeReview,
                system=CODE_REVIEW_SYSTEM,
                messages=[
                    {
                        "role": "user",
                        "content": f"<problem>\n{problem.description[:4000]}\n</problem>\n"
                        f"<code language=\"{payload.language}\">\n{payload.code[:8000]}\n</code>\n"
                        f"<test_results>{results_summary}</test_results>",
                    }
                ],
                chain="code_review",
                max_tokens=1000,
            )
        except RuntimeError:
            return None  # review is best-effort; submission result stands on its own

    @staticmethod
    def _to_out(submission: CodingSubmission, results, review, xp: int) -> SubmissionOut:
        return SubmissionOut(
            id=submission.id,
            problem_id=submission.problem_id,
            language=submission.language,
            status=submission.status,
            passed_count=submission.passed_count,
            total_count=submission.total_count,
            results=results,
            review=review,
            runtime_ms=submission.runtime_ms,
            xp_awarded=xp,
            created_at=submission.created_at,
        )
