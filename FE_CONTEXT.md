# Smart Face Attendance System (SFAS) - Frontend Development Guide

## Overview

Build a modern, minimalistic React frontend for the Smart Face Attendance System. The app enables face-based attendance tracking with support for multiple face recognition models.

---

## Tech Stack

| Technology | Purpose |
|------------|---------|
| **React 18+** | UI Framework |
| **Vite** | Build tool |
| **TypeScript** | Type safety |
| **shadcn/ui** | Component library |
| **Tailwind CSS** | Styling |
| **React Router v6** | Routing |
| **TanStack Query** | Server state management |
| **Zustand** | Client state management |
| **Axios** | HTTP client |
| **React Webcam** | Camera access |
| **Lucide React** | Icons |

---

## Design Philosophy

### Core Principles
1. **Minimalistic** - Clean interfaces with purposeful whitespace
2. **Modern** - Subtle gradients, glassmorphism, smooth animations
3. **Accessible** - High contrast, keyboard navigation, screen reader support
4. **Responsive** - Mobile-first, works on tablets and desktops
5. **Fast** - Optimistic updates, skeleton loaders, lazy loading

### Color Palette
```css
/* Light Mode */
--background: 0 0% 100%;
--foreground: 240 10% 3.9%;
--primary: 221 83% 53%;        /* Blue - actions, links */
--success: 142 76% 36%;        /* Green - check-in success */
--warning: 38 92% 50%;         /* Orange - warnings */
--destructive: 0 84% 60%;      /* Red - errors, check-out */
--muted: 240 4.8% 95.9%;       /* Gray backgrounds */

/* Dark Mode */
--background: 240 10% 3.9%;
--foreground: 0 0% 98%;
```

### Typography
- **Font**: Inter (Google Fonts)
- **Headings**: Bold, larger sizes
- **Body**: Regular weight, readable line height

---

## Project Structure

```
frontend/
├── public/
│   └── favicon.ico
├── src/
│   ├── assets/                    # Static assets
│   ├── components/
│   │   ├── ui/                    # shadcn components
│   │   ├── layout/
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   ├── MainLayout.tsx
│   │   │   └── AuthLayout.tsx
│   │   ├── camera/
│   │   │   ├── WebcamCapture.tsx
│   │   │   ├── FacePreview.tsx
│   │   │   └── CaptureButton.tsx
│   │   ├── attendance/
│   │   │   ├── AttendanceCard.tsx
│   │   │   ├── AttendanceList.tsx
│   │   │   ├── AttendanceStats.tsx
│   │   │   └── CheckInOutButton.tsx
│   │   ├── users/
│   │   │   ├── UserCard.tsx
│   │   │   ├── UserForm.tsx
│   │   │   └── UserTable.tsx
│   │   └── faces/
│   │       ├── FaceCard.tsx
│   │       ├── FaceRegistration.tsx
│   │       └── ModelSelector.tsx
│   ├── pages/
│   │   ├── auth/
│   │   │   ├── Login.tsx
│   │   │   └── Register.tsx
│   │   ├── dashboard/
│   │   │   └── Dashboard.tsx
│   │   ├── attendance/
│   │   │   ├── MarkAttendance.tsx
│   │   │   ├── AttendanceHistory.tsx
│   │   │   └── AttendanceReport.tsx
│   │   ├── users/
│   │   │   ├── UserList.tsx
│   │   │   └── UserProfile.tsx
│   │   └── faces/
│   │       └── FaceManagement.tsx
│   ├── hooks/
│   │   ├── useAuth.ts
│   │   ├── useCamera.ts
│   │   ├── useAttendance.ts
│   │   └── useFaces.ts
│   ├── services/
│   │   ├── api.ts                 # Axios instance
│   │   ├── auth.service.ts
│   │   ├── user.service.ts
│   │   ├── face.service.ts
│   │   └── attendance.service.ts
│   ├── stores/
│   │   ├── authStore.ts
│   │   └── settingsStore.ts
│   ├── types/
│   │   ├── auth.types.ts
│   │   ├── user.types.ts
│   │   ├── face.types.ts
│   │   └── attendance.types.ts
│   ├── lib/
│   │   └── utils.ts               # shadcn utils
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css
├── .env
├── .env.example
├── package.json
├── tailwind.config.js
├── tsconfig.json
└── vite.config.ts
```

---

## Pages & Features

### 1. Authentication Pages

#### Login Page (`/login`)
```
┌─────────────────────────────────────────────────┐
│                                                 │
│           ┌─────────────────────┐               │
│           │    SFAS Logo        │               │
│           │  Smart Face Attend  │               │
│           └─────────────────────┘               │
│                                                 │
│           ┌─────────────────────┐               │
│           │ Email               │               │
│           └─────────────────────┘               │
│           ┌─────────────────────┐               │
│           │ Password        👁  │               │
│           └─────────────────────┘               │
│                                                 │
│           ┌─────────────────────┐               │
│           │      Sign In        │               │
│           └─────────────────────┘               │
│                                                 │
│           Don't have account? Register          │
│                                                 │
└─────────────────────────────────────────────────┘
```

