import { useState } from 'react';
import { format, subDays, startOfMonth, endOfMonth } from 'date-fns';
import { Calendar, Download, ChevronLeft, ChevronRight } from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { MainLayout } from '@/components/layout';
import { useAttendance } from '@/hooks/useAttendance';

type DateFilter = 'today' | 'week' | 'month' | 'custom';

export default function AttendanceHistory() {
  const [dateFilter, setDateFilter] = useState<DateFilter>('month');
  const [page, setPage] = useState(1);
  const limit = 10;

  const getDateRange = () => {
    const today = new Date();
    switch (dateFilter) {
      case 'today':
        return {
          start_date: format(today, 'yyyy-MM-dd'),
          end_date: format(today, 'yyyy-MM-dd'),
        };
      case 'week':
        return {
          start_date: format(subDays(today, 7), 'yyyy-MM-dd'),
          end_date: format(today, 'yyyy-MM-dd'),
        };
      case 'month':
      default:
        return {
          start_date: format(startOfMonth(today), 'yyyy-MM-dd'),
          end_date: format(endOfMonth(today), 'yyyy-MM-dd'),
        };
    }
  };

  const { start_date, end_date } = getDateRange();

  const { records, total, totalPages, isLoading, stats, isStatsLoading } = useAttendance({
    page,
    limit,
    start_date,
    end_date,
  });

  const formatTime = (isoString?: string) => {
    if (!isoString) return '--:--';
    try {
      const date = new Date(isoString);
      if (isNaN(date.getTime())) return 'Invalid';
      return format(date, 'h:mm a');
    } catch (e) {
      return 'Invalid';
    }
  };

  const formatHours = (hours?: number) => {
    if (!hours) return '0h 0m';
    const h = Math.floor(hours);
    const m = Math.round((hours - h) * 60);
    return `${h}h ${m}m`;
  };

  const getStatusBadge = (checkIn?: string, checkOut?: string) => {
    if (!checkIn) {
      return <Badge variant="destructive">Absent</Badge>;
    }
    if (!checkOut) {
      return <Badge className="bg-primary hover:bg-primary/90">In</Badge>;
    }
    return <Badge variant="secondary">Done</Badge>;
  };

  const exportToCSV = () => {
    const headers = ['Date', 'Name', 'Emp ID', 'Check In', 'Check Out', 'Hours', 'Status'];
    const rows = records.map((record) => {
      let dateStr = '-';
      try {
        const d = record.date || record.check_in_time;
        if (d && !isNaN(new Date(d).getTime())) {
          dateStr = format(new Date(d), 'yyyy-MM-dd');
        }
      } catch (e) {}

      return [
        dateStr,
        record.user_name || 'Unknown',
        record.emp_id || '-',
        record.check_in_time ? formatTime(record.check_in_time) : '-',
        record.check_out_time ? formatTime(record.check_out_time) : '-',
        formatHours(
          record.check_in_time && record.check_out_time
            ? (new Date(record.check_out_time).getTime() - new Date(record.check_in_time).getTime()) /
                (1000 * 60 * 60)
            : 0
        ),
        record.check_out_time ? 'Done' : record.check_in_time ? 'In' : 'Absent',
      ];
    });

    const csv = [headers.join(','), ...rows.map((row) => row.join(','))].join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `attendance_${start_date}_${end_date}.csv`;
    a.click();
  };

  return (
    <MainLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold">Attendance History</h1>
          <p className="text-muted-foreground">View and export your attendance records</p>
        </div>

        {/* Stats Cards */}
        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Days Present</CardTitle>
            </CardHeader>
            <CardContent>
              {isStatsLoading ? (
                <Skeleton className="h-8 w-16" />
              ) : (
                <div className="text-2xl font-bold">{stats?.present_days || 0}</div>
              )}
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Average Hours</CardTitle>
            </CardHeader>
            <CardContent>
              {isStatsLoading ? (
                <Skeleton className="h-8 w-16" />
              ) : (
                <div className="text-2xl font-bold">{stats?.avg_hours?.toFixed(1) || 0}h</div>
              )}
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">On-time Rate</CardTitle>
            </CardHeader>
            <CardContent>
              {isStatsLoading ? (
                <Skeleton className="h-8 w-16" />
              ) : (
                <div className="text-2xl font-bold">
                  {((stats?.on_time_rate || 0) * 100).toFixed(0)}%
                </div>
              )}
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Late Arrivals</CardTitle>
            </CardHeader>
            <CardContent>
              {isStatsLoading ? (
                <Skeleton className="h-8 w-16" />
              ) : (
                <div className="text-2xl font-bold">{stats?.late_arrivals || 0}</div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Filters */}
        <Card>
          <CardContent className="pt-6">
            <div className="flex flex-wrap gap-4 items-center justify-between">
              <div className="flex items-center gap-4">
                <Calendar className="h-5 w-5 text-muted-foreground" />
                <Select
                  value={dateFilter}
                  onValueChange={(value) => {
                    setDateFilter(value as DateFilter);
                    setPage(1);
                  }}
                >
                  <SelectTrigger className="w-40">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="today">Today</SelectItem>
                    <SelectItem value="week">This Week</SelectItem>
                    <SelectItem value="month">This Month</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <Button variant="outline" onClick={exportToCSV}>
                <Download className="mr-2 h-4 w-4" />
                Export CSV
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Table */}
        <Card>
          <CardContent className="pt-6">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Date</TableHead>
                  <TableHead>Name</TableHead>
                  <TableHead>Emp ID</TableHead>
                  <TableHead>Check In</TableHead>
                  <TableHead>Check Out</TableHead>
                  <TableHead>Hours</TableHead>
                  <TableHead>Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {isLoading ? (
                  [...Array(5)].map((_, i) => (
                    <TableRow key={i}>
                      <TableCell><Skeleton className="h-4 w-24" /></TableCell>
                      <TableCell><Skeleton className="h-4 w-32" /></TableCell>
                      <TableCell><Skeleton className="h-4 w-16" /></TableCell>
                      <TableCell><Skeleton className="h-4 w-16" /></TableCell>
                      <TableCell><Skeleton className="h-4 w-16" /></TableCell>
                      <TableCell><Skeleton className="h-4 w-16" /></TableCell>
                      <TableCell><Skeleton className="h-4 w-16" /></TableCell>
                    </TableRow>
                  ))
                ) : records.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={7} className="text-center text-muted-foreground py-8">
                      No attendance records found
                    </TableCell>
                  </TableRow>
                ) : (
                  records.map((record) => {
                    const hours =
                      record.check_in_time && record.check_out_time
                        ? (new Date(record.check_out_time).getTime() -
                            new Date(record.check_in_time).getTime()) /
                          (1000 * 60 * 60)
                        : undefined;
                    return (
                      <TableRow key={record.id}>
                        <TableCell className="font-medium">
                          {(() => {
                            try {
                              const dateStr = record.date || record.check_in_time;
                              if (!dateStr) return 'Unknown Date';
                              const date = new Date(dateStr);
                              if (isNaN(date.getTime())) return 'Invalid Date';
                              return format(date, 'MMM d, yyyy');
                            } catch (e) {
                              return 'Invalid Date';
                            }
                          })()}
                        </TableCell>
                        <TableCell>
                          <div className="flex flex-col">
                            <span className="font-medium">{record.user_name}</span>
                          </div>
                        </TableCell>
                        <TableCell className="font-mono text-xs">
                          {record.emp_id || '-'}
                        </TableCell>
                        <TableCell>{formatTime(record.check_in_time)}</TableCell>
                        <TableCell>{formatTime(record.check_out_time)}</TableCell>
                        <TableCell>{formatHours(hours)}</TableCell>
                        <TableCell>
                          {getStatusBadge(record.check_in_time, record.check_out_time)}
                        </TableCell>
                      </TableRow>
                    );
                  })
                )}
              </TableBody>
            </Table>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-between mt-4 pt-4 border-t">
                <p className="text-sm text-muted-foreground">
                  Showing {(page - 1) * limit + 1}-{Math.min(page * limit, total)} of {total}
                </p>
                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setPage(page - 1)}
                    disabled={page === 1}
                  >
                    <ChevronLeft className="h-4 w-4" />
                  </Button>
                  <span className="text-sm">
                    Page {page} of {totalPages}
                  </span>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setPage(page + 1)}
                    disabled={page === totalPages}
                  >
                    <ChevronRight className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </MainLayout>
  );
}
