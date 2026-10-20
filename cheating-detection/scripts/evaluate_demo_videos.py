"""Offline event evaluation on separately recorded clips. Never trains a model."""
import argparse
import json
import os
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))


def event_metrics(expected, alerts):
    detected, delays = 0, []
    for event in expected:
        hits = [a['video_seconds'] for a in alerts if a['type'] == event['type']
                and event['start'] <= a['video_seconds'] <= event['end']]
        if hits:
            detected += 1
            delays.append(min(hits) - event['start'])
    false = [a for a in alerts if not any(e['type'] == a['type'] and
             e['start'] <= a['video_seconds'] <= e['end'] for e in expected)]
    return dict(expected_events=len(expected), detected_events=detected,
                missed_events=len(expected)-detected, false_alerts=len(false),
                latency_video_seconds=delays, false_alert_details=false)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--manifest', type=Path, default=ROOT / 'demo/recordings/manifest.json')
    parser.add_argument('--model', type=Path, default=ROOT / 'models/phone_v3_colab/weights/best.pt')
    parser.add_argument('--output', type=Path, default=ROOT / 'artifacts/demo-video-evaluation.json')
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding='utf-8'))
    report = dict(model=str(args.model.resolve()), clips=[],
                  timing='Detector sampled every .1 source seconds; 10s source-time notification cooldown. Latency uses source time, not end-to-end browser latency.',
                  limitations='Events require complete human labels for all event types; detector presence alone does not verify bounding-box correctness.')
    ready = []
    for clip in manifest['clips']:
        path = (args.manifest.parent / clip['file']).resolve()
        if not path.is_file() or clip.get('events') is None:
            report['clips'].append(dict(file=clip['file'], status='missing_video_or_labels'))
            continue
        events = clip['events']
        for event in events:
            assert isinstance(event['type'], str) and 0 <= event['start'] < event['end'], 'Invalid event interval'
        for i, event in enumerate(events):
            assert not any(other['type'] == event['type'] and
                max(other['start'], event['start']) <= min(other['end'], event['end'])
                for other in events[:i]), 'Overlapping same-type events must be merged'
        ready.append((clip, path))
    if ready:
        assert args.model.is_file(), 'Missing model'
        os.environ['EXAMGUARD_PHONE_CONFIRM_MODEL'] = str(args.model.resolve())
        os.environ.setdefault('YOLO_CONFIG_DIR', str(ROOT / 'artifacts'))
        import cv2
        from yolo_detector import YOLODetector
        from pose_factory import create_pose_analyzer
        from temporal import SourceClock, SampleGate
        from fusion_engine import FusionEngine
        from detection_labels import is_phone_label
        detector = YOLODetector()
        assert detector.phone_confirm_model is not None, detector.phone_confirm_error
        for clip, path in ready:
            analyzer, fusion = create_pose_analyzer(), FusionEngine()
            cap = cv2.VideoCapture(str(path))
            try:
                assert cap.isOpened(), f'Cannot decode {path}'
                fps = cap.get(cv2.CAP_PROP_FPS)
                assert fps > 0, 'Missing source FPS'
                clock, sampling = SourceClock(fps), SampleGate(.1)
                count, alerts, observations, cooldown = 0, [], [], {}
                started = time.perf_counter()
                detections = []
                while True:
                    ok, frame = cap.read()
                    if not ok:
                        break
                    seconds = clock.timestamp(count, cap.get(cv2.CAP_PROP_POS_MSEC))
                    fresh = sampling.due(seconds)
                    if fresh:
                        detections = detector.detect(frame)
                        observations.append(dict(video_seconds=seconds, phones=[d for d in detections
                            if d.get('is_cheat') and is_phone_label(d['label'])]))
                    result = fusion.update(detections, analyzer.analyze(frame, timestamp=seconds), yolo_fresh=fresh, timestamp=seconds)
                    for event in result['events']:
                        now = time.perf_counter()
                        if seconds - cooldown.get(event.event_type, float('-inf')) < 10:
                            continue
                        cooldown[event.event_type] = seconds
                        alerts.append(dict(type=event.event_type, video_seconds=seconds,
                                           processing_seconds=now-started, detail=event.detail))
                    count += 1
                elapsed = time.perf_counter()-started
                assert count, 'Empty video'
                assert all(e['end'] <= count/fps for e in clip['events']), 'Label beyond video duration'
                report['clips'].append(dict(file=clip['file'], status='evaluated', frames=count,
                    video_seconds=count/fps, processing_fps=count/elapsed,
                    alerts=alerts, detector_observations=observations, pose=analyzer.model_status(),
                    timestamp_fallbacks=clock.fallbacks,
                    **event_metrics(clip['events'], alerts)))
            finally:
                cap.release()
                analyzer.close()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    print(args.output)


if __name__ == '__main__':
    main()
