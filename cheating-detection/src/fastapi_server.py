"""Local API for one camera or a video file, with measured metrics and alerts."""
import asyncio
from contextlib import asynccontextmanager
import logging
import os
from pathlib import Path
import threading
import time

import cv2
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from config import BASE_DIR, CAMERA_INDEX, VIDEO_SOURCE, FRAME_WIDTH, FRAME_HEIGHT, YOLO_PHONE_CONFIRM_MODEL
from fusion_engine import FusionEngine
from alert_logger import AlertLogger
from display_ui import DisplayUI
from temporal import SourceClock, SampleGate

SNAPSHOT_DIR = Path(os.environ.get('EXAMGUARD_SNAPSHOT_DIR', str(Path(BASE_DIR) / 'snapshots')))
SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
DEMO_VIDEO_DIR = (Path(BASE_DIR) / 'video').resolve()
DEMO_VIDEO_LABELS = {
    '01_binh_thuong.mp4.mp4': ('01 · Bình thường', 'Ngồi làm bài, không có điện thoại'),
    '02_viet_bai.mp4.mp4': ('02 · Viết bài', 'Viết và nhìn xuống giấy'),
    '03_may_tinh.mp4.mp4': ('03 · Máy tính', 'Dùng máy tính Casio'),
    '04_hop_but.mp4.mp4': ('04 · Hộp bút / sổ', 'Vật dễ nhầm với điện thoại'),
    '05_dien_thoai_ro.mp4.mp4': ('05 · Điện thoại rõ', 'Cầm điện thoại rõ trước camera'),
    '06_dien_thoai_kho.mp4.mp4': ('06 · Điện thoại khó', 'Điện thoại xa hoặc bị che'),
}
DEMO_VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mov', '.mkv'}
DEMO_CAMERA = dict(kind='camera', index=CAMERA_INDEX, label='Webcam trực tiếp',
                   description=f'Camera máy hiện tại (chỉ số {CAMERA_INDEX})')
log = logging.getLogger(__name__)
WS_SEND_TIMEOUT = 1.0


def _open_capture(source):
    """Open a source, trying Windows camera backends before the default one."""
    if not isinstance(source, int):
        return cv2.VideoCapture(source)

    # Some Windows camera drivers expose a stream through DirectShow but not
    # Media Foundation (or the reverse). Try both before OpenCV's auto choice.
    candidates = []
    if os.name == 'nt':
        candidates.extend([
            (getattr(cv2, 'CAP_DSHOW', None), 'DirectShow'),
            (getattr(cv2, 'CAP_MSMF', None), 'Media Foundation'),
        ])
    candidates.append((getattr(cv2, 'CAP_ANY', 0), 'Auto'))
    seen = set()
    for backend, _name in candidates:
        if backend is None or backend in seen:
            continue
        seen.add(backend)
        cap = cv2.VideoCapture(source, backend)
        if cap.isOpened():
            return cap
        cap.release()
    return None

class AppState:
    def __init__(self):
        self.lock = threading.RLock()
        self.worker = None
        self.stop_event = threading.Event()
        self.loop = None
        self.running = False
        self.status = 'stopped'
        self.error = None
        self.latest_jpeg = None
        self.fps = 0.0
        self.risk_score = 0
        self.risk_level = 'OK'
        # None means use the source configured through EXAMGUARD_VIDEO_SOURCE.
        self.video_source = None
        self.model = self.unloaded_model()

    @staticmethod
    def unloaded_model():
        return dict(configured_phone=YOLO_PHONE_CONFIRM_MODEL, loaded_phone=None,
                    phone_name=Path(YOLO_PHONE_CONFIRM_MODEL).parent.parent.name,
                    detector=None, status='not_loaded', error=None,
                    pose=dict(backend=os.environ.get('EXAMGUARD_POSE_BACKEND', 'mediapipe'), status='not_loaded'))

    def metrics(self):
        with self.lock:
            source_value = self.current_source()
            if isinstance(source_value, int):
                source = dict(kind='camera', name=f'Webcam {source_value}', index=source_value)
            else:
                source = dict(kind='video', name=Path(source_value).name)
            return dict(running=self.running, status=self.status, error=self.error,
                        model=dict(self.model),
                        source=source,
                        warning=(f"Không nạp được model xác nhận; đang dùng {self.model['detector']}. "
                                 f"{self.model['error'] or ''}") if self.model['status'] == 'fallback' else None,
                        fps=self.fps, score=self.risk_score, level=self.risk_level)

    def current_source(self):
        """Return the selected demo source or the environment-configured source."""
        return VIDEO_SOURCE if self.video_source is None else self.video_source

state = AppState()

