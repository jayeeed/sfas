import { useEffect, useState, useCallback } from 'react';
import Webcam from 'react-webcam';

export interface CameraDevice {
  deviceId: string;
  label: string;
}

interface UseCameraOptions {
  autoStart?: boolean;
}

interface UseCameraReturn {
  webcamRef: React.RefObject<Webcam | null>;
  isReady: boolean;
  error: string | null;
  devices: CameraDevice[];
  selectedDevice: string | null;
  selectDevice: (deviceId: string) => void;
  capture: () => string | null;
  requestPermission: () => Promise<boolean>;
}

export function useCamera(options: UseCameraOptions = {}): UseCameraReturn {
  const { autoStart = false } = options;
  const [webcamRef] = useState<React.RefObject<Webcam | null>>({ current: null });
  const [isReady, setIsReady] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [devices, setDevices] = useState<CameraDevice[]>([]);
  const [selectedDevice, setSelectedDevice] = useState<string | null>(null);

  const getDevices = useCallback(async () => {
    try {
      const mediaDevices = await navigator.mediaDevices.enumerateDevices();
      const videoDevices = mediaDevices
        .filter((device) => device.kind === 'videoinput')
        .map((device, index) => ({
          deviceId: device.deviceId,
          label: device.label || `Camera ${index + 1}`,
        }));
      setDevices(videoDevices);
      if (videoDevices.length > 0 && !selectedDevice) {
        setSelectedDevice(videoDevices[0].deviceId);
      }
    } catch (err) {
      setError('Failed to get camera devices');
    }
  }, [selectedDevice]);

  const requestPermission = useCallback(async (): Promise<boolean> => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      stream.getTracks().forEach((track) => track.stop());
      await getDevices();
      setError(null);
      return true;
    } catch (err) {
      if (err instanceof DOMException) {
        if (err.name === 'NotAllowedError') {
          setError('Camera permission denied. Please enable camera access in your browser settings.');
        } else if (err.name === 'NotFoundError') {
          setError('No camera found. Please connect a camera and try again.');
        } else {
          setError('Failed to access camera. Please try again.');
        }
      }
      return false;
    }
  }, [getDevices]);

  useEffect(() => {
    if (autoStart) {
      requestPermission();
    }
  }, [autoStart, requestPermission]);

  const selectDevice = useCallback((deviceId: string) => {
    setSelectedDevice(deviceId);
  }, []);

  const capture = useCallback((): string | null => {
    if (webcamRef.current) {
      const imageSrc = webcamRef.current.getScreenshot();
      return imageSrc;
    }
    return null;
  }, [webcamRef]);

  const handleUserMedia = useCallback(() => {
    setIsReady(true);
    setError(null);
  }, []);

  const handleUserMediaError = useCallback((err: string | DOMException) => {
    setIsReady(false);
    if (typeof err === 'string') {
      setError(err);
    } else {
      setError(err.message || 'Failed to access camera');
    }
  }, []);

  // Attach handlers to ref
  useEffect(() => {
    const ref = webcamRef as { current: Webcam | null; onUserMedia?: () => void; onUserMediaError?: (err: string | DOMException) => void };
    ref.onUserMedia = handleUserMedia;
    ref.onUserMediaError = handleUserMediaError;
  }, [webcamRef, handleUserMedia, handleUserMediaError]);

  return {
    webcamRef,
    isReady,
    error,
    devices,
    selectedDevice,
    selectDevice,
    capture,
    requestPermission,
  };
}
