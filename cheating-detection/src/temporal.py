"""Source-time primitives shared by live processing and offline experiments."""
import math
import time
from collections import deque


class SourceClock:
    def __init__(self, fps, *, live=False):
        self.live = live
        self.fps = float(fps)
        if not live and (not math.isfinite(self.fps) or self.fps <= 0):
            raise ValueError('Video needs a valid source FPS')
        self.origin = time.monotonic()
        self.last = None
        self.fallbacks = 0

    def timestamp(self, frame_index, position_ms=None):
        if self.live:
            value = time.monotonic() - self.origin
        else:
            value = float(position_ms) / 1000 if position_ms is not None else float('nan')
            if not math.isfinite(value) or value < 0 or (self.last is not None and value <= self.last):
                # Explicit CFR fallback when a decoder does not expose valid PTS.
                value = frame_index / self.fps
                if self.last is not None:
                    value = max(value, self.last + 1 / self.fps)
                self.fallbacks += 1
        self.last = value
        return value


class SampleGate:
    def __init__(self, interval=.1):
        if interval <= 0:
            raise ValueError('Sampling interval must be positive')
        self.interval = interval
        self.next_time = 0.0

    def due(self, timestamp):
        if timestamp + 1e-9 < self.next_time:
            return False
        self.next_time = (math.floor((timestamp + 1e-9) / self.interval) + 1) * self.interval
        return True


class HoldTimer:
    def __init__(self, duration, max_gap=.5):
        self.duration, self.max_gap = duration, max_gap
        self.start = self.last = None

    def update(self, active, timestamp):
        if not math.isfinite(timestamp) or (self.last is not None and timestamp <= self.last):
            raise ValueError('Observations require strictly increasing finite source time')
        gap = self.last is not None and timestamp - self.last > self.max_gap
        self.last = timestamp
        if not active:
            self.start = None
            return False
        if self.start is None or gap:
            self.start = timestamp
        return timestamp - self.start + 1e-9 >= self.duration


class GestureEpisodeTracker:
    """Track a sustained gesture and short repeated episodes on source time."""

    def __init__(self, duration=2.0, max_gap=.5, repeat_window=20.0,
                 repeat_count=3, min_episode=.35):
        self.duration = float(duration)
        self.max_gap = float(max_gap)
        self.repeat_window = float(repeat_window)
        self.repeat_count = int(repeat_count)
        self.min_episode = float(min_episode)
        self.start = None
        self.last = None
        self.triggered = False
        self._current_recorded = False
        self._repeat_triggered = False
        self._episodes = deque()

    def _prune(self, timestamp):
        while self._episodes and timestamp - self._episodes[0] > self.repeat_window:
            self._episodes.popleft()

    def update(self, active, timestamp):
        if not math.isfinite(timestamp) or (self.last is not None and timestamp <= self.last):
            raise ValueError('Gesture observations require strictly increasing finite source time')

        gap = self.last is not None and timestamp - self.last > self.max_gap
        self.last = timestamp
        event = False
        repeated_event = False

        if active:
            if self.start is None or gap:
                self.start = timestamp
                self.triggered = False
                self._current_recorded = False
            duration = timestamp - self.start
            if duration + 1e-9 >= self.duration and not self.triggered:
                self.triggered = True
                self._episodes.append(timestamp)
                self._current_recorded = True
                event = True
        else:
            if self.start is not None:
                duration = timestamp - self.start
                if duration + 1e-9 >= self.min_episode and not self._current_recorded:
                    self._episodes.append(timestamp)
            self.start = None
            self.triggered = False
            self._current_recorded = False
            duration = 0.0

        self._prune(timestamp)
        if len(self._episodes) < self.repeat_count:
            self._repeat_triggered = False
        elif event:
            self._repeat_triggered = True
        elif not self._repeat_triggered and not event:
            repeated_event = True
            self._repeat_triggered = True
        return dict(active=bool(active), duration=max(0.0, duration),
                    event=event or repeated_event,
                    sustained_event=event, repeated_event=repeated_event,
                    episodes=len(self._episodes))


class PhoneTracker:
    """One-to-one spatial association; not person identity tracking."""
    def __init__(self, duration=.2, max_gap=.5, min_observations=3):
        self.duration, self.max_gap = duration, max_gap
        self.min_observations = min_observations
        self.tracks = []
        self.last = None

    def update(self, observations, timestamp):
        from fusion_engine import _boxes_overlap
        if not math.isfinite(timestamp) or (self.last is not None and timestamp <= self.last):
            raise ValueError('Phone observations require strictly increasing source time')
        if self.last is not None and timestamp - self.last > self.max_gap:
            self.tracks = []
        self.last = timestamp
        pairs = []
        for index, box in observations:
            for previous, (old_box, start, count) in enumerate(self.tracks):
                if _boxes_overlap(box, old_box):
                    distance = sum((box[k] + box[k+2] - old_box[k] - old_box[k+2]) ** 2 for k in (0, 1))
                    pairs.append((distance, index, previous))
        matches, used = {}, set()
        for _, index, previous in sorted(pairs):
            if index not in matches and previous not in used:
                matches[index] = previous
                used.add(previous)
        tracks, confirmed = [], set()
        for index, box in observations:
            start, count = (self.tracks[matches[index]][1], self.tracks[matches[index]][2] + 1) if index in matches else (timestamp, 1)
            tracks.append((box, start, count))
            if count >= self.min_observations and timestamp - start + 1e-9 >= self.duration:
                confirmed.add(index)
        self.tracks = tracks
        return confirmed
