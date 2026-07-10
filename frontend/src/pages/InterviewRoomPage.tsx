import { AnimatePresence, motion } from 'framer-motion';
import { useEffect, useRef, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';

import { apiErrorMessage } from '../api/client';
import { useAnswer, useFinishInterview, useSession } from '../api/hooks';
import { Card, DifficultyChip, ErrorNote, Spinner } from '../components/ui';
import { useVoice } from '../features/useVoice';
import type { CoachEvaluation } from '../types';

interface ChatItem {
  role: 'interviewer' | 'me';
  text: string;
  coach?: CoachEvaluation;
}

export default function InterviewRoomPage() {
  const { sessionId } = useParams();
  const id = Number(sessionId);
  const { data: session, isLoading } = useSession(id);
  const answerMutation = useAnswer(id);
  const finishMutation = useFinishInterview(id);
  const navigate = useNavigate();
  const voice = useVoice();

  const [chat, setChat] = useState<ChatItem[]>([]);
  const [draft, setDraft] = useState('');
  const [difficulty, setDifficulty] = useState('medium');
  const [voiceMode, setVoiceMode] = useState(false);
  const [showCoach, setShowCoach] = useState<CoachEvaluation | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const hydrated = useRef(false);

  // Hydrate chat from persisted transcript (supports resuming a session).
  useEffect(() => {
    if (!session || hydrated.current) return;
    hydrated.current = true;
    const items: ChatItem[] = [];
    for (const turn of session.turns ?? []) {
      items.push({ role: 'interviewer', text: turn.question });
      if (turn.answer) items.push({ role: 'me', text: turn.answer, coach: turn.coach ?? undefined });
    }
    setChat(items);
    setDifficulty(session.difficulty);
  }, [session]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chat, showCoach]);

  // Voice mode: read new interviewer questions aloud.
  useEffect(() => {
    if (!voiceMode || chat.length === 0) return;
    const last = chat[chat.length - 1];
    if (last.role === 'interviewer') voice.speak(last.text);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [chat.length, voiceMode]);

  // Voice transcript flows into the draft as the user speaks.
  useEffect(() => {
    if (voice.listening) setDraft(voice.transcript);
  }, [voice.transcript, voice.listening]);

  if (isLoading || !session) return <div className="py-20"><Spinner label="Loading session…" /></div>;

  const completed = session.status !== 'active';
  const busy = answerMutation.isPending || finishMutation.isPending;

  const send = async () => {
    const text = draft.trim();
    if (!text || busy) return;
    let voiceMetrics: object | undefined;
    if (voice.listening) voiceMetrics = voice.stopListening();
    setChat((c) => [...c, { role: 'me', text }]);
    setDraft('');
    try {
      const res = await answerMutation.mutateAsync({ answer: text, voice_metrics: voiceMetrics });
      setChat((c) => {
        const copy = [...c];
        copy[copy.length - 1] = { ...copy[copy.length - 1], coach: res.coach };
        return [...copy, { role: 'interviewer', text: res.next_question }];
      });
      setDifficulty(res.difficulty);
      setShowCoach(res.coach);
    } catch {
      /* error shown below */
    }
  };

  const finish = async () => {
    voice.stopSpeaking();
    try {
      await finishMutation.mutateAsync();
      navigate('/app/feedback', { state: { sessionId: id } });
    } catch {
      /* error shown below */
    }
  };

  const answeredCount = chat.filter((c) => c.role === 'me').length;

  return (
    <div className="animate-fade-in grid gap-4 lg:grid-cols-3">
      {/* Chat column */}
      <div className="flex min-h-[70vh] flex-col lg:col-span-2">
        <div className="glass mb-3 flex items-center justify-between px-4 py-3">
          <div className="flex items-center gap-2 text-sm font-semibold">
            🎤 {session.topic}
            {session.company && <span className="chip bg-slate-500/15 text-slate-500">{session.company}</span>}
            <DifficultyChip level={difficulty} />
          </div>
          <div className="flex items-center gap-2">
            {voice.supported && (
              <button
                className={`btn text-xs ${voiceMode ? 'bg-brand-600 text-white' : 'btn-ghost'}`}
                onClick={() => { setVoiceMode(!voiceMode); voice.stopSpeaking(); }}
                title="Voice interview mode"
              >
                🗣️ Voice {voiceMode ? 'on' : 'off'}
              </button>
            )}
            <button className="btn-ghost text-xs" onClick={finish} disabled={busy || answeredCount === 0}>
              {finishMutation.isPending ? 'Scoring…' : 'End & get report'}
            </button>
          </div>
        </div>

        <div className="glass flex-1 space-y-4 overflow-y-auto p-4">
          <AnimatePresence initial={false}>
            {chat.map((item, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className={`flex ${item.role === 'me' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                    item.role === 'me'
                      ? 'bg-gradient-to-r from-brand-600 to-violet-600 text-white'
                      : 'border border-slate-200 bg-white dark:border-white/10 dark:bg-white/5'
                  }`}
                >
                  {item.role === 'interviewer' && <div className="mb-1 text-xs font-semibold text-brand-500">Interviewer</div>}
                  {item.text}
                  {item.coach && (
                    <button
                      className="mt-2 block text-xs underline decoration-dotted opacity-80"
                      onClick={() => setShowCoach(item.coach!)}
                    >
                      Coach score: {item.coach.score}/10 — view feedback
                    </button>
                  )}
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
          {answerMutation.isPending && <Spinner label="Interviewer is thinking…" />}
          <div ref={bottomRef} />
        </div>

        {answerMutation.isError && <div className="mt-2"><ErrorNote message={apiErrorMessage(answerMutation.error)} /></div>}
        {finishMutation.isError && <div className="mt-2"><ErrorNote message={apiErrorMessage(finishMutation.error)} /></div>}

        {!completed && (
          <div className="mt-3 flex items-end gap-2">
            {voiceMode && (
              <button
                className={`btn h-[46px] w-[46px] shrink-0 rounded-full text-lg ${
                  voice.listening ? 'animate-pulse-slow bg-rose-600 text-white'
                  : voice.starting ? 'animate-pulse bg-amber-500 text-white'
                  : 'bg-brand-600 text-white'
                }`}
                onClick={() => (voice.listening ? send() : voice.startListening())}
                disabled={voice.starting}
                title={voice.listening ? 'Stop & send' : voice.starting ? 'Requesting microphone…' : 'Start speaking'}
              >
                {voice.listening ? '■' : voice.starting ? '…' : '🎙️'}
              </button>
            )}
            <textarea
              className="input min-h-[46px] resize-y"
              rows={2}
              placeholder={voiceMode ? 'Speak, or type here…' : 'Type your answer… (Enter to send, Shift+Enter for newline)'}
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  send();
                }
              }}
              maxLength={4000}
              disabled={busy}
            />
            <button className="btn-primary h-[46px]" onClick={send} disabled={busy || !draft.trim()}>Send</button>
          </div>
        )}
      </div>

      {/* Coach panel */}
      <div className="space-y-4">
        <Card>
          <div className="mb-2 text-sm font-semibold">🧑‍🏫 AI Coach</div>
          {showCoach ? (
            <div className="space-y-3 text-sm">
              <div className="flex items-center gap-2">
                <div className={`text-2xl font-extrabold ${showCoach.score >= 7 ? 'text-emerald-500' : showCoach.score >= 5 ? 'text-amber-500' : 'text-rose-500'}`}>
                  {showCoach.score}/10
                </div>
                <div className="text-xs text-slate-500">for your last answer</div>
              </div>
              <div>
                <div className="text-xs font-semibold uppercase text-emerald-500">What was good</div>
                <p className="text-slate-600 dark:text-slate-300">{showCoach.good}</p>
              </div>
              <div>
                <div className="text-xs font-semibold uppercase text-rose-500">What was weak</div>
                <p className="text-slate-600 dark:text-slate-300">{showCoach.weak}</p>
              </div>
              <div>
                <div className="text-xs font-semibold uppercase text-violet-500">How FAANG evaluates this</div>
                <p className="text-slate-600 dark:text-slate-300">{showCoach.faang_view}</p>
              </div>
              {showCoach.score < 6 && (
                <div className="rounded-xl border border-rose-500/30 bg-rose-500/10 px-3 py-2 text-xs text-rose-600 dark:text-rose-400">
                  This answer missed the bar — study the checklist below. Every point listed must
                  appear in a full-marks answer.
                </div>
              )}
              {showCoach.key_points?.length > 0 && (
                <div className="rounded-xl border border-amber-500/30 bg-amber-500/5 p-3">
                  <div className="mb-1.5 text-xs font-semibold uppercase text-amber-600 dark:text-amber-400">
                    ✅ A complete answer must cover
                  </div>
                  <ul className="ml-4 list-disc space-y-1 text-slate-600 dark:text-slate-300">
                    {showCoach.key_points.map((point, i) => <li key={i}>{point}</li>)}
                  </ul>
                </div>
              )}
              <details
                key={`ideal-${showCoach.score}-${showCoach.ideal_answer.length}`}
                open={showCoach.score < 6}
                className="rounded-xl border border-slate-200 p-3 dark:border-white/10"
              >
                <summary className="cursor-pointer text-xs font-semibold text-brand-500">
                  {showCoach.score < 6 ? 'Ideal answer (shown because your answer scored below 6)' : 'Show ideal answer'}
                </summary>
                <p className="mt-2 text-slate-600 dark:text-slate-300">{showCoach.ideal_answer}</p>
              </details>
            </div>
          ) : (
            <p className="text-sm text-slate-500">
              Answer a question and your per-answer coaching appears here: strengths, gaps,
              how FAANG interviewers would score it, and an ideal answer.
            </p>
          )}
        </Card>
        <Card>
          <div className="mb-2 text-sm font-semibold">Session</div>
          <ul className="space-y-1 text-sm text-slate-500">
            <li>Questions answered: <b className="text-slate-700 dark:text-slate-200">{answeredCount}</b></li>
            <li>Current difficulty: <DifficultyChip level={difficulty} /></li>
            <li>Type: {session.session_type.replace('_', ' ')}</li>
          </ul>
          <p className="mt-3 text-xs text-slate-500">
            Difficulty adapts to your performance. Strong answers → harder questions.
          </p>
        </Card>
        {voiceMode && (
          <Card>
            <div className="mb-1 text-sm font-semibold">🗣️ Voice mode</div>
            <p className="text-xs text-slate-500">
              {voice.starting ? 'Requesting microphone access — accept the browser prompt…' :
               voice.speaking ? 'Interviewer is speaking — press 🎙️ to interrupt.' :
               voice.listening ? 'Listening… press ■ to send your answer.' :
               'Press 🎙️ and answer out loud. Pace and filler words are scored.'}
            </p>
            {voice.error && (
              <div className="mt-2 rounded-xl border border-rose-500/30 bg-rose-500/10 px-3 py-2 text-xs text-rose-600 dark:text-rose-400">
                {voice.error}
              </div>
            )}
            {voice.listening && voice.transcript && (
              <p className="mt-2 rounded-xl bg-slate-100 px-3 py-2 text-xs italic text-slate-500 dark:bg-white/5">
                “{voice.transcript.slice(-160)}”
              </p>
            )}
          </Card>
        )}
      </div>
    </div>
  );
}
