"""Four-way phone experiment. Never trains or invents missing video labels."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from phone_experiment import VARIANTS, PhoneExperimentDetector, EpisodeBuilder, episode_metrics, validate_events
from temporal import SourceClock, SampleGate


def sha(path):
    with open(path, 'rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, default=ROOT/'demo/recordings/manifest.json')
    parser.add_argument('--model', type=Path, default=ROOT/'models/phone_v3_colab/weights/best.pt')
    parser.add_argument('--output', type=Path, default=ROOT/'artifacts/research/video-ablation.json')
    parser.add_argument('--variants', nargs='+', choices=VARIANTS, default=list(VARIANTS))
    parser.add_argument('--allowed-filter', action='store_true', help='Separate C/D experiment only; legacy allowed-object veto')
    args = parser.parse_args()
    code_files = ['scripts/evaluate_phone_ablation.py','src/phone_experiment.py','src/temporal.py','src/yolo_detector.py','src/config.py','src/fusion_engine.py']
    code_hashes = {name:sha(ROOT/name) for name in code_files}
    if args.output.exists():
        parser.error('Output already exists; use a new path to preserve experiment evidence')
    if args.allowed_filter and any(v not in ('combined','temporal') for v in args.variants):
        parser.error('--allowed-filter only supports combined/temporal in a separate experiment')
    from config import YOLO_WORLD_MODEL, PHONE_CONF_THRESHOLD, PHONE_CONFIRM_CONF, PHONE_CONFIRM_IOU, YOLO_IOU_THRESHOLD, YOLO_WORLD_CHEAT_CLASSES, YOLO_WORLD_ALLOWED_CLASSES
    manifest = json.loads(args.manifest.read_text(encoding='utf-8-sig'))
    report = dict(created_at=datetime.now(timezone.utc).isoformat(), purpose=manifest.get('purpose'),
        status='pending', manifest=str(args.manifest.resolve()), manifest_sha256=sha(args.manifest),
        model=str(args.model.resolve()), python=sys.version, platform=platform.platform(),
        settings=dict(world_phone_conf=PHONE_CONF_THRESHOLD, phone_conf=PHONE_CONFIRM_CONF,
            confirm_iou=PHONE_CONFIRM_IOU, nms_iou=YOLO_IOU_THRESHOLD, sample_seconds=.1,
            persistence_seconds=.2, persistence_min_observations=3, max_gap_seconds=.5,
            allowed_filter=args.allowed_filter, pose='disabled', device='cpu', imgsz=640,
            prompt=YOLO_WORLD_CHEAT_CLASSES+YOLO_WORLD_ALLOWED_CLASSES),
        limitations=['Pilot only; phone event presence labels do not establish bbox correctness.',
            'Source-time first-alarm latency excludes display/network. FPS measured on full decode loop after warm-up.',
            'Episodes group contiguous positive samples. Each GT matches once by onset; fragments count as unmatched predictions.',
            'Phone-only ablation, not the full dashboard pipeline. The allowed veto is disabled unless explicitly enabled.'],
        clips=[], runs=[])
    ready = []
    for clip in manifest['clips']:
        path = (args.manifest.parent / clip['file']).resolve()
        if not path.is_file() or clip.get('events') is None:
            report['clips'].append(dict(file=clip['file'], status='missing_video_or_labels'))
            continue
        validate_events(clip['events'])
        report['clips'].append(dict(file=clip['file'], status='ready', sha256=sha(path), metadata=clip))
        ready.append((clip,path))
    if ready:
        if not args.model.is_file():
            raise FileNotFoundError(args.model)
        os.environ.setdefault('YOLO_CONFIG_DIR', str(ROOT/'artifacts'))
        import cv2
        import ultralytics
        import torch
        report.update(model_sha256=sha(args.model), world_sha256=sha(YOLO_WORLD_MODEL),
                      ultralytics=ultralytics.__version__, torch=torch.__version__, opencv=cv2.__version__)
        for variant in args.variants:
            load_start = time.perf_counter()
            detector = PhoneExperimentDetector(variant, args.model, allowed_filter=args.allowed_filter)
            load_seconds = time.perf_counter()-load_start
            for clip, path in ready:
                capture = cv2.VideoCapture(str(path))
                try:
                    if not capture.isOpened():
                        raise ValueError(f'Cannot open video: {path}')
                    fps = capture.get(cv2.CAP_PROP_FPS)
                    clock, gate = SourceClock(fps), SampleGate(.1)
                    builder = EpisodeBuilder(variant)
                    ok, first = capture.read()
                    if not ok:
                        raise ValueError(f'Empty video: {path}')
                    warm_start = time.perf_counter()
                    detector.detect(first)
                    warm_seconds = time.perf_counter()-warm_start
                    capture.release()
                    capture = cv2.VideoCapture(str(path))
                    observations, raw_alerts, notifications = [], [], []
                    last_notification = float('-inf')
                    frames = 0
                    started = time.perf_counter()
                    while True:
                        ok, frame = capture.read()
                        if not ok:
                            break
                        seconds = clock.timestamp(frames, capture.get(cv2.CAP_PROP_POS_MSEC))
                        frames += 1
                        if not gate.due(seconds):
                            continue
                        tick = time.perf_counter()
                        phones = detector.detect(frame)
                        active = builder.update(phones, seconds)
                        observations.append(dict(source_seconds=seconds, phones=phones,
                            active=active, detection_seconds=time.perf_counter()-tick))
                        if active:
                            raw_alerts.append(seconds)
                            if seconds-last_notification >= 10-1e-9:
                                notifications.append(seconds)
                                last_notification = seconds
                    elapsed = time.perf_counter()-started
                    duration = clock.last+1/fps
                    if any(e['end'] > duration+1e-6 for e in clip['events']):
                        raise ValueError(f'Event outside decoded duration: {path}')
                    expected = [e for e in clip['events'] if e['type']=='PHONE_DETECTED']
                    report['runs'].append(dict(variant=variant, file=clip['file'], frames=frames,
                        source_seconds=duration, evaluated_samples=len(observations),
                        source_timestamp_fallbacks=clock.fallbacks, model_load_seconds=load_seconds,
                        warmup_seconds=warm_seconds, processing_seconds=elapsed, processing_fps=frames/elapsed,
                        detector_samples_per_wall_second=len(observations)/elapsed,
                        observations=observations, raw_positive_samples=len(raw_alerts),
                        notifications_after_10s_cooldown=notifications, episodes=builder.episodes,
                        metrics=episode_metrics(expected,builder.episodes)))
                finally:
                    capture.release()
            del detector
        if report['model_sha256'] != sha(args.model) or report['world_sha256'] != sha(YOLO_WORLD_MODEL):
            raise ValueError('Model changed during experiment')
        for clip in report['clips']:
            if clip['status']=='ready' and clip['sha256'] != sha(args.manifest.parent/clip['file']):
                raise ValueError('Video changed during experiment')
        report['status'] = 'partial' if len(ready)!=len(manifest['clips']) else 'evaluated'
    else:
        report['status'] = 'missing_video_or_labels'
    if report['manifest_sha256'] != sha(args.manifest):
        raise ValueError('Manifest changed during experiment')
    if code_hashes != {name:sha(ROOT/name) for name in code_files}:
        raise ValueError('Experiment code changed during evaluation')
    report['code_sha256'] = code_hashes
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temp = args.output.with_suffix('.tmp')
    temp.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    temp.replace(args.output)
    print(json.dumps(dict(status=report['status'],ready_clips=len(ready),runs=len(report['runs']),output=str(args.output)),ensure_ascii=False))


if __name__ == '__main__':
    main()
