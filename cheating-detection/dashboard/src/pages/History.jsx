import { useState, useMemo } from 'react';
import { VIOLATION_TYPES } from '../utils/constants';


export default function History({ events }) {
  const [filter, setFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  // Events received in this browser session only.
  const allEvents = useMemo(() => {
    const combined = [...events];
    // Deduplicate by id
    const seen = new Set();
    return combined.filter(e => {
      if (seen.has(e.id)) return false;
      seen.add(e.id);
      return true;
    }).sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
  }, [events]);

  const filteredEvents = useMemo(() => {
    return allEvents.filter(e => {
      if (filter !== 'all' && e.severity !== filter) return false;
      if (searchTerm && !e.detail?.toLowerCase().includes(searchTerm.toLowerCase()) &&
          !e.type?.toLowerCase().includes(searchTerm.toLowerCase())) return false;
      return true;
    });
  }, [allEvents, filter, searchTerm]);

  const formatTime = (date) => {
    const d = new Date(date);
    return d.toLocaleString('vi-VN', { hour12: false });
  };

  return (
    <div className="history-page">
      <div className="history-header">
        <div>
          <h1 className="history-title">📋 Lịch sử vi phạm</h1>
          <p className="history-subtitle">
            Tổng cộng {allEvents.length} sự kiện gần nhất trong phiên trình duyệt (tối đa 100)
          </p>
        </div>

        <div className="history-actions">
          <div className="history-search">
            <span className="search-icon">🔍</span>
            <input
              type="text"
              placeholder="Tìm kiếm..."
              value={searchTerm}
              onChange={e => setSearchTerm(e.target.value)}
              className="search-input"
            />
          </div>

          <div className="filter-group">
            {[
              { value: 'all', label: 'Tất cả' },
              { value: 'danger', label: '🔴 Vi phạm' },
              { value: 'warn', label: '🟡 Nghi vấn' },
            ].map(f => (
              <button
                key={f.value}
                className={`filter-btn ${filter === f.value ? 'active' : ''}`}
                onClick={() => setFilter(f.value)}
              >
                {f.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="history-table-wrapper">
        <table className="history-table">
          <thead>
            <tr>
              <th>Thời gian</th>
              <th>Camera</th>
              <th>Loại vi phạm</th>
              <th>Mức độ</th>
              <th>Chi tiết</th>
              <th>Điểm</th>
            </tr>
          </thead>
          <tbody>
            {filteredEvents.map((event, i) => {
              const meta = VIOLATION_TYPES[event.type] || {};
              return (
                <tr key={event.id || i} className={`row-${event.severity}`}>
                  <td className="cell-time">{formatTime(event.timestamp)}</td>
                  <td className="cell-camera">{event.cameraName || '—'}</td>
                  <td className="cell-type">
                    <span className="type-badge">
                      <span>{meta.icon || '⚠️'}</span>
                      <span>{meta.label || event.type}</span>
                    </span>
                  </td>
                  <td>
                    <span className={`severity-badge ${event.severity}`}>
                      {event.severity === 'danger' ? 'VI PHẠM' : 'NGHI VẤN'}
                    </span>
                  </td>
                  <td className="cell-detail">{event.detail}</td>
                  <td className="cell-score">
                    <span className="score-value">+{event.score}</span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>

        {filteredEvents.length === 0 && (
          <div className="history-empty">
            <span style={{ fontSize: 32 }}>🔍</span>
            <p>Không tìm thấy kết quả</p>
          </div>
        )}
      </div>
    </div>
  );
}
