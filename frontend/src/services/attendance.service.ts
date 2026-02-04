import api from './api';
import type {
  AttendanceRecord,
  AttendanceListParams,
  AttendanceListResponse,
  AttendanceStats,
  MarkAttendanceRequest,
  MarkAttendanceResponse,
  TodayStatus,
} from '@/types';

export const attendanceService = {
  async markAttendance(data: MarkAttendanceRequest): Promise<MarkAttendanceResponse> {
    const response = await api.post<MarkAttendanceResponse>('/attendance/mark', data);
    return response.data;
  },

  async getAttendanceList(params?: AttendanceListParams): Promise<AttendanceListResponse> {
    const response = await api.get<AttendanceListResponse>('/attendance', { params });
    return response.data;
  },

  async getAttendanceById(id: string): Promise<AttendanceRecord> {
    const response = await api.get<AttendanceRecord>(`/attendance/${id}`);
    return response.data;
  },

  async getAttendanceStats(userId: string): Promise<AttendanceStats> {
    const response = await api.get<AttendanceStats>(`/attendance/stats/${userId}`);
    return response.data;
  },

  async getMyStats(): Promise<AttendanceStats> {
    const response = await api.get<AttendanceStats>('/attendance/stats/me');
    return response.data;
  },

  async getTodayStatus(): Promise<TodayStatus> {
    const response = await api.get<TodayStatus>('/attendance/today');
    return response.data;
  },

  async getRecentActivity(limit: number = 5): Promise<AttendanceRecord[]> {
    const response = await api.get<AttendanceListResponse>('/attendance', {
      params: { limit, page: 1 },
    });
    return response.data.items;
  },
};
