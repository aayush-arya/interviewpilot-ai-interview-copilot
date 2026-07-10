import { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';

import { useProblems } from '../api/hooks';
import { Card, DifficultyChip, EmptyState, Spinner } from '../components/ui';

const DIFFICULTIES = ['all', 'easy', 'medium', 'hard'] as const;

export default function CodingPage() {
  const { data: problems, isLoading } = useProblems();
  const [difficulty, setDifficulty] = useState<(typeof DIFFICULTIES)[number]>('all');
  const [topic, setTopic] = useState('all');
  const [search, setSearch] = useState('');

  const topics = useMemo(
    () => ['all', ...Array.from(new Set((problems ?? []).map((p) => p.topic))).sort()],
    [problems]
  );

  const filtered = useMemo(
    () =>
      (problems ?? []).filter(
        (p) =>
          (difficulty === 'all' || p.difficulty === difficulty) &&
          (topic === 'all' || p.topic === topic) &&
          (!search || p.title.toLowerCase().includes(search.toLowerCase()))
      ),
    [problems, difficulty, topic, search]
  );

  const counts = useMemo(() => {
    const base = { easy: 0, medium: 0, hard: 0 } as Record<string, number>;
    for (const p of problems ?? []) base[p.difficulty] = (base[p.difficulty] ?? 0) + 1;
    return base;
  }, [problems]);

  if (isLoading) return <div className="py-20"><Spinner label="Loading problems…" /></div>;

  return (
    <div className="animate-fade-in space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Coding Interview</h1>
        <p className="text-sm text-slate-500">
          Solve in Python, JavaScript, Java or C++. Hidden tests + AI senior-reviewer feedback on every submission.
        </p>
      </div>

      {/* Filters */}
      <div className="glass flex flex-wrap items-center gap-3 p-3">
        <div className="flex gap-1.5">
          {DIFFICULTIES.map((d) => (
            <button
              key={d}
              onClick={() => setDifficulty(d)}
              className={`chip !px-3 !py-1.5 capitalize transition ${
                difficulty === d
                  ? d === 'easy' ? 'bg-emerald-600 text-white'
                    : d === 'medium' ? 'bg-amber-600 text-white'
                    : d === 'hard' ? 'bg-rose-600 text-white'
                    : 'bg-brand-600 text-white'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200 dark:bg-white/5 dark:text-slate-300 dark:hover:bg-white/10'
              }`}
            >
              {d}{d !== 'all' && ` (${counts[d] ?? 0})`}
            </button>
          ))}
        </div>
        <select className="input !w-44 !py-1.5" value={topic} onChange={(e) => setTopic(e.target.value)}>
          {topics.map((t) => (
            <option key={t} value={t}>{t === 'all' ? 'All topics' : t}</option>
          ))}
        </select>
        <input
          className="input !w-52 !py-1.5"
          placeholder="Search problems…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <span className="ml-auto text-xs text-slate-500">
          {filtered.length} of {problems?.length ?? 0} problems
        </span>
      </div>

      {filtered.length ? (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {filtered.map((p) => (
            <Link key={p.id} to={`/app/coding/${p.id}`}>
              <Card className="h-full transition hover:border-brand-500/50">
                <div className="flex items-start justify-between gap-2">
                  <div className="font-semibold">{p.title}</div>
                  <DifficultyChip level={p.difficulty} />
                </div>
                <div className="chip mt-3 bg-slate-500/10 text-slate-500">{p.topic}</div>
              </Card>
            </Link>
          ))}
        </div>
      ) : (
        <EmptyState
          icon="🔍"
          title="No problems match your filters"
          sub={problems?.length ? 'Try a different difficulty or topic.' : 'Run `python -m app.seed` in the backend.'}
        />
      )}
    </div>
  );
}