**Features:**
- Email and password fields with validation
- Show/hide password toggle
- Loading state on submit
- Error handling with toast notifications
- Redirect to dashboard on success
- Link to registration page

#### Register Page (`/register`)
- Name, email, password, confirm password
- Password strength indicator
- Role selection (if allowed)
- Terms acceptance checkbox

---

### 2. Dashboard Page (`/dashboard`)

```
┌─────────────────────────────────────────────────────────────────┐
│  ☰  Smart Face Attendance                    👤 John Doe  ⚙️    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Good Morning, John! 👋                                         │
│  Today is Tuesday, February 4, 2026                             │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ ✓ Checked In │  │   8:32 AM    │  │  4h 28m      │          │
│  │   Today      │  │  Check-in    │  │  Working     │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                                                         │   │
│  │     ┌─────────────────────────────────────┐             │   │
│  │     │                                     │             │   │
│  │     │         📷 Camera Feed              │             │   │
│  │     │                                     │             │   │
│  │     │         [Face Preview]              │             │   │
│  │     │                                     │             │   │
│  │     └─────────────────────────────────────┘             │   │
│  │                                                         │   │
│  │     ┌─────────────────────────────────────┐             │   │
│  │     │        🔴 Check Out                 │             │   │
│  │     └─────────────────────────────────────┘             │   │
│  │                                                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Recent Activity                                                │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ ✓ Checked in today at 8:32 AM (confidence: 95.4%)       │   │
│  │ ✓ Checked out yesterday at 5:15 PM                      │   │
│  │ ✓ Checked in yesterday at 9:00 AM                       │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Features:**
- Welcome message with current date/time
- Today's attendance status cards
- Quick check-in/check-out via camera
- Recent activity list
- Weekly attendance summary chart

---

### 3. Mark Attendance Page (`/attendance/mark`)

This is the **core feature** of the app.

```
┌─────────────────────────────────────────────────────────────────┐
│  ← Back    Mark Attendance                                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                                                         │   │
│  │                                                         │   │
│  │                   ┌───────────────┐                     │   │
│  │                   │               │                     │   │
│  │                   │   📷 Camera   │                     │   │
│  │                   │     Feed      │                     │   │
│  │                   │               │                     │   │
│  │                   │  ┌─────────┐  │                     │   │
│  │                   │  │  Face   │  │                     │   │
│  │                   │  │ Detected│  │                     │   │
│  │                   │  └─────────┘  │                     │   │
│  │                   │               │                     │   │
│  │                   └───────────────┘                     │   │
│  │                                                         │   │
│  │    Model: [MobileFaceNet ▼]   Camera: [Front ▼]         │   │
│  │                                                         │   │
│  │    ┌─────────────────────────────────────────────┐      │   │
│  │    │              📸 Capture & Mark              │      │   │
│  │    └─────────────────────────────────────────────┘      │   │
│  │                                                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Instructions:                                                  │
│  1. Position your face in the frame                             │
│  2. Ensure good lighting                                        │
│  3. Click "Capture & Mark" to record attendance                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Flow:**
1. User opens camera (request permission if needed)
2. Live camera feed displays with face detection overlay
3. User selects recognition model (optional, defaults to MobileFaceNet)
4. User clicks "Capture & Mark"
5. App captures frame, sends to API
6. Show loading spinner during API call
7. On success: Show success animation with user name and action (check-in/out)
8. On failure: Show error with retry option

**States:**
- Camera loading
- Camera active (ready to capture)
- Capturing (processing)
- Success (with confetti animation)
- Error (with retry button)

---

### 4. Face Management Page (`/faces`)

