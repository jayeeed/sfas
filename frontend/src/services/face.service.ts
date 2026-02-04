import api from './api';
import type {
  Face,
  FaceModel,
  RegisterFaceRequest,
  RegisterFaceResponse,
  UserFacesResponse,
} from '@/types';

export interface FaceModelInfoResponse {
  models: Array<{
    id: FaceModel;
    name: string;
    description: string;
  }>;
}

export const faceService = {
  async getAvailableModels(): Promise<FaceModelInfoResponse> {
    const response = await api.get<FaceModelInfoResponse>('/faces/models');
    return response.data;
  },

  async registerFace(data: RegisterFaceRequest): Promise<RegisterFaceResponse> {
    const response = await api.post<RegisterFaceResponse>('/faces/register', data);
    return response.data;
  },

  async getUserFaces(userId: string): Promise<UserFacesResponse> {
    const response = await api.get<UserFacesResponse>(`/faces/${userId}`);
    return response.data;
  },

  async deleteFace(faceId: string): Promise<void> {
    await api.delete(`/faces/${faceId}`);
  },

  async getMyFaces(): Promise<Face[]> {
    const response = await api.get<UserFacesResponse>('/faces/me');
    return response.data.faces;
  },
};
