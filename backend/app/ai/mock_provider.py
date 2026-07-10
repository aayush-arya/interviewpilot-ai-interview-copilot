"""Deterministic offline AI provider.

Used when ANTHROPIC_API_KEY is absent and in the test suite. Every structured
response validates against app.schemas.ai_contracts (enforced by tests), and
behavior is a plausible simulation: coach scores react to answer quality
signals, the interviewer asks topic-relevant questions and follow-ups.
"""
import hashlib
import json

from app.ai.provider import AIProvider

_QUESTION_BANK: dict[str, list[str]] = {
    "technical": [
        "Let's start simple: can you explain what happens in {topic} when you need to handle concurrent access to shared state?",
        "Interesting. Now, how would you debug a memory issue in a {topic} application in production?",
        "You mentioned some assumptions there — what are the trade-offs of the approach you described, and when would it break down?",
        "Let's go deeper: walk me through how you would optimize a slow {topic} operation you've encountered in a real project.",
        "How does {topic} behave under failure, and how would you design for graceful degradation?",
        "Suppose your {topic} code works on your machine but fails intermittently in production. Walk me through your debugging process step by step.",
        "Explain the difference between the two most commonly confused concepts in {topic}, and when choosing the wrong one actually hurts.",
        "How would you test {topic} code properly? Take me from unit tests up to what you'd monitor in production.",
        "Walk me through the memory model / lifecycle relevant to {topic} — what happens from allocation to cleanup?",
        "If you had to explain the internals of {topic} to a junior engineer, which mechanism would you start with and why?",
        "Tell me about the worst performance bug you can imagine in {topic}. How would it manifest and how would you find it?",
        "What changes in your {topic} approach when the data no longer fits in memory on one machine?",
    ],
    "behavioral": [
        "Tell me about a time you had a serious disagreement with a teammate about a technical decision. What happened?",
        "You described the situation — what was the measurable result, and what would you do differently today?",
        "Tell me about a project that failed. What was your specific role in that failure?",
        "Describe a time you had to learn something completely new under a tight deadline.",
        "Tell me about a time you took ownership of a problem that wasn't officially yours.",
        "Describe a situation where you received hard critical feedback. How did you respond?",
        "Tell me about a time you had to deliver bad news to a stakeholder or manager.",
        "Give me an example of a time you simplified something complex — a system, a process, or a decision.",
        "Tell me about a time you had to work with a difficult or underperforming teammate.",
        "Describe your proudest technical achievement. Why that one?",
        "Tell me about a time you missed a deadline. What did you do when you realized you would miss it?",
        "Describe a time you influenced a decision without having authority.",
    ],
    "system_design": [
        "Let's design {topic}. Before anything else — what clarifying questions would you ask, and what are the core functional requirements?",
        "Good. Give me rough capacity estimates: users, requests per second, storage growth per year.",
        "Walk me through your data model and API design for the write path.",
        "How would you introduce caching here, and what consistency problems does that create?",
        "Your service just went viral and traffic is 50x. What breaks first, and how do you scale it?",
        "Where do you place queues in this design, and what happens when a consumer falls behind?",
        "Pick your database for this system and defend the choice — SQL or NoSQL, and why?",
        "How does your design handle a full region outage? Walk me through the failover.",
        "What does the read path look like at p99? Where is latency hiding in your design?",
        "How would you shard the data as it grows, and what re-sharding pain are you signing up for?",
        "What would you monitor in this system, and what alert would wake you up at 3am?",
        "Which single component of your design would you rewrite first at 10x scale, and to what?",
    ],
    "hr": [
        "Walk me through your career so far and what you're looking for in your next role.",
        "Why do you want to work here specifically, rather than a similar company?",
        "Where do you see yourself in five years, and how does this role get you there?",
        "What compensation expectations do you have, and how flexible are they?",
        "Why are you leaving (or why did you leave) your current position?",
        "What kind of team environment do you do your best work in?",
        "Tell me about a gap or transition in your resume — what were you doing during that time?",
        "What would your current manager say is your biggest strength and biggest weakness?",
        "What questions do you have for me about the team or the company?",
    ],
}

