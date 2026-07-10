import { Link } from 'react-router-dom';

import { useDashboard } from '../api/hooks';
import { TrendChart } from '../components/charts';
import { Card, EmptyState, ProgressRing, RecommendationChip, ScoreBar, SectionTitle, Spinner, StatCard } from '../components/ui';

export default function DashboardPage() {
  const { data, isLoading, error } = useDashboard();

  if (isLoading) return <div className="py-20"><Spinner label="Loading your dashboard…" /></div>;
  if (error || !data) return <EmptyState icon="⚠️" title="Could not load dashboard" sub="Is the backend running on port 8002?" />;

  return (
    <div className="animate-fade-in space-y-6">
      {/* Top row: readiness + stats */}
      <div className="grid gap-4 lg:grid-cols-4">
        <Card className="flex flex-col items-center justify-center gap-2 lg:row-span-2">
          <ProgressRing value={data.readiness_percent} size={150} label="Interview ready" />
          <p className="text-center text-xs text-slate-500">
            Weighted from recent scores, practice volume, resume & streak
          </p>
          {data.days_until_deadline != null && (
            <div className="chip bg-violet-500/15 text-violet-600 dark:text-violet-300">
              ⏳ {data.days_until_deadline} days until your interview
            </div>
          )}
        </Card>
        <StatCard icon="🔥" label="Streak" value={`${data.streak_count} days`} sub="Practice daily to keep it alive" />
        <StatCard icon="⭐" label="Level" value={data.level} sub={`${data.xp} / ${data.next_level_xp} XP`} />
        <StatCard icon="🎤" label="Interviews" value={data.sessions_completed} sub="completed sessions" />
        <StatCard icon="💻" label="Problems solved" value={data.problems_solved} sub="all tests passing" />
        <StatCard icon="📄" label="Resume score" value={data.resume_score ?? '—'} sub={data.resume_score == null ? 'Upload your resume' : 'ATS score'} />
        <StatCard icon="🏅" label="Badges" value={data.badges.length} sub={data.badges.map((b) => b.icon).join(' ') || 'none yet'} />
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        {/* Score trend */}
        <Card className="lg:col-span-2">
          <SectionTitle>Weekly improvement</SectionTitle>
          {data.score_trend.length >= 2 ? (
            <div className="h-56"><TrendChart points={data.score_trend} label="Overall score" /></div>
          ) : (
            <EmptyState icon="📈" title="Not enough data yet" sub="Complete a couple of interviews to see your trend." />
          )}
        </Card>

        {/* Recommendations */}
        <Card>
          <SectionTitle>Recommended practice</SectionTitle>
          <div className="space-y-2">
            {data.recommended_topics.map((topic) => (
              <Link
                key={topic}
                to="/app/interview"
                state={{ topic }}
                className="flex items-center justify-between rounded-xl border border-slate-200 px-3 py-2.5 text-sm transition hover:border-brand-500 hover:bg-brand-500/5 dark:border-white/10"
              >
                <span>{topic}</span><span className="text-brand-500">→</span>
              </Link>
            ))}
          </div>
        </Card>
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        {/* Weak / strong areas */}
        <Card>
          <SectionTitle>Weak areas</SectionTitle>
          {data.weak_areas.length ? (
            <div className="space-y-3">
              {data.weak_areas.map((w) => <ScoreBar key={w.topic} label={`${w.topic} (${w.sessions})`} value={Math.round(w.average_score)} />)}
            </div>
          ) : (
            <p className="text-sm text-slate-500">No data yet — finish an interview.</p>
          )}
          <SectionTitle><span className="mt-4 block">Strong areas</span></SectionTitle>
          {data.strong_areas.length ? (
            <div className="space-y-3">
              {data.strong_areas.map((s) => <ScoreBar key={s.topic} label={`${s.topic} (${s.sessions})`} value={Math.round(s.average_score)} />)}
            </div>
          ) : (
            <p className="text-sm text-slate-500">—</p>
          )}
        </Card>

        {/* Recent feedback */}
        <Card className="lg:col-span-2">
          <SectionTitle right={<Link to="/app/feedback" className="text-xs text-brand-500 hover:underline">View all</Link>}>
            Recent AI feedback
          </SectionTitle>
          {data.recent_feedback.length ? (
            <div className="space-y-3">
              {data.recent_feedback.map((f) => (
                <div key={f.session_id} className="rounded-xl border border-slate-200 p-3 dark:border-white/10">
                  <div className="flex items-center justify-between">
                    <div className="text-sm font-semibold">{f.topic || 'Interview'} — {f.overall}/100</div>
                    <RecommendationChip value={f.recommendation} />
                  </div>
                  <p className="mt-1 line-clamp-2 text-sm text-slate-500">{f.summary}</p>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState
              icon="🎤"
              title="No interviews yet"
              sub="Your feedback reports will appear here."
              action={<Link to="/app/interview" className="btn-primary">Start your first interview</Link>}
            />
          )}
        </Card>
      </div>
    </div>
  );
}