```
┌─────────────────────────────────────────────────────────────────┐
│  Face Management                           [+ Register Face]    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  My Registered Faces                                            │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │  ┌───────┐  │  │  ┌───────┐  │  │  ┌───────┐  │             │
│  │  │ Photo │  │  │  │ Photo │  │  │  │ Photo │  │             │
│  │  └───────┘  │  │  └───────┘  │  │  └───────┘  │             │
│  │             │  │             │  │             │              │
│  │ MobileFace  │  │ InsightFace │  │  FaceNet   │              │
│  │ Registered  │  │ Registered  │  │ Registered │              │
│  │ Jan 15, 26  │  │ Jan 15, 26  │  │ Jan 15, 26 │              │
│  │             │  │             │  │            │               │
│  │   [Delete]  │  │   [Delete]  │  │  [Delete]  │              │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Face Registration Modal:**
```
┌─────────────────────────────────────────────────┐
│  Register New Face                          ✕   │
├─────────────────────────────────────────────────┤
│                                                 │
│     ┌─────────────────────────────┐             │
│     │       📷 Camera Feed        │             │
│     │                             │             │
│     │      [Face Detected ✓]      │             │
│     │                             │             │
│     └─────────────────────────────┘             │
│                                                 │
│  Select Model:                                  │
│  ┌─────────────────────────────────────────┐   │
│  │ ○ MobileFaceNet (Fast, lightweight)     │   │
│  │ ● InsightFace (High accuracy)           │   │
│  │ ○ FaceNet (Balanced)                    │   │
│  └─────────────────────────────────────────┘   │
│                                                 │
│  Tips:                                          │
│  • Look directly at the camera                 │
│  • Ensure even lighting on your face           │
│  • Remove glasses if possible                  │
│                                                 │
│  ┌─────────────────────────────────────────┐   │
│  │            📸 Capture & Register         │   │
│  └─────────────────────────────────────────┘   │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

### 5. Attendance History Page (`/attendance/history`)

```
┌─────────────────────────────────────────────────────────────────┐
│  Attendance History                                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Filter: [This Month ▼]  [All Users ▼]  [Export CSV]           │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Date        │ Check In  │ Check Out │ Hours   │ Status  │   │
│  ├─────────────────────────────────────────────────────────┤   │
│  │ Feb 4, 2026 │ 8:32 AM   │ --:--     │ 4h 28m  │ 🟢 In   │   │
│  │ Feb 3, 2026 │ 9:00 AM   │ 5:15 PM   │ 8h 15m  │ ✓ Done  │   │
│  │ Feb 2, 2026 │ 8:45 AM   │ 5:30 PM   │ 8h 45m  │ ✓ Done  │   │
│  │ Feb 1, 2026 │ --:--     │ --:--     │ 0h      │ ✗ Absent│   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  [< Prev]                                           [Next >]    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

### 6. User Management Page (`/users`) - Admin Only

```
┌─────────────────────────────────────────────────────────────────┐
│  User Management                               [+ Add User]     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Search: [🔍 Search users...]    Role: [All ▼]                  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 👤 │ Name           │ Email              │ Role    │ Act│   │
│  ├─────────────────────────────────────────────────────────┤   │
│  │ 😊 │ John Doe       │ john@example.com   │ User    │ ⋮  │   │
│  │ 😊 │ Jane Smith     │ jane@example.com   │ Admin   │ ⋮  │   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Showing 1-10 of 45 users                      [< 1 2 3 ... >]  │
│                                                                 │
└─────────────────────────────────────────────────────────────────
```

---

## API Integration

### Base Configuration
```typescript
// src/services/api.ts
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - add auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor - handle 401, refresh token
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Try refresh token or redirect to login
    }
    return Promise.reject(error);
  }
);

export default api;
```

### API Endpoints Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/auth/register` | POST | Register new user |
| `/auth/login` | POST | Login (OAuth2 form) |
| `/auth/refresh` | POST | Refresh access token |
| `/auth/me` | GET | Get current user |
| `/users` | GET | List users (admin) |
| `/users/{id}` | GET | Get user by ID |
| `/users/{id}` | PATCH | Update user |
| `/users/{id}` | DELETE | Delete user (admin) |
| `/faces/models` | GET | List available models |
| `/faces/register` | POST | Register face |
| `/faces/{user_id}` | GET | Get user's faces |
| `/faces/{id}` | DELETE | Delete face |
| `/attendance/mark` | POST | Mark attendance |
| `/attendance` | GET | List attendance |
| `/attendance/{id}` | GET | Get attendance record |
| `/attendance/stats/{user_id}` | GET | Get attendance stats |

### Key API Request Examples

```typescript
// Mark Attendance
const markAttendance = async (imageBase64: string, model: string = 'mobilefacenet') => {
  const response = await api.post('/attendance/mark', {
    image: imageBase64,
    camera_id: 'web_camera',
    model: model,  // 'mobilefacenet' | 'insightface' | 'facenet'
  });
  return response.data;
};

// Register Face
const registerFace = async (userId: string, imageBase64: string, model: string) => {
  const response = await api.post('/faces/register', {
    user_id: userId,
    image: imageBase64,
    model: model,
  });
  return response.data;
};
```

---

## Component Guidelines

### Camera Component
```typescript
// src/components/camera/WebcamCapture.tsx
import Webcam from 'react-webcam';

interface WebcamCaptureProps {
  onCapture: (imageSrc: string) => void;
  isCapturing: boolean;
}

// Features:
// - Request camera permission on mount
// - Show permission denied message if blocked
// - Mirror the video for natural selfie view
// - Overlay face detection box (optional)
// - Capture button with loading state
// - Switch camera (front/back on mobile)
```

