import { ArrowLeft } from 'lucide-react';
import { Link } from 'react-router-dom';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { MainLayout } from '@/components/layout';
import { ContinuousScanner } from '@/components/attendance/ContinuousScanner';

export default function MarkAttendance() {
  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center gap-4">
          <Link to="/dashboard">
            <Button variant="ghost" size="icon">
              <ArrowLeft className="h-5 w-5" />
            </Button>
          </Link>
          <div>
            <h1 className="text-2xl font-bold">Attendance Check-in Station</h1>
            <p className="text-muted-foreground">
              Continuous face scanning for automatic attendance marking
            </p>
          </div>
        </div>

        {/* Scanner Card */}
        <Card>
          <CardHeader>
            <CardTitle>Continuous Scanner</CardTitle>
            <CardDescription>
              Start the scanner to automatically detect and mark attendance for recognized faces.
              The system will scan every 2 seconds and log all successful check-ins.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ContinuousScanner />
          </CardContent>
        </Card>

        {/* Instructions */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">How It Works</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li className="flex items-start gap-2">
                <span className="text-primary font-medium">1.</span>
                Click "Start Continuous Scanning" to begin automatic detection
              </li>
              <li className="flex items-start gap-2">
                <span className="text-primary font-medium">2.</span>
                Users walk up to the camera and look at it
              </li>
              <li className="flex items-start gap-2">
                <span className="text-primary font-medium">3.</span>
                System automatically recognizes faces and marks attendance
              </li>
              <li className="flex items-start gap-2">
                <span className="text-primary font-medium">4.</span>
                Successful check-ins appear in the sidebar in real-time
              </li>
              <li className="flex items-start gap-2">
                <span className="text-primary font-medium">5.</span>
                Click "Stop Scanning" when check-in period is complete
              </li>
            </ul>
          </CardContent>
        </Card>
      </div>
    </MainLayout>
  );
}
