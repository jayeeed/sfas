import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { attendanceService } from '@/services';
import { useToast } from '@/hooks/use-toast';
import type { AttendanceListParams, MarkAttendanceRequest } from '@/types';

export function useAttendance(params?: AttendanceListParams) {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  // Get attendance list
  const attendanceQuery = useQuery({
    queryKey: ['attendance', params],
    queryFn: () => attendanceService.getAttendanceList(params),
  });

  // Get today's status
  const todayStatusQuery = useQuery({
    queryKey: ['attendance', 'today'],
    queryFn: () => attendanceService.getTodayStatus(),
  });

  // Get recent activity
  const recentActivityQuery = useQuery({
    queryKey: ['attendance', 'recent'],
    queryFn: () => attendanceService.getRecentActivity(5),
  });

  // Get my stats
  const statsQuery = useQuery({
    queryKey: ['attendance', 'stats', 'me'],
    queryFn: () => attendanceService.getMyStats(),
  });

  // Get system stats (admin only)
  const systemStatsQuery = useQuery({
    queryKey: ['attendance', 'stats', 'system'],
    queryFn: () => attendanceService.getSystemStats(),
    enabled: false, // Will be enabled by component if user is admin
  });

  // Mark attendance mutation
  const markAttendanceMutation = useMutation({
    mutationFn: (data: MarkAttendanceRequest) => attendanceService.markAttendance(data),
    onSuccess: (response) => {
      // Only show toast for recognized users (success: true)
      if (response.success) {
        queryClient.invalidateQueries({ queryKey: ['attendance'] });
        toast({
          title: response.action === 'check_in' ? '✅ Checked In!' : '👋 Checked Out!',
          description: `${response.user_name} ${response.emp_id ? `(${response.emp_id})` : ''} - Confidence: ${(response.confidence * 100).toFixed(1)}%`,
        });
      } else {
        // For unknown (guest), we don't show toast, but the query should succeed
        // ContinuousScanner handles the UI update
      }
    },
    onError: (error: Error) => {
      toast({
        title: 'Attendance marking failed',
        description: error.message || 'Could not mark attendance. Please try again.',
        variant: 'destructive',
      });
    },
  });

  return {
    // Attendance list
    records: attendanceQuery.data?.items || [],
    total: attendanceQuery.data?.total || 0,
    totalPages: attendanceQuery.data?.total_pages || 0,
    isLoading: attendanceQuery.isLoading,
    isError: attendanceQuery.isError,
    refetch: attendanceQuery.refetch,

    // Today's status
    todayStatus: todayStatusQuery.data,
    isTodayLoading: todayStatusQuery.isLoading,

    // Recent activity
    recentActivity: recentActivityQuery.data || [],
    isRecentLoading: recentActivityQuery.isLoading,

    // Stats
    stats: statsQuery.data,
    isStatsLoading: statsQuery.isLoading,

    // System stats
    systemStats: systemStatsQuery.data,
    isSystemStatsLoading: systemStatsQuery.isLoading,
    refetchSystemStats: systemStatsQuery.refetch,

    // Mark attendance
    markAttendance: markAttendanceMutation.mutate,
    isMarking: markAttendanceMutation.isPending,
    markResult: markAttendanceMutation.data,
  };
}
