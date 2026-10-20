import { useEffect, useRef } from 'react';
import { VIOLATION_TYPES } from '../utils/constants';
import './EventLog.css';

export default function EventLog({ events, onClear }) {
  const listRef = useRef(null);

  // Auto-scroll to top (newest first)
  useEffect(() => {
    if (listRef.current) {
      listRef.current.scrollTop = 0;
    }
  }, [events.length]);

  const getSeverityClass = (severity) => {
    if (severity === 'critical') return 'severity-critical';
    if (severity === 'danger') return 'severity-danger';
    return 'severity-warn';
  };

  const formatTime = (date) => {
    return date.toLocaleTimeString('vi-VN', { hour12: false });
  };

  return (
    <aside className="event-panel">
      {/* Header */}
      <div className="event-header">
        <div className="event-title">
          <span>🚨</span>
          <span>Nhật ký Cảnh báo</span>
          {events.length > 0 && (
            <span className="event-badge-count">
              {events.length > 99 ? '99+' : events.length}
            </span>
          )}
        </div>
        <div className="event-header-actions">
          <button
            className="event-btn-icon"
            onClick={onClear}
            title="Xóa danh sách trên trình duyệt; giữ nguyên log máy chủ"
          >
            🗑
          </button>
        </div>
      </div>

      {/* Event list */}
      <div className="event-list" ref={listRef}>
        {events.length === 0 ? (
          <div className="event-empty">
            <div className="event-empty-icon">🔍</div>
            <p>Chưa phát hiện sự kiện nào…</p>
            <p style={{ fontSize: 11, marginTop: 4 }}>
              Cảnh báo sẽ xuất hiện khi phiên giám sát đang chạy
            </p>
          </div>
        ) : (
          events.map(event => {
            const meta = VIOLATION_TYPES[event.type] || {};
            const sevClass = getSeverityClass(event.severity);

            return (
              <div key={event.id} className={`event-item ${sevClass}`}>
                <div className="event-item-header">
                  <span className={`event-item-type ${sevClass}`}>
                    <span>{meta.icon || '⚠️'}</span>
                    <span>{event.label || meta.label || event.type}</span>
                  </span>
                  <span className="event-item-time">
                    {formatTime(event.timestamp)}
                  </span>
                </div>
                <div className="event-item-detail">{event.detail}</div>
                {event.imageUrl && <a href={event.imageUrl} target="_blank" rel="noreferrer">Xem ảnh cảnh báo</a>}
                <div className="event-item-camera">
                  <div className={`event-severity-dot ${event.severity === 'danger' || event.severity === 'critical' ? 'danger' : 'warn'}`} />
                  <span>📷 {event.cameraName}</span>
                </div>
              </div>
            );
          })
        )}
      </div>
    </aside>
  );
}
