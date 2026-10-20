import VideoFeed from './VideoFeed';

import './VideoGrid.css';

export default function VideoGrid({ cameras, alertingCameras }) {
  const gridClass = `grid-${cameras.length}`;

  return (
    <div className="video-grid-container">
      <div className={`video-grid ${gridClass}`}>
        {cameras.map(camera => (
          <VideoFeed
            key={camera.id}
            camera={camera}
            isAlerting={alertingCameras.has(camera.id)}
          />
        ))}
      </div>
    </div>
  );
}
