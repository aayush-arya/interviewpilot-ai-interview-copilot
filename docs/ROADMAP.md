# Future Enhancements

**Near-term**
- Token streaming for interviewer questions (SSE) — perceived-latency win.
- Server-side voice: Whisper STT + high-quality TTS; per-answer prosody metrics (pace, pauses, confidence estimation from audio features).
- ChromaDB question bank: embed seeded + generated questions, retrieve nearest for company/topic grounding (interface seam: `QuestionSource`).
- Webcam analysis (opt-in): posture/eye-contact suggestions via on-device MediaPipe (privacy-preserving).
- Email summaries (SES) + calendar (.ics) interview reminders; PDF report export (reportlab).

**Product**
- Coding contest mode: timed rooms, ELO ranking, difficulty ladder (schema already supports submissions/events).
- Peer mock interviews (WebRTC) with AI as evaluator.
- Interview replay with turn-by-turn coach overlay (transcript data already persisted).
- Team/enterprise workspaces: recruiter dashboards, candidate cohorts, custom question banks.
- Payments (Stripe) + subscription tiers; usage metering already event-logged.

**Platform**
- Judge0/Firecracker execution backend for multi-tenant code running.
- Alembic migration baseline + zero-downtime deploy playbook.
- Golden-set AI regression suite gating model upgrades.
- Mobile app (React Native) reusing the API layer.
