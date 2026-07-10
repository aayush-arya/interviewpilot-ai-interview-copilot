import {
  ArcElement, BarElement, CategoryScale, Chart as ChartJS, Filler, Legend, LinearScale,
  LineElement, PointElement, RadialLinearScale, Tooltip,
} from 'chart.js';
import { Bar, Line, Radar } from 'react-chartjs-2';

import { useAppSelector } from '../store';
import type { TopicMastery, TrendPoint } from '../types';

ChartJS.register(
  CategoryScale, LinearScale, PointElement, LineElement, BarElement, ArcElement,
  RadialLinearScale, Filler, Tooltip, Legend
);

function useChartColors() {
  const theme = useAppSelector((s) => s.ui.theme);
  return {
    grid: theme === 'dark' ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.07)',
    text: theme === 'dark' ? '#94a3b8' : '#64748b',
  };
}

export function TrendChart({ points, label, color = '#6366f1' }: { points: TrendPoint[]; label: string; color?: string }) {
  const { grid, text } = useChartColors();
  return (
    <Line
      data={{
        labels: points.map((p) => p.date.slice(5)),
        datasets: [{
          label,
          data: points.map((p) => p.value),
          borderColor: color,
          backgroundColor: `${color}25`,
          fill: true,
          tension: 0.35,
          pointRadius: 3,
        }],
      }}
      options={{
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { color: grid }, ticks: { color: text } },
          y: { grid: { color: grid }, ticks: { color: text }, suggestedMin: 0, suggestedMax: 100 },
        },
      }}
    />
  );
}

export function FrequencyChart({ points }: { points: TrendPoint[] }) {
  const { grid, text } = useChartColors();
  return (
    <Bar
      data={{
        labels: points.map((p) => p.date.slice(5)),
        datasets: [{ label: 'activities', data: points.map((p) => p.value), backgroundColor: '#8b5cf6', borderRadius: 6 }],
      }}
      options={{
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { display: false }, ticks: { color: text } },
          y: { grid: { color: grid }, ticks: { color: text, stepSize: 1 } },
        },
      }}
    />
  );
}

export function ScoreRadar({ scores }: { scores: Record<string, number> }) {
  const { grid, text } = useChartColors();
  return (
    <Radar
      data={{
        labels: Object.keys(scores),
        datasets: [{
          label: 'Score',
          data: Object.values(scores),
          borderColor: '#6366f1',
          backgroundColor: 'rgba(99,102,241,0.2)',
          pointBackgroundColor: '#6366f1',
        }],
      }}
      options={{
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          r: {
            min: 0, max: 100,
            grid: { color: grid },
            angleLines: { color: grid },
            pointLabels: { color: text, font: { size: 11 } },
            ticks: { display: false },
          },
        },
      }}
    />
  );
}

export function MasteryBars({ items }: { items: TopicMastery[] }) {
  const { grid, text } = useChartColors();
  return (
    <Bar
      data={{
        labels: items.map((m) => m.topic),
        datasets: [{
          label: 'avg score',
          data: items.map((m) => m.average_score),
          backgroundColor: items.map((m) =>
            m.average_score >= 75 ? '#10b981' : m.average_score >= 50 ? '#f59e0b' : '#f43f5e'
          ),
          borderRadius: 6,
        }],
      }}
      options={{
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { min: 0, max: 100, grid: { color: grid }, ticks: { color: text } },
          y: { grid: { display: false }, ticks: { color: text } },
        },
      }}
    />
  );
}
