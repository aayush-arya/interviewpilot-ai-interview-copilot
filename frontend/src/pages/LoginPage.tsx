import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Link, useLocation, useNavigate } from 'react-router-dom';

import client, { apiErrorMessage, tokenStore } from '../api/client';
import { ErrorNote } from '../components/ui';
import { setUser, useAppDispatch } from '../store';
import AuthLayout from './AuthLayout';

interface Form {
  email: string;
  password: string;
}

export default function LoginPage() {
  const { register, handleSubmit, formState } = useForm<Form>();
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const location = useLocation();

  const onSubmit = async (form: Form) => {
    setBusy(true);
    setError('');
    try {
      const { data } = await client.post('/auth/login', form);
      tokenStore.set(data.access_token, data.refresh_token);
      const me = await client.get('/users/me');
      dispatch(setUser(me.data));
      navigate((location.state as any)?.from?.pathname ?? '/app', { replace: true });
    } catch (e) {
      setError(apiErrorMessage(e));
    } finally {
      setBusy(false);
    }
  };

  const oauth = async (provider: 'google' | 'github') => {
    try {
      const { data } = await client.get(`/auth/oauth/${provider}/url`);
      window.location.href = data.url;
    } catch (e) {
      setError(apiErrorMessage(e));
    }
  };

  return (
    <AuthLayout title="Welcome back" sub="Sign in to continue your prep">
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        {error && <ErrorNote message={error} />}
        <input
          className="input !bg-white/10"
          placeholder="Email"
          type="email"
          autoComplete="email"
          {...register('email', { required: true })}
        />
        <input
          className="input !bg-white/10"
          placeholder="Password"
          type="password"
          autoComplete="current-password"
          {...register('password', { required: true })}
        />
        <button className="btn-primary w-full" disabled={busy || formState.isSubmitting}>
          {busy ? 'Signing in…' : 'Sign in'}
        </button>
      </form>
      <div className="my-4 flex items-center gap-3 text-xs text-slate-500">
        <div className="h-px flex-1 bg-white/10" /> or <div className="h-px flex-1 bg-white/10" />
      </div>
      <div className="grid grid-cols-2 gap-3">
        <button className="btn-ghost !border-white/20 !text-slate-200" onClick={() => oauth('google')}>Google</button>
        <button className="btn-ghost !border-white/20 !text-slate-200" onClick={() => oauth('github')}>GitHub</button>
      </div>
      <div className="mt-5 flex justify-between text-sm text-slate-400">
        <Link className="hover:text-brand-400" to="/forgot-password">Forgot password?</Link>
        <Link className="hover:text-brand-400" to="/register">Create account</Link>
      </div>
      <p className="mt-4 text-center text-xs text-slate-500">Demo: demo@user.com / Demo@1234</p>
    </AuthLayout>
  );
}
