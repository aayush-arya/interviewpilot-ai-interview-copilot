import { useAnalytics, useLeaderboard } from '../api/hooks';
import { FrequencyChart, MasteryBars, TrendChart } from '../components/charts';
import { Card, EmptyState, ProgressRing, SectionTitle, Spinner, StatCard } from '../components/ui';

export default function AnalyticsPage() {
  const { data, isLoading } = useAnalytics();
  const { data: leaderboard } = useLeaderboard();

  if (isLoading) return <div className="py-20"><Spinner label="Crunching your numbers…" /></div>;
  if (!data) return <EmptyState icon="📈" title="No analytics yet" />;

  return (
    <div className="animate-fade-in space-y-6">
      <h1 className="text-2xl font-bold">Analytics</h1>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card className="flex items-center justify-center">
          <ProgressRing value={data.success_prediction} label="Success prediction" />
        </Card>
        <StatCard icon="🎤" label="Total sessions" value={data.total_sessions} />
        <StatCard icon="💻" label="Submissions" value={data.total_submissions} />
        <StatCard icon="🎯" label="Average score" value={data.average_score} sub="across all interviews" />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <SectionTitle>Interview score trend</SectionTitle>
          {data.score_trend.length >= 2
            ? <div className="h-56"><TrendChart points={data.score_trend} label="score" /></div>
            : <p className="py-8 text-center text-sm text-slate-500">Complete more interviews to unlock this chart.</p>}
        </Card>
        <Card>
          <SectionTitle>Confidence trend</SectionTitle>
          {data.confidence_trend.length >= 2
            ? <div className="h-56"><TrendChart points={data.confidence_trend} label="confidence" color="#8b5cf6" /></div>
            : <p className="py-8 text-center text-sm text-slate-500">Complete more interviews to unlock this chart.</p>}
        </Card>
        <Card>
          <SectionTitle>Practice frequency (30 days)</SectionTitle>
          {data.practice_frequency.length
            ? <div className="h-56"><FrequencyChart points={data.practice_frequency} /></div>
            : <p className="py-8 text-center text-sm text-slate-500">No practice activity yet.</p>}
        </Card>
        <Card>
          <SectionTitle>Topic mastery</SectionTitle>
          {data.topic_mastery.length
            ? <div className="h-56"><MasteryBars items={data.topic_mastery} /></div>
            : <p className="py-8 text-center text-sm text-slate-500">Interview across topics to build your mastery map.</p>}
        </Card>
      </div>

      <Card>
        <SectionTitle>Leaderboard</SectionTitle>
        {leaderboard?.length ? (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-xs uppercase text-slate-500">
                  <th className="py-2">#</th><th>Name</th><th>Level</th><th>XP</th><th>Streak</th>
                </tr>
              </thead>
              <tbody>
                {leaderboard.map((entry) => (
                  <tr key={entry.rank} className={`border-t border-slate-200 dark:border-white/10 ${entry.is_me ? 'bg-brand-500/10 font-semibold' : ''}`}>
                    <td className="py-2">{entry.rank <= 3 ? ['🥇', '🥈', '🥉'][entry.rank - 1] : entry.rank}</td>
                    <td>{entry.full_name}{entry.is_me && ' (you)'}</td>
                    <td>Lv {entry.level}</td>
                    <td>{entry.xp}</td>
                    <td>🔥 {entry.streak_count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-sm text-slate-500">—</p>
        )}
      </Card>
    </div>
  );
}
