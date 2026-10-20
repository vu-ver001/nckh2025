import { apiUrl } from '../utils/api';
import './VideoFeed.css';
export default function VideoFeed({ camera, isAlerting }) {
  const active = camera.status === 'active';
  return <div className={`video-feed ${isAlerting ? 'alerting' : ''}`}>
    {active ? <img src={apiUrl('/video_feed')} alt={camera.name} className="video-canvas"
      style={{ width: '100%', height: '100%', objectFit: 'contain' }} />
      : <div className="video-canvas" style={{ display: 'grid', placeItems: 'center', background: '#070d1a', color: '#94a3b8' }}>Chưa có luồng video — nhấn Bắt đầu</div>}
    <div className="video-info-bar"><div className="video-cam-name">{camera.name}</div>
      <div className="video-fps-badge">{active ? `${camera.fps} FPS` : 'Chưa chạy'}</div></div>
    <div className="video-bottom-bar"><span className="video-location">{camera.location}</span></div>
    <div className={`video-alert-overlay ${isAlerting ? 'active' : ''}`} />
    {isAlerting && <div className="video-alert-toast">⚠ CẢNH BÁO CẦN KIỂM TRA</div>}
  </div>;
}
