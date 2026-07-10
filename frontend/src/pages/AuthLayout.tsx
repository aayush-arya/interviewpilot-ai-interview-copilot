import { motion } from 'framer-motion';
import type { ReactNode } from 'react';
import { Link } from 'react-router-dom';

export default function AuthLayout({ title, sub, children }: { title: string; sub?: string; children: ReactNode }) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-slate-950 via-indigo-950/70 to-slate-950 p-4">
      <motion.div
        initial={{ opacity: 0, y: 16, scale: 0.98 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.45 }}
        className="w-full max-w-md rounded-3xl border border-white/10 bg-white/5 p-8 text-slate-100 shadow-2xl backdrop-blur-2xl"
      >
        <Link to="/" className="mb-6 block text-center text-xl font-extrabold">
          🎯 Interview<span className="bg-gradient-to-r from-brand-400 to-violet-400 bg-clip-text text-transparent">Pilot</span>
        </Link>
        <h1 className="text-center text-2xl font-bold">{title}</h1>
        {sub && <p className="mt-1 text-center text-sm text-slate-400">{sub}</p>}
        <div className="mt-6">{children}</div>
      </motion.div>
    </div>
  );
}