# Keyword → rubric checklist. The mock coach picks the best-matching rubric so the
# "must-have points" are relevant to the question actually asked.
_KEY_POINT_RUBRICS: list[tuple[tuple[str, ...], list[str]]] = [
    (("concurrent", "shared state", "thread", "race"), [
        "Define the race-condition risk: two writers or read-modify-write on shared data",
        "Name at least two mechanisms: locks/mutexes, atomic operations, or concurrent collections",
        "Explain the trade-off: contention and deadlock risk vs. safety",
        "Mention lock-free alternatives for read-heavy loads (immutability, copy-on-write)",
        "Give a concrete example from a real project with the outcome",
    ]),
    (("memory", "leak", "allocation", "lifecycle"), [
        "Describe reproduction/observation first: metrics, heap dumps, profiler output",
        "Name concrete tools for the stack (profiler, heap analyzer, GC logs)",
        "Distinguish leak vs. legitimate growth vs. fragmentation",
        "Explain the common root causes: unbounded caches, listeners never removed, closures holding references",
        "State the fix AND the regression guard (test or alert) you'd add",
    ]),
    (("debug", "intermittent", "production", "fails"), [
        "Start with evidence gathering: logs, metrics, traces — not guessing",
        "Form a hypothesis and state how you'd falsify it",
        "Mention environment diffs: config, data volume, concurrency, clock/timezone",
        "Explain safe reproduction: staging with production-like data or feature-flagged canary",
        "Close the loop: root cause, fix, and the monitor/test that prevents recurrence",
    ]),
    (("trade-off", "break down", "assumptions", "confused concepts"), [
        "State both sides explicitly — what you gain and what you pay",
        "Quantify where possible (latency, memory, cost, complexity)",
        "Name the boundary condition where the chosen approach stops working",
        "Offer the alternative you'd switch to past that boundary",
        "Anchor with a real scenario where you saw the trade-off bite",
    ]),
    (("optimize", "slow", "performance", "latency", "p99"), [
        "Measure before optimizing: profile and identify the actual bottleneck",
        "Name the specific hotspot type: I/O, N+1 queries, allocation churn, algorithmic complexity",
        "Give the fix hierarchy: algorithm > data access pattern > caching > hardware",
        "Quantify the improvement you achieved or would target",
        "Mention the cost of the optimization: complexity, staleness, memory",
    ]),
    (("test", "monitor",), [
        "Cover the pyramid: unit → integration → end-to-end, with rough proportions",
        "Name what each layer catches and what it can't",
        "Include edge cases and failure-path tests, not just happy path",
        "Extend to production: metrics, alerts, and what 'healthy' looks like",
        "Mention CI enforcement so tests actually gate merges",
    ]),
    (("requirements", "clarifying", "functional"), [
        "Ask about scale first: users, QPS, data size",
        "Separate functional from non-functional requirements (latency, availability, consistency)",
        "Identify the core use cases and explicitly cut scope",
        "State assumptions out loud and get agreement before designing",
        "Mention read/write ratio — it drives the whole design",
    ]),
    (("capacity", "estimates", "storage growth"), [
        "Start from daily active users and requests per user",
        "Convert to QPS with the peak factor (2-3x average)",
        "Estimate per-record size and multiply out to storage per year",
        "Derive bandwidth and cache-size implications",
        "Sanity-check the numbers — state when they'd force sharding",
    ]),
    (("caching", "consistency"), [
        "Choose the pattern: cache-aside, read-through, or write-through — and justify it",
        "State the staleness problem caching creates and your invalidation strategy",
        "Mention TTLs vs. explicit invalidation trade-off",
        "Address the thundering-herd / cache-stampede problem",
        "Say what you would NOT cache and why",
    ]),
    (("shard", "scale", "50x", "10x", "region", "failover", "queue"), [
        "Identify the first bottleneck concretely (usually the database or a hot partition)",
        "Explain horizontal scaling for stateless tiers behind a load balancer",
        "Give a shard key and discuss hot-key skew",
        "Cover failure handling: replication, failover, and data-loss window (RPO/RTO)",
        "Mention backpressure: what happens when a downstream component falls behind",
    ]),
    (("disagreement", "conflict", "difficult", "influence"), [
        "Situation: name the stakes and why the disagreement mattered",
        "Show you sought to understand the other position first",
        "Describe resolving on evidence (data, prototype, doc), not seniority",
        "Result: what shipped and what the measurable outcome was",
        "Reflection: what you'd do differently — shows growth",
    ]),
    (("failed", "failure", "missed a deadline", "bad news"), [
        "Own your specific contribution to the failure — no blame-shifting",
        "Show early communication the moment risk appeared",
        "Describe concrete damage control, not just apology",
        "State the lesson as a changed behavior, not a platitude",
        "End with a later example where the changed behavior paid off",
    ]),
    (("career", "five years", "why do you want", "leaving", "compensation", "gap"), [
        "Keep the narrative coherent: each move should have a reason",
        "Connect your goal specifically to THIS role and company",
        "Stay positive about previous employers",
        "Be direct and researched on numbers if compensation is asked",
        "End with genuine questions that show you researched the team",
    ]),
]

