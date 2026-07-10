import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';

import { useAppSelector } from '../store';

const FEATURES = [
  { icon: '🎤', title: 'AI Mock Interviews', text: 'A senior-engineer AI that asks follow-ups, challenges weak answers, and adapts difficulty in real time.' },
  { icon: '📄', title: 'Resume Analyzer', text: 'ATS + recruiter + technical scoring, then a rewritten resume, cover letter and LinkedIn summary.' },
  { icon: '💻', title: 'Real Coding Rounds', text: 'Monaco editor, hidden test cases, and a senior-reviewer code review with complexity analysis.' },
  { icon: '🗣️', title: 'Voice Mode', text: 'Speak your answers. We track pace, filler words and confidence — like the real thing.' },
  { icon: '🏢', title: 'Company Styles', text: 'Google, Amazon, Goldman Sachs, startups — each with its authentic interview style and bar.' },
  { icon: '📈', title: 'Deep Analytics', text: 'Readiness score, weak-topic detection, score trends, and a personalized 30-day roadmap.' },
];

export default function LandingPage() {
  const user = useAppSelector((s) => s.auth.user);
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-950 to-indigo-950/60 text-slate-100">
      <header className="mx-auto flex max-w-6xl items-center justify-between px-6 py-5">
        <div className="text-xl font-extrabold">🎯 Interview<span className="bg-gradient-to-r from-brand-400 to-violet-400 bg-clip-text text-transparent">Pilot</span></div>
        <nav className="flex items-center gap-3">
          {user ? (
            <Link to="/app" className="btn-primary">Open Dashboard</Link>
          ) : (
            <>
              <Link to="/login" className="btn-ghost !border-white/20 !text-slate-200">Sign in</Link>
              <Link to="/register" className="btn-primary">Get started</Link>
            </>
          )}
        </nav>
      </header>

      <section className="mx-auto max-w-4xl px-6 pb-20 pt-16 text-center">
        <motion.h1
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-4xl font-extrabold leading-tight sm:text-6xl"
        >
          Interview like it's <span className="bg-gradient-to-r from-brand-400 via-violet-400 to-fuchsia-400 bg-clip-text text-transparent">the real thing</span>
        </motion.h1>
        <motion.p
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.15 }}
          className="mx-auto mt-5 max-w-2xl text-lg text-slate-300"
        >
          Your AI interview copilot: adaptive mock interviews, resume analysis, live coding rounds,
          voice practice, and feedback that reads like a real hiring committee's.
        </motion.p>
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="mt-8 flex justify-center gap-3"
        >
          <Link to={user ? '/app' : '/register'} className="btn-primary !px-7 !py-3 !text-base">Start practicing free</Link>
          <a href="#features" className="btn-ghost !border-white/20 !px-7 !py-3 !text-base !text-slate-200">See features</a>
        </motion.div>
      </section>

      <section id="features" className="mx-auto grid max-w-6xl gap-4 px-6 pb-24 sm:grid-cols-2 lg:grid-cols-3">
        {FEATURES.map((f, i) => (
          <motion.div
            key={f.title}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.4, delay: i * 0.06 }}
            className="rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur-xl"
          >
            <div className="text-3xl">{f.icon}</div>
            <div className="mt-3 font-bold">{f.title}</div>
            <p className="mt-1.5 text-sm text-slate-300">{f.text}</p>
          </motion.div>
        ))}
      </section>

      <footer className="border-t border-white/10 py-8 text-center text-sm text-slate-400">
        InterviewPilot — built with FastAPI, React & Claude.
      </footer>
    </div>
  );
}
