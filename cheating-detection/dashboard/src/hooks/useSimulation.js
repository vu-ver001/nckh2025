import { useState, useEffect, useCallback, useRef } from 'react';
import { VIOLATION_LIST } from '../utils/constants';
import { CAMERAS } from '../data/mockData';

/**
 * useSimulation — Hook tự động sinh mock events
 * Sinh violation events mỗi 3-8 giây, tự cập nhật risk score
 */
export function useSimulation() {
  const [events, setEvents] = useState([]);
  const [riskScore, setRiskScore] = useState(0);
  const [riskHistory, setRiskHistory] = useState(Array(60).fill(0));
  const [alertingCameras, setAlertingCameras] = useState(new Set());
  const [totalViolations, setTotalViolations] = useState(0);
  const eventIdRef = useRef(0);
  const decayTimerRef = useRef(null);

  // Generate a random violation event
  const generateEvent = useCallback(() => {
    const violationType = VIOLATION_LIST[Math.floor(Math.random() * VIOLATION_LIST.length)];
    const camera = CAMERAS[Math.floor(Math.random() * CAMERAS.length)];
    const studentNum = Math.floor(Math.random() * 40) + 1;

    const details = {
      PHONE_DETECTED: `Thí sinh #${studentNum.toString().padStart(2, '0')} sử dụng điện thoại — Confidence: ${(75 + Math.random() * 20).toFixed(0)}%`,
      CHEAT_SHEET: `Phát hiện tài liệu dưới bàn — Confidence: ${(78 + Math.random() * 18).toFixed(0)}%`,
      LOOKING_AWAY: `Thí sinh #${studentNum.toString().padStart(2, '0')} quay đầu sang ${Math.random() > 0.5 ? 'trái' : 'phải'} — ${(2 + Math.random() * 6).toFixed(1)}s`,
      HEAD_DOWN: `Thí sinh #${studentNum.toString().padStart(2, '0')} cúi đầu bất thường — kéo dài ${(3 + Math.random() * 10).toFixed(0)} giây`,
      HAND_NEAR_EAR: `Thí sinh #${studentNum.toString().padStart(2, '0')} có cử chỉ tay gần vùng tai — cần kiểm tra`,
      HAND_SUSPICIOUS: `Thí sinh #${studentNum.toString().padStart(2, '0')} tay ở vị trí bất thường`,
    };

    eventIdRef.current += 1;
    const event = {
      id: `evt-${eventIdRef.current}-${Date.now()}`,
      type: violationType.type,
      label: violationType.label,
      icon: violationType.icon,
      severity: violationType.severity,
      score: violationType.score,
      cameraId: camera.id,
      cameraName: camera.name,
      detail: details[violationType.type] || violationType.label,
      timestamp: new Date(),
    };

    setEvents(prev => [event, ...prev].slice(0, 100)); // Keep last 100
    setTotalViolations(prev => prev + 1);

    // Update risk score
    setRiskScore(prev => {
      const newScore = Math.min(prev + violationType.score, 20);
      return newScore;
    });

    // Flash camera alert
    setAlertingCameras(prev => {
      const next = new Set(prev);
      next.add(camera.id);
      return next;
    });

    // Clear camera alert after 3 seconds
    setTimeout(() => {
      setAlertingCameras(prev => {
        const next = new Set(prev);
        next.delete(camera.id);
        return next;
      });
    }, 3000);

    return event;
  }, []);

  // Score decay over time
  useEffect(() => {
    decayTimerRef.current = setInterval(() => {
      setRiskScore(prev => Math.max(prev - 1, 0));
    }, 2000);

    return () => clearInterval(decayTimerRef.current);
  }, []);

  // Update risk history
  useEffect(() => {
    const historyInterval = setInterval(() => {
      setRiskHistory(prev => {
        const next = [...prev.slice(1), riskScore];
        return next;
      });
    }, 1000);

    return () => clearInterval(historyInterval);
  }, [riskScore]);

  // Auto-generate events at random intervals
  useEffect(() => {
    let timeoutId;

    const scheduleNext = () => {
      const delay = 3000 + Math.random() * 5000; // 3-8 seconds
      timeoutId = setTimeout(() => {
        generateEvent();
        scheduleNext();
      }, delay);
    };

    // Start after a short initial delay
    timeoutId = setTimeout(() => {
      generateEvent();
      scheduleNext();
    }, 2000);

    return () => clearTimeout(timeoutId);
  }, [generateEvent]);

  const clearEvents = useCallback(() => {
    setEvents([]);
    setTotalViolations(0);
    setRiskScore(0);
  }, []);

  return {
    events,
    riskScore,
    riskHistory,
    alertingCameras,
    totalViolations,
    generateEvent,
    clearEvents,
  };
}
