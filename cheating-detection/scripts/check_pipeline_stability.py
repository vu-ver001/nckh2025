"""Timed component soak test on a repeated technical video, not an accuracy benchmark."""
import argparse
import json
import os
from pathlib import Path
import sys
import time
import hashlib
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--video', type=Path, required=True)
    parser.add_argument('--seconds', type=float, default=1800)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('Use a new output file')
    if args.seconds <= 0:
        parser.error('Duration must be positive')
    import cv2
    from pose_factory import create_pose_analyzer
    from yolo_detector import YOLODetector
    from fusion_engine import FusionEngine
    from temporal import SampleGate
    try:
        import psutil
        process = psutil.Process()
    except ImportError:
        process = None
    args.output.parent.mkdir(parents=True, exist_ok=True)
    detector, pose, fusion = YOLODetector(), create_pose_analyzer(), FusionEngine()
    cap = cv2.VideoCapture(str(args.video))
    if not cap.isOpened():
        raise ValueError('Cannot open video')
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        raise ValueError('Invalid FPS')
    gate, count, loops, alerts = SampleGate(.1), 0, 0, 0
    started = checkpoint = time.perf_counter()
    samples, detections = [], []
    report = dict(status='running', requested_seconds=args.seconds,
        source=str(args.video.resolve()), sha256=hashlib.sha256(args.video.read_bytes()).hexdigest(),
        model=detector.model_status(), pose=pose.model_status(),
        limitation='Repeated technical input. Tests decode/models/fusion/draw/JPEG, not WebSocket clients, physical camera or independent accuracy.')
    try:
        while time.perf_counter()-started < args.seconds:
            ok, frame = cap.read()
            if not ok:
                cap.release()
                cap = cv2.VideoCapture(str(args.video))
                ok, frame = cap.read()
                if not ok:
                    raise ValueError('Cannot restart video')
                loops += 1
            timestamp = count / fps
            fresh = gate.due(timestamp)
            if fresh:
                detections = detector.detect(frame)
            analysis = pose.analyze(frame, timestamp=timestamp)
            result = fusion.update(detections, analysis, yolo_fresh=fresh, timestamp=timestamp)
            alerts += len(result['events'])
            annotated = pose.draw(frame, analysis)
            ok, jpeg = cv2.imencode('.jpg', annotated)
            if not ok:
                raise ValueError('JPEG encoder failure')
            count += 1
            now = time.perf_counter()
            if now-checkpoint >= 30:
                record = dict(elapsed=now-started,frames=count,average_fps=count/(now-started),
                              rss_bytes=process.memory_info().rss if process else None)
                samples.append(record)
                print(json.dumps(record),flush=True)
                checkpoint=now
        report['status']='passed'
    except Exception as exc:
        report.update(status='failed',error=str(exc))
        raise
    finally:
        cap.release()
        pose.close()
        report.update(elapsed_seconds=time.perf_counter()-started,frames=count,
                      replay_loops=loops,raw_events=alerts,samples=samples)
        args.output.write_text(json.dumps(report,indent=2),encoding='utf-8')
        print(args.output,flush=True)


if __name__ == '__main__':
    main()
