import { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';

import { useReports } from '../api/hooks';
import { ScoreRadar } from '../components/charts';
import { Card, EmptyState, RecommendationChip, SectionTitle, Spinner } from '../components/ui';
import type { Report } from '../types';

export default function FeedbackPage() {
  const { data: reports, isLoading } = useReports();
  const location = useLocation();
  const [selected, setSelected] = useState<Report | null>(null);

  // Deep-link from "End & get report"
  useEffect(() => {
    const sid = (location.state as any)?.sessionId;
    if (sid && reports) setSelected(reports.find((r) => r.session_id === sid) ?? reports[0] ?? null);
    else if (reports && !selected) setSelected(reports[0] ?? null);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [reports]);

  if (isLoading) return <div className="py-20"><Spinner label="Loading reports…" /></div>;
  if (!reports?.length) {
    return <EmptyState icon="📝" title="No feedback reports yet" sub="Finish a mock interview to get your first hiring-committee style report." />;
  }

  return (
    <div className="animate-fade-in grid gap-4 lg:grid-cols-3">
      {/* Report list */}
      <div className="space-y-2">
        <h1 className="text-xl font-bold">Feedback Reports</h1>
        {reports.map((r) => (
          <button
            key={r.id}
            onClick={() => setSelected(r)}
            className={`w-full rounded-xl border p-3 text-left text-sm transition ${
              selected?.id === r.id ? 'border-brand-500 bg-brand-500/10' : 'border-slate-200 hover:border-brand-400 dark:border-white/10'
            }`}
          >
            <div className="flex items-center justify-between">
              <span className="font-semibold">{r.topic || r.session_type || 'Interview'}</span>
              <span className="font-bold">{r.overall}</span>
            </div>
            <div className="mt-1 flex items-center justify-between text-xs text-slate-500">
              <span>{new Date(r.created_at).toLocaleDateString()}</span>
              <RecommendationChip value={r.hiring_recommendation} />
            </div>
          </button>
        ))}
      </div>

      {/* Detail */}
      {selected && (
        <div className="space-y-4 lg:col-span-2">
          <Card>
            <div className="flex flex-wrap items-center justify-between gap-2">
              <div>
                <div className="text-lg font-bold">{selected.topic || 'Interview'} {selected.company ? `@ ${selected.company}` : ''}</div>
                <div className="text-xs text-slate-500">{new Date(selected.created_at).toLocaleString()}</div>
              </div>
              <div className="flex items-center gap-3">
                <div className="text-3xl font-extrabold text-brand-500">{selected.overall}<span className="text-base text-slate-500">/100</span></div>
                <RecommendationChip value={selected.hiring_recommendation} />
              </div>
            </div>
            <p className="mt-3 text-sm text-slate-600 dark:text-slate-300">{selected.summary}</p>
          </Card>

          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <SectionTitle>Dimension scores</SectionTitle>
              <div className="h-64">
                <ScoreRadar
                  scores={{
                    Communication: selected.communication,
                    Confidence: selected.confidence,
                    'Technical Accuracy': selected.technical_accuracy,
                    'Problem Solving': selected.problem_solving,
                    Overall: selected.overall,
                  }}
                />
              </div>
            </Card>
            <div className="space-y-4">
              <Card>
                <SectionTitle>Strengths</SectionTitle>
                <ul className="ml-4 list-disc space-y-1 text-sm text-slate-600 dark:text-slate-300">
                  {selected.strengths.map((s, i) => <li key={i}>{s}</li>)}
                </ul>
              </Card>
              <Card>
                <SectionTitle>How to improve</SectionTitle>
                <ul className="ml-4 list-disc space-y-1 text-sm text-slate-600 dark:text-slate-300">
                  {selected.improvements.map((s, i) => <li key={i}>{s}</li>)}
                </ul>
              </Card>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
