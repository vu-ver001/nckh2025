import { useState } from 'react';
import './SettingsPanel.css';

export default function SettingsPanel() {
  const [conf, setConf] = useState(45);
  const [headThreshold, setHeadThreshold] = useState(65);
  const [frames, setFrames] = useState(10);
  const [headDownThreshold, setHeadDownThreshold] = useState(50);
  const [handEarDist, setHandEarDist] = useState(45);

  const [toggles, setToggles] = useState({
    phone: true,
    headTurn: true,
    handNearEar: true,
    handSuspicious: true,
    headDown: true,
    cheatSheet: true,
    autoSnapshot: true,
    soundAlert: false,
  });

  const handleToggle = (key) => {
    setToggles(prev => ({ ...prev, [key]: !prev[key] }));
  };

  return (
    <div className="settings-page">
      <div className="settings-header">
        <h1 className="settings-title">⚙️ Cài đặt hệ thống</h1>
        <p className="settings-subtitle">
          Bản xem thử giao diện — thay đổi ở đây chưa được áp dụng vào phiên giám sát.
        </p>
      </div>

      <fieldset disabled style={{ border: 0, padding: 0, margin: 0 }}>
      {/* Detection Thresholds */}
      <div className="settings-section">
        <div className="settings-section-title">
          <span>🎯</span>
          <span>Ngưỡng phát hiện AI</span>
        </div>

        <div className="setting-slider">
          <div className="setting-slider-header">
            <span className="setting-slider-label">Độ tin cậy YOLO (Confidence)</span>
            <span className="setting-slider-value">{conf}%</span>
          </div>
          <input
            type="range" min="20" max="95" value={conf}
            onChange={e => setConf(Number(e.target.value))}
          />
        </div>

        <div className="setting-slider">
          <div className="setting-slider-header">
            <span className="setting-slider-label">Ngưỡng quay đầu (Head Turn Ratio)</span>
            <span className="setting-slider-value">{(headThreshold / 100).toFixed(2)}</span>
          </div>
          <input
            type="range" min="30" max="90" value={headThreshold}
            onChange={e => setHeadThreshold(Number(e.target.value))}
          />
        </div>

        <div className="setting-slider">
          <div className="setting-slider-header">
            <span className="setting-slider-label">Ngưỡng cúi đầu (Head Down Ratio)</span>
            <span className="setting-slider-value">{(headDownThreshold / 100).toFixed(2)}</span>
          </div>
          <input
            type="range" min="20" max="80" value={headDownThreshold}
            onChange={e => setHeadDownThreshold(Number(e.target.value))}
          />
        </div>

        <div className="setting-slider">
          <div className="setting-slider-header">
            <span className="setting-slider-label">Frames xác nhận (Confirmation)</span>
            <span className="setting-slider-value">{frames} frames</span>
          </div>
          <input
            type="range" min="3" max="30" value={frames}
            onChange={e => setFrames(Number(e.target.value))}
          />
        </div>

        <div className="setting-slider">
          <div className="setting-slider-header">
            <span className="setting-slider-label">Tỷ lệ khoảng cách tay–tai theo vai</span>
            <span className="setting-slider-value">{(handEarDist / 100).toFixed(2)}</span>
          </div>
          <input
            type="range" min="20" max="70" value={handEarDist}
            onChange={e => setHandEarDist(Number(e.target.value))}
          />
        </div>
      </div>

      {/* Detection Types */}
      <div className="settings-section">
        <div className="settings-section-title">
          <span>🔍</span>
          <span>Loại phát hiện</span>
        </div>

        {[
          { key: 'phone', label: 'Điện thoại', icon: '📱' },
          { key: 'cheatSheet', label: 'Tài liệu / Phao thi', icon: '📄' },
          { key: 'headTurn', label: 'Quay đầu sang ngang', icon: '👀' },
          { key: 'headDown', label: 'Cúi đầu bất thường', icon: '⬇️' },
          { key: 'handNearEar', label: 'Tay gần vùng tai / cần kiểm tra', icon: '✋' },
          { key: 'handSuspicious', label: 'Tay ở vị trí bất thường', icon: '🤚' },
        ].map(item => (
          <div key={item.key} className="setting-toggle">
            <span className="setting-toggle-label">
              <span>{item.icon}</span>
              <span>{item.label}</span>
            </span>
            <label className="toggle-switch">
              <input
                type="checkbox"
                checked={toggles[item.key]}
                onChange={() => handleToggle(item.key)}
              />
              <div className="toggle-track" />
            </label>
          </div>
        ))}
      </div>

      {/* System Options */}
      <div className="settings-section">
        <div className="settings-section-title">
          <span>💾</span>
          <span>Tùy chọn hệ thống</span>
        </div>

        <div className="setting-toggle">
          <span className="setting-toggle-label">
            <span>📸</span>
            <span>Tự động chụp ảnh vi phạm</span>
          </span>
          <label className="toggle-switch">
            <input
              type="checkbox"
              checked={toggles.autoSnapshot}
              onChange={() => handleToggle('autoSnapshot')}
            />
            <div className="toggle-track" />
          </label>
        </div>

        <div className="setting-toggle">
          <span className="setting-toggle-label">
            <span>🔔</span>
            <span>Âm thanh cảnh báo</span>
          </span>
          <label className="toggle-switch">
            <input
              type="checkbox"
              checked={toggles.soundAlert}
              onChange={() => handleToggle('soundAlert')}
            />
            <div className="toggle-track" />
          </label>
        </div>
      </div>
      </fieldset>
    </div>
  );
}
