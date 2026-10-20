import sys
from pathlib import Path
from types import SimpleNamespace
import unittest
import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from mediapipe_analyzer import MediaPipeAnalyzer
from config import HEAD_TURN_FRAMES_NEEDED, HEAD_DOWN_FRAMES_NEEDED


class PoseLogicTests(unittest.TestCase):
    def setUp(self):
        self.analyzer = MediaPipeAnalyzer.__new__(MediaPipeAnalyzer)
        self.analyzer._head_turn_counter = 0
        self.analyzer._head_down_counter = 0
        self.frame = np.zeros((100, 100, 3), dtype=np.uint8)

    def analyze(self, data):
        self.analyzer.pose_model = lambda *a, **kw: [SimpleNamespace(
            keypoints=SimpleNamespace(data=torch.tensor(data, dtype=torch.float32)))]
        return self.analyzer.analyze(self.frame)

    def test_unobserved_eyes_do_not_establish_head_turn(self):
        for _ in range(HEAD_TURN_FRAMES_NEEDED + 2):
            output = self.analyze(np.zeros((1, 17, 3)))
            self.assertFalse(output['looking_away'])

    def test_lost_person_resets_behavior_history(self):
        self.analyzer._head_turn_counter = HEAD_TURN_FRAMES_NEEDED
        self.analyzer._head_down_counter = HEAD_DOWN_FRAMES_NEEDED
        self.analyze(np.zeros((0, 17, 3)))
        self.assertEqual(self.analyzer._head_turn_counter, 0)
        self.assertEqual(self.analyzer._head_down_counter, 0)

    def test_missing_shoulder_cannot_extend_head_down(self):
        self.analyzer._head_down_counter = HEAD_DOWN_FRAMES_NEEDED
        data = np.zeros((1, 17, 3))
        data[0, 0] = [80, 45, 1]
        data[0, 1] = [40, 40, 1]
        data[0, 2] = [60, 40, 1]
        self.assertFalse(self.analyze(data)['head_down'])

    def test_visible_head_turn_still_detected(self):
        data = np.zeros((1, 17, 3))
        data[0, 0] = [80, 45, 1]
        data[0, 1] = [40, 40, 1]
        data[0, 2] = [60, 40, 1]
        for _ in range(HEAD_TURN_FRAMES_NEEDED):
            result = self.analyze(data)
        self.assertTrue(result['looking_away'])

    def test_hand_near_ear_requires_temporal_hold(self):
        data = np.zeros((1, 17, 3))
        data[0, 0] = [50, 45, 1]
        data[0, 1] = [45, 40, 1]
        data[0, 2] = [55, 40, 1]
        data[0, 3] = [40, 45, 1]
        data[0, 4] = [60, 45, 1]
        data[0, 5] = [30, 60, 1]
        data[0, 6] = [70, 60, 1]
        hand = [(41 / 100, 46 / 100, 1)]
        normalized = data[0] / [100, 100, 1]
        output = dict(looking_away=False, head_down=False, hand_near_ear=False,
                      hand_near_ear_event=False, hand_suspicious=False)
        self.assertFalse(self.analyzer.analyze_keypoints(normalized, output,
                                                         timestamp=0, hand_points=hand)['hand_near_ear'])
        for timestamp in (.5, 1.0, 1.5):
            output = dict(looking_away=False, head_down=False, hand_near_ear=False,
                          hand_near_ear_event=False, hand_suspicious=False)
            result = self.analyzer.analyze_keypoints(normalized, output,
                                                     timestamp=timestamp, hand_points=hand)
        output = dict(looking_away=False, head_down=False, hand_near_ear=False,
                      hand_near_ear_event=False, hand_suspicious=False)
        result = self.analyzer.analyze_keypoints(normalized, output,
                                                 timestamp=2.0, hand_points=hand)
        self.assertTrue(result['hand_near_ear'])
        self.assertTrue(result['hand_near_ear_event'])