_DEFAULT_KEY_POINTS = [
    "Open with a one-sentence direct answer to the question",
    "Support it with a concrete example from real experience",
    "Quantify the impact (latency, throughput, cost, or time saved)",
    "State the main trade-off or limitation of your approach",
    "Close with when you would choose an alternative",
]


def _key_points_for(question: str) -> list[str]:
    q = question.lower()
    best: list[str] | None = None
    best_hits = 0
    for keywords, points in _KEY_POINT_RUBRICS:
        hits = sum(1 for k in keywords if k in q)
        if hits > best_hits:
            best_hits = hits
            best = points
    return best or _DEFAULT_KEY_POINTS

_STRONG_SIGNALS = (
    "because", "trade-off", "tradeoff", "complexity", "o(", "for example", "in my project",
    "measured", "latency", "throughput", "index", "cache", "test", "edge case", "instead",
)


def _h(text: str, mod: int) -> int:
    return int(hashlib.sha256(text.encode()).hexdigest(), 16) % mod


class MockAIProvider(AIProvider):
    def complete(self, *, system, messages, chain, max_tokens=800, json_mode=False, deep=False):
        handler = getattr(self, f"_{chain}", None)
        if handler is None:
            raise ValueError(f"MockAIProvider has no handler for chain '{chain}'")
        return handler(system, messages)

    # --- plain-text chains -------------------------------------------------
    def _resume_digest(self, system, messages):
        return (
            "Mid-level software engineer, ~3 years experience. Skills: Java, Spring Boot, SQL, "
            "React basics, Docker. Notable projects: an order-management microservice and a "
            "log-analytics dashboard. Gaps: no cloud certifications, limited system design "
            "exposure, metrics missing from most accomplishments."
        )

    def _interviewer(self, system, messages):
        import re

        from app.ai.companies import signature_questions
        from app.ai.question_bank import get_question

        # Classify from the persona header ONLY — the full prompt may contain a
        # resume digest whose free text mentions e.g. "system design".
        header = system.split("\n\nRules", 1)[0]
        if "behavioral interview" in header:
            session_type = "behavioral"
        elif "system design interview" in header:
            session_type = "system_design"
        elif "HR interviewer" in header:
            session_type = "hr"
        else:
            session_type = "technical"
        topic = "Data Structures & Algorithms"
        if "interview on:" in header:
            topic = header.split("interview on:")[1].split("\n")[0].strip().rstrip(".").split(" at ")[0].strip()
        elif "conducting a " in header:
            seg = header.split("conducting a ", 1)[1]
            topic = seg.split(" technical interview")[0].strip()

        difficulty_match = re.search(r"Current difficulty: (easy|medium|hard)", system)
        difficulty = difficulty_match.group(1) if difficulty_match else "medium"

        company_match = re.search(r" at ([^.\n]{2,60})\.", system.split("\n")[0])
        company = company_match.group(1).strip() if company_match else None

        asked = sum(1 for m in messages if m["role"] == "assistant")

        if session_type == "technical":
            # Interleave company signature questions (every 3rd question) with the
            # topic × difficulty bank (60 distinct questions per tier).
            company_bank = signature_questions(company) if company else []
            if company_bank and asked % 3 == 1:
                return company_bank[(asked // 3) % len(company_bank)]
            return get_question(topic, difficulty, asked)

        bank = _QUESTION_BANK[session_type]
        return bank[asked % len(bank)].format(topic=topic)

    # --- structured chains -------------------------------------------------
    def _coach(self, system, messages):
        content = messages[-1]["content"]
        question = ""
        answer = content
        if "<question>" in content:
            question = content.split("<question>", 1)[1].split("</question>", 1)[0]
        if "<answer>" in content:
            answer = content.split("<answer>", 1)[1].split("</answer>", 1)[0]
        answer = answer.lower()

        key_points = _key_points_for(question)
        signal_hits = sum(1 for s in _STRONG_SIGNALS if s in answer)
        covered = sum(1 for p in key_points if any(w in answer for w in p.lower().split()[:3]))
        length_score = min(len(answer) // 120, 3)  # up to 3 points for substance
        score = max(1, min(10, 1 + length_score + min(signal_hits, 3) + min(covered, 3)))

        ideal = (
            "A full-marks answer covers, in order: "
            + "; ".join(f"({i + 1}) {p[0].lower() + p[1:]}" for i, p in enumerate(key_points))
            + "."
        )
        return json.dumps({
            "score": score,
            "good": "You structured the answer and grounded it in concrete details."
            if score >= 6 else "You attempted the question and stayed on topic.",
            "weak": "You did not discuss trade-offs or quantify the impact — senior candidates always do."
            if score < 8 else "Minor: tighten the opening; you took a while to get to the point.",
            "faang_view": "A FAANG interviewer scores structure, depth, and trade-off awareness. "
            f"This answer would currently calibrate around {'L4/L5' if score >= 7 else 'L3 borderline' if score >= 5 else 'below the bar'}.",
            "ideal_answer": ideal,
            "key_points": key_points,
        })

    def _resume_analysis(self, system, messages):
        base = 55 + _h(messages[-1]["content"], 20)  # 55-74, deterministic per resume
        return json.dumps({
            "ats_score": base, "recruiter_score": base + 4, "technical_score": base + 2,
            "communication_score": base - 3, "confidence_score": base,
            "missing_skills": ["Kubernetes", "System design vocabulary", "Cloud certification (AWS SAA)"],
            "weak_descriptions": ["'Worked on backend services' — no scope, stack, or impact stated"],
            "grammar_issues": ["Inconsistent tense: mixes past and present within the same role"],
            "ats_issues": ["Skills listed inside a table — many ATS parsers drop table content"],
            "keyword_gaps": ["REST API", "microservices", "CI/CD", "unit testing"],
            "experience_gaps": ["No measurable outcomes for the most recent 12 months"],
            "improvement_suggestions": [
                "Rewrite every bullet as Action + Technology + Measurable result",
                "Move skills out of tables into a plain comma-separated section",
                "Add a 2-line summary targeting the specific role",
            ],
            "summary": "A solid mid-level resume weakened by vague bullets and ATS-hostile "
            "formatting. Quantifying impact and flattening the layout would raise every score.",
        })

    def _resume_docs(self, system, messages):
        return json.dumps({
            "improved_resume": "# Improved Resume\n\n## Summary\nBackend engineer with 3+ years "
            "building Java/Spring Boot microservices. Cut order-processing latency [40%] by "
            "redesigning the queue pipeline.\n\n## Experience\n**Software Engineer** — Acme Corp\n"
            "- Designed and shipped an order-management microservice (Spring Boot, PostgreSQL, "
            "Redis) handling [50k] orders/day\n- Reduced p95 API latency from [800ms] to [200ms] "
            "by adding read-through caching and query indexing\n- Introduced CI/CD (GitHub "
            "Actions) cutting release time from days to [30 min]\n\n## Skills\nJava, Spring Boot, "
            "SQL, PostgreSQL, Redis, Docker, React, Git, CI/CD",
            "cover_letter": "Dear Hiring Manager,\n\nI'm applying for the Backend Engineer role. "
            "In my current position I own an order-management microservice processing [50k] "
            "orders daily, where I cut p95 latency by [75%]. Your team's focus on scalable "
            "services matches exactly the work I want to go deeper on...\n\nSincerely,\n[Name]",
            "linkedin_summary": "I'm a backend engineer who likes making slow systems fast. Over "
            "the last three years I've built Java/Spring Boot microservices, redesigned queue "
            "pipelines, and learned that most performance problems are really data-model "
            "problems. Currently going deep on distributed systems and cloud architecture. "
            "Open to backend roles where reliability and scale actually matter.",
        })

    def _plan(self, system, messages):
        requested = 30
        content = messages[-1]["content"]
        if "days_available:" in content:
            try:
                requested = max(7, min(60, int(content.split("days_available:")[1].split()[0])))
            except ValueError:
                pass
        topics = [
            "Data Structures: arrays & strings", "Linked lists & stacks", "Trees & BST",
            "Graphs & BFS/DFS", "Dynamic programming basics", "SQL & indexing deep-dive",
            "OOP & design patterns", "Operating systems fundamentals", "Networking essentials",
            "System design: fundamentals", "System design: caching & queues", "Mock interview checkpoint",
            "Behavioral: STAR stories", "Spring Boot internals", "REST API design",
        ]
        days = [
            {
                "day": i + 1,
                "topic": topics[i % len(topics)],
                "goals": [f"Study {topics[i % len(topics)]} for 90 minutes", "Solve 2 practice problems", "Write a 5-line summary of what you learned"],
            }
            for i in range(requested)
        ]
        return json.dumps({
            "days": days,
            "weekly_goals": ["Complete 2 mock interviews", "Solve 10 coding problems", "Revise one weak topic end-to-end"],
            "skill_gaps": ["System design vocabulary", "DP problem recognition", "Quantified behavioral stories"],
            "priority_topics": ["Data Structures & Algorithms", "System Design", "SQL"],
        })

    def _report(self, system, messages):
        content = messages[-1]["content"]
        scores = [int(s) for s in _extract_scores(content)]
        avg10 = sum(scores) / len(scores) if scores else 5.5
        base = int(avg10 * 10)
        reco = ("strong_hire" if base >= 85 else "hire" if base >= 70
                else "lean_hire" if base >= 50 else "no_hire")
        return json.dumps({
            "overall": base, "communication": max(0, base - 5), "confidence": max(0, base - 8),
            "technical_accuracy": min(100, base + 3), "problem_solving": base,
            "hiring_recommendation": reco,
            "summary": "The candidate showed consistent engagement across the session. Answers "
            "were strongest where grounded in concrete project experience and weakest on "
            "trade-off analysis. With targeted practice on articulating depth, the next "
            "session should score noticeably higher.",
            "strengths": ["Stayed structured under follow-up pressure", "Grounded answers in real project work"],
            "improvements": ["Always state trade-offs before being asked", "Quantify results (latency, throughput, cost) in every example", "Practice concise 60-second openings"],
        })

    def _code_review(self, system, messages):
        passed_all = '"passed": false' not in messages[-1]["content"]
        return json.dumps({
            "verdict": "good" if passed_all else "needs_work",
            "time_complexity": "O(n)",
            "space_complexity": "O(n)",
            "correctness_notes": "The solution handles the main cases correctly."
            if passed_all else "The solution fails at least one test — trace the failing input through your loop by hand.",
            "edge_cases_missed": [] if passed_all else ["Empty input", "Single-element input"],
            "quality_issues": ["Variable names could be more descriptive (e.g. `d` → `seen`)"],
            "optimizations": ["A single-pass hash-map approach avoids the second loop"],
            "score": 82 if passed_all else 55,
        })


def _extract_scores(content: str) -> list[str]:
    import re

    return re.findall(r"score[\"']?\s*[:=]\s*(\d+)", content)
