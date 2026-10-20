import { NAV_ITEMS } from '../utils/constants';

import './Sidebar.css';

export default function Sidebar({ cameras, activePage, onNavigate, totalViolations, alertingCameras }) {
  return (
    <aside className="sidebar">
      {/* Navigation */}
      <nav className="sidebar-nav">
        <div className="sidebar-section-label">Điều hướng</div>
        {NAV_ITEMS.map(item => (
          <div
            key={item.id}
            className={`nav-item ${activePage === item.id ? 'active' : ''}`}
            onClick={() => onNavigate(item.id)}
          >
            <span className="nav-icon">{item.icon}</span>
            <span className="nav-label">{item.label}</span>
            {item.id === 'history' && totalViolations > 0 && (
              <span className="nav-badge">{totalViolations > 99 ? '99+' : totalViolations}</span>
            )}
          </div>
        ))}
      </nav>

      <div className="sidebar-divider" />

      {/* Quick Stats */}
      <div className="sidebar-stats">
        <div className="sidebar-section-label">Thống kê nhanh</div>
        <div className="stat-card">
          <span className="stat-card-label">Tổng thí sinh</span>
          <span className="stat-card-value">—</span>
          <span className="stat-card-sub">Chưa có số liệu thí sinh</span>
        </div>
        <div className="stat-card">
          <span className="stat-card-label">Thời gian giám sát</span>
          <span className="stat-card-value" style={{ fontSize: 18 }}>—</span>
          <span className="stat-card-sub">Chưa có thống kê thời lượng</span>
        </div>
      </div>

      <div className="sidebar-divider" />

      {/* Camera List */}
      <div className="sidebar-cameras">
        <div className="sidebar-section-label">📷 Cameras</div>
        {cameras.map(cam => (
          <div key={cam.id} className="camera-item">
            <div className={`camera-dot ${alertingCameras.has(cam.id) ? 'alert' : cam.status}`} />
            <span className="camera-name">{cam.name}</span>
            <span className="camera-fps">{cam.status === 'active' ? `${cam.fps} FPS` : 'Chưa chạy'}</span>
          </div>
        ))}
      </div>

      {/* Footer */}
      <div className="sidebar-footer">
        <div className="sidebar-footer-text">
          ExamGuard AI v2.0<br />
          Model đang dùng: xem Tổng quan
        </div>
      </div>
    </aside>
  );
}
