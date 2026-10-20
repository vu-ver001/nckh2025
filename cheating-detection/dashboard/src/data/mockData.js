// ═══════════════════════════════════════════════════════════
// Mock Data — ExamGuard AI Dashboard
// Dữ liệu giả lập cho cameras, violations, history
// ═══════════════════════════════════════════════════════════

export const CAMERAS = [
  {
    id: 1,
    name: 'Phòng A1 — Cam 01',
    location: 'Góc trái phía trước',
    status: 'active',
    students: 35,
    fps: 42,
  },
  {
    id: 2,
    name: 'Phòng A1 — Cam 02',
    location: 'Góc phải phía sau',
    status: 'active',
    students: 35,
    fps: 38,
  },
  {
    id: 3,
    name: 'Phòng A2 — Cam 01',
    location: 'Trung tâm trên cao',
    status: 'active',
    students: 40,
    fps: 45,
  },
  {
    id: 4,
    name: 'Phòng A2 — Cam 02',
    location: 'Cửa sau bên trái',
    status: 'active',
    students: 40,
    fps: 36,
  },
];

export const MOCK_VIOLATIONS = [
  {
    id: 'v001',
    type: 'PHONE_DETECTED',
    cameraId: 1,
    cameraName: 'Phòng A1 — Cam 01',
    detail: 'Thí sinh #12 sử dụng điện thoại dưới bàn — Confidence: 89%',
    severity: 'danger',
    timestamp: new Date(Date.now() - 120000),
    score: 12,
  },
  {
    id: 'v002',
    type: 'LOOKING_AWAY',
    cameraId: 2,
    cameraName: 'Phòng A1 — Cam 02',
    detail: 'Thí sinh #08 quay đầu sang trái liên tục 5 giây',
    severity: 'warn',
    timestamp: new Date(Date.now() - 90000),
    score: 5,
  },
  {
    id: 'v004',
    type: 'HEAD_DOWN',
    cameraId: 1,
    cameraName: 'Phòng A1 — Cam 01',
    detail: 'Thí sinh #23 cúi đầu bất thường — kéo dài 8 giây',
    severity: 'warn',
    timestamp: new Date(Date.now() - 45000),
    score: 4,
  },
  {
    id: 'v005',
    type: 'HAND_NEAR_EAR',
    cameraId: 4,
    cameraName: 'Phòng A2 — Cam 02',
    detail: 'Thí sinh #31 có cử chỉ tay gần vùng tai — cần kiểm tra',
    severity: 'danger',
    timestamp: new Date(Date.now() - 30000),
    score: 6,
  },
];

export const MOCK_HISTORY = [
  ...MOCK_VIOLATIONS,
  {
    id: 'v006',
    type: 'CHEAT_SHEET',
    cameraId: 2,
    cameraName: 'Phòng A1 — Cam 02',
    detail: 'Phát hiện tài liệu dưới bàn — Confidence: 82%',
    severity: 'danger',
    timestamp: new Date(Date.now() - 300000),
    score: 8,
  },
  {
    id: 'v007',
    type: 'LOOKING_AWAY',
    cameraId: 3,
    cameraName: 'Phòng A2 — Cam 01',
    detail: 'Thí sinh #15 nhìn sang bạn bên cạnh 3 lần trong 2 phút',
    severity: 'warn',
    timestamp: new Date(Date.now() - 400000),
    score: 5,
  },
  {
    id: 'v008',
    type: 'HAND_SUSPICIOUS',
    cameraId: 1,
    cameraName: 'Phòng A1 — Cam 01',
    detail: 'Thí sinh #07 tay ở vị trí bất thường — dưới bàn kéo dài',
    severity: 'warn',
    timestamp: new Date(Date.now() - 500000),
    score: 4,
  },
  {
    id: 'v009',
    type: 'PHONE_DETECTED',
    cameraId: 4,
    cameraName: 'Phòng A2 — Cam 02',
    detail: 'Thí sinh #28 lấy điện thoại từ túi quần — Confidence: 91%',
    severity: 'danger',
    timestamp: new Date(Date.now() - 600000),
    score: 12,
  },
  {
    id: 'v010',
    type: 'HEAD_DOWN',
    cameraId: 2,
    cameraName: 'Phòng A1 — Cam 02',
    detail: 'Thí sinh #19 cúi đầu rất thấp — kéo dài 12 giây',
    severity: 'warn',
    timestamp: new Date(Date.now() - 700000),
    score: 4,
  },
];

// Skeleton keypoints (17-point COCO format)
export const SKELETON_CONNECTIONS = [
  [0, 1], [0, 2], [1, 3], [2, 4],        // head
  [5, 6],                                   // shoulders
  [5, 7], [7, 9],                           // left arm
  [6, 8], [8, 10],                          // right arm
  [5, 11], [6, 12],                         // torso
  [11, 12],                                 // hip
  [11, 13], [13, 15],                       // left leg
  [12, 14], [14, 16],                       // right leg
];

// Base skeleton pose (normalized 0-1 coordinates, seated student)
export const BASE_SKELETON = [
  { x: 0.50, y: 0.12 },  // 0: nose
  { x: 0.48, y: 0.10 },  // 1: left eye
  { x: 0.52, y: 0.10 },  // 2: right eye
  { x: 0.45, y: 0.11 },  // 3: left ear
  { x: 0.55, y: 0.11 },  // 4: right ear
  { x: 0.40, y: 0.25 },  // 5: left shoulder
  { x: 0.60, y: 0.25 },  // 6: right shoulder
  { x: 0.35, y: 0.40 },  // 7: left elbow
  { x: 0.65, y: 0.40 },  // 8: right elbow
  { x: 0.38, y: 0.55 },  // 9: left wrist
  { x: 0.62, y: 0.55 },  // 10: right wrist
  { x: 0.43, y: 0.55 },  // 11: left hip
  { x: 0.57, y: 0.55 },  // 12: right hip
  { x: 0.42, y: 0.72 },  // 13: left knee
  { x: 0.58, y: 0.72 },  // 14: right knee
  { x: 0.41, y: 0.90 },  // 15: left ankle
  { x: 0.59, y: 0.90 },  // 16: right ankle
];

// Mock bounding boxes for YOLO overlays
export const MOCK_BOUNDING_BOXES = [
  {
    label: 'PHONE',
    confidence: 0.89,
    x: 0.32, y: 0.50, w: 0.08, h: 0.14,
    isCheat: true,
  },
  {
    label: 'PERSON',
    confidence: 0.95,
    x: 0.30, y: 0.08, w: 0.40, h: 0.85,
    isCheat: false,
  },
];
