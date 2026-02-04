## 1. Backend Architecture Overview

**Core responsibilities**

* Face registration (enrollment)
* Face recognition (attendance marking)
* Attendance record management
* Authentication & authorization
* Model inference service
* Storage (faces + attendance logs)

**Tech stack**

* **FastAPI** – REST API
* **OpenCV** – face detection & preprocessing
* **Lightweight face recognition model**

  * Examples: MobileFaceNet, FaceNet (compressed), InsightFace (ONNX)
* **ONNX Runtime / PyTorch (CPU)** – inference
* **PostgreSQL / SQLite** – structured data
* **Local file system / S3-compatible storage** – face images & embeddings
* **JWT** – API authentication
* **Celery / BackgroundTasks** – async heavy tasks (optional)

---

## 2. Project Structure

```
backend/
├── app/
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── logging.py
│   ├── api/
│   │   ├── routes/
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   ├── faces.py
│   │   │   └── attendance.py
│   ├── models/
│   │   ├── user.py
│   │   ├── face.py
│   │   └── attendance.py
│   ├── services/
│   │   ├── face_detection.py
│   │   ├── face_embedding.py
│   │   ├── face_matching.py
│   │   └── attendance_service.py
│   ├── db/
│   │   ├── base.py
│   │   ├── session.py
│   │   └── migrations/
│   └── utils/
│       ├── image_utils.py
│       └── time_utils.py
├── models/
│   └── face_model.onnx
├── storage/
│   └── face_images/
└── requirements.txt
```

---

## 3. Database Design

### 3.1 Users Table

```
id (UUID / int)
name
email
role (admin/user)
created_at
```

### 3.2 Face Data Table

```
id
user_id (FK)
embedding (vector / blob)
image_path
created_at
```

### 3.3 Attendance Table

```
id
user_id (FK)
date
check_in_time
check_out_time
confidence_score
source (camera_id)
```

---

## 4. Face Recognition Pipeline (Backend Logic)

### Step-by-step flow

1. Receive image (base64 or multipart)
2. Convert image → OpenCV format
3. Detect face using OpenCV (Haar / DNN)
4. Align & crop face
5. Resize (e.g., 112x112)
6. Generate embedding using small model
7. Compare embedding with stored embeddings
8. Match if similarity > threshold
9. Mark attendance

---

## 5. Model Strategy (Small & Fast)

**Recommended**

* **MobileFaceNet (ONNX)**

  * ~4–6MB
  * CPU-friendly
  * Good accuracy for controlled environments

**Why embeddings instead of classification**

* Scales better
* New users don’t require retraining
* Faster inference

---

## 6. Face Enrollment Module

### API

```
POST /faces/register
```

### Implementation Steps

1. Authenticate admin
2. Accept user ID + image
3. Validate image quality
4. Detect exactly **one face**
5. Generate embedding
6. Store:

   * Embedding in DB
   * Image in storage
7. Return success

**Important rules**

* Store multiple embeddings per user (3–5 images)
* Reject blurry or multi-face images

---

## 7. Face Recognition & Attendance Module

### API

```
POST /attendance/mark
```

### Implementation Steps

1. Receive image + camera ID
2. Detect face
3. Generate embedding
4. Fetch all stored embeddings
5. Perform similarity search (Cosine distance)
6. Find best match
7. Check confidence threshold
8. Mark attendance:

   * Check-in if not exists
   * Check-out if already checked in
9. Return user info + confidence

---

## 8. Face Matching Logic

**Similarity metric**

* Cosine similarity

**Optimization**

* Cache embeddings in memory (Redis / in-process)
* Batch comparisons using NumPy

**Threshold example**

```
similarity >= 0.65 → match
```

---

## 9. FastAPI Performance Strategy

* Use **dependency injection** for DB sessions
* Load face model once at startup
* Use `BackgroundTasks` for image saving
* Async endpoints for I/O
* CPU-bound tasks run in thread pool

---

## 10. Authentication & Security

* JWT-based authentication
* Role-based access control
* Rate-limit attendance endpoint
* Encrypt embeddings at rest (optional)
* Log all recognition attempts

---

## 11. Logging & Monitoring

* Log:

  * Recognition confidence
  * Failed attempts
  * Camera ID
* Store error images for debugging
* Metrics:

  * Avg inference time
  * False rejection rate

---

## 12. Testing Strategy

### Unit Tests

* Face detection
* Embedding generation
* Similarity calculation

### Integration Tests

* Full attendance flow
* Enrollment → recognition

### Edge Cases

* No face detected
* Multiple faces
* Low confidence match
* Duplicate attendance

---

## 13. Deployment Plan

* Dockerize FastAPI app
* Mount model & storage volumes
* CPU-only inference
* Optional:

  * GPU build for future scaling

---

## 14. Future Enhancements (Optional)

* Multi-camera support
* Liveness detection
* Offline sync
* Vector DB (FAISS)
* Face anti-spoofing