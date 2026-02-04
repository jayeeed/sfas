import { useState, useRef, useCallback } from 'react';
import Webcam from 'react-webcam';
import { format } from 'date-fns';
import { ScanFace, Plus, Trash2, Loader2, Camera, RefreshCw, XCircle, User } from 'lucide-react';
import { Input } from '@/components/ui/input';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { MainLayout } from '@/components/layout';
import { useFaces } from '@/hooks/useFaces';
import { useAuthStore } from '@/stores/authStore';
import { FACE_MODELS, FaceModel } from '@/types';

export default function FaceManagement() {
  const { user } = useAuthStore();
  const { faces, isLoading, registerFace, isRegistering, deleteFace, isDeleting } = useFaces();

  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [selectedModel, setSelectedModel] = useState<FaceModel>('mobilefacenet');
  const [cameraError, setCameraError] = useState<string | null>(null);
  const [name, setName] = useState('');
  const [empId, setEmpId] = useState('');
  const webcamRef = useRef<Webcam>(null);

  const videoConstraints = {
    width: 480,
    height: 360,
    facingMode: 'user',
  };

  const handleCameraError = useCallback((error: string | DOMException) => {
    const errorMessage = typeof error === 'string' ? error : error.message;
    if (errorMessage.includes('NotAllowed') || errorMessage.includes('Permission')) {
      setCameraError('Camera permission denied. Please enable camera access.');
    } else {
      setCameraError('Failed to access camera. Please try again.');
    }
  }, []);

  const handleRegister = useCallback(() => {
    if (!webcamRef.current || !user) return;
    if (!name.trim() || !empId.trim()) {
      setCameraError('Please enter person name and ID.');
      return;
    }

    const imageSrc = webcamRef.current.getScreenshot();
    if (!imageSrc) {
      setCameraError('Failed to capture image. Please try again.');
      return;
    }

    const base64Image = imageSrc.split(',')[1];

    registerFace(
      {
        user_id: user.id,
        name: name.trim(),
        emp_id: empId.trim(),
        image: base64Image,
        model: selectedModel,
      },
      {
        onSuccess: () => {
          setIsDialogOpen(false);
          setCameraError(null);
          setName('');
          setEmpId('');
        },
      }
    );
  }, [registerFace, selectedModel, user, name, empId]);

  const handleDelete = useCallback(
    (faceId: string) => {
      deleteFace(faceId);
    },
    [deleteFace]
  );

  return (
    <MainLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">Face Management</h1>
            <p className="text-muted-foreground">Manage your registered faces for attendance</p>
          </div>

          <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                Register Face
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle>Register New Face</DialogTitle>
                <DialogDescription>
                  Capture your face to register with a recognition model
                </DialogDescription>
              </DialogHeader>

              <div className="grid md:grid-cols-2 gap-6">
                {/* Left Column: Camera Preview */}
                <div className="space-y-4">
                  <div className="aspect-[4/3] bg-muted rounded-lg overflow-hidden relative shadow-inner">
                    {cameraError ? (
                      <div className="flex flex-col items-center justify-center h-full p-4 text-center">
                        <XCircle className="h-12 w-12 text-destructive mb-2" />
                        <p className="text-sm text-destructive">{cameraError}</p>
                        <Button
                          variant="outline"
                          size="sm"
                          className="mt-2"
                          onClick={() => setCameraError(null)}
                        >
                          <RefreshCw className="mr-2 h-3 w-3" />
                          Retry
                        </Button>
                      </div>
                    ) : (
                      <div className="relative w-full h-full flex items-center justify-center bg-black">
                        <Webcam
                          ref={webcamRef}
                          audio={false}
                          screenshotFormat="image/jpeg"
                          videoConstraints={videoConstraints}
                          onUserMediaError={handleCameraError}
                          mirrored
                          className="w-full h-full object-cover"
                        />
                        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                          <div className="w-48 h-48 border-2 border-dashed border-primary/50 rounded-full" />
                        </div>
                      </div>
                    )}
                  </div>
                  <div className="text-xs text-center text-muted-foreground">
                    <p>Position your face within the circle (even lighting, no glasses)</p>
                  </div>
                </div>

                {/* Right Column: Controls */}
                <div className="flex flex-col justify-between space-y-4">
                  <div className="space-y-4">
                    {/* Person Info Fields */}
                    <div className="grid grid-cols-2 gap-3">
                      <div className="space-y-1.5">
                        <Label htmlFor="personName">Person Name</Label>
                        <Input
                          id="personName"
                          placeholder="John Doe"
                          value={name}
                          onChange={(e) => setName(e.target.value)}
                        />
                      </div>
                      <div className="space-y-1.5">
                        <Label htmlFor="personId">Person ID</Label>
                        <Input
                          id="personId"
                          placeholder="EMP001"
                          value={empId}
                          onChange={(e) => setEmpId(e.target.value)}
                        />
                      </div>
                    </div>

                    {/* Model Selection */}
                    <div className="space-y-2">
                       <Label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                        Recognition Model
                      </Label>
                      <RadioGroup
                        value={selectedModel}
                        onValueChange={(value) => setSelectedModel(value as FaceModel)}
                        className="grid gap-2"
                      >
                        {FACE_MODELS.map((model) => (
                          <div
                            key={model.id}
                            className={`flex items-start space-x-3 p-2.5 rounded-md border text-sm cursor-pointer transition-colors ${
                              selectedModel === model.id 
                                ? 'bg-primary/5 border-primary' 
                                : 'hover:bg-muted/50'
                            }`}
                          >
                            <RadioGroupItem value={model.id} id={model.id} className="mt-0.5" />
                            <Label htmlFor={model.id} className="grid gap-0.5 cursor-pointer w-full">
                              <div className="flex items-center justify-between">
                                <span className="font-medium">{model.name}</span>
                                {model.recommended && (
                                  <Badge variant="secondary" className="text-[10px] px-1.5 h-4">
                                    Recommended
                                  </Badge>
                                )}
                              </div>
                              <span className="text-xs text-muted-foreground line-clamp-1">
                                {model.description}
                              </span>
                            </Label>
                          </div>
                        ))}
                      </RadioGroup>
                    </div>
                  </div>

                  {/* Action Button */}
                  <Button
                    className="w-full mt-4"
                    size="lg"
                    onClick={handleRegister}
                    disabled={isRegistering || !!cameraError || !name.trim() || !empId.trim()}
                  >
                    {isRegistering ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Registering...
                      </>
                    ) : (
                      <>
                        <Camera className="mr-2 h-4 w-4" />
                        Capture & Register
                      </>
                    )}
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>
        </div>

        {/* Face Gallery */}
        <div>
          <h2 className="text-lg font-semibold mb-4">Registered Faces</h2>

          {isLoading ? (
            <div className="grid gap-3 grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
              {[...Array(5)].map((_, i) => (
                <Card key={i}>
                  <CardContent className="p-3">
                    <Skeleton className="aspect-square rounded-md mb-2" />
                    <Skeleton className="h-3 w-20 mb-1" />
                    <Skeleton className="h-2 w-16" />
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : faces.length === 0 ? (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-12">
                <ScanFace className="h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="font-medium mb-1">No faces registered</h3>
                <p className="text-sm text-muted-foreground mb-4">
                  Register your face to start using attendance
                </p>
                <Button onClick={() => setIsDialogOpen(true)}>
                  <Plus className="mr-2 h-4 w-4" />
                  Register Face
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="grid gap-3 grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
              {faces.map((face) => {
                const modelInfo = FACE_MODELS.find((m) => m.id === face.model);
                return (
                  <Card key={face.id} className="overflow-hidden">
                    <CardContent className="p-0">
                      <div className="aspect-square bg-muted flex items-center justify-center relative group">
                        {face.image_url ? (
                          <img
                            src={face.image_url}
                            alt={face.name || 'Registered face'}
                            className="w-full h-full object-cover"
                          />
                        ) : (
                          <User className="h-10 w-10 text-muted-foreground" />
                        )}
                        
                        {/* Delete Button - Top Right */}
                        <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
                          <AlertDialog>
                            <AlertDialogTrigger asChild>
                              <Button
                                variant="destructive"
                                size="icon"
                                className="h-8 w-8 rounded-full shadow-md"
                              >
                                <Trash2 className="h-4 w-4" />
                              </Button>
                            </AlertDialogTrigger>
                            <AlertDialogContent>
                              <AlertDialogHeader>
                                <AlertDialogTitle>Delete Face Registration?</AlertDialogTitle>
                                <AlertDialogDescription>
                                  This will remove {face.name}'s face registration.
                                </AlertDialogDescription>
                              </AlertDialogHeader>
                              <AlertDialogFooter>
                                <AlertDialogCancel>Cancel</AlertDialogCancel>
                                <AlertDialogAction
                                  onClick={() => handleDelete(face.id)}
                                  className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                                >
                                  {isDeleting ? (
                                    <Loader2 className="h-4 w-4 animate-spin" />
                                  ) : (
                                    'Delete'
                                  )}
                                </AlertDialogAction>
                              </AlertDialogFooter>
                            </AlertDialogContent>
                          </AlertDialog>
                        </div>
                      </div>
                      <div className="p-2 space-y-1">
                        <p className="text-sm font-medium truncate">{face.name || 'Unknown'}</p>
                        <p className="text-xs text-muted-foreground truncate">ID: {face.emp_id || 'N/A'}</p>
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </MainLayout>
  );
}
