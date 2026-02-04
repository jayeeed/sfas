import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/stores/authStore';
import { authService } from '@/services';
import { useToast } from '@/hooks/use-toast';
import type { LoginRequest, RegisterRequest } from '@/types';

export function useAuth() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { toast } = useToast();
  const {
    user,
    isAuthenticated,
    isLoading,
    login: storeLogin,
    logout: storeLogout,
    setLoading,
    setUser,
  } = useAuthStore();

  // Check current user on mount
  const { refetch: checkAuth } = useQuery({
    queryKey: ['auth', 'me'],
    queryFn: async () => {
      const accessToken = localStorage.getItem('access_token');
      if (!accessToken) {
        setLoading(false);
        return null;
      }
      try {
        const userData = await authService.getCurrentUser();
        setUser(userData);
        setLoading(false);
        return userData;
      } catch {
        storeLogout();
        return null;
      }
    },
    enabled: false,
    retry: false,
  });

  // Login mutation
  const loginMutation = useMutation({
    mutationFn: (data: LoginRequest) => authService.login(data),
    onSuccess: (response) => {
      storeLogin(response.user, response.access_token, response.refresh_token);
      queryClient.invalidateQueries({ queryKey: ['auth'] });
      toast({
        title: 'Welcome back!',
        description: `Logged in as ${response.user.name}`,
      });
      navigate('/dashboard');
    },
    onError: (error: Error) => {
      toast({
        title: 'Login failed',
        description: error.message || 'Invalid credentials',
        variant: 'destructive',
      });
    },
  });

  // Register mutation
  const registerMutation = useMutation({
    mutationFn: (data: RegisterRequest) => authService.register(data),
    onSuccess: () => {
      toast({
        title: 'Registration successful!',
        description: 'Please login with your credentials',
      });
      navigate('/login');
    },
    onError: (error: Error) => {
      toast({
        title: 'Registration failed',
        description: error.message || 'Could not create account',
        variant: 'destructive',
      });
    },
  });

  // Logout function
  const logout = async () => {
    await authService.logout();
    storeLogout();
    queryClient.clear();
    navigate('/login');
    toast({
      title: 'Logged out',
      description: 'You have been logged out successfully',
    });
  };

  return {
    user,
    isAuthenticated,
    isLoading,
    login: loginMutation.mutate,
    register: registerMutation.mutate,
    logout,
    checkAuth,
    isLoggingIn: loginMutation.isPending,
    isRegistering: registerMutation.isPending,
  };
}
