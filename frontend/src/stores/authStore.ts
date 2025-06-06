import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { AuthState, User } from '../types/authTypes';

export const useAuthStore = create(
  persist<AuthState>(
    (set) => ({
      accessToken: null,
      user: null,
      setToken: (token: string) => set({ accessToken: token }),
      setUser: (user: User) => set({ user }),
      clearAuth: () => set({ accessToken: null, user: null }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        accessToken: state.accessToken,
        user: state.user,
        setToken: state.setToken,
        setUser: state.setUser,
        clearAuth: state.clearAuth,
      }),
    }
  )
);