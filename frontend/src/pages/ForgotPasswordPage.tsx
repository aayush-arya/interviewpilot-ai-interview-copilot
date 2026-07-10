import { useState } from 'react';
import { Link } from 'react-router-dom';

import client, { apiErrorMessage } from '../api/client';
import { ErrorNote } from '../components/ui';
import AuthLayout from './AuthLayout';

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [sent, setSent] = useState(false);
  const [error, setError] = useState('');

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await client.post('/auth/forgot-password', { email });
      setSent(true);
    } catch (err) {
      setError(apiErrorMessage(err));
    }
  };

  return (
    <AuthLayout title="Reset your password" sub="We'll email you a reset link">
      {sent ? (
        <div className="rounded-xl border border-emerald-500/30 bg-emerald-500/10 px-4 py-3 text-sm text-emerald-400">
          If that email exists, a reset link is on its way. Check your inbox (or the server log in dev mode).
        </div>
      ) : (
        <form onSubmit={submit} className="space-y-4">
          {error && <ErrorNote message={error} />}
          <input className="input !bg-white/10" placeholder="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          <button className="btn-primary w-full">Send reset link</button>
        </form>
      )}
      <p className="mt-5 text-center text-sm text-slate-400">
        <Link className="text-brand-400 hover:underline" to="/login">Back to sign in</Link>
      </p>
    </AuthLayout>
  );
}
