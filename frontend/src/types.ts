export interface User {
  id: number;
  email: string;
  full_name: string;
  avatar_url: string | null;
  provider: string;
  role: string;
  xp: number;
  level: number;
  streak_count: number;
  target_role: string | null;
  target_company: string | null;
  interview_deadline: string | null;
}

export interface TokenPair {
  access_token: string;
  refresh_token: string;
}

export interface CoachEvaluation {
  score: number;
  good: string;
  weak: string;
  faang_view: string;
  ideal_answer: string;
  key_points: string[];
}

export interface Turn {
  turn_index: number;
  question: string;
  answer: string | null;
  coach: CoachEvaluation | null;
  difficulty_at_turn: string;
}

export interface InterviewSession {
  id: number;
  session_type: string;
  topic: string;
  company: string | null;
  difficulty: string;
  status: string;
  started_at: string;
  ended_at: string | null;
  turns?: Turn[];
}

export interface AnswerResponse {
  coach: CoachEvaluation;
  next_question: string;
  difficulty: string;
  turn_index: number;
  xp_awarded: number;
}

export interface Report {
  id: number;
  session_id: number;
  overall: number;
  communication: number;
  confidence: number;
  technical_accuracy: number;
  problem_solving: number;
  hiring_recommendation: string;
  summary: string;
  strengths: string[];
  improvements: string[];
  created_at: string;
  session_type?: string | null;
  topic?: string | null;
  company?: string | null;
}

export interface ResumeAnalysis {
  ats_score: number;
  recruiter_score: number;
  technical_score: number;
  communication_score: number;
  confidence_score: number;
  missing_skills: string[];
  weak_descriptions: string[];
  grammar_issues: string[];
  ats_issues: string[];
  keyword_gaps: string[];
  experience_gaps: string[];
  improvement_suggestions: string[];
  summary: string;
}

export interface Resume {
  id: number;
  filename: string;
  ats_score: number;
  recruiter_score: number;
  technical_score: number;
  communication_score: number;
  confidence_score: number;
  analysis: ResumeAnalysis | null;
  improved_resume: string;
  cover_letter: string;
  linkedin_summary: string;
  created_at: string;
}

export interface PlanDay {
  day: number;
  topic: string;
  goals: string[];
}

export interface Plan {
  id: number;
  resume_id: number | null;
  roadmap: {
    days: PlanDay[];
    weekly_goals: string[];
    skill_gaps: string[];
    priority_topics: string[];
  };
  created_at: string;
  days_until_deadline: number | null;
}

export interface TrendPoint {
  date: string;
  value: number;
}

export interface TopicMastery {
  topic: string;
  average_score: number;
  sessions: number;
}

export interface Dashboard {
  readiness_percent: number;
  streak_count: number;
  xp: number;
  level: number;
  next_level_xp: number;
  resume_score: number | null;
  sessions_completed: number;
  problems_solved: number;
  weak_areas: TopicMastery[];
  strong_areas: TopicMastery[];
  recommended_topics: string[];
  score_trend: TrendPoint[];
  recent_feedback: {
    session_id: number;
    overall: number;
    recommendation: string;
    summary: string;
    topic: string;
    created_at: string;
  }[];
  badges: { code: string; name: string; icon: string; description: string }[];
  days_until_deadline: number | null;
}

export interface Analytics {
  score_trend: TrendPoint[];
  confidence_trend: TrendPoint[];
  practice_frequency: TrendPoint[];
  topic_mastery: TopicMastery[];
  success_prediction: number;
  total_sessions: number;
  total_submissions: number;
  average_score: number;
}

export interface ProblemSummary {
  id: number;
  title: string;
  slug: string;
  difficulty: string;
  topic: string;
}

export interface ProblemDetail extends ProblemSummary {
  description: string;
  starter_code: Record<string, string>;
  visible_tests: { input: string; expected: string }[];
  time_limit_ms: number;
}

export interface TestResult {
  index: number;
  hidden: boolean;
  passed: boolean;
  input: string | null;
  expected: string | null;
  actual: string | null;
  error: string | null;
}

export interface CodeReview {
  verdict: string;
  time_complexity: string;
  space_complexity: string;
  correctness_notes: string;
  edge_cases_missed: string[];
  quality_issues: string[];
  optimizations: string[];
  score: number;
}

export interface Submission {
  id: number;
  problem_id: number;
  language: string;
  status: string;
  passed_count: number;
  total_count: number;
  results: TestResult[];
  review: CodeReview | null;
  runtime_ms: number;
  xp_awarded: number;
  created_at: string;
}

export interface RunResult {
  stdout: string;
  stderr: string;
  exit_code: number;
  timed_out: boolean;
  runtime_ms: number;
}

export interface LeaderboardEntry {
  rank: number;
  full_name: string;
  level: number;
  xp: number;
  streak_count: number;
  is_me: boolean;
}
