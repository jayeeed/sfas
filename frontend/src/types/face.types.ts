export type FaceModel = 'mobilefacenet' | 'insightface' | 'facenet';

export interface Face {
  id: string;
  user_id: string;
  name?: string;
  emp_id?: string;
  model: FaceModel;
  image_url?: string;
  created_at: string;
}

export interface FaceModelInfo {
  id: FaceModel;
  name: string;
  description: string;
  recommended?: boolean;
}

export const FACE_MODELS: FaceModelInfo[] = [
  {
    id: 'mobilefacenet',
    name: 'MobileFaceNet',
    description: 'Fast & lightweight (~30ms)',
    recommended: true,
  },
  {
    id: 'insightface',
    name: 'InsightFace',
    description: 'High accuracy (~100ms)',
    recommended: false,
  },
  {
    id: 'facenet',
    name: 'FaceNet',
    description: 'Balanced (~80ms)',
    recommended: false,
  },
];

export interface RegisterFaceRequest {
  user_id: string;
  name?: string;
  emp_id?: string;
  image: string; // base64
  model: FaceModel;
}

export interface RegisterFaceResponse {
  face: Face;
  message: string;
}

export interface UserFacesResponse {
  faces: Face[];
}
