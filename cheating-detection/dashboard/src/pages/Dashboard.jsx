import VideoGrid from '../components/VideoGrid';
import EventLog from '../components/EventLog';
import MetricsStrip from '../components/MetricsStrip';
import RiskGauge from '../components/RiskGauge';

/**
 * Dashboard — Main surveillance page
 * Layout: VideoGrid (center) + EventLog (right panel)
 * VideoGrid includes MetricsStrip at bottom
 */
export default function Dashboard({
  cameras, backendFps, isConnected, backendStatus, backendError, backendWarning, backendModel, controlCamera,
  demoVideos, demoCamera, selectedVideo, sourceBusy, selectVideo, restartCamera,
  events,
  riskScore,
  riskHistory,
  alertingCameras,
  onClearEvents,
}) {
  return (
    <div className="dashboard-page">
      {/* Center: Video Grid + Metrics */}
      <div className="dashboard-center">
        <div className="session-controls">
          <div className="demo-source-picker">
            <label htmlFor="demo-video-select">Nguồn demo</label>
            <select
              id="demo-video-select"
              value={selectedVideo}
              onChange={event => selectVideo(event.target.value)}
              disabled={!isConnected || sourceBusy || (demoVideos.length === 0 && !demoCamera)}
            >
              {demoVideos.length === 0 && !demoCamera && <option value="">Đang tải danh sách…</option>}
              {demoCamera && <option value="__webcam__">{demoCamera.label}</option>}
              {demoVideos.map(video => (
                <option key={video.filename} value={video.filename}>{video.label}</option>
              ))}
            </select>
            <span className="demo-source-description">
              {selectedVideo === '__webcam__'
                ? demoCamera?.description || 'Camera máy hiện tại'
                : demoVideos.find(video => video.filename === selectedVideo)?.description || 'Chọn kịch bản để chạy'}
            </span>
          </div>
          <div className="demo-actions">
            <button onClick={() => controlCamera('start')} disabled={!isConnected || sourceBusy || ['starting', 'running', 'stopping'].includes(backendStatus)}>Bắt đầu</button>
            <button onClick={() => controlCamera('stop')} disabled={!isConnected || sourceBusy || !['starting', 'running'].includes(backendStatus)}>Dừng</button>
            <button className="secondary" onClick={restartCamera} disabled={!isConnected || sourceBusy || backendStatus === 'starting'}>Chạy lại từ đầu</button>
          </div>
          {backendError && <p role="alert">{backendError}</p>}
          {backendWarning && <p>{backendWarning}</p>}
          {sourceBusy && <p className="demo-source-status">Đang chuyển nguồn…</p>}
          <p data-testid="model-status">{!isConnected ? 'Model: chưa kết nối backend'
            : backendModel?.status === 'loaded' ? `Đang dùng: ${backendModel.detector} + ${backendModel.phone_name}`
            : backendModel?.status === 'fallback' ? `Đang dùng: ${backendModel.detector} (không có xác nhận điện thoại)`
            : `Model cấu hình: ${backendModel?.phone_name || 'chưa xác định'} — chưa nạp`}</p>
          {isConnected && backendModel?.pose && <p data-testid="pose-status">
            Tư thế: {backendModel.pose.backend} — {backendModel.pose.status === 'loaded' ? 'đã nạp' : 'chưa nạp'}
          </p>}
        </div>
        <VideoGrid cameras={cameras} alertingCameras={alertingCameras} />
        <MetricsStrip fps={backendFps} isConnected={isConnected} status={backendStatus} />
      </div>

      {/* Right: Event Log + Risk Gauge */}
      <div className="dashboard-right">
        <EventLog events={events} onClear={onClearEvents} />
        <RiskGauge riskScore={riskScore} riskHistory={riskHistory} />
      </div>
    </div>
  );
}
