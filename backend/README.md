# Smart Face Attendance System (SFAS)

A FastAPI-based backend for face recognition attendance management, supporting multiple face recognition models.

## Features

- **Face Registration**: Register faces using MobileFaceNet, InsightFace, or FaceNet
- **Face Recognition Attendance**: Mark attendance via face recognition
- **User Management**: Role-based access control (admin, user)
- **Multi-Model Support**: Choose the recognition model per request
- **JWT Authentication**: Secure API with access and refresh tokens

## Quick Start

### 1. Install Dependencies

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your settings
```

### 3. Download Face Recognition Models

Download the ONNX models and place them in the `models/` directory:

```
backend/models/
├── mobilefacenet/
│   └── mobilefacenet.onnx      # ~4MB
├── insightface/
│   └── w600k_r50.onnx          # ~250MB (optional)
├── facenet/
│   └── facenet.onnx            # ~95MB (optional)
└── detection/
    └── face_detection_yunet_2023mar.onnx  # ~230KB (optional, uses Haar if missing)
```

**Model Sources:**
- **MobileFaceNet**: [GitHub MobileFaceNet](https://github.com/AlfredXiangWu/MobileFaceNet_ONNX)
- **InsightFace**: [InsightFace Model Zoo](https://github.com/deepinsight/insightface/tree/master/model_zoo)
- **FaceNet**: [HuggingFace FaceNet-ONNX](https://huggingface.co/edtrain/FaceNet-ONNX)
- **YuNet Detector**: [OpenCV Zoo](https://github.com/opencv/opencv_zoo/tree/main/models/face_detection_yunet)

### 4. Run the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Access API Docs

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Overview

### Authentication
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/auth/register` | POST | Register new user |
| `/api/v1/auth/login` | POST | Login and get tokens |
| `/api/v1/auth/refresh` | POST | Refresh access token |
| `/api/v1/auth/me` | GET | Get current user |

### Users (Admin only)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/users` | GET | List all users |
| `/api/v1/users/{id}` | GET | Get user by ID |
| `/api/v1/users/{id}` | PATCH | Update user |
| `/api/v1/users/{id}` | DELETE | Delete user |

### Faces
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/faces/models` | GET | List available models |
| `/api/v1/faces/register` | POST | Register face for user |
| `/api/v1/faces/{user_id}` | GET | Get user's registered faces |
| `/api/v1/faces/{face_id}` | DELETE | Delete face registration |

### Attendance
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/attendance/mark` | POST | Mark attendance via face recognition |
| `/api/v1/attendance` | GET | List attendance records |
| `/api/v1/attendance/{id}` | GET | Get attendance record |
| `/api/v1/attendance/stats/{user_id}` | GET | Get attendance statistics |

## Usage Examples

### Register a Face
```bash
POST /api/v1/faces/register
{
    "user_id": "user-uuid",
    "image": "base64_encoded_image...",
    "model": "mobilefacenet"  # or "insightface", "facenet"
}
```

### Mark Attendance
```bash
POST /api/v1/attendance/mark
{
    "image": "base64_encoded_image...",
    "camera_id": "entrance_cam_01",
    "model": "mobilefacenet"  # or "insightface", "facenet"
}
```

Response:
```json
{
    "success": true,
    "user_id": "user-uuid",
    "user_name": "John Doe",
    "action": "check_in",
    "confidence": 0.8542,
    "model_used": "mobilefacenet",
    "timestamp": "2026-02-04T10:00:00Z",
    "attendance_id": "attendance-uuid"
}
```

## Model Comparison

| Model | Size | Speed (CPU) | Accuracy | Best For |
|-------|------|-------------|----------|----------|
| MobileFaceNet | ~4MB | ~30ms | Good | Real-time, mobile |
| InsightFace | ~250MB | ~100ms | Excellent | High-security |
| FaceNet | ~95MB | ~80ms | Very Good | Balanced |

## Project Structure

```
backend/
├── app/
│   ├── api/routes/      # API endpoints
│   ├── core/            # Config, security, logging
│   ├── db/              # Database models & session
│   ├── models/          # SQLAlchemy models
│   ├── services/        # Face detection/embedding/matching
│   ├── utils/           # Image & time utilities
│   └── main.py          # FastAPI application
├── models/              # ONNX model files
├── storage/             # Face images storage
├── tests/               # Test files
├── requirements.txt
└── .env.example
```

## License

This project is for educational and research purposes. 

> ⚠️ **Note**: InsightFace models are for non-commercial use only. Contact InsightFace for commercial licensing.
