# AI Workflows & Prompt Engineering Strategy

All AI access goes through `app/ai/provider.py` (`AIProvider` ABC). `ClaudeProvider` uses the Anthropic SDK; `MockAIProvider` returns deterministic, schema-valid responses for offline/CI use. Model is configurable via `AI_MODEL` env (default `claude-sonnet-4-6`; use a stronger model for resume analysis via `AI_MODEL_DEEP`).

## Prompt design principles used throughout (`app/ai/prompts.py`)

1. **Role + rubric + output contract.** Every system prompt sets a persona ("senior interviewer at {company}"), an explicit behavioral rubric (never reveal answers, one question at a time, challenge wrong claims), and a strict JSON output schema when structured data is needed.
2. **JSON mode via prefilling.** For structured outputs the request appends an assistant prefill of `{` and instructs "Respond with only a JSON object matching …". Responses are parsed with a tolerant extractor (`extract_json`) that strips code fences and trailing prose, then validated; on validation failure the call is retried once with the error appended.
3. **Conversation memory.** The interviewer chain replays the persisted transcript as alternating user/assistant messages — no summarization needed at typical interview lengths (≤ 20 turns). Long-session summarization is a roadmap item.
4. **Resume awareness.** When the user has an analyzed resume, a ~400-token digest (skills, experience, gaps) is injected into the interviewer system prompt: questions reference the candidate's actual projects.
5. **Prompt chaining, not one mega-prompt.** Each turn runs two focused calls (coach evaluation, then next question) instead of one overloaded call — cheaper retries, independently testable, and the coach rubric can't leak into interviewer behavior.

## Chains

### 1. Resume Analysis (`ResumeService`)
```
PDF → pypdf text extraction
  → CHAIN A "analyst": scores (ATS/recruiter/technical/communication/confidence),
       issues[], missing_skills[], keyword_gaps[], grammar_fixes[]   [JSON]
  → CHAIN B "writer": improved_resume, cover_letter, linkedin_summary [markdown sections]
```
Chain B receives Chain A's issue list so rewrites target detected problems (prompt chaining with intermediate grounding).

### 2. Interview Plan (`PlanService`)
Resume digest + target role + deadline → 30-day roadmap JSON (`days[]`, `weekly_goals[]`, `skill_gaps[]`, `priority_topics[]`). Deadline compresses the schedule: the prompt receives `days_available` and must fit phases inside it.

### 3. Mock Interview turn (`InterviewService.answer`)
```
answer received
 ├─ COACH: system=coach rubric, user=Q+A → {score 0-10, good, weak, faang_view, ideal_answer}
 ├─ ADAPTIVE DIFFICULTY: mean(last 2 coach scores) ≥ 7.5 → harder; ≤ 4 → easier
 └─ INTERVIEWER: system=persona(track, company style, difficulty, resume digest)
                 messages=[full transcript] → next question (follow-up or new topic)
```
Company style presets (`COMPANY_STYLES`) adjust tone and emphasis: Google → algorithms + "why", Amazon → Leadership Principles woven into technical follow-ups, Goldman → puzzles + low-level details, startups → pragmatism + breadth, service-based → fundamentals + syntax fluency.

### 4. Session Feedback (`FeedbackService`)
Transcript + per-turn coach scores → synthesis call → report JSON (5 dimension scores, hiring recommendation with the standard 4-tier scale, strengths[], improvements[]). Dimension scores are **anchored**: the prompt includes the numeric coach scores so the synthesis can't hallucinate a grade inconsistent with per-turn evidence.

### 5. Code Review (`CodingService`)
Problem statement + code + test results → review JSON: correctness notes, time/space complexity, edge cases missed, code-quality issues, optimization suggestions, verdict. Test results are computed by the runner **first** and given to the model — the model never guesses whether tests passed.

## Evaluation pipeline

- `tests/test_ai_contracts.py` validates every Mock response against the same Pydantic schemas used to parse real Claude output — contract drift breaks CI.
- `extract_json` + single retry-with-error keeps malformed-output rate near zero in production.
- Every AI call is logged to `activity/ai` logger with latency, token usage, and chain name for cost monitoring.
- Golden-set regression (roadmap): replay 20 recorded transcripts through the coach chain and diff score distribution on model upgrades.

## Cost controls
Answer length capped (4k chars), transcript replay capped at 40 messages, `max_tokens` tuned per chain (coach 700, interviewer 300, report 1200, resume 2500).
