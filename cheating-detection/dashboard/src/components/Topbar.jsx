import { useClock } from '../hooks/useClock';
import { MAX_RISK_SCORE } from '../utils/constants';
import './Topbar.css';

export default function Topbar({ riskScore, riskLevel, totalViolations, cameras, isConnected, backendStatus }) {
  const clock = useClock();

  const statuses = {
    OK: { className: 'safe', text: 'CHƯA CÓ CẢNH BÁO' },
    LOW: { className: 'monitoring', text: 'CẦN THEO DÕI' },
    MEDIUM: { className: 'warn', text: 'CẢNH BÁO VỪA' },
    HIGH: { className: 'danger', text: 'CẢNH BÁO CAO' },
    CRITICAL: { className: 'danger', text: 'CẢNH BÁO RẤT CAO' },
  };
  const status = !isConnected ? { className: 'warn', text: 'MẤT KẾT NỐI' }
    : backendStatus !== 'running' ? { className: 'monitoring', text: { starting: 'ĐANG KHỞI ĐỘNG', stopping: 'ĐANG DỪNG', error: 'LỖI NGUỒN VIDEO / AI', stopped: 'CHƯA GIÁM SÁT' }[backendStatus] || 'CHƯA GIÁM SÁT' }
    : statuses[riskLevel] || statuses.OK;
  const activeCams = cameras?.filter(c => c.status === 'active').length || 0;

  return (
    <header className="topbar">
      <div className="topbar-brand">
        <div className="brand-icon">🎓</div>
        <div className="brand-text">
          <span className="brand-name">ExamGuard AI</span>
          <span className="brand-sub">Hệ thống Giám sát Thi cử Thông minh</span>
        </div>
      </div>

      <div className="topbar-center">
        <div className={`status-badge ${status.className}`}>
          <div className="status-dot"></div>
          <span>{status.text}</span>
        </div>
      </div>

      <div className="topbar-right">
        <div className="topbar-stat">
          <span>📷</span>
          <span className="topbar-stat-value">{activeCams}</span>
          <span>cameras</span>
        </div>
        <div className="topbar-stat">
          <span>🚨</span>
          <span className="topbar-stat-value">{totalViolations}</span>
          <span>vi phạm</span>
        </div>
        <span className="topbar-clock">{clock}</span>
      </div>
    </header>
  );
}