class ConnectionManager:
    def __init__(self):
        self.connections = {}

    async def connect(self, websocket):
        await websocket.accept()
        self.connections[websocket] = asyncio.Lock()

    def disconnect(self, websocket):
        self.connections.pop(websocket, None)

    async def send(self, websocket, message):
        lock = self.connections.get(websocket)
        if lock is not None:
            try:
                # Bound lock acquisition as well as socket writes.
                async with asyncio.timeout(WS_SEND_TIMEOUT):
                    async with lock:
                        await websocket.send_json(message)
            except TimeoutError:
                self.disconnect(websocket)
                raise

    async def broadcast(self, message):
        async def deliver(websocket):
            try:
                await self.send(websocket, message)
            except Exception:
                self.disconnect(websocket)
        await asyncio.gather(*(deliver(ws) for ws in list(self.connections)))

manager = ConnectionManager()

@asynccontextmanager
async def lifespan(app):
    state.loop = asyncio.get_running_loop()
    yield
    state.stop_event.set()
    if state.worker:
        await asyncio.to_thread(state.worker.join, 5)
    state.loop = None

app = FastAPI(title='ExamGuard AI API', lifespan=lifespan)
app.add_middleware(CORSMiddleware,
    allow_origins=['http://localhost:5173', 'http://127.0.0.1:5173'],
    allow_methods=['GET', 'POST'], allow_headers=['*'])
app.mount('/snapshots', StaticFiles(directory=SNAPSHOT_DIR), name='snapshots')

def _demo_video_catalog():
    """Return the curated video set shown in the demo picker."""
    rows = []
    for filename, (label, description) in DEMO_VIDEO_LABELS.items():
        path = DEMO_VIDEO_DIR / filename
        if path.is_file():
            rows.append(dict(filename=filename, label=label, description=description))
    return rows

def _resolve_demo_video(filename):
    if not isinstance(filename, str) or not filename:
        raise HTTPException(422, 'Cần chọn một video demo.')
    candidate = (DEMO_VIDEO_DIR / filename).resolve()
    if candidate.parent != DEMO_VIDEO_DIR or candidate.suffix.lower() not in DEMO_VIDEO_EXTENSIONS:
        raise HTTPException(400, 'Video phải nằm trong thư mục video demo.')
    if not candidate.is_file():
        raise HTTPException(404, 'Không tìm thấy video demo đã chọn.')
    return candidate

def create_components():
    # Keep status endpoints usable if AI dependencies/models fail.
    from yolo_detector import YOLODetector
    from pose_factory import create_pose_analyzer
    return YOLODetector(), create_pose_analyzer()

