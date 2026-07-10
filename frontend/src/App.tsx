import { useEffect } from 'react';
import { Navigate, Route, Routes, useLocation } from 'react-router-dom';

import client, { tokenStore } from './api/client';
import AppShell from './components/AppShell';
import { setUser, useAppDispatch, useAppSelector } from './store';

import AdminPage from './pages/AdminPage';
import AnalyticsPage from './pages/AnalyticsPage';
import CodingPage from './pages/CodingPage';
import CodingRoomPage from './pages/CodingRoomPage';
import CompaniesPage from './pages/CompaniesPage';
import DashboardPage from './pages/DashboardPage';
import FeedbackPage from './pages/FeedbackPage';
import ForgotPasswordPage from './pages/ForgotPasswordPage';
import InterviewRoomPage from './pages/InterviewRoomPage';
import InterviewSetupPage from './pages/InterviewSetupPage';
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import OAuthCompletePage from './pages/OAuthCompletePage';
import PlanPage from './pages/PlanPage';
import RegisterPage from './pages/RegisterPage';
import ResetPasswordPage from './pages/ResetPasswordPage';
import ResumePage from './pages/ResumePage';
import SettingsPage from './pages/SettingsPage';

function ProtectedRoute({ children }: { children: JSX.Element }) {
  const { user, initialized } = useAppSelector((s) => s.auth);
  const location = useLocation();
  if (!initialized) return null; // bootstrapping
  if (!user) return <Navigate to="/login" state={{ from: location }} replace />;
  return children;
}

export default function App() {
  const dispatch = useAppDispatch();
  const theme = useAppSelector((s) => s.ui.theme);

  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark');
  }, [theme]);

  // Session bootstrap: restore user from stored tokens.
  useEffect(() => {
    if (!tokenStore.access) {
      dispatch(setUser(null));
      return;
    }
    client
      .get('/users/me')
      .then(({ data }) => dispatch(setUser(data)))
      .catch(() => dispatch(setUser(null)));
  }, [dispatch]);

  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/forgot-password" element={<ForgotPasswordPage />} />
      <Route path="/reset-password" element={<ResetPasswordPage />} />
      <Route path="/oauth-complete" element={<OAuthCompletePage />} />
      <Route
        path="/app"
        element={
          <ProtectedRoute>
            <AppShell />
          </ProtectedRoute>
        }
      >
        <Route index element={<DashboardPage />} />
        <Route path="interview" element={<InterviewSetupPage />} />
        <Route path="interview/:sessionId" element={<InterviewRoomPage />} />
        <Route path="coding" element={<CodingPage />} />
        <Route path="coding/:problemId" element={<CodingRoomPage />} />
        <Route path="resume" element={<ResumePage />} />
        <Route path="plan" element={<PlanPage />} />
        <Route path="companies" element={<CompaniesPage />} />
        <Route path="feedback" element={<FeedbackPage />} />
        <Route path="analytics" element={<AnalyticsPage />} />
        <Route path="settings" element={<SettingsPage />} />
        <Route path="admin" element={<AdminPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
