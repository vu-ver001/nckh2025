import sys
from pathlib import Path
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from temporal import PhoneTracker, SourceClock, SampleGate, HoldTimer, GestureEpisodeTracker
from fusion_engine import FusionEngine

PHONE = dict(label='cell phone', confidence=.8, bbox=(0, 0, 100, 100), is_cheat=True)


class TemporalTests(unittest.TestCase):
    def test_video_pts_and_explicit_cfr_fallback(self):
        clock = SourceClock(10)
        self.assertEqual(clock.timestamp(0, 0), 0)
        self.assertEqual(clock.timestamp(1, 0), .1)
        self.assertEqual(clock.fallbacks, 1)
        self.assertEqual(clock.timestamp(2, 300), .3)
        with self.assertRaises(ValueError):
            SourceClock(float('nan'))

    def test_sampling_uses_time_not_frame_number(self):
        gate = SampleGate(.1)
        times = [i / 30 for i in range(30)]
        self.assertEqual([round(t, 2) for t in times if gate.due(t)], [i/10 for i in range(10)])

    def test_phone_gap_cannot_inherit_old_confirmation(self):
        tracker = PhoneTracker()
        observations = [(0, PHONE['bbox'])]
        self.assertFalse(tracker.update(observations, 0))
        self.assertFalse(tracker.update(observations, .1))
        self.assertEqual(tracker.update(observations, .2), {0})
        self.assertFalse(tracker.update(observations, 2))
        with self.assertRaises(ValueError):
            tracker.update(observations, 2)

    def test_cached_phone_cannot_confirm_or_raise_score(self):
        engine = FusionEngine()
        engine.update([PHONE], {}, timestamp=0)
        for i in range(1, 20):
            self.assertFalse(engine.update([PHONE], {}, timestamp=i/100, yolo_fresh=False)['events'])
        self.assertFalse(engine.update([PHONE], {}, timestamp=.2)['events'])
        self.assertTrue(engine.update([PHONE], {}, timestamp=.3)['events'])
        score = engine.current_score
        self.assertEqual(engine.update([PHONE], {}, timestamp=.4)['score'], score)

    def test_score_uses_elapsed_time_at_different_sampling_rates(self):
        def run(rate):
            engine = FusionEngine()
            for i in range(rate * 3):
                t = i / rate
                engine.update([], {'looking_away': t < 1}, timestamp=t)
            return engine.update([], {}, timestamp=3)['score']
        self.assertEqual(run(10), run(30))

    def test_hold_resets_on_missing_or_long_gap(self):
        hold = HoldTimer(.2)
        self.assertFalse(hold.update(True, 0))
        self.assertTrue(hold.update(True, .2))
        self.assertFalse(hold.update(True, 2))
        self.assertFalse(hold.update(False, 2.1))
        self.assertFalse(hold.update(True, 2.2))

    def test_gesture_requires_hold_and_emits_once_per_episode(self):
        tracker = GestureEpisodeTracker(duration=2.0)
        self.assertFalse(tracker.update(True, 0)['event'])
        for timestamp in (.5, 1.0, 1.5):
            self.assertFalse(tracker.update(True, timestamp)['event'])
        self.assertTrue(tracker.update(True, 2.0)['event'])
        self.assertFalse(tracker.update(True, 2.1)['event'])
        self.assertFalse(tracker.update(False, 2.2)['event'])
        self.assertFalse(tracker.update(True, 2.3)['event'])

    def test_gesture_repetition_can_trigger_review_cue(self):
        tracker = GestureEpisodeTracker(duration=2.0, min_episode=.2, repeat_count=3)
        for start in (0.0, 1.0):
            tracker.update(True, start)
            tracker.update(False, start + .3)
        tracker.update(True, 2.0)
        result = tracker.update(False, 2.3)
        self.assertTrue(result['repeated_event'])
        self.assertEqual(result['episodes'], 3)

    def test_timed_reset_and_one_to_one_boxes(self):
        tracker = PhoneTracker()
        a = (0, (0,0,100,100))
        b = (1, (30,0,130,100))
        tracker.update([a], 0)
        tracker.update([a], .1)
        self.assertEqual(tracker.update([a,b], .2), {0})
        engine = FusionEngine()
        engine.update([PHONE], {}, timestamp=100)
        engine.reset()
        self.assertFalse(engine.update([PHONE], {}, timestamp=0)['events'])
