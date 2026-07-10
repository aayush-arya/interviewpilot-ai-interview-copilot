import { configureStore, createSlice, type PayloadAction } from '@reduxjs/toolkit';
import { useDispatch, useSelector, type TypedUseSelectorHook } from 'react-redux';

import type { User } from '../types';
import { tokenStore } from '../api/client';

interface AuthState {
  user: User | null;
  initialized: boolean;
}

const authSlice = createSlice({
  name: 'auth',
  initialState: { user: null, initialized: false } as AuthState,
  reducers: {
    setUser(state, action: PayloadAction<User | null>) {
      state.user = action.payload;
      state.initialized = true;
    },
    logout(state) {
      state.user = null;
      state.initialized = true;
      tokenStore.clear();
    },
  },
});

type Theme = 'dark' | 'light';

// Dark-first design; only an explicit user choice switches to light.
const initialTheme: Theme = (localStorage.getItem('ip_theme') as Theme | null) ?? 'dark';

const uiSlice = createSlice({
  name: 'ui',
  initialState: { theme: initialTheme },
  reducers: {
    toggleTheme(state) {
      state.theme = state.theme === 'dark' ? 'light' : 'dark';
      localStorage.setItem('ip_theme', state.theme);
    },
  },
});

export const { setUser, logout } = authSlice.actions;
export const { toggleTheme } = uiSlice.actions;

export const store = configureStore({
  reducer: { auth: authSlice.reducer, ui: uiSlice.reducer },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
export const useAppDispatch: () => AppDispatch = useDispatch;
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;
