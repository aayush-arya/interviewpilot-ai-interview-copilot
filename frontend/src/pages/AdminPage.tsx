import { useAdminStats, useAdminUsers } from '../api/hooks';
import { Card, EmptyState, SectionTitle, Spinner, StatCard } from '../components/ui';
import { useAppSelector } from '../store';

export default function AdminPage() {
  const user = useAppSelector((s) => s.auth.user);
  const isAdmin = user?.role === 'admin';
  const { data: stats, isLoading } = useAdminStats(isAdmin);
  const { data: users } = useAdminUsers(isAdmin);

  if (!isAdmin) return <EmptyState icon="🛡️" title="Admin access required" sub="Sign in as admin@user.com to view this page." />;
  if (isLoading) return <div className="py-20"><Spinner label="Loading admin stats…" /></div>;

  return (
    <div className="animate-fade-in space-y-6">
      <h1 className="text-2xl font-bold">Admin Dashboard</h1>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard icon="👥" label="Users" value={stats?.total_users ?? 0} />
        <StatCard icon="🎤" label="Interview sessions" value={stats?.total_sessions ?? 0} />
        <StatCard icon="💻" label="Code submissions" value={stats?.total_submissions ?? 0} />
        <StatCard icon="🎯" label="Avg interview score" value={stats?.average_interview_score ?? 0} />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <SectionTitle>Sessions by type</SectionTitle>
          <ul className="space-y-1 text-sm">
            {Object.entries(stats?.sessions_by_type ?? {}).map(([type, count]) => (
              <li key={type} className="flex justify-between border-b border-slate-200 py-1.5 last:border-0 dark:border-white/10">
                <span className="capitalize">{type.replace('_', ' ')}</span><b>{count as number}</b>
              </li>
            ))}
          </ul>
        </Card>
        <Card>
          <SectionTitle>Activity events (AI usage proxy)</SectionTitle>
          <ul className="space-y-1 text-sm">
            {Object.entries(stats?.ai_events_by_kind ?? {}).map(([kind, count]) => (
              <li key={kind} className="flex justify-between border-b border-slate-200 py-1.5 last:border-0 dark:border-white/10">
                <span>{kind.replace(/_/g, ' ')}</span><b>{count as number}</b>
              </li>
            ))}
          </ul>
        </Card>
      </div>

      <Card>
        <SectionTitle>Users</SectionTitle>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-xs uppercase text-slate-500">
                <th className="py-2">Name</th><th>Email</th><th>Role</th><th>Level</th><th>XP</th><th>Streak</th>
              </tr>
            </thead>
            <tbody>
              {(users ?? []).map((u) => (
                <tr key={u.id} className="border-t border-slate-200 dark:border-white/10">
                  <td className="py-2">{u.full_name}</td>
                  <td>{u.email}</td>
                  <td><span className={`chip ${u.role === 'admin' ? 'bg-violet-500/15 text-violet-500' : 'bg-slate-500/10 text-slate-500'}`}>{u.role}</span></td>
                  <td>{u.level}</td>
                  <td>{u.xp}</td>
                  <td>{u.streak_count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
