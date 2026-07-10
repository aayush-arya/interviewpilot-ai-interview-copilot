import axios, { AxiosError } from 'axios';

// Local dev: relative path works via the Vite proxy to localhost:8002.
// Production (Vercel): set VITE_API_BASE_URL to the deployed backend's URL,
// e.g. https://interviewpilot-api.onrender.com/api/v1
const client = axios.create({ baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1' });

export const tokenStore = {
  get access() {
    return localStorage.getItem('ip_access');
  },
  get refresh() {
    return localStorage.getItem('ip_refresh');
  },
  set(access: string, refresh: string) {
    localStorage.setItem('ip_access', access);
    localStorage.setItem('ip_refresh', refresh);
  },
  clear() {
    localStorage.removeItem('ip_access');
    localStorage.removeItem('ip_refresh');
  },
};

client.interceptors.request.use((config) => {
  const token = tokenStore.access;
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

let refreshing: Promise<string> | null = null;

async function refreshAccessToken(): Promise<string> {
  const refresh = tokenStore.refresh;
  if (!refresh) throw new Error('no refresh token');
  const { data } = await axios.post('/api/v1/auth/refresh', { refresh_token: refresh });
  tokenStore.set(data.access_token, data.refresh_token);
  return data.access_token;
}

client.interceptors.response.use(undefined, async (error: AxiosError) => {
  const original = error.config!;
  const isAuthRoute = original.url?.startsWith('/auth/');
  if (error.response?.status === 401 && !isAuthRoute && !(original as any)._retried) {
    (original as any)._retried = true;
    try {
      refreshing = refreshing ?? refreshAccessToken();
      const token = await refreshing;
      refreshing = null;
      original.headers.Authorization = `Bearer ${token}`;
      return client(original);
    } catch {
      refreshing = null;
      tokenStore.clear();
      window.location.href = '/login';
    }
  }
  throw error;
});

export function apiErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const detail = (error.response?.data as any)?.detail;
    if (typeof detail === 'string') return detail;
    if (Array.isArray(detail)) return detail.map((d) => d.msg).join(', ');
    return error.message;
  }
  return String(error);
}

export default client;
