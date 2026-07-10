import { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

import { apiErrorMessage } from '../api/client';
import { useCatalog, useStartInterview } from '../api/hooks';
import { Card, ErrorNote, SectionTitle, Spinner } from '../components/ui';

const TYPES = [
  { key: 'technical', label: 'Technical', icon: '⚙️', desc: 'Deep-dive on a language, framework or CS topic' },
  { key: 'system_design', label: 'System Design', icon: '🏗️', desc: 'Design Instagram, Uber, Netflix… with a principal engineer' },
  { key: 'behavioral', label: 'Behavioral', icon: '🤝', desc: 'STAR stories: leadership, conflict, failure, ownership' },
  { key: 'hr', label: 'HR Round', icon: '💼', desc: 'Motivation, culture fit, salary conversation' },
];

const SYSTEM_DESIGN_TOPICS = [
  'Design Instagram', 'Design WhatsApp', 'Design Uber', 'Design Netflix', 'Design YouTube',
  'Design a URL Shortener', 'Design Twitter', 'Design a Rate Limiter',
];

export default function InterviewSetupPage() {
  const location = useLocation();
  const { data: catalog } = useCatalog();
  const [type, setType] = useState('technical');
  const [topic, setTopic] = useState<string>((location.state as any)?.topic ?? 'Data Structures & Algorithms');
  const [company, setCompany] = useState<string>((location.state as any)?.company ?? '');
  const [difficulty, setDifficulty] = useState('medium');
  const start = useStartInterview();
  const navigate = useNavigate();

  const topics = type === 'system_design'
    ? SYSTEM_DESIGN_TOPICS
    : type === 'behavioral' ? ['Behavioral'] : type === 'hr' ? ['HR'] : (catalog?.tracks ?? []);

  const begin = async () => {
    const session = await start.mutateAsync({
      session_type: type,
      topic: type === 'behavioral' ? 'Behavioral' : type === 'hr' ? 'HR' : topic,
      company: company || null,
      difficulty,
    });
    navigate(`/app/interview/${session.id}`);
  };

  return (
    <div className="animate-fade-in mx-auto max-w-3xl space-y-6">
      <h1 className="text-2xl font-bold">Set up your mock interview</h1>

      <Card>
        <SectionTitle>Interview type</SectionTitle>
        <div className="grid gap-3 sm:grid-cols-2">
          {TYPES.map((t) => (
            <button
              key={t.key}
              onClick={() => { setType(t.key); if (t.key === 'system_design') setTopic(SYSTEM_DESIGN_TOPICS[0]); }}
              className={`rounded-xl border p-4 text-left transition ${
                type === t.key
                  ? 'border-brand-500 bg-brand-500/10 ring-2 ring-brand-500/30'
                  : 'border-slate-200 hover:border-brand-400 dark:border-white/10'
              }`}
            >
              <div className="text-2xl">{t.icon}</div>
              <div className="mt-1 font-semibold">{t.label}</div>
              <div className="text-xs text-slate-500">{t.desc}</div>
            </button>
          ))}
        </div>
      </Card>

      {(type === 'technical' || type === 'system_design') && (
        <Card>
          <SectionTitle>Topic</SectionTitle>
          <div className="flex flex-wrap gap-2">
            {topics.map((t) => (
              <button
                key={t}
                onClick={() => setTopic(t)}
                className={`chip !px-3 !py-1.5 transition ${
                  topic === t
                    ? 'bg-brand-600 text-white'
                    : 'bg-slate-100 text-slate-600 hover:bg-brand-500/15 dark:bg-white/5 dark:text-slate-300'
                }`}
              >
                {t}
              </button>
            ))}
          </div>
        </Card>
      )}

      <Card>
        <SectionTitle>Company style & difficulty</SectionTitle>
        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label className="mb-1 block text-xs text-slate-500">Company (optional)</label>
            <select className="input" value={company} onChange={(e) => setCompany(e.target.value)}>
              <option value="">Generic top-tier company</option>
              {(catalog?.companies ?? []).map((c) => (
                <option key={c.name} value={c.name}>{c.name}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="mb-1 block text-xs text-slate-500">Starting difficulty (adapts as you go)</label>
            <div className="flex gap-2">
              {['easy', 'medium', 'hard'].map((d) => (
                <button
                  key={d}
                  onClick={() => setDifficulty(d)}
                  className={`btn flex-1 border text-sm capitalize ${
                    difficulty === d ? 'border-brand-500 bg-brand-500/10 text-brand-600 dark:text-brand-300' : 'border-slate-200 dark:border-white/10'
                  }`}
                >
                  {d}
                </button>
              ))}
            </div>
          </div>
        </div>
      </Card>

      {start.isError && <ErrorNote message={apiErrorMessage(start.error)} />}
      <button className="btn-primary w-full !py-3 !text-base" onClick={begin} disabled={start.isPending}>
        {start.isPending ? <Spinner label="Preparing your interviewer…" /> : '🎤 Start interview'}
      </button>
    </div>
  );
}
