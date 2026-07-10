import { useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';

import client, { apiErrorMessage } from '../api/client';
import { ErrorNote } from '../components/ui';
import AuthLayout from './AuthLayout';

export default function ResetPasswordPage() {
  const [params] = useSearchParams();
  const token = params.get('token') ?? '';
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await client.post('/auth/reset-password', { token, new_password: password });
      navigate('/login');
    } catch (err) {
      setError(apiErrorMessage(err));
    }
  };

  if (!token) {
    return (
      <AuthLayout title="Invalid link">
        <p className="text-center text-sm text-slate-400">
          This reset link is missing its token. <Link to="/forgot-password" className="text-brand-400">Request a new one</Link>.
        </p>
      </AuthLayout>
    );
  }

  return (
    <AuthLayout title="Choose a new password">
      <form onSubmit={submit} className="space-y-4">
        {error && <ErrorNote message={error} />}
        <input
          className="input !bg-white/10"
          placeholder="New password (8+ chars, letters & numbers)"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          minLength={8}
        />
        <button className="btn-primary w-full">Update password</button>
      </form>
    </AuthLayout>
  );
}
