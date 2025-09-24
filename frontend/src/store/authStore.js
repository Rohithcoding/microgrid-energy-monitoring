import { create } from 'zustand';
import { persist } from 'zustand/middleware';

const useAuthStore = create(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      login: async (username, password) => {
        set({ isLoading: true, error: null });
        
        try {
          const response = await fetch('http://localhost:8000/auth/login', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password }),
          });

          if (!response.ok) {
            throw new Error('Invalid credentials');
          }

          const data = await response.json();
          
          set({
            user: data.user,
            token: data.access_token,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });

          return { success: true };
        } catch (error) {
          set({
            isLoading: false,
            error: error.message,
          });
          return { success: false, error: error.message };
        }
      },

      logout: () => {
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          error: null,
        });
      },

      clearError: () => {
        set({ error: null });
      },

      // Mock login for demo purposes
      mockLogin: (role = 'operator') => {
        const mockUser = {
          id: 1,
          username: role === 'admin' ? 'admin' : 'operator',
          email: `${role}@microgrid.com`,
          role: role,
          is_active: true,
        };

        set({
          user: mockUser,
          token: 'mock-jwt-token',
          isAuthenticated: true,
          isLoading: false,
          error: null,
        });
      },

      hasRole: (requiredRole) => {
        const { user } = get();
        if (!user) return false;
        
        const roleHierarchy = {
          'operator': 1,
          'admin': 2,
        };
        
        return roleHierarchy[user.role] >= roleHierarchy[requiredRole];
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

export default useAuthStore;