def detection_thread():
    cap = analyzer = logger = None
    try:
        source = state.current_source()
        source_is_camera = isinstance(source, int)
        cap = _open_capture(source)
        if cap is None or not cap.isOpened():
            if source_is_camera:
                raise RuntimeError(
                    f'Không mở được webcam {source}. Hãy kiểm tra camera đã cắm/bật, '
                    'quyền Camera của Windows, privacy mode/màn trập của laptop và '
                    'ứng dụng khác có đang giữ camera không.'
                )
            raise RuntimeError('Không mở được video đã cấu hình.')
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
        detector, analyzer = create_components()
        with state.lock:
            metadata = detector.model_status()
            if isinstance(metadata, dict):
                state.model = metadata
                pose_metadata = analyzer.model_status()
                if isinstance(pose_metadata, dict):
                    state.model['pose'] = pose_metadata
        fusion, logger = FusionEngine(), AlertLogger()
        ui = DisplayUI(int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                       int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        last_alert_time = {}
        frame_idx, fps_counter = 0, 0
        fps_start = time.perf_counter()
        yolo_dets = []
        source_clock = SourceClock(cap.get(cv2.CAP_PROP_FPS), live=source_is_camera)
        sample_gate = SampleGate(.1)
        while not state.stop_event.is_set():
            ret, frame = cap.read()
            if not ret:
                if source_is_camera:
                    raise RuntimeError('Camera ngừng cung cấp khung hình.')
                break
            if source_is_camera:
                frame = cv2.flip(frame, 1)
            source_seconds = source_clock.timestamp(frame_idx, cap.get(cv2.CAP_PROP_POS_MSEC))
            fresh = sample_gate.due(source_seconds)
            frame_idx += 1
            if fresh:
                yolo_dets = detector.detect(frame)
            analysis = analyzer.analyze(frame, timestamp=source_seconds)
            result = fusion.update(yolo_dets, analysis, yolo_fresh=fresh, timestamp=source_seconds)
            frame = analyzer.draw(frame, analysis)
            frame = ui.render(frame, result, state.fps, yolo_dets, analysis)
            frame = ui.draw_alert_flash(frame, result['level'])
            for event in result['events']:
                now = time.time()
                if source_seconds - last_alert_time.get(event.event_type, float('-inf')) < 10:
                    continue
                logger.log(event.event_type, event.detail, event.score, event.level)
                last_alert_time[event.event_type] = source_seconds
                snapshot_url = None
                if event.level in {'HIGH', 'CRITICAL'} or event.event_type in {
                    'CHEAT_SHEET', 'PHONE_DETECTED', 'HAND_NEAR_EAR'
                }:
                    filename = f'{event.event_type}_{time.time_ns()}.jpg'
                    if cv2.imwrite(str(SNAPSHOT_DIR / filename), frame):
                        snapshot_url = f'/snapshots/{filename}'
                message = dict(type=event.event_type, detail=event.detail,
                               level=event.level, score=event.score,
                               image=snapshot_url, timestamp=now, source_seconds=source_seconds)
                if state.loop and state.loop.is_running():
                    future = asyncio.run_coroutine_threadsafe(manager.broadcast(message), state.loop)
                    try:
                        future.result(timeout=5)
                    except Exception:
                        future.cancel()
                        log.warning('Alert delivery failed; detection continues', exc_info=True)
            encoded, jpeg = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            fps_counter += 1
            elapsed = time.perf_counter() - fps_start
            with state.lock:
                state.status = 'running'
                state.risk_score, state.risk_level = result['score'], result['level']
                if encoded:
                    state.latest_jpeg = jpeg.tobytes()
                if elapsed >= 0.5:
                    state.fps = round(fps_counter / elapsed, 1)
                    fps_counter, fps_start = 0, time.perf_counter()
    except Exception as exc:
        log.exception('Detection stopped')
        with state.lock:
            state.error, state.status = str(exc), 'error'
    finally:
        for resource, method in [(cap, 'release'), (analyzer, 'close'), (logger, 'close')]:
            if resource is not None:
                try:
                    getattr(resource, method)()
                except Exception:
                    log.exception('Resource cleanup failed')
        with state.lock:
            state.running = False
            state.latest_jpeg = None
            state.fps = 0.0
            state.risk_score, state.risk_level = 0, 'OK'
            state.model = state.unloaded_model()
            if state.status != 'error':
                state.status = 'stopped'

def ensure_started():
    with state.lock:
        if state.worker and state.worker.is_alive():
            if state.stop_event.is_set():
                raise HTTPException(409, 'Phiên trước đang dừng; hãy thử lại sau.')
            return
        state.stop_event.clear()
        state.running, state.status, state.error = True, 'starting', None
        state.latest_jpeg = None
        state.model = state.unloaded_model()
        state.fps, state.risk_score, state.risk_level = 0.0, 0, 'OK'
        state.worker = threading.Thread(target=detection_thread, daemon=True)
        state.worker.start()

@app.post('/start')
def start_camera():
    ensure_started()
    return state.metrics()

@app.get('/demo/videos')
def list_demo_videos():
    return dict(videos=_demo_video_catalog(), camera=DEMO_CAMERA)

@app.post('/source')
def select_source(payload: dict):
    """Select a curated video or the configured local webcam for the next Start."""
    selection = payload if isinstance(payload, dict) else {}
    source_kind = selection.get('kind', 'video')
    if source_kind == 'camera':
        camera_index = selection.get('index', CAMERA_INDEX)
        if isinstance(camera_index, bool) or not isinstance(camera_index, int) or camera_index < 0:
            raise HTTPException(422, 'Chỉ số webcam phải là số nguyên không âm.')
        selected_source = camera_index
    elif source_kind == 'video':
        path = _resolve_demo_video(selection.get('filename'))
        selected_source = str(path)
    else:
        raise HTTPException(422, 'Nguồn phải là video demo hoặc webcam.')
    with state.lock:
        if state.worker and state.worker.is_alive():
            raise HTTPException(409, 'Hãy dừng phiên hiện tại trước khi đổi nguồn.')
        state.video_source = selected_source
        state.error = None
        state.status = 'stopped'
        state.latest_jpeg = None
        state.fps, state.risk_score, state.risk_level = 0.0, 0, 'OK'
        state.model = state.unloaded_model()
    return state.metrics()

@app.post('/stop')
def stop_camera():
    with state.lock:
        state.stop_event.set()
        if state.running:
            state.status = 'stopping'
        worker = state.worker
    if worker:
        worker.join(timeout=5)
    return state.metrics()

@app.get('/status')
def get_status():
    return state.metrics()

async def frame_generator():
    worker = state.worker
    while worker and worker.is_alive() and state.worker is worker:
        with state.lock:
            jpeg = state.latest_jpeg
        if jpeg:
            yield b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + jpeg + b'\r\n'
        await asyncio.sleep(0.033)

@app.get('/video_feed')
async def video_feed():
    return StreamingResponse(frame_generator(),
        media_type='multipart/x-mixed-replace; boundary=frame')

@app.websocket('/ws/alerts')
async def websocket_alerts(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await manager.send(websocket, {'heartbeat': True, **state.metrics()})
            await asyncio.sleep(1)
    except (WebSocketDisconnect, RuntimeError, OSError, TimeoutError):
        pass
    finally:
        manager.disconnect(websocket)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000)
