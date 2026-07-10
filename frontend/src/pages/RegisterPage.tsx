import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Link, useNavigate } from 'react-router-dom';

import client, { apiErrorMessage, tokenStore } from '../api/client';
import { ErrorNote } from '../components/ui';
import { setUser, useAppDispatch } from '../store';
import AuthLayout from './AuthLayout';

interface Form {
  full_name: string;
  email: string;
  password: string;
}

export default function RegisterPage() {
  const { register, handleSubmit, formState: { errors } } = useForm<Form>();
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const dispatch = useAppDispatch();
  const navigate = useNavigate();

  const onSubmit = async (form: Form) => {
    setBusy(true);
    setError('');
    try {
      await client.post('/auth/register', form);
      const { data } = await client.post('/auth/login', { email: form.email, password: form.password });
      tokenStore.set(data.access_token, data.refresh_token);
      const me = await client.get('/users/me');
      dispatch(setUser(me.data));
      navigate('/app', { replace: true });
    } catch (e) {
      setError(apiErrorMessage(e));
    } finally {
      setBusy(false);
    }
  };

  return (
    <AuthLayout title="Create your account" sub="Free to start — no card required">
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        {error && <ErrorNote message={error} />}
        <input className="input !bg-white/10" placeholder="Full name" {...register('full_name', { required: 'Name is required' })} />
        <input className="input !bg-white/10" placeholder="Email" type="email" autoComplete="email" {...register('email', { required: 'Email is required' })} />
        <div>
          <input
            className="input !bg-white/10"
            placeholder="Password (8+ chars, letters & numbers)"
            type="password"
            autoComplete="new-password"
            {...register('password', {
              required: 'Password is required',
              minLength: { value: 8, message: 'At least 8 characters' },
              validate: (v) => (/[A-Za-z]/.test(v) && /\d/.test(v)) || 'Must contain letters and numbers',
            })}
          />
          {errors.password && <p className="mt-1 text-xs text-rose-400">{errors.password.message}</p>}
        </div>
        <button className="btn-primary w-full" disabled={busy}>{busy ? 'Creating…' : 'Create account'}</button>
      </form>
      <p className="mt-5 text-center text-sm text-slate-400">
        Already registered? <Link className="text-brand-400 hover:underline" to="/login">Sign in</Link>
      </p>
    </AuthLayout>
  );
}
