import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

import client, { tokenStore } from '../api/client';
import { Spinner } from '../components/ui';
import { setUser, useAppDispatch } from '../store';
import AuthLayout from './AuthLayout';

/** OAuth callback landing: tokens arrive in the URL fragment (never sent to servers). */
export default function OAuthCompletePage() {
  const navigate = useNavigate();
  const dispatch = useAppDispatch();

  useEffect(() => {
    const params = new URLSearchParams(window.location.hash.slice(1));
    const access = params.get('access_token');
    const refresh = params.get('refresh_token');
    if (!access || !refresh) {
      navigate('/login', { replace: true });
      return;
    }
    tokenStore.set(access, refresh);
    window.history.replaceState(null, '', '/oauth-complete');
    client
      .get('/users/me')
      .then(({ data }) => {
        dispatch(setUser(data));
        navigate('/app', { replace: true });
      })
      .catch(() => navigate('/login', { replace: true }));
  }, [navigate, dispatch]);

  return (
    <AuthLayout title="Signing you in…">
      <div className="flex justify-center py-6"><Spinner label="Completing sign-in" /></div>
    </AuthLayout>
  );
}
