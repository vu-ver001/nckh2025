import sys
from pathlib import Path
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from evaluate_demo_videos import event_metrics


class VideoMetricsTests(unittest.TestCase):
    def test_counts_missed_false_and_first_detection_delay(self):
        expected = [dict(type='PHONE_DETECTED', start=5, end=10),
                    dict(type='PHONE_DETECTED', start=20, end=25)]
        alerts = [dict(type='PHONE_DETECTED', video_seconds=t) for t in (2, 7, 8)]
        result = event_metrics(expected, alerts)
        self.assertEqual(result['detected_events'], 1)
        self.assertEqual(result['missed_events'], 1)
        self.assertEqual(result['false_alerts'], 1)
        self.assertEqual(result['latency_video_seconds'], [2])

    def test_negative_scene_flags_behavior_alerts(self):
        result = event_metrics([], [dict(type='HEAD_DOWN', video_seconds=1)])
        self.assertEqual(result['false_alerts'], 1)