### Model Selector
```typescript
// src/components/faces/ModelSelector.tsx
// Radio group for selecting face recognition model

const models = [
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
```

---

## Step-by-Step Implementation

### Phase 1: Project Setup (Day 1)

1. **Create Vite React Project**
   ```bash
   npm create vite@latest frontend -- --template react-ts
   cd frontend
   npm install
   ```

2. **Install Dependencies**
   ```bash
   # shadcn/ui setup
   npx shadcn@latest init
   
   # Core dependencies
   npm install axios @tanstack/react-query zustand react-router-dom
   
   # Camera
   npm install react-webcam
   
   # Icons
   npm install lucide-react
   
   # Date handling
   npm install date-fns
   
   # Form validation
   npm install react-hook-form @hookform/resolvers zod
   ```

3. **Add shadcn Components**
   ```bash
   npx shadcn@latest add button card input label
   npx shadcn@latest add dialog dropdown-menu avatar
   npx shadcn@latest add table tabs toast
   npx shadcn@latest add select radio-group badge
   npx shadcn@latest add skeleton alert separator
   ```

4. **Configure Environment**
   ```env
   # .env
   VITE_API_URL=http://localhost:8000
   ```

### Phase 2: Core Structure (Day 2)

1. Set up routing with React Router
2. Create layout components (Header, Sidebar, MainLayout)
3. Implement auth store with Zustand
4. Create API service layer
5. Set up React Query provider

### Phase 3: Authentication (Day 3)

1. Build Login page with form validation
2. Build Register page
3. Implement JWT token storage and refresh
4. Create protected route wrapper
5. Add auth context/hook

### Phase 4: Dashboard & Camera (Day 4-5)

1. Create Dashboard page layout
2. Implement WebcamCapture component
3. Build capture and preview flow
4. Add model selector
5. Integrate with `/attendance/mark` API
6. Add success/error animations

### Phase 5: Face Management (Day 6)

1. Build FaceManagement page
2. Create face registration modal
3. Implement face list with delete
4. Add multi-model registration support

### Phase 6: Attendance History (Day 7)

1. Build AttendanceHistory page
2. Add date range filters
3. Implement pagination
4. Create export to CSV feature
5. Add attendance stats cards

### Phase 7: User Management (Day 8)

1. Build UserList page (admin only)
2. Create user edit modal
3. Add user search and filters
4. Implement role-based UI

### Phase 8: Polish & Testing (Day 9-10)

1. Add loading skeletons
2. Implement dark mode
3. Add responsive design adjustments
4. Error boundary implementation
5. End-to-end testing

---

## UI/UX Best Practices

### Loading States
- Use skeleton loaders for content
- Show spinners for actions
- Disable buttons during submission
- Preserve form data on errors

### Error Handling
- Toast notifications for API errors
- Inline validation messages for forms
- Retry buttons for failed requests
- Clear error messages in user's language

### Animations
```css
/* Smooth page transitions */
.page-enter {
  opacity: 0;
  transform: translateY(10px);
}
.page-enter-active {
  opacity: 1;
  transform: translateY(0);
  transition: all 200ms ease-out;
}

/* Success pulse for check-in */
@keyframes success-pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
}
```

### Accessibility
- All interactive elements keyboard accessible
- Proper ARIA labels on buttons
- Focus indicators visible
- Color not sole indicator of state
- Alt text on all images

---

## Environment Variables

```env
# .env.example
VITE_API_URL=http://localhost:8000
VITE_APP_NAME="Smart Face Attendance"
VITE_DEFAULT_MODEL=mobilefacenet
```

---

## Testing Checklist

- [ ] Login with valid credentials
- [ ] Login with invalid credentials (shows error)
- [ ] Token refresh works automatically
- [ ] Camera permission request works
- [ ] Face capture and mark attendance
- [ ] Check-in shows correct action
- [ ] Check-out shows correct action
- [ ] Face registration with all 3 models
- [ ] Face deletion works
- [ ] Attendance history loads with pagination
- [ ] Date filters work correctly
- [ ] User management (admin only)
- [ ] Responsive on mobile devices
- [ ] Dark mode toggle works
- [ ] Error states display correctly

---

## Recommended File to Start With

1. `src/services/api.ts` - API configuration
2. `src/stores/authStore.ts` - Auth state management
3. `src/pages/auth/Login.tsx` - Login page
4. `src/components/camera/WebcamCapture.tsx` - Camera component
5. `src/pages/attendance/MarkAttendance.tsx` - Core feature page

---

## Summary

Build a clean, modern face attendance app using React + shadcn/ui. Focus on:

1. **Simplicity** - Users should mark attendance in 2 clicks
2. **Speed** - Optimize for fast recognition response
3. **Feedback** - Clear success/error states
4. **Mobile-first** - Works great on phones for quick check-in

The camera-based attendance marking is the hero feature - make it prominent and polished.
