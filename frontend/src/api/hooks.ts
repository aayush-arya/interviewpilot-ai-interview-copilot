import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import type {
  Analytics, AnswerResponse, Dashboard, InterviewSession, LeaderboardEntry, Plan,
  ProblemDetail, ProblemSummary, Report, Resume, RunResult, Submission, User,
} from '../types';
import client from './client';

export const useDashboard = () =>
  useQuery<Dashboard>({
    queryKey: ['dashboard'],
    queryFn: async () => (await client.get('/dashboard')).data,
  });

export const useAnalytics = () =>
  useQuery<Analytics>({
    queryKey: ['analytics'],
    queryFn: async () => (await client.get('/analytics')).data,
  });

export const useLeaderboard = () =>
  useQuery<LeaderboardEntry[]>({
    queryKey: ['leaderboard'],
    queryFn: async () => (await client.get('/users/leaderboard')).data,
  });

export const useCatalog = () =>
  useQuery<{ tracks: string[]; companies: { name: string; blurb: string }[] }>({
    queryKey: ['catalog'],
    queryFn: async () => (await client.get('/interviews/catalog')).data,
    staleTime: Infinity,
  });

export const useLatestResume = () =>
  useQuery<Resume | null>({
    queryKey: ['resume'],
    queryFn: async () => (await client.get('/resumes/latest')).data,
  });

export const useAnalyzeResume = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (file: File) => {
      const form = new FormData();
      form.append('file', file);
      return (await client.post<Resume>('/resumes/analyze', form)).data;
    },
    onSuccess: (data) => {
      qc.setQueryData(['resume'], data);
      qc.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
};

export const useLatestPlan = () =>
  useQuery<Plan | null>({
    queryKey: ['plan'],
    queryFn: async () => (await client.get('/plans/latest')).data,
  });

export const useGeneratePlan = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async () => (await client.post<Plan>('/plans/generate')).data,
    onSuccess: (data) => qc.setQueryData(['plan'], data),
  });
};

export const useSessions = () =>
  useQuery<InterviewSession[]>({
    queryKey: ['sessions'],
    queryFn: async () => (await client.get('/interviews')).data,
  });

export const useSession = (id: number | null) =>
  useQuery<InterviewSession>({
    queryKey: ['session', id],
    queryFn: async () => (await client.get(`/interviews/${id}`)).data,
    enabled: id != null,
  });

export const useStartInterview = () =>
  useMutation({
    mutationFn: async (payload: {
      session_type: string;
      topic: string;
      company?: string | null;
      difficulty: string;
    }) => (await client.post<InterviewSession>('/interviews', payload)).data,
  });

export const useAnswer = (sessionId: number) =>
  useMutation({
    mutationFn: async (payload: { answer: string; voice_metrics?: object }) =>
      (await client.post<AnswerResponse>(`/interviews/${sessionId}/answer`, payload)).data,
  });

export const useFinishInterview = (sessionId: number) => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async () => (await client.post<Report>(`/interviews/${sessionId}/finish`)).data,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['dashboard'] });
      qc.invalidateQueries({ queryKey: ['reports'] });
    },
  });
};

export const useReports = () =>
  useQuery<Report[]>({
    queryKey: ['reports'],
    queryFn: async () => (await client.get('/interviews/reports/all')).data,
  });

export const useProblems = () =>
  useQuery<ProblemSummary[]>({
    queryKey: ['problems'],
    queryFn: async () => (await client.get('/coding/problems')).data,
  });

export const useProblem = (id: number | null) =>
  useQuery<ProblemDetail>({
    queryKey: ['problem', id],
    queryFn: async () => (await client.get(`/coding/problems/${id}`)).data,
    enabled: id != null,
  });

export const useRunCode = () =>
  useMutation({
    mutationFn: async (payload: { language: string; code: string; stdin: string }) =>
      (await client.post<RunResult>('/coding/run', payload)).data,
  });

export const useSubmitCode = (problemId: number) => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: { language: string; code: string }) =>
      (await client.post<Submission>(`/coding/problems/${problemId}/submit`, payload)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['dashboard'] }),
  });
};

export const useUpdateProfile = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: Partial<User> & { interview_deadline?: string | null }) =>
      (await client.patch<User>('/users/me', payload)).data,
    onSuccess: () => qc.invalidateQueries(),
  });
};

export const useAdminStats = (enabled: boolean) =>
  useQuery({
    queryKey: ['admin-stats'],
    queryFn: async () => (await client.get('/admin/stats')).data,
    enabled,
  });

export const useAdminUsers = (enabled: boolean) =>
  useQuery<User[]>({
    queryKey: ['admin-users'],
    queryFn: async () => (await client.get('/admin/users')).data,
    enabled,
  });
