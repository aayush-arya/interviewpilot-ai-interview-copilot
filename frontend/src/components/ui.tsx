import { motion } from 'framer-motion';
import type { ReactNode } from 'react';

export function Card({ children, className = '' }: { children: ReactNode; className?: string }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35 }}
      className={`glass p-5 ${className}`}
    >
      {children}
    </motion.div>
  );
}

export function SectionTitle({ children, right }: { children: ReactNode; right?: ReactNode }) {
  return (
    <div className="mb-3 flex items-center justify-between">
      <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
        {children}
      </h2>
      {right}
    </div>
  );
}

export function Spinner({ label }: { label?: string }) {
  return (
    <div className="flex items-center gap-3 text-sm text-slate-500">
      <div className="h-5 w-5 animate-spin rounded-full border-2 border-brand-500 border-t-transparent" />
      {label}
    </div>
  );
}

export function StatCard({ label, value, sub, icon }: { label: string; value: ReactNode; sub?: string; icon?: string }) {
  return (
    <Card className="flex items-center gap-4">
      {icon && <div className="text-3xl">{icon}</div>}
      <div>
        <div className="text-xs font-medium uppercase tracking-wide text-slate-500 dark:text-slate-400">{label}</div>
        <div className="text-2xl font-bold">{value}</div>
        {sub && <div className="text-xs text-slate-500">{sub}</div>}
      </div>
    </Card>
  );
}

export function ScoreBar({ label, value }: { label: string; value: number }) {
  const color = value >= 75 ? 'bg-emerald-500' : value >= 50 ? 'bg-amber-500' : 'bg-rose-500';
  return (
    <div>
      <div className="mb-1 flex justify-between text-sm">
        <span className="text-slate-600 dark:text-slate-300">{label}</span>
        <span className="font-semibold">{value}</span>
      </div>
      <div className="h-2 rounded-full bg-slate-200 dark:bg-white/10">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${value}%` }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
          className={`h-2 rounded-full ${color}`}
        />
      </div>
    </div>
  );
}

export function ProgressRing({ value, size = 120, label }: { value: number; size?: number; label?: string }) {
  const radius = (size - 12) / 2;
  const circumference = 2 * Math.PI * radius;
  const hue = Math.round((value / 100) * 140); // red → green
  return (
    <div className="relative inline-flex items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        <circle cx={size / 2} cy={size / 2} r={radius} fill="none" strokeWidth="10" className="stroke-slate-200 dark:stroke-white/10" />
        <motion.circle
          cx={size / 2} cy={size / 2} r={radius} fill="none" strokeWidth="10" strokeLinecap="round"
          stroke={`hsl(${hue} 80% 50%)`}
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: circumference * (1 - value / 100) }}
          transition={{ duration: 1, ease: 'easeOut' }}
        />
      </svg>
      <div className="absolute text-center">
        <div className="text-2xl font-extrabold">{value}%</div>
        {label && <div className="text-[10px] uppercase tracking-wide text-slate-500">{label}</div>}
      </div>
    </div>
  );
}

const DIFFICULTY_STYLES: Record<string, string> = {
  easy: 'bg-emerald-500/15 text-emerald-600 dark:text-emerald-400',
  medium: 'bg-amber-500/15 text-amber-600 dark:text-amber-400',
  hard: 'bg-rose-500/15 text-rose-600 dark:text-rose-400',
};

export function DifficultyChip({ level }: { level: string }) {
  return <span className={`chip ${DIFFICULTY_STYLES[level] ?? DIFFICULTY_STYLES.medium}`}>{level}</span>;
}

const RECO_STYLES: Record<string, [string, string]> = {
  strong_hire: ['Strong Hire', 'bg-emerald-500/15 text-emerald-600 dark:text-emerald-400'],
  hire: ['Hire', 'bg-teal-500/15 text-teal-600 dark:text-teal-400'],
  lean_hire: ['Lean Hire', 'bg-amber-500/15 text-amber-600 dark:text-amber-400'],
  no_hire: ['No Hire', 'bg-rose-500/15 text-rose-600 dark:text-rose-400'],
};

export function RecommendationChip({ value }: { value: string }) {
  const [label, style] = RECO_STYLES[value] ?? RECO_STYLES.lean_hire;
  return <span className={`chip ${style}`}>{label}</span>;
}

export function EmptyState({ icon, title, sub, action }: { icon: string; title: string; sub?: string; action?: ReactNode }) {
  return (
    <div className="flex flex-col items-center gap-2 py-12 text-center">
      <div className="text-4xl">{icon}</div>
      <div className="font-semibold">{title}</div>
      {sub && <div className="max-w-sm text-sm text-slate-500">{sub}</div>}
      {action && <div className="mt-3">{action}</div>}
    </div>
  );
}

export function ErrorNote({ message }: { message: string }) {
  return (
    <div className="rounded-xl border border-rose-500/30 bg-rose-500/10 px-4 py-2.5 text-sm text-rose-600 dark:text-rose-400">
      {message}
    </div>
  );
}
