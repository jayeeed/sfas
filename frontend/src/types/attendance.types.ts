import { FaceModel } from './face.types';

export type AttendanceType = 'check_in' | 'check_out';
export type AttendanceStatus = 'in' | 'done' | 'absent';

export interface AttendanceRecord {
  id: string;
  user_id: string;
  user_name?: string;
  check_in?: string;
  check_out?: string;
  type: AttendanceType;
  confidence: number;
  model: FaceModel;
  camera_id?: string;
  created_at: string;
}

export interface MarkAttendanceRequest {
  image: string; // base64
  camera_id?: string;
  model?: FaceModel;
}

export interface MarkAttendanceResponse {
  success: boolean;
  user_id: string;
  user_name: string;
  emp_id?: string;
  action: AttendanceType;
  confidence: number;
  model_used: string;
  timestamp: string;
  attendance_id: string;
}

export interface AttendanceListParams {
  page?: number;
  limit?: number;
  user_id?: string;
  start_date?: string;
  end_date?: string;
}

export interface AttendanceListResponse {
  items: AttendanceRecord[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

export interface AttendanceStats {
  present_days: number;
  absent_days: number;
  total_hours: number;
  avg_hours: number;
  on_time_rate: number;
  late_arrivals: number;
}

export interface TodayStatus {
  is_checked_in: boolean;
  check_in_time?: string;
  check_out_time?: string;
  working_hours?: number;
}
