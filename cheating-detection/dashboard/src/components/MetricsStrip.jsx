import './MetricsStrip.css';
export default function MetricsStrip({ fps, isConnected, status }) {
  const metrics = [
    ['FPS xử lý', isConnected && status === 'running' ? fps.toFixed(1) : '—', 'Đo tại backend'],
    ['Precision toàn hệ thống', '—', 'Chưa đánh giá trên video phòng thi'],
    ['Báo động nhầm', '—', 'Cần video có nhãn đối chiếu'],
    ['Nguồn video', '1', 'Một nguồn video được cấu hình'],
  ];
  return <div className="metrics-strip">{metrics.map(([label, value, note]) =>
    <div className="metric-cell" key={label}>
      <div className="metric-label">{label}</div>
      <div className="metric-value">{value}</div>
      <div className="metric-sub">{note}</div>
    </div>)}</div>;
}
