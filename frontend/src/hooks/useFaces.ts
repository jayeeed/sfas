import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { faceService } from '@/services';
import { useToast } from '@/hooks/use-toast';
import { useAuthStore } from '@/stores/authStore';
import type { RegisterFaceRequest } from '@/types';

export function useFaces() {
  const queryClient = useQueryClient();
  const { toast } = useToast();
  const { user } = useAuthStore();

  // Get my faces
  const facesQuery = useQuery({
    queryKey: ['faces', 'me'],
    queryFn: () => faceService.getMyFaces(),
    enabled: !!user,
  });

  // Get available models
  const modelsQuery = useQuery({
    queryKey: ['faces', 'models'],
    queryFn: () => faceService.getAvailableModels(),
  });

  // Register face mutation
  const registerFaceMutation = useMutation({
    mutationFn: (data: RegisterFaceRequest) => faceService.registerFace(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['faces'] });
      toast({
        title: 'Face registered!',
        description: 'Your face has been successfully registered.',
      });
    },
    onError: (error: Error) => {
      toast({
        title: 'Registration failed',
        description: error.message || 'Could not register face. Please try again.',
        variant: 'destructive',
      });
    },
  });

  // Delete face mutation
  const deleteFaceMutation = useMutation({
    mutationFn: (faceId: string) => faceService.deleteFace(faceId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['faces'] });
      toast({
        title: 'Face deleted',
        description: 'Face registration has been removed.',
      });
    },
    onError: (error: Error) => {
      toast({
        title: 'Delete failed',
        description: error.message || 'Could not delete face. Please try again.',
        variant: 'destructive',
      });
    },
  });

  return {
    faces: facesQuery.data || [],
    isLoading: facesQuery.isLoading,
    isError: facesQuery.isError,
    refetch: facesQuery.refetch,

    models: modelsQuery.data?.models || [],
    isModelsLoading: modelsQuery.isLoading,

    registerFace: registerFaceMutation.mutate,
    isRegistering: registerFaceMutation.isPending,

    deleteFace: deleteFaceMutation.mutate,
    isDeleting: deleteFaceMutation.isPending,
  };
}
