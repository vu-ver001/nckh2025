"""Isolated phone ablation, with explicit detector selection and no pose scoring."""
import math
from detection_labels import is_phone_label
from temporal import PhoneTracker

VARIANTS = ('world', 'phone', 'combined', 'temporal')


class PhoneExperimentDetector:
    def __init__(self, variant, model_path, *, allowed_filter=False):
        from ultralytics import YOLO
        from yolo_detector import YOLODetector
        from config import YOLO_WORLD_MODEL, YOLO_WORLD_CHEAT_CLASSES, YOLO_WORLD_ALLOWED_CLASSES
        if variant not in VARIANTS:
            raise ValueError(f'Invalid variant: {variant}')
        if allowed_filter and variant not in ('combined', 'temporal'):
            raise ValueError('Allowed-filter experiment is separate from the four-way ablation')
        self.variant, self.allowed_filter = variant, allowed_filter
        self.core = YOLODetector.__new__(YOLODetector)
        self.core.inference_options = dict(device='cpu', imgsz=640)
        self.core.phone_confirm_model = None
        if variant != 'phone':
            self.core.world_model = YOLO(YOLO_WORLD_MODEL)
            self.core.world_model.set_classes(YOLO_WORLD_CHEAT_CLASSES + YOLO_WORLD_ALLOWED_CLASSES)
        if variant != 'world':
            self.core.phone_confirm_model = YOLO(str(model_path))
            if 'phone' not in self.core.phone_confirm_model.names.values():
                raise ValueError('Checkpoint has no phone class')

    def detect(self, frame):
        if self.variant == 'phone':
            detections = self.core._confirm_phones(frame, [], allow_overlap=True)
        else:
            detections = self.core._detect_world(frame, confirm=self.variant != 'world',
                                                filter_allowed=self.allowed_filter)
        return [d for d in detections if d['is_cheat'] and is_phone_label(d['label'])]


class EpisodeBuilder:
    """Consecutive active samples form one episode; a missing sample ends it."""
    def __init__(self, variant, max_gap=.5):
        self.tracker = PhoneTracker() if variant == 'temporal' else None
        self.max_gap = max_gap
        self.episodes = []
        self.current = None
        self.last = None

    def update(self, phones, timestamp):
        if not math.isfinite(timestamp) or (self.last is not None and timestamp <= self.last):
            raise ValueError('Episode samples require increasing timestamps')
        if self.last is not None and timestamp - self.last > self.max_gap:
            self.current = None
        self.last = timestamp
        active = bool(self.tracker.update(list(enumerate(d['bbox'] for d in phones)), timestamp)) if self.tracker else bool(phones)
        if active:
            if self.current is None:
                self.current = dict(type='PHONE_DETECTED', start=timestamp, end=timestamp)
                self.episodes.append(self.current)
            else:
                self.current['end'] = timestamp
        else:
            self.current = None
        return active


def validate_events(events):
    if not isinstance(events, list):
        raise ValueError('Events must be a reviewed list')
    for i, event in enumerate(events):
        if not isinstance(event.get('type'), str) or not all(math.isfinite(event[k]) for k in ('start', 'end')) or not 0 <= event['start'] < event['end']:
            raise ValueError('Invalid event interval')
        if any(other['type'] == event['type'] and max(other['start'], event['start']) <= min(other['end'], event['end']) for other in events[:i]):
            raise ValueError('Merge overlapping/touching same-type events before evaluation')


def episode_metrics(expected, predicted):
    """One-to-one matching by first alarm onset within labeled interval (inclusive).

    A prediction starting before ground truth is false even if it later overlaps.
    Fragmented/repeated episodes cannot create extra TP for the same true event.
    """
    validate_events(expected)
    used, matches, false = set(), [], []
    for pi, prediction in sorted(enumerate(predicted), key=lambda item: item[1]['start']):
        candidates = [i for i, event in enumerate(expected) if i not in used and
            event['type'] == prediction['type'] and event['start'] <= prediction['start'] <= event['end']]
        if candidates:
            gi = min(candidates, key=lambda i: expected[i]['start'])
            used.add(gi)
            matches.append(dict(prediction=pi, ground_truth=gi,
                                latency_seconds=prediction['start'] - expected[gi]['start']))
        else:
            false.append(pi)
    tp, fp, fn = len(matches), len(false), len(expected)-len(matches)
    return dict(tp=tp, fp=fp, fn=fn, expected_events=len(expected),
        precision=tp/(tp+fp) if tp+fp else 0, recall=tp/(tp+fn) if tp+fn else 0,
        f1=2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else 0,
        matches=matches, false_episode_indices=false,
        missed_event_indices=[i for i in range(len(expected)) if i not in used])
