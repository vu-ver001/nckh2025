# ============================================================
# main.py - Pipeline Chính (Refactored v2.0)
# Hệ thống giám sát phát hiện gian lận thi cử
# YOLO + MediaPipe + Fusion Engine
# ============================================================

import sys
import os
import time
import threading

import cv2
import numpy as np

# Thêm src vào path để import các module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (
    CAMERA_INDEX, FRAME_WIDTH, FRAME_HEIGHT,
    YOLO_POSE_MODEL, SAVE_VIDEO, LOG_VIDEO_PATH, LOG_DIR,
)
from yolo_detector import YOLODetector
from mediapipe_analyzer import MediaPipeAnalyzer
from fusion_engine import FusionEngine
from alert_logger import AlertLogger
from display_ui import DisplayUI


# ─── Thread-safe shared state ─────────────────────────────
class SharedState:
    def __init__(self):
        self.lock = threading.Lock()
        self.yolo_detections = []
        self.yolo_generation = 0
        self.frame_generation = 0
        self.mp_analysis = {}
        self.fusion_result = {"score": 0, "level": "OK", "events": [], "should_alert": False}
        self.latest_frame = None
        self.running = True


def yolo_worker(detector: YOLODetector, state: SharedState):
    """
    Worker thread riêng cho YOLO để tránh block FPS của camera.
    YOLO chạy chậm hơn MediaPipe → chạy thread riêng.
    """
    last_frame_generation = -1
    while state.running:
        with state.lock:
            frame = state.latest_frame
            generation = state.frame_generation

        if frame is None or generation == last_frame_generation:
            time.sleep(0.01)
            continue

        detections = detector.detect(frame)

        with state.lock:
            state.yolo_detections = detections
            state.yolo_generation += 1
        last_frame_generation = generation

        time.sleep(0.01)   # ~30ms interval (không cần every frame)


def main():
    print("=" * 60)
    print("  CHEATING DETECTION SYSTEM v2.0")
    print("  YOLO + MediaPipe | Thoi gian thuc")
    print("=" * 60)

    # ── Init components ────────────────────────────────────
    detector  = YOLODetector(use_custom_model=False)
    analyzer  = MediaPipeAnalyzer()
    fusion    = FusionEngine()
    logger    = AlertLogger()
    state     = SharedState()

    # ── Camera setup ───────────────────────────────────────
    # Hỗ trợ video file hoặc webcam
    source = CAMERA_INDEX
    if len(sys.argv) > 1:
        source = sys.argv[1]          # python main.py video.mp4
        print(f"[Main] Using video file: {source}")
    else:
        print(f"[Main] Using camera index: {source}")

    cap = cv2.VideoCapture(source)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, 30)

    if not cap.isOpened():
        print("[ERROR] Khong mo duoc camera/video!")
        sys.exit(1)

    actual_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"[Main] Resolution: {actual_w}x{actual_h}")

    ui = DisplayUI(actual_w, actual_h)

    # ── Video recording (optional) ─────────────────────────
    video_writer = None
    if SAVE_VIDEO:
        os.makedirs(LOG_DIR, exist_ok=True)
        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        video_writer = cv2.VideoWriter(LOG_VIDEO_PATH, fourcc, 20.0, (actual_w, actual_h))

    # ── Start YOLO in background thread ───────────────────
    yolo_thread = threading.Thread(
        target=yolo_worker, args=(detector, state), daemon=True
    )
    yolo_thread.start()
    print("[Main] YOLO worker thread started.")

    # ── FPS tracking ──────────────────────────────────────
    fps_counter = 0
    fps_value   = 0.0
    fps_time    = time.time()

    # ── Alert cooldown (chống spam log) ───────────────────
    last_alert_time = {}

    print("[Main] System running. Press ESC or Q to quit.\n")

    # ══════════════════════════════════════════════════════
    # Main loop
    # ══════════════════════════════════════════════════════
    last_yolo_generation = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            print("[Main] Video ended or camera disconnected.")
            break

        # Flip để nhìn như gương
        frame = cv2.flip(frame, 1)

        # Share frame với YOLO thread
        with state.lock:
            state.latest_frame = frame.copy()
            state.frame_generation += 1
            yolo_generation = state.yolo_generation
            yolo_dets = list(state.yolo_detections)

        # ── MediaPipe analysis (main thread, mỗi frame) ───
        mp_result = analyzer.analyze(frame)

        # ── Fusion engine ─────────────────────────────────
        fusion_result = fusion.update(yolo_dets, mp_result, yolo_fresh=yolo_generation != last_yolo_generation)
        last_yolo_generation = yolo_generation

        # ── Log alerts (với cooldown 3s/loại event) ───────
        for event in fusion_result["events"]:
            et = event.event_type
            now = time.time()
            if now - last_alert_time.get(et, 0) > 3.0:
                logger.log(et, event.detail, event.score, event.level)
                last_alert_time[et] = now

        # ── Draw MediaPipe skeleton ────────────────────────
        frame = analyzer.draw(frame, mp_result)

        # ── Draw UI overlay ───────────────────────────────
        frame = ui.render(frame, fusion_result, fps_value, yolo_dets, mp_result)
        frame = ui.draw_alert_flash(frame, fusion_result["level"])

        # ── FPS calculation ───────────────────────────────
        fps_counter += 1
        elapsed = time.time() - fps_time
        if elapsed >= 0.5:
            fps_value   = fps_counter / elapsed
            fps_counter = 0
            fps_time    = time.time()

        # ── Display ───────────────────────────────────────
        cv2.imshow("Cheating Detection System v2.0", frame)

        if SAVE_VIDEO and video_writer:
            video_writer.write(frame)

        # ESC hoặc Q để thoát
        key = cv2.waitKey(1) & 0xFF
        if key in (27, ord("q"), ord("Q")):
            print("[Main] Exiting...")
            break

    # ── Cleanup ──────────────────────────────────────────
    state.running = False
    cap.release()
    analyzer.close()
    logger.close()
    if video_writer:
        video_writer.release()
    cv2.destroyAllWindows()
    print("[Main] Session ended. Check logs/ for alert history.")


if __name__ == "__main__":
    main()