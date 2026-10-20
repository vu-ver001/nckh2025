# ============================================================
# web_server.py - Flask Server tích hợp YOLO + Pose
# Stream video đã xử lý lên dashboard qua MJPEG + SSE
# ============================================================
# Cài thêm: venv\Scripts\pip install flask
# Chạy: venv\Scripts\python.exe src\web_server.py
# Mở: http://localhost:5000
# ============================================================

import sys, os, time, json, threading, queue, cv2

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, Response, render_template_string, stream_with_context
from config  import CAMERA_INDEX, FRAME_WIDTH, FRAME_HEIGHT
from yolo_detector       import YOLODetector
from mediapipe_analyzer  import MediaPipeAnalyzer
from fusion_engine       import FusionEngine
from alert_logger        import AlertLogger
from display_ui          import DisplayUI

app   = Flask(__name__)

# Thư mục chứa ảnh vi phạm
SNAPSHOT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "snapshots")
os.makedirs(SNAPSHOT_DIR, exist_ok=True)

# ── Shared state ───────────────────────────────────────────
class AppState:
    def __init__(self):
        self.lock          = threading.Lock()
        self.latest_jpeg   = None        # JPEG bytes for MJPEG stream
        self.alert_queue   = queue.Queue(maxsize=50)
        self.running       = False
        self.fps           = 0.0
        self.risk_score    = 0
        self.risk_level    = "OK"
        self.metrics       = {"fps": 0, "score": 0, "level": "OK"}

state = AppState()

# ── Detection thread ───────────────────────────────────────
def detection_thread():
    detector = YOLODetector()
    analyzer = MediaPipeAnalyzer()
    fusion   = FusionEngine()
    logger   = AlertLogger()
    last_alert_time = {}

    cap = cv2.VideoCapture(CAMERA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    if not cap.isOpened():
        print("[WebServer] ERROR: Khong mo duoc camera!")
        state.running = False
        return

    W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    ui = DisplayUI(W, H)

    # FPS
    fps_counter  = 0
    fps_t        = time.time()

    YOLO_SKIP = 3   # Chạy YOLO mỗi 3 frame để tăng FPS
    frame_idx  = 0
    yolo_dets  = []

    print(f"[WebServer] Camera {W}x{H} - bắt đầu stream...")

    while state.running:
        ret, frame = cap.read()
        if not ret:
            time.sleep(0.05)
            continue

        frame = cv2.flip(frame, 1)
        frame_idx += 1

        # YOLO (skip frames)
        if frame_idx % YOLO_SKIP == 0:
            yolo_dets = detector.detect(frame)

        # MediaPipe (mỗi frame)
        mp_result = analyzer.analyze(frame)

        # Fusion
        fusion_result = fusion.update(yolo_dets, mp_result, yolo_fresh=frame_idx % YOLO_SKIP == 0)

        # Log + push alert
        for event in fusion_result["events"]:
            et  = event.event_type
            now = time.time()
            # Tăng giãn cách giữa các lần chụp/log lên 10 giây để tránh spam
            if now - last_alert_time.get(et, 0) > 10.0:
                logger.log(et, event.detail, event.score, event.level)
                last_alert_time[et] = now
                
                # Chụp ảnh vi phạm nếu mức độ nghiêm trọng
                snapshot_url = None
                if event.level in ["HIGH", "CRITICAL"] or et in ["CHEAT_SHEET", "PHONE_DETECTED", "HAND_NEAR_EAR"]:
                    # Vẽ khung AI lên frame gốc để có bằng chứng
                    snap_frame = frame.copy()
                    snap_frame = analyzer.draw(snap_frame, mp_result)
                    snap_frame = ui.render(snap_frame, fusion_result, state.fps, yolo_dets, mp_result)
                    
                    filename = f"{et}_{int(now)}.jpg"
                    filepath = os.path.join(SNAPSHOT_DIR, filename)
                    cv2.imwrite(filepath, snap_frame)
                    snapshot_url = f"/snapshots/{filename}"

                # Push to SSE queue
                alert_data = {
                    "type":   et,
                    "detail": event.detail,
                    "level":  event.level,
                    "score":  event.score,
                    "image":  snapshot_url
                }
                if not state.alert_queue.full():
                    state.alert_queue.put(alert_data)

        # Draw skeleton
        frame = analyzer.draw(frame, mp_result)

        # Draw UI overlay
        frame = ui.render(frame, fusion_result, state.fps, yolo_dets, mp_result)
        frame = ui.draw_alert_flash(frame, fusion_result["level"])

        # Update shared metrics
        with state.lock:
            state.risk_score = fusion_result["score"]
            state.risk_level = fusion_result["level"]

        # Encode to JPEG
        encode_params = [cv2.IMWRITE_JPEG_QUALITY, 85]
        _, jpeg = cv2.imencode('.jpg', frame, encode_params)
        with state.lock:
            state.latest_jpeg = jpeg.tobytes()

        # FPS calc
        fps_counter += 1
        elapsed = time.time() - fps_t
        if elapsed >= 0.5:
            state.fps = round(fps_counter / elapsed, 1)
            fps_counter = 0
            fps_t = time.time()

    cap.release()
    analyzer.close()
    logger.close()
    print("[WebServer] Detection thread stopped.")

# ─── Flask Routes ──────────────────────────────────────────

@app.route('/')
def index():
    """Serve main dashboard."""
    web_dir  = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'web')
    html_path = os.path.join(web_dir, 'index.html')
    with open(html_path, encoding='utf-8') as f:
        return f.read()

@app.route('/video_feed')
def video_feed():
    """MJPEG stream của video đã xử lý."""
    def generate():
        while True:
            with state.lock:
                jpeg = state.latest_jpeg
            if jpeg:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + jpeg + b'\r\n')
            time.sleep(0.033)   # ~30fps cap

    return Response(
        stream_with_context(generate()),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

@app.route('/alerts')
def alerts():
    """SSE stream for real-time alerts."""
    def event_stream():
        while True:
            try:
                alert = state.alert_queue.get(timeout=1.0)
                data = json.dumps(alert, ensure_ascii=False)
                yield f"data: {data}\n\n"
            except queue.Empty:
                # Heartbeat + metrics
                metrics = json.dumps({
                    "heartbeat": True,
                    "fps":   state.fps,
                    "score": state.risk_score,
                    "level": state.risk_level,
                }, ensure_ascii=False)
                yield f"data: {metrics}\n\n"

    return Response(
        stream_with_context(event_stream()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
        }
    )

@app.route('/start')
def start():
    if not state.running:
        state.running = True
        t = threading.Thread(target=detection_thread, daemon=True)
        t.start()
    return 'OK'

@app.route('/stop')
def stop():
    state.running = False
    return 'OK'

@app.route('/status')
def status():
    return json.dumps({
        "running": state.running,
        "fps":     state.fps,
        "score":   state.risk_score,
        "level":   state.risk_level,
    })

@app.route('/snapshots/<path:filename>')
def serve_snapshot(filename):
    """Serve ảnh vi phạm."""
    from flask import send_from_directory
    return send_from_directory(SNAPSHOT_DIR, filename)

# ─── Entry point ───────────────────────────────────────────
if __name__ == '__main__':
    print("=" * 50)
    print("  ExamGuard AI - Web Server")
    print("  Mo trinh duyet: http://localhost:5500")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5500, threaded=True, debug=False)
