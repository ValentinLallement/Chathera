import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { AuthState, User } from '../types/authTypes';

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      accessToken: null,
      user: null,
      setToken: (token: string) => set({ accessToken: token }),
      setUser: (user: User) => set({ user }),
      clearAuth: () => {
        set({ accessToken: null, user: null });
        localStorage.removeItem('auth-storage');
      },
    }),
    {
      name: 'auth-storage',
      // Only persist the token and user data, not the functions
      partialize: (state) => ({
        accessToken: state.accessToken,
        user: state.user,
      }),
    }
  )
);