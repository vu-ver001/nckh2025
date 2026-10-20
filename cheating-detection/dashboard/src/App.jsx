import { useState } from 'react';
import Topbar from './components/Topbar';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import History from './pages/History';
import Settings from './pages/Settings';
import { useWebSocket } from './hooks/useWebSocket';

import './App.css';

export default function App() {
  const [activePage, setActivePage] = useState('dashboard');
  const {
    events,
    riskScore,
    riskHistory,
    alertingCameras,
    totalViolations,
    clearEvents,
    backendFps,
    isConnected,
    backendStatus,
    backendError,
    backendWarning,
    backendModel,
    backendSource,
    demoVideos,
    demoCamera,
    selectedVideo,
    sourceBusy,
    riskLevel,
    controlCamera,
    selectVideo,
    restartCamera,
  } = useWebSocket();

  const sourceLabel = backendSource?.name === 'technical-fixture.avi'
    ? 'Video lặp ảnh validation — chỉ kiểm thử kỹ thuật'
    : backendSource ? `${backendSource.kind === 'camera' ? 'Webcam' : 'Video'}: ${backendSource.name}` : 'Nguồn video đã cấu hình';
  const cameras = [{ id: 1, name: 'Camera 1', location: sourceLabel, status: isConnected && backendStatus === 'running' ? 'active' : 'offline', fps: backendFps }];
  const renderPage = () => {
    switch (activePage) {
      case 'history':
        return <History events={events} />;
      case 'settings':
        return <Settings />;
      case 'dashboard':
      default:
        return (
          <Dashboard
            cameras={cameras}
            backendFps={backendFps}
            isConnected={isConnected}
            backendStatus={backendStatus}
            backendError={backendError}
            backendWarning={backendWarning}
            backendModel={backendModel}
            controlCamera={controlCamera}
            demoVideos={demoVideos}
            demoCamera={demoCamera}
            selectedVideo={selectedVideo}
            sourceBusy={sourceBusy}
            selectVideo={selectVideo}
            restartCamera={restartCamera}
            events={events}
            riskScore={riskScore}
            riskHistory={riskHistory}
            alertingCameras={alertingCameras}
            onClearEvents={clearEvents}
          />
        );
    }
  };

  return (
    <div className="app-layout">
      <Topbar
        riskScore={riskScore}
        totalViolations={totalViolations}
        cameras={cameras}
        isConnected={isConnected}
        backendStatus={backendStatus}
        riskLevel={riskLevel}
      />
      <div className="app-body">
        <Sidebar
          cameras={cameras}
          activePage={activePage}
          onNavigate={setActivePage}
          totalViolations={totalViolations}
          alertingCameras={alertingCameras}
        />
        {renderPage()}
      </div>
    </div>
  );
}
