import { useState, useEffect } from 'react';

/**
 * useClock — Hook trả về chuỗi thời gian realtime
 */
export function useClock() {
  const [time, setTime] = useState(formatTime());

  useEffect(() => {
    const interval = setInterval(() => {
      setTime(formatTime());
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  return time;
}

function formatTime() {
  return new Date().toLocaleTimeString('vi-VN', { hour12: false });
}
