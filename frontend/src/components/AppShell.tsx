import { useEffect, useState } from 'react';
import { Link, NavLink, Outlet, useNavigate } from 'react-router-dom';

import client from '../api/client';
import { logout, setUser, toggleTheme, useAppDispatch, useAppSelector } from '../store';

const NAV = [
  { to: '/app', label: 'Dashboard', icon: '📊', end: true },
  { to: '/app/interview', label: 'Mock Interview', icon: '🎤' },
  { to: '/app/coding', label: 'Coding', icon: '💻' },
  { to: '/app/resume', label: 'Resume', icon: '📄' },
  { to: '/app/plan', label: 'Study Plan', icon: '🗓️' },
  { to: '/app/companies', label: 'Companies', icon: '🏢' },
  { to: '/app/feedback', label: 'Feedback', icon: '📝' },
  { to: '/app/analytics', label: 'Analytics', icon: '📈' },
  { to: '/app/settings', label: 'Settings', icon: '⚙️' },
];

export default function AppShell() {
  const user = useAppSelector((s) => s.auth.user);
  const theme = useAppSelector((s) => s.ui.theme);
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark');
  }, [theme]);

  const handleLogout = () => {
    dispatch(logout());
    navigate('/');
  };

  const nav = (
    <nav className="flex flex-col gap-1 p-3">
      {NAV.map((item) => (
        <NavLink
          key={item.to}
          to={item.to}
          end={item.end}
          onClick={() => setMobileOpen(false)}
          className={({ isActive }) =>
            `flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition ${
              isActive
                ? 'bg-gradient-to-r from-brand-600/20 to-violet-600/20 text-brand-600 dark:text-brand-300'
                : 'text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-white/5'
            }`
          }
        >
          <span>{item.icon}</span> {item.label}
        </NavLink>
      ))}
      {user?.role === 'admin' && (
        <NavLink
          to="/app/admin"
          onClick={() => setMobileOpen(false)}
          className={({ isActive }) =>
            `flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition ${
              isActive ? 'bg-brand-600/20 text-brand-600 dark:text-brand-300' : 'text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-white/5'
            }`
          }
        >
          <span>🛡️</span> Admin
        </NavLink>
      )}
    </nav>
  );

  return (
    <div className="flex min-h-screen">
      {/* Desktop sidebar */}
      <aside className="sticky top-0 hidden h-screen w-60 shrink-0 border-r border-slate-200 bg-white/60 backdrop-blur-xl dark:border-white/10 dark:bg-slate-950/60 lg:block">
        <Link to="/app" className="flex items-center gap-2 px-5 py-5 text-lg font-extrabold">
          <span className="text-2xl">🎯</span> Interview<span className="bg-gradient-to-r from-brand-500 to-violet-500 bg-clip-text text-transparent">Pilot</span>
        </Link>
        {nav}
      </aside>

      {/* Mobile drawer */}
      {mobileOpen && (
        <div className="fixed inset-0 z-40 lg:hidden" onClick={() => setMobileOpen(false)}>
          <div className="absolute inset-0 bg-black/50" />
          <aside className="glass-strong absolute left-0 top-0 h-full w-64 rounded-none" onClick={(e) => e.stopPropagation()}>
            <div className="px-5 py-5 text-lg font-extrabold">🎯 InterviewPilot</div>
            {nav}
          </aside>
        </div>
      )}

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="sticky top-0 z-30 flex items-center justify-between border-b border-slate-200 bg-white/70 px-4 py-3 backdrop-blur-xl dark:border-white/10 dark:bg-slate-950/70">
          <div className="flex items-center gap-3">
            <button className="btn-ghost !p-2 lg:hidden" onClick={() => setMobileOpen(true)} aria-label="Open menu">☰</button>
            <div className="hidden text-sm text-slate-500 sm:block">
              {user && <>Welcome back, <span className="font-semibold text-slate-700 dark:text-slate-200">{user.full_name.split(' ')[0]}</span></>}
            </div>
          </div>
          <div className="flex items-center gap-2">
            {user && (
              <div className="chip bg-amber-500/15 text-amber-600 dark:text-amber-400" title="Daily streak">
                🔥 {user.streak_count}
              </div>
            )}
            {user && (
              <div className="chip bg-brand-500/15 text-brand-600 dark:text-brand-300" title="Level / XP">
                ⭐ Lv {user.level} · {user.xp} XP
              </div>
            )}
            <button
              className="btn-ghost !p-2"
              onClick={() => dispatch(toggleTheme())}
              aria-label="Toggle theme"
              title="Toggle dark / light mode"
            >
              {theme === 'dark' ? '🌙' : '☀️'}
            </button>
            <button className="btn-ghost" onClick={handleLogout}>Logout</button>
          </div>
        </header>
        <main className="mx-auto w-full max-w-6xl flex-1 p-4 sm:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

export function useRefreshUser() {
  const dispatch = useAppDispatch();
  return async () => {
    const { data } = await client.get('/users/me');
    dispatch(setUser(data));
  };
}
