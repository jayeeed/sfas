import { useState, useRef, useCallback, useEffect } from 'react';
import Webcam from 'react-webcam';
import { Loader2, CheckCircle, XCircle, SwitchCamera, Play, Square, Users } from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { useAttendance } from '@/hooks/useAttendance';
import { useSettingsStore } from '@/stores/settingsStore';
import { FACE_MODELS, FaceModel } from '@/types';

interface RecognitionResult {
  id: string;
  userName: string;
  empId?: string;
  action: 'check_in' | 'check_out';
  confidence: number;
  timestamp: Date;
  success: boolean;
}

export function ContinuousScanner() {
  const webcamRef = useRef<Webcam>(null);
  const scanIntervalRef = useRef<NodeJS.Timeout | null>(null);
  
  const [isScanning, setIsScanning] = useState(false);
  const [cameraError, setCameraError] = useState<string | null>(null);
  const [facingMode, setFacingMode] = useState<'user' | 'environment'>('user');
  const [selectedModel, setSelectedModel] = useState<FaceModel>(() => {
    return useSettingsStore.getState().defaultModel;
  });
  const [results, setResults] = useState<RecognitionResult[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);

  const { markAttendance, isMarking } = useAttendance();

  const videoConstraints = {
    width: 640,
    height: 480,
    facingMode: facingMode,
  };

  const handleCameraError = useCallback((error: string | DOMException) => {
    const errorMessage = typeof error === 'string' ? error : error.message;
    if (errorMessage.includes('NotAllowed') || errorMessage.includes('Permission')) {
      setCameraError('Camera permission denied. Please enable camera access in your browser settings.');
    } else if (errorMessage.includes('NotFound')) {
      setCameraError('No camera found. Please connect a camera and try again.');
    } else {
      setCameraError('Failed to access camera. Please try again.');
    }
    setIsScanning(false);
  }, []);

  const processFrame = useCallback(async () => {
    if (!webcamRef.current || isProcessing || isMarking) return;

    const imageSrc = webcamRef.current.getScreenshot();
    if (!imageSrc) return;

    setIsProcessing(true);

    const base64Image = imageSrc.split(',')[1];

    markAttendance(
      {
        image: base64Image,
        model: selectedModel,
        camera_id: 'web_camera',
      },
      {
        onSuccess: (response) => {
          const newResult: RecognitionResult = {
            id: crypto.randomUUID(),
            userName: response.user_name,
            empId: response.emp_id,
            action: response.action,
            confidence: response.confidence,
            timestamp: new Date(),
            success: response.success, // Use response success status
          };
          setResults((prev) => [newResult, ...prev].slice(0, 50));
          setIsProcessing(false);
        },
        onError: () => {
          // Silent fail for API errors (e.g. network issues)
          // But 404s are now handled as success=false in usage
          setIsProcessing(false);
        },
      }
    );
  }, [isProcessing, isMarking, markAttendance, selectedModel]);

  const startScanning = useCallback(() => {
    setIsScanning(true);
    // Scan every 2 seconds
    scanIntervalRef.current = setInterval(() => {
      processFrame();
    }, 2000);
  }, [processFrame]);

  const stopScanning = useCallback(() => {
    setIsScanning(false);
    if (scanIntervalRef.current) {
      clearInterval(scanIntervalRef.current);
      scanIntervalRef.current = null;
    }
  }, []);

  const toggleCamera = useCallback(() => {
    setFacingMode((prev) => (prev === 'user' ? 'environment' : 'user'));
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (scanIntervalRef.current) {
        clearInterval(scanIntervalRef.current);
      }
    };
  }, []);

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  if (cameraError) {
    return (
      <div className="flex flex-col items-center justify-center h-full p-8 text-center">
        <XCircle className="h-16 w-16 text-destructive mb-4" />
        <p className="text-destructive font-medium mb-4">{cameraError}</p>
        <Button onClick={() => setCameraError(null)} variant="outline">
          Try Again
        </Button>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Camera Feed */}
      <div className="lg:col-span-2 space-y-4">
        <div className="relative aspect-[4/3] bg-muted rounded-lg overflow-hidden">
          <Webcam
            ref={webcamRef}
            audio={false}
            screenshotFormat="image/jpeg"
            videoConstraints={videoConstraints}
            onUserMediaError={handleCameraError}
            mirrored={facingMode === 'user'}
            className="w-full h-full object-cover"
          />
          
          {/* Scanning overlay */}
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
            <div className={`w-48 h-48 md:w-64 md:h-64 border-2 border-dashed rounded-full transition-colors ${
              isScanning ? 'border-primary animate-pulse' : 'border-muted-foreground/50'
            }`} />
          </div>

          {/* Status indicator */}
          <div className="absolute top-4 left-4">
            <Badge variant={isScanning ? 'default' : 'secondary'} className="gap-1">
              {isScanning ? (
                <>
                  <span className="h-2 w-2 rounded-full bg-red-500 animate-pulse" />
                  Scanning...
                </>
              ) : (
                'Ready'
              )}
            </Badge>
          </div>

          {/* Processing indicator */}
          {isProcessing && (
            <div className="absolute bottom-4 left-4">
              <Badge variant="outline" className="gap-1 bg-background/80">
                <Loader2 className="h-3 w-3 animate-spin" />
                Processing...
              </Badge>
            </div>
          )}
        </div>

        {/* Controls */}
        <div className="flex flex-wrap gap-4">
          <div className="flex-1 min-w-[150px]">
            <label className="text-sm font-medium mb-2 block">Model</label>
            <Select
              value={selectedModel}
              onValueChange={(value) => setSelectedModel(value as FaceModel)}
              disabled={isScanning}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {FACE_MODELS.map((model) => (
                  <SelectItem key={model.id} value={model.id}>
                    <div className="flex items-center gap-2">
                      {model.name}
                      {model.recommended && (
                        <span className="text-xs bg-primary/10 text-primary px-1.5 py-0.5 rounded">
                          Recommended
                        </span>
                      )}
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div>
            <label className="text-sm font-medium mb-2 block">Camera</label>
            <Button variant="outline" onClick={toggleCamera} disabled={isScanning}>
              <SwitchCamera className="mr-2 h-4 w-4" />
              {facingMode === 'user' ? 'Front' : 'Back'}
            </Button>
          </div>
        </div>

        {/* Start/Stop Button */}
        <Button
          size="lg"
          className="w-full"
          onClick={isScanning ? stopScanning : startScanning}
          variant={isScanning ? 'destructive' : 'default'}
        >
          {isScanning ? (
            <>
              <Square className="mr-2 h-5 w-5" />
              Stop Scanning
            </>
          ) : (
            <>
              <Play className="mr-2 h-5 w-5" />
              Start Continuous Scanning
            </>
          )}
        </Button>
      </div>

      {/* Recognition Results */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold flex items-center gap-2">
            <Users className="h-5 w-5" />
            Recent Check-ins
          </h3>
          <Badge variant="outline">{results.length}</Badge>
        </div>

        <ScrollArea className="h-[400px] lg:h-[500px] rounded-md border p-4">
          {results.length === 0 ? (
            <div className="text-center text-muted-foreground py-8">
              <Users className="h-12 w-12 mx-auto mb-2 opacity-50" />
              <p>No check-ins yet</p>
              <p className="text-sm">Start scanning to see results</p>
            </div>
          ) : (
            <div className="space-y-3">
              {results.map((result) => (
                <div
                  key={result.id}
                  className="flex items-center gap-3 p-3 rounded-lg bg-muted/50 animate-in slide-in-from-top-2"
                >
                  <div className="flex-shrink-0">
                    {result.success ? (
                      <CheckCircle className="h-5 w-5 text-primary" />
                    ) : (
                      <div className="h-5 w-5 rounded-full border-2 border-yellow-500 flex items-center justify-center">
                        <span className="text-xs font-bold text-yellow-500">?</span>
                      </div>
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium truncate">
                      {result.userName}
                      {result.empId && <span className="text-muted-foreground text-sm ml-1">({result.empId})</span>}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {result.action === 'check_in' ? '✅ Checked In' : '👋 Checked Out'} • {formatTime(result.timestamp)}
                    </p>
                  </div>
                  <Badge variant="outline" className="text-xs">
                    {(result.confidence * 100).toFixed(0)}%
                  </Badge>
                </div>
              ))}
            </div>
          )}
        </ScrollArea>
      </div>
    </div>
  );
}
