import { useRef, useEffect, useCallback } from 'react';
import { MAX_RISK_SCORE } from '../utils/constants';
import './RiskGauge.css';

export default function RiskGauge({ riskScore, riskHistory }) {
  const canvasRef = useRef(null);
  const percentage = Math.min((riskScore / MAX_RISK_SCORE) * 100, 100);

  const getScoreClass = () => {
    if (riskScore >= 9) return 'danger';
    if (riskScore >= 2) return 'warn';
    return 'safe';
  };

  // Draw sparkline chart
  const drawChart = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width;
    canvas.height = rect.height;

    const ctx = canvas.getContext('2d');
    const W = canvas.width;
    const H = canvas.height;
    const pts = riskHistory;
    const step = W / (pts.length - 1);

    ctx.clearRect(0, 0, W, H);

    // Fill area
    const gradient = ctx.createLinearGradient(0, 0, 0, H);
    gradient.addColorStop(0, 'rgba(59, 130, 246, 0.35)');
    gradient.addColorStop(1, 'rgba(59, 130, 246, 0.02)');

    ctx.beginPath();
    pts.forEach((v, i) => {
      const x = i * step;
      const y = H - (v / MAX_RISK_SCORE * (H - 6)) - 3;
      i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
    });
    ctx.lineTo(W, H);
    ctx.lineTo(0, H);
    ctx.closePath();
    ctx.fillStyle = gradient;
    ctx.fill();

    // Line
    ctx.beginPath();
    pts.forEach((v, i) => {
      const x = i * step;
      const y = H - (v / MAX_RISK_SCORE * (H - 6)) - 3;
      i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
    });

    // Line gradient based on value
    const lineGrad = ctx.createLinearGradient(0, 0, W, 0);
    lineGrad.addColorStop(0, '#3b82f6');
    lineGrad.addColorStop(0.5, '#06b6d4');
    lineGrad.addColorStop(1, '#3b82f6');
    ctx.strokeStyle = lineGrad;
    ctx.lineWidth = 2;
    ctx.lineJoin = 'round';
    ctx.lineCap = 'round';
    ctx.stroke();

    // Last point dot
    const lastVal = pts[pts.length - 1];
    const lastX = W;
    const lastY = H - (lastVal / MAX_RISK_SCORE * (H - 6)) - 3;
    ctx.fillStyle = '#06b6d4';
    ctx.beginPath();
    ctx.arc(lastX - 1, lastY, 3, 0, Math.PI * 2);
    ctx.fill();

    // Glow
    ctx.fillStyle = 'rgba(6, 182, 212, 0.3)';
    ctx.beginPath();
    ctx.arc(lastX - 1, lastY, 6, 0, Math.PI * 2);
    ctx.fill();
  }, [riskHistory]);

  useEffect(() => {
    drawChart();
  }, [drawChart]);

  useEffect(() => {
    const handleResize = () => drawChart();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [drawChart]);

  return (
    <>
      <div className="risk-gauge">
        <div className="risk-gauge-header">
          <span className="risk-gauge-label">Mức độ Rủi ro</span>
          <span className={`risk-gauge-score ${getScoreClass()}`}>
            {riskScore} / {MAX_RISK_SCORE}
          </span>
        </div>
        <div className="risk-track">
          <div className="risk-fill" style={{ width: `${percentage}%` }} />
        </div>
        <div className="risk-ticks">
          <span>Thấp</span>
          <span>Nghi ngờ</span>
          <span>Báo động</span>
        </div>
      </div>

      <div className="risk-chart-section">
        <div className="risk-chart-label">
          <span>📈</span>
          <span>Rủi ro theo thời gian</span>
        </div>
        <canvas ref={canvasRef} className="risk-chart-canvas" />
      </div>
    </>
  );
}
