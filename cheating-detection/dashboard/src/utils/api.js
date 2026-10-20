export const API_BASE = (import.meta.env.VITE_API_BASE || '/api').replace(/\/$/, '');
export const apiUrl = path => `${API_BASE}${path}`;
export function websocketUrl() {
  const url = new URL(apiUrl('/ws/alerts'), window.location.href);
  url.protocol = url.protocol === 'https:' ? 'wss:' : 'ws:';
  return url.href;
}
