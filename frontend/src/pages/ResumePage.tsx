import { useRef, useState } from 'react';
import ReactMarkdown from 'react-markdown';

import { apiErrorMessage } from '../api/client';
import { useAnalyzeResume, useLatestResume } from '../api/hooks';
import { Card, ErrorNote, ScoreBar, SectionTitle, Spinner } from '../components/ui';

const DOC_TABS = [
  { key: 'improved_resume', label: '✨ Improved Resume' },
  { key: 'cover_letter', label: '✉️ Cover Letter' },
  { key: 'linkedin_summary', label: '💼 LinkedIn Summary' },
] as const;

const ISSUE_SECTIONS = [
  ['missing_skills', 'Missing skills', '🧩'],
  ['weak_descriptions', 'Weak descriptions', '📉'],
  ['grammar_issues', 'Grammar', '✏️'],
  ['ats_issues', 'ATS issues', '🤖'],
  ['keyword_gaps', 'Keyword gaps', '🔑'],
  ['experience_gaps', 'Experience gaps', '🕳️'],
  ['improvement_suggestions', 'Suggestions', '💡'],
] as const;

export default function ResumePage() {
  const { data: resume, isLoading } = useLatestResume();
  const analyze = useAnalyzeResume();
  const fileRef = useRef<HTMLInputElement>(null);
  const [docTab, setDocTab] = useState<(typeof DOC_TABS)[number]['key']>('improved_resume');
  const [dragOver, setDragOver] = useState(false);

  const upload = (file: File | undefined) => {
    if (file) analyze.mutate(file);
  };

  if (isLoading) return <div className="py-20"><Spinner label="Loading…" /></div>;

  return (
    <div className="animate-fade-in space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Resume Analyzer</h1>
        <p className="text-sm text-slate-500">Upload a PDF — get ATS scores, issues, an improved resume, cover letter and LinkedIn summary.</p>
      </div>

      {/* Upload zone */}
      <div
        className={`glass flex cursor-pointer flex-col items-center gap-2 border-2 border-dashed p-8 text-center transition ${
          dragOver ? '!border-brand-500 bg-brand-500/10' : 'border-slate-300 dark:border-white/15'
        }`}
        onClick={() => fileRef.current?.click()}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(e) => { e.preventDefault(); setDragOver(false); upload(e.dataTransfer.files[0]); }}
      >
        <div className="text-4xl">📄</div>
        <div className="font-semibold">{resume ? 'Upload a new version' : 'Drop your resume PDF here'}</div>
        <div className="text-xs text-slate-500">PDF only, max 5 MB</div>
        <input ref={fileRef} hidden type="file" accept="application/pdf" onChange={(e) => upload(e.target.files?.[0])} />
      </div>

      {analyze.isPending && (
        <Card><Spinner label="Claude is analyzing your resume — scoring, detecting issues, and rewriting it (~30s)…" /></Card>
      )}
      {analyze.isError && <ErrorNote message={apiErrorMessage(analyze.error)} />}

      {resume && !analyze.isPending && (
        <>
          {/* Scores */}
          <Card>
            <SectionTitle>Scores — {resume.filename}</SectionTitle>
            <div className="grid gap-4 sm:grid-cols-2">
              <ScoreBar label="ATS Score" value={resume.ats_score} />
              <ScoreBar label="Recruiter Score" value={resume.recruiter_score} />
              <ScoreBar label="Technical Score" value={resume.technical_score} />
              <ScoreBar label="Communication Score" value={resume.communication_score} />
              <ScoreBar label="Confidence Score" value={resume.confidence_score} />
            </div>
            {resume.analysis?.summary && (
              <p className="mt-4 rounded-xl bg-slate-100 p-3 text-sm text-slate-600 dark:bg-white/5 dark:text-slate-300">
                {resume.analysis.summary}
              </p>
            )}
          </Card>

          {/* Issues */}
          {resume.analysis && (
            <Card>
              <SectionTitle>Detected issues & suggestions</SectionTitle>
              <div className="grid gap-4 md:grid-cols-2">
                {ISSUE_SECTIONS.map(([key, label, icon]) => {
                  const items = resume.analysis![key] as string[];
                  if (!items?.length) return null;
                  return (
                    <div key={key} className="rounded-xl border border-slate-200 p-3 dark:border-white/10">
                      <div className="mb-1.5 text-sm font-semibold">{icon} {label}</div>
                      <ul className="ml-4 list-disc space-y-1 text-sm text-slate-600 dark:text-slate-300">
                        {items.map((item, i) => <li key={i}>{item}</li>)}
                      </ul>
                    </div>
                  );
                })}
              </div>
            </Card>
          )}

          {/* Generated documents */}
          <Card>
            <SectionTitle>Generated documents</SectionTitle>
            <div className="mb-3 flex flex-wrap gap-2">
              {DOC_TABS.map((t) => (
                <button
                  key={t.key}
                  onClick={() => setDocTab(t.key)}
                  className={`chip !px-3 !py-1.5 ${docTab === t.key ? 'bg-brand-600 text-white' : 'bg-slate-100 text-slate-600 dark:bg-white/5 dark:text-slate-300'}`}
                >
                  {t.label}
                </button>
              ))}
              <button
                className="chip !px-3 !py-1.5 bg-slate-100 text-slate-600 hover:bg-brand-500/15 dark:bg-white/5 dark:text-slate-300"
                onClick={() => navigator.clipboard.writeText(resume[docTab])}
              >
                📋 Copy
              </button>
            </div>
            <div className="prose prose-sm max-w-none rounded-xl bg-slate-100 p-4 text-slate-700 dark:prose-invert dark:bg-white/5 dark:text-slate-300">
              <ReactMarkdown skipHtml>{resume[docTab] || '_Not generated_'}</ReactMarkdown>
            </div>
            <p className="mt-2 text-xs text-slate-500">Values in [brackets] are estimates — replace them with your real numbers.</p>
          </Card>
        </>
      )}
    </div>
  );
}
