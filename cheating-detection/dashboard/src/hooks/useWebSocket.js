import { useState, useEffect, useCallback, useRef } from 'react';
import { VIOLATION_LIST } from '../utils/constants';
import { apiUrl, websocketUrl } from '../utils/api';

export function useWebSocket(url = websocketUrl()) {
  const [events, setEvents] = useState([]);
  const [riskScore, setRiskScore] = useState(0);
  const [riskLevel, setRiskLevel] = useState('OK');
  const [riskHistory, setRiskHistory] = useState(Array(60).fill(0));
  const [alertingCameras, setAlertingCameras] = useState(new Set());
  const [totalViolations, setTotalViolations] = useState(0);
  const [backendFps, setBackendFps] = useState(0);
  const [backendStatus, setBackendStatus] = useState('stopped');
  const [backendError, setBackendError] = useState(null);
  const [backendWarning, setBackendWarning] = useState(null);
  const [backendModel, setBackendModel] = useState(null);
  const [backendSource, setBackendSource] = useState(null);
  const [demoVideos, setDemoVideos] = useState([]);
  const [demoCamera, setDemoCamera] = useState(null);
  const [selectedVideo, setSelectedVideo] = useState('');
  const [sourceBusy, setSourceBusy] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const eventId = useRef(0);
  const flashTimer = useRef(null);
  const demoVideosRef = useRef([]);

  useEffect(() => {
    let disposed = false;
    fetch(apiUrl('/demo/videos'))
      .then(response => response.ok ? response.json() : Promise.reject(new Error('Không tải được danh sách video demo')))
      .then(data => {
        if (disposed) return;
        const videos = Array.isArray(data.videos) ? data.videos : [];
        demoVideosRef.current = videos;
        setDemoVideos(videos);
        setDemoCamera(data.camera || { kind: 'camera', index: 0, label: 'Webcam trực tiếp', description: 'Camera máy hiện tại' });
        setSelectedVideo(current => current || videos[0]?.filename || '');
      })
      .catch(error => { if (!disposed) setBackendError(error.message); });
    return () => { disposed = true; };
  }, []);

  useEffect(() => {
    let disposed = false;
    let ws;
    let reconnectTimer;
    const connect = () => {
      if (disposed) return;
      ws = new WebSocket(url);
      ws.onopen = () => { if (!disposed) setIsConnected(true); };
      ws.onmessage = event => {
        if (disposed) return;
        try {
          const data = JSON.parse(event.data);
          if (data.heartbeat) {
            setBackendFps(Number(data.fps) || 0);
            setRiskScore(Number(data.score) || 0);
            setRiskLevel(data.level || 'OK');
            setBackendStatus(data.status || 'stopped');
            setBackendError(data.error || null);
            setBackendWarning(data.warning || null);
            setBackendModel(data.model || null);
            setBackendSource(data.source || null);
            if (data.source?.kind === 'camera') {
              setSelectedVideo('__webcam__');
            } else if (data.source?.name && demoVideosRef.current.some(video => video.filename === data.source.name)) {
              setSelectedVideo(data.source.name);
            }
            setRiskHistory(prev => [...prev.slice(1), Number(data.score) || 0]);
            return;
          }
          if (typeof data.type !== 'string') return;
          const meta = VIOLATION_LIST.find(v => v.type === data.type) || { label: data.type, icon: '⚠️' };
          const newEvent = {
            id: `evt-${++eventId.current}`, type: data.type, label: meta.label, icon: meta.icon,
            severity: data.level === 'CRITICAL' ? 'critical' : data.level === 'HIGH' ? 'danger' : 'warn',
            score: data.score || 0, cameraId: 1, cameraName: 'Camera 1',
            detail: data.detail || meta.label,
            timestamp: new Date(data.timestamp ? data.timestamp * 1000 : Date.now()),
            imageUrl: data.image ? apiUrl(data.image) : null,
          };
          setEvents(prev => [newEvent, ...prev].slice(0, 100));
          setTotalViolations(prev => prev + 1);
          setAlertingCameras(new Set([1]));
          clearTimeout(flashTimer.current);
          flashTimer.current = setTimeout(() => setAlertingCameras(new Set()), 3000);
        } catch (error) { console.error('Invalid alert message', error); }
      };
      ws.onclose = () => {
        if (disposed) return;
        setIsConnected(false);
        setBackendFps(0);
        setBackendStatus('stopped');
        setBackendModel(null);
        setBackendSource(null);
        setBackendWarning(null);
        setRiskScore(0);
        setRiskLevel('OK');
        setAlertingCameras(new Set());
        reconnectTimer = setTimeout(connect, 3000);
      };
      ws.onerror = () => ws.close();
    };
    connect();
    return () => {
      disposed = true;
      clearTimeout(reconnectTimer);
      clearTimeout(flashTimer.current);
      if (ws) ws.close();
    };
  }, [url]);

  const controlCamera = useCallback(async action => {
    try {
      const response = await fetch(apiUrl(`/${action}`), { method: 'POST' });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Không điều khiển được nguồn video');
      setBackendStatus(data.status);
      setBackendError(data.error || null);
      setBackendWarning(data.warning || null);
      setBackendModel(data.model || null);
      setBackendSource(data.source || null);
      return data;
    } catch (error) { setBackendError(error.message); }
  }, []);

  const selectVideo = useCallback(async filename => {
    setSourceBusy(true);
    setBackendError(null);
    try {
      if (['starting', 'running', 'stopping'].includes(backendStatus)) {
        await controlCamera('stop');
      }
      const response = await fetch(apiUrl('/source'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(filename === '__webcam__'
          ? { kind: 'camera', index: demoCamera?.index ?? 0 }
          : { kind: 'video', filename }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Không đổi được video demo');
      setSelectedVideo(filename);
      setBackendStatus(data.status || 'stopped');
      setBackendError(data.error || null);
      setBackendWarning(data.warning || null);
      setBackendModel(data.model || null);
      setBackendSource(data.source || null);
      setEvents([]);
      setTotalViolations(0);
      setRiskScore(0);
      setRiskLevel('OK');
      setAlertingCameras(new Set());
    } catch (error) {
      setBackendError(error.message);
    } finally {
      setSourceBusy(false);
    }
  }, [backendStatus, controlCamera, demoCamera]);

  const clearEvents = useCallback(() => {
    setEvents([]);
    setTotalViolations(0);
  }, []);

  const restartCamera = useCallback(async () => {
    setSourceBusy(true);
    try {
      if (['starting', 'running', 'stopping'].includes(backendStatus)) {
        await controlCamera('stop');
      }
      clearEvents();
      setRiskScore(0);
      setRiskLevel('OK');
      setAlertingCameras(new Set());
      await controlCamera('start');
    } finally {
      setSourceBusy(false);
    }
  }, [backendStatus, controlCamera, clearEvents]);
  return { events, riskScore, riskLevel, riskHistory, alertingCameras, totalViolations,
    backendFps, backendStatus, backendError, backendWarning, backendModel, backendSource,
    demoVideos, demoCamera, selectedVideo, sourceBusy, isConnected, controlCamera, selectVideo,
    restartCamera, clearEvents };
}
