import { apiErrorMessage } from '../api/client';
import { useGeneratePlan, useLatestPlan } from '../api/hooks';
import { Card, EmptyState, ErrorNote, SectionTitle, Spinner } from '../components/ui';

export default function PlanPage() {
  const { data: plan, isLoading } = useLatestPlan();
  const generate = useGeneratePlan();

  if (isLoading) return <div className="py-20"><Spinner label="Loading plan…" /></div>;

  return (
    <div className="animate-fade-in space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold">Personalized Study Plan</h1>
          <p className="text-sm text-slate-500">A roadmap built from your resume, weak areas and interview deadline.</p>
        </div>
        <button className="btn-primary" onClick={() => generate.mutate()} disabled={generate.isPending}>
          {generate.isPending ? 'Generating…' : plan ? '🔄 Regenerate plan' : '✨ Generate my plan'}
        </button>
      </div>

      {generate.isPending && <Card><Spinner label="Building your personalized roadmap…" /></Card>}
      {generate.isError && <ErrorNote message={apiErrorMessage(generate.error)} />}

      {!plan && !generate.isPending && (
        <EmptyState
          icon="🗓️"
          title="No plan yet"
          sub="Upload your resume first for the most personalized roadmap, set your interview deadline in Settings, then generate."
        />
      )}

      {plan && (
        <>
          {plan.days_until_deadline != null && (
            <Card className="!bg-gradient-to-r !from-brand-600/15 !to-violet-600/15 text-center">
              <div className="text-3xl font-extrabold">{plan.days_until_deadline} days</div>
              <div className="text-sm text-slate-500">until your target interview date</div>
            </Card>
          )}

          <div className="grid gap-4 lg:grid-cols-3">
            <Card>
              <SectionTitle>Priority topics</SectionTitle>
              <div className="flex flex-wrap gap-2">
                {plan.roadmap.priority_topics.map((t) => (
                  <span key={t} className="chip bg-brand-500/15 text-brand-600 dark:text-brand-300">{t}</span>
                ))}
              </div>
            </Card>
            <Card>
              <SectionTitle>Skill gaps</SectionTitle>
              <ul className="ml-4 list-disc space-y-1 text-sm text-slate-600 dark:text-slate-300">
                {plan.roadmap.skill_gaps.map((g, i) => <li key={i}>{g}</li>)}
              </ul>
            </Card>
            <Card>
              <SectionTitle>Weekly goals</SectionTitle>
              <ul className="ml-4 list-disc space-y-1 text-sm text-slate-600 dark:text-slate-300">
                {plan.roadmap.weekly_goals.map((g, i) => <li key={i}>{g}</li>)}
              </ul>
            </Card>
          </div>

          <Card>
            <SectionTitle>Day-by-day roadmap ({plan.roadmap.days.length} days)</SectionTitle>
            <div className="relative ml-3 space-y-4 border-l-2 border-brand-500/30 pl-6">
              {plan.roadmap.days.map((d) => (
                <div key={d.day} className="relative">
                  <div className="absolute -left-[31px] top-1 flex h-5 w-5 items-center justify-center rounded-full bg-brand-600 text-[10px] font-bold text-white">
                    {d.day}
                  </div>
                  <div className="font-semibold">{d.topic}</div>
                  <ul className="ml-4 list-disc text-sm text-slate-500">
                    {d.goals.map((g, i) => <li key={i}>{g}</li>)}
                  </ul>
                </div>
              ))}
            </div>
          </Card>
        </>
      )}
    </div>
  );
}
