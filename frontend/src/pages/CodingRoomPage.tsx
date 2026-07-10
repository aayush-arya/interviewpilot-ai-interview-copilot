import Editor from '@monaco-editor/react';
import { useEffect, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { useParams } from 'react-router-dom';

import { apiErrorMessage } from '../api/client';
import { useProblem, useRunCode, useSubmitCode } from '../api/hooks';
import { Card, DifficultyChip, ErrorNote, Spinner } from '../components/ui';
import { useAppSelector } from '../store';
import type { Submission } from '../types';

const MONACO_LANG: Record<string, string> = { python: 'python', javascript: 'javascript', java: 'java', cpp: 'cpp' };

export default function CodingRoomPage() {
  const { problemId } = useParams();
  const id = Number(problemId);
  const { data: problem, isLoading } = useProblem(id);
  const run = useRunCode();
  const submit = useSubmitCode(id);
  const theme = useAppSelector((s) => s.ui.theme);

  const [language, setLanguage] = useState('python');
  const [code, setCode] = useState('');
  const [stdin, setStdin] = useState('');
  const [tab, setTab] = useState<'tests' | 'output' | 'review'>('tests');
  const [submission, setSubmission] = useState<Submission | null>(null);

  useEffect(() => {
    if (problem) {
      setCode(problem.starter_code[language] ?? '');
      setStdin(problem.visible_tests[0]?.input ?? '');
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [problem, language]);

  if (isLoading || !problem) return <div className="py-20"><Spinner label="Loading problem…" /></div>;

  const doRun = async () => {
    setTab('output');
    await run.mutateAsync({ language, code, stdin });
  };

  const doSubmit = async () => {
    setTab('tests');
    const result = await submit.mutateAsync({ language, code });
    setSubmission(result);
    if (result.review) setTab('review');
  };

  return (
    <div className="animate-fade-in grid gap-4 xl:grid-cols-2">
      {/* Problem statement */}
      <Card className="max-h-[85vh] overflow-y-auto">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-bold">{problem.title}</h1>
          <DifficultyChip level={problem.difficulty} />
        </div>
        <div className="prose prose-sm mt-3 max-w-none text-slate-600 dark:prose-invert dark:text-slate-300">
          <ReactMarkdown skipHtml>{problem.description}</ReactMarkdown>
        </div>
        <div className="mt-4">
          <div className="text-xs font-semibold uppercase text-slate-500">Visible test cases</div>
          {problem.visible_tests.map((t, i) => (
            <div key={i} className="mt-2 rounded-xl bg-slate-100 p-3 font-mono text-xs dark:bg-white/5">
              <div><span className="text-slate-500">input:</span> {t.input}</div>
              <div><span className="text-slate-500">expected:</span> {t.expected}</div>
            </div>
          ))}
          <p className="mt-2 text-xs text-slate-500">+ hidden test cases run on submit.</p>
        </div>
      </Card>

      {/* Editor + results */}
      <div className="space-y-3">
        <div className="glass overflow-hidden">
          <div className="flex items-center justify-between border-b border-slate-200 px-3 py-2 dark:border-white/10">
            <select className="input !w-40 !py-1.5" value={language} onChange={(e) => setLanguage(e.target.value)}>
              <option value="python">Python</option>
              <option value="javascript">JavaScript</option>
              <option value="java">Java</option>
              <option value="cpp">C++</option>
            </select>
            <div className="flex gap-2">
              <button className="btn-ghost !py-1.5 text-xs" onClick={doRun} disabled={run.isPending}>
                {run.isPending ? 'Running…' : '▶ Run'}
              </button>
              <button className="btn-primary !py-1.5 text-xs" onClick={doSubmit} disabled={submit.isPending}>
                {submit.isPending ? 'Judging…' : '✓ Submit'}
              </button>
            </div>
          </div>
          <Editor
            height="46vh"
            language={MONACO_LANG[language]}
            value={code}
            onChange={(v) => setCode(v ?? '')}
            theme={theme === 'dark' ? 'vs-dark' : 'light'}
            options={{ fontSize: 13, minimap: { enabled: false }, scrollBeyondLastLine: false, tabSize: 4, quickSuggestions: true }}
          />
        </div>

        <Card>
          <div className="mb-3 flex gap-2 text-xs font-semibold">
            {(['tests', 'output', 'review'] as const).map((t) => (
              <button
                key={t}
                onClick={() => setTab(t)}
                className={`chip !px-3 !py-1.5 capitalize ${tab === t ? 'bg-brand-600 text-white' : 'bg-slate-100 text-slate-500 dark:bg-white/5'}`}
              >
                {t === 'tests' ? 'Test results' : t === 'output' ? 'Run output' : 'AI review'}
              </button>
            ))}
          </div>

          {(run.isError || submit.isError) && (
            <ErrorNote message={apiErrorMessage(run.error ?? submit.error)} />
          )}

          {tab === 'output' && (
            <div className="space-y-2">
              <label className="block text-xs text-slate-500">Custom stdin</label>
              <textarea className="input font-mono text-xs" rows={2} value={stdin} onChange={(e) => setStdin(e.target.value)} />
              {run.data && (
                <pre className={`overflow-x-auto rounded-xl p-3 font-mono text-xs ${run.data.exit_code === 0 ? 'bg-slate-100 dark:bg-white/5' : 'bg-rose-500/10 text-rose-500'}`}>
                  {run.data.timed_out ? '⏱ Time limit exceeded' : (run.data.stdout || run.data.stderr || '(no output)')}
                  {'\n'}— exit {run.data.exit_code}, {run.data.runtime_ms}ms
                </pre>
              )}
            </div>
          )}

          {tab === 'tests' && (
            submission ? (
              <div className="space-y-2">
                <div className={`text-sm font-bold ${submission.status === 'passed' ? 'text-emerald-500' : 'text-rose-500'}`}>
                  {submission.status.toUpperCase()} — {submission.passed_count}/{submission.total_count} tests
                  {submission.xp_awarded > 0 && <span className="ml-2 text-amber-500">+{submission.xp_awarded} XP</span>}
                </div>
                {submission.results.map((r) => (
                  <div key={r.index} className={`rounded-xl border p-2.5 font-mono text-xs ${r.passed ? 'border-emerald-500/30 bg-emerald-500/5' : 'border-rose-500/30 bg-rose-500/5'}`}>
                    <div className="font-sans font-semibold">
                      {r.passed ? '✅' : '❌'} Test {r.index + 1} {r.hidden && <span className="text-slate-400">(hidden)</span>}
                    </div>
                    {!r.hidden && !r.passed && (
                      <div className="mt-1 space-y-0.5 text-slate-500">
                        <div>input: {r.input}</div>
                        <div>expected: {r.expected}</div>
                        <div>actual: {r.actual || r.error}</div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-slate-500">Submit your solution to run visible + hidden tests.</p>
            )
          )}

          {tab === 'review' && (
            submission?.review ? (
              <div className="space-y-3 text-sm">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="chip bg-brand-500/15 capitalize text-brand-600 dark:text-brand-300">{submission.review.verdict.replace('_', ' ')}</span>
                  <span className="chip bg-slate-500/10 text-slate-500">time {submission.review.time_complexity}</span>
                  <span className="chip bg-slate-500/10 text-slate-500">space {submission.review.space_complexity}</span>
                  <span className="chip bg-amber-500/15 text-amber-600">score {submission.review.score}/100</span>
                </div>
                <p className="text-slate-600 dark:text-slate-300">{submission.review.correctness_notes}</p>
                {submission.review.edge_cases_missed.length > 0 && (
                  <div>
                    <div className="text-xs font-semibold uppercase text-rose-500">Edge cases missed</div>
                    <ul className="ml-4 list-disc text-slate-600 dark:text-slate-300">
                      {submission.review.edge_cases_missed.map((e, i) => <li key={i}>{e}</li>)}
                    </ul>
                  </div>
                )}
                {submission.review.optimizations.length > 0 && (
                  <div>
                    <div className="text-xs font-semibold uppercase text-emerald-500">Optimizations</div>
                    <ul className="ml-4 list-disc text-slate-600 dark:text-slate-300">
                      {submission.review.optimizations.map((o, i) => <li key={i}>{o}</li>)}
                    </ul>
                  </div>
                )}
                {submission.review.quality_issues.length > 0 && (
                  <div>
                    <div className="text-xs font-semibold uppercase text-violet-500">Code quality</div>
                    <ul className="ml-4 list-disc text-slate-600 dark:text-slate-300">
                      {submission.review.quality_issues.map((q, i) => <li key={i}>{q}</li>)}
                    </ul>
                  </div>
                )}
              </div>
            ) : (
              <p className="text-sm text-slate-500">The AI senior-reviewer feedback appears after you submit.</p>
            )
          )}
        </Card>
      </div>
    </div>
  );
}
