import { format } from 'date-fns';
import {
  CheckCircle2,
  Clock,
  Timer,
  Calendar,
  Camera,
} from 'lucide-react';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { Badge } from '@/components/ui/badge';
import { MainLayout } from '@/components/layout';
import { useAuthStore } from '@/stores/authStore';
import { useAttendance } from '@/hooks/useAttendance';
import { Link } from 'react-router-dom';

export default function Dashboard() {
  const { user } = useAuthStore();
  const {
    todayStatus,
    isTodayLoading,
    recentActivity,
    isRecentLoading,
    stats,
    isStatsLoading,
  } = useAttendance();

  const greeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good Morning';
    if (hour < 18) return 'Good Afternoon';
    return 'Good Evening';
  };

  const formatTime = (isoString?: string) => {
    if (!isoString) return '--:--';
    return format(new Date(isoString), 'h:mm a');
  };

  const formatWorkingHours = (hours?: number) => {
    if (!hours) return '0h 0m';
    const h = Math.floor(hours);
    const m = Math.round((hours - h) * 60);
    return `${h}h ${m}m`;
  };

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Welcome Section */}
        <div>
          <h1 className="text-2xl font-bold tracking-tight">
            {greeting()}, {user?.name?.split(' ')[0]}! 👋
          </h1>
          <p className="text-muted-foreground">
            Today is {format(new Date(), 'EEEE, MMMM d, yyyy')}
          </p>
        </div>

        {/* Status Cards */}
        <div className="grid gap-4 md:grid-cols-3">
          {/* Check-in Status */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Today's Status</CardTitle>
              <CheckCircle2 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              {isTodayLoading ? (
                <Skeleton className="h-8 w-24" />
              ) : (
                <>
                  <div className="text-2xl font-bold">
                    {todayStatus?.is_checked_in ? (
                      <Badge className="bg-green-500 hover:bg-green-600 text-lg px-3 py-1">
                        Checked In
                      </Badge>
                    ) : (
                      <Badge variant="secondary" className="text-lg px-3 py-1">
                        Not Yet
                      </Badge>
                    )}
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">
                    {todayStatus?.is_checked_in ? 'You are marked present' : 'Mark your attendance'}
                  </p>
                </>
              )}
            </CardContent>
          </Card>

          {/* Check-in Time */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Check-in Time</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              {isTodayLoading ? (
                <Skeleton className="h-8 w-24" />
              ) : (
                <>
                  <div className="text-2xl font-bold">
                    {formatTime(todayStatus?.check_in_time)}
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">
                    {todayStatus?.check_out_time
                      ? `Out: ${formatTime(todayStatus.check_out_time)}`
                      : 'Not checked out yet'}
                  </p>
                </>
              )}
            </CardContent>
          </Card>

          {/* Working Hours */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Working Hours</CardTitle>
              <Timer className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              {isTodayLoading ? (
                <Skeleton className="h-8 w-24" />
              ) : (
                <>
                  <div className="text-2xl font-bold">
                    {formatWorkingHours(todayStatus?.working_hours)}
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">
                    {todayStatus?.is_checked_in && !todayStatus?.check_out_time
                      ? 'Currently working'
                      : 'Today'}
                  </p>
                </>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Quick Action - Only show for Admin */}
        {user?.role === 'admin' && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Camera className="h-5 w-5" />
                Check-in Station
              </CardTitle>
              <CardDescription>
                Start continuous face scanning to mark attendance for users
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Link to="/attendance/mark">
                <Button size="lg" className="w-full md:w-auto">
                  <Camera className="mr-2 h-5 w-5" />
                  Start Check-in
                </Button>
              </Link>
            </CardContent>
          </Card>
        )}

        {/* Stats and Recent Activity */}
        <div className="grid gap-6 md:grid-cols-2">
          {/* Monthly Stats */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calendar className="h-5 w-5" />
                This Month
              </CardTitle>
            </CardHeader>
            <CardContent>
              {isStatsLoading ? (
                <div className="space-y-3">
                  <Skeleton className="h-4 w-full" />
                  <Skeleton className="h-4 w-full" />
                  <Skeleton className="h-4 w-full" />
                </div>
              ) : (
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Days Present</span>
                    <span className="font-medium">{stats?.present_days || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Days Absent</span>
                    <span className="font-medium">{stats?.absent_days || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Average Hours</span>
                    <span className="font-medium">
                      {stats?.avg_hours?.toFixed(1) || 0}h
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">On-time Rate</span>
                    <span className="font-medium">
                      {((stats?.on_time_rate || 0) * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Recent Activity */}
          <Card>
            <CardHeader>
              <CardTitle>Recent Activity</CardTitle>
            </CardHeader>
            <CardContent>
              {isRecentLoading ? (
                <div className="space-y-3">
                  {[...Array(3)].map((_, i) => (
                    <Skeleton key={i} className="h-12 w-full" />
                  ))}
                </div>
              ) : recentActivity.length === 0 ? (
                <p className="text-muted-foreground text-sm">No recent activity</p>
              ) : (
                <div className="space-y-3">
                  {recentActivity.map((record) => (
                    <div
                      key={record.id}
                      className="flex items-center justify-between py-2 border-b last:border-0"
                    >
                      <div className="flex items-center gap-3">
                        <div
                          className={`h-2 w-2 rounded-full ${
                            record.type === 'check_in'
                              ? 'bg-green-500'
                              : 'bg-orange-500'
                          }`}
                        />
                        <div>
                          <p className="text-sm font-medium">
                            {record.type === 'check_in' ? 'Checked in' : 'Checked out'}
                          </p>
                          <p className="text-xs text-muted-foreground">
                            {format(new Date(record.created_at), 'MMM d, h:mm a')}
                          </p>
                        </div>
                      </div>
                      <Badge variant="outline" className="text-xs">
                        {(record.confidence * 100).toFixed(0)}%
                      </Badge>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </MainLayout>
  );
}
