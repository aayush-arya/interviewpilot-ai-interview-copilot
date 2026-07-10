import { useState } from 'react';

import { apiErrorMessage } from '../api/client';
import { useUpdateProfile } from '../api/hooks';
import { Card, ErrorNote, SectionTitle } from '../components/ui';
import { setUser, toggleTheme, useAppDispatch, useAppSelector } from '../store';

export default function SettingsPage() {
  const user = useAppSelector((s) => s.auth.user)!;
  const theme = useAppSelector((s) => s.ui.theme);
  const dispatch = useAppDispatch();
  const update = useUpdateProfile();

  const [fullName, setFullName] = useState(user.full_name);
  const [targetRole, setTargetRole] = useState(user.target_role ?? '');
  const [targetCompany, setTargetCompany] = useState(user.target_company ?? '');
  const [deadline, setDeadline] = useState(user.interview_deadline ?? '');
  const [saved, setSaved] = useState(false);

  const save = async () => {
    const updated = await update.mutateAsync({
      full_name: fullName,
      target_role: targetRole || null,
      target_company: targetCompany || null,
      interview_deadline: deadline || null,
    } as any);
    dispatch(setUser(updated));
    setSaved(true);
    setTimeout(() => setSaved(false), 2500);
  };

  return (
    <div className="animate-fade-in mx-auto max-w-2xl space-y-6">
      <h1 className="text-2xl font-bold">Settings</h1>

      <Card>
        <SectionTitle>Profile & goals</SectionTitle>
        <div className="space-y-4">
          <div>
            <label className="mb-1 block text-xs text-slate-500">Full name</label>
            <input className="input" value={fullName} onChange={(e) => setFullName(e.target.value)} />
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className="mb-1 block text-xs text-slate-500">Target role</label>
              <input className="input" placeholder="e.g. Backend Engineer" value={targetRole} onChange={(e) => setTargetRole(e.target.value)} />
            </div>
            <div>
              <label className="mb-1 block text-xs text-slate-500">Target company</label>
              <input className="input" placeholder="e.g. Google" value={targetCompany} onChange={(e) => setTargetCompany(e.target.value)} />
            </div>
          </div>
          <div>
            <label className="mb-1 block text-xs text-slate-500">Interview deadline (drives your plan & countdown)</label>
            <input className="input" type="date" value={deadline} onChange={(e) => setDeadline(e.target.value)} />
          </div>
          {update.isError && <ErrorNote message={apiErrorMessage(update.error)} />}
          <button className="btn-primary" onClick={save} disabled={update.isPending}>
            {update.isPending ? 'Saving…' : saved ? '✓ Saved' : 'Save changes'}
          </button>
        </div>
      </Card>

      <Card>
        <SectionTitle>Appearance</SectionTitle>
        <div className="flex items-center justify-between">
          <div className="text-sm">Theme: <b className="capitalize">{theme}</b></div>
          <button className="btn-ghost" onClick={() => dispatch(toggleTheme())}>
            Switch to {theme === 'dark' ? 'light ☀️' : 'dark 🌙'}
          </button>
        </div>
      </Card>

      <Card>
        <SectionTitle>Account</SectionTitle>
        <div className="text-sm text-slate-500">
          <div>Email: <b className="text-slate-700 dark:text-slate-200">{user.email}</b></div>
          <div>Sign-in method: <b className="capitalize text-slate-700 dark:text-slate-200">{user.provider}</b></div>
          <div>Level {user.level} · {user.xp} XP · 🔥 {user.streak_count}-day streak</div>
        </div>
      </Card>
    </div>
  );
}
