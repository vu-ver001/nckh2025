// ═══════════════════════════════════════════════════════════
// Constants & Design Token exports for JS
// ═══════════════════════════════════════════════════════════

export const SEVERITY = {
  SAFE: 'safe',
  WARN: 'warn',
  DANGER: 'danger',
  CRITICAL: 'critical',
};

export const SEVERITY_COLORS = {
  safe: '#10b981',
  warn: '#f59e0b',
  danger: '#ef4444',
  critical: '#dc2626',
};

export const VIOLATION_TYPES = {
  PHONE_DETECTED: {
    type: 'PHONE_DETECTED',
    label: 'Phát hiện điện thoại',
    icon: '📱',
    severity: SEVERITY.DANGER,
    score: 12,
  },
  CHEAT_SHEET: {
    type: 'CHEAT_SHEET',
    label: 'Phát hiện tài liệu',
    icon: '📄',
    severity: SEVERITY.DANGER,
    score: 8,
  },
  LOOKING_AWAY: {
    type: 'LOOKING_AWAY',
    label: 'Quay đầu sang ngang',
    icon: '👀',
    severity: SEVERITY.WARN,
    score: 5,
  },
  HEAD_DOWN: {
    type: 'HEAD_DOWN',
    label: 'Cúi đầu bất thường',
    icon: '⬇️',
    severity: SEVERITY.WARN,
    score: 4,
  },
  HAND_NEAR_EAR: {
    type: 'HAND_NEAR_EAR',
    label: 'Tay gần vùng tai — cần kiểm tra',
    icon: '✋',
    severity: SEVERITY.WARN,
    score: 4,
  },
  HAND_SUSPICIOUS: {
    type: 'HAND_SUSPICIOUS',
    label: 'Tay ở vị trí bất thường',
    icon: '🤚',
    severity: SEVERITY.WARN,
    score: 4,
  },
};

export const VIOLATION_LIST = Object.values(VIOLATION_TYPES);

export const NAV_ITEMS = [
  { id: 'dashboard', label: 'Tổng quan', icon: '📊' },
  { id: 'history', label: 'Lịch sử vi phạm', icon: '📋' },
  { id: 'settings', label: 'Cài đặt', icon: '⚙️' },
];

export const MAX_RISK_SCORE = 30;
