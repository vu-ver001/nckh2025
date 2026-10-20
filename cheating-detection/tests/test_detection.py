import sys
from pathlib import Path
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from fusion_engine import FusionEngine
from config import (PHONE_PERSIST_FRAMES, SCORE_DECAY_FRAMES,
                    YOLO_WORLD_CHEAT_CLASSES, YOLO_WORLD_ALLOWED_CLASSES)
from yolo_detector import _classify_world_label, YOLODetector


def detection(label='cell phone', bbox=(0, 0, 100, 100), **kwargs):
    return dict(label=label, confidence=0.9, bbox=bbox, is_cheat=True, **kwargs)


class DetectionTests(unittest.TestCase):
    def test_invalid_existing_checkpoint_sets_actual_fallback(self):
        with patch('yolo_detector.USE_YOLO_WORLD', True), \
             patch('yolo_detector.os.path.isfile', return_value=True):
            with patch('yolo_detector.YOLO', side_effect=[Mock(), RuntimeError('Invalid checkpoint')]):
                model = YOLODetector()
        self.assertEqual(model.model_status()['status'], 'fallback')
        self.assertEqual(model.model_status()['error'], 'Invalid checkpoint')
        self.assertIsNone(model.model_status()['loaded_phone'])

    def test_book_and_notebook_are_distinct_classes(self):
        for label, category in [('book', 'cheat'), ('notebook', 'allowed'), ('box', 'allowed')]:
            self.assertEqual(_classify_world_label(label, YOLO_WORLD_CHEAT_CLASSES,
                                                 YOLO_WORLD_ALLOWED_CLASSES)[0], category)

    def test_phone_cannot_inherit_another_phones_observations(self):
        engine = FusionEngine()
        a, b = detection(), detection(bbox=(200, 200, 300, 300))
        engine.update([a], {})
        engine.update([a, b], {})
        self.assertFalse(engine.update([b], {})['events'])
        self.assertEqual(len(engine.update([b], {})['events']), 1)

    def test_one_track_cannot_confirm_two_current_phones(self):
        engine = FusionEngine()
        a, b = detection(), detection(bbox=(30, 0, 130, 100))
        engine.update([a], {})
        engine.update([a], {})
        self.assertEqual(len(engine.update([a, b], {})['events']), 1)

    def test_earphone_is_not_phone(self):
        for label in ['earphone', 'wireless earphone', 'earbud']:
            self.assertEqual(_classify_world_label(label, [label], []), ('cheat', 'earphone'))
            result = FusionEngine().update([detection(label)], {})
            self.assertEqual(result['events'], [])

    def test_hand_near_ear_is_a_low_review_event_with_reason(self):
        result = FusionEngine().update([], {
            'hand_near_ear_event': True,
            'hand_near_ear_duration': 2.4,
            'hand_near_ear_episodes': 1,
        }, timestamp=0)
        self.assertEqual([event.event_type for event in result['events']], ['HAND_NEAR_EAR'])
        self.assertEqual(result['events'][0].level, 'LOW')
        self.assertIn('2.4s', result['events'][0].detail)

    def test_phone_requires_fresh_consecutive_observations(self):
        engine = FusionEngine()
        dets = [detection()]
        self.assertFalse(engine.update(dets, {})['events'])
        for _ in range(10):
            self.assertFalse(engine.update(dets, {}, yolo_fresh=False)['events'])
        for _ in range(PHONE_PERSIST_FRAMES - 2):
            self.assertFalse(engine.update(dets, {})['events'])
        self.assertEqual(engine.update(dets, {})['events'][0].event_type, 'PHONE_DETECTED')
        score = engine.current_score
        self.assertEqual(engine.update(dets, {}, yolo_fresh=False)['score'], score)

    def test_missing_phone_resets_confirmation(self):
        engine = FusionEngine()
        engine.update([detection()], {})
        engine.update([], {})
        for _ in range(PHONE_PERSIST_FRAMES - 1):
            self.assertFalse(engine.update([detection()], {})['events'])

    def test_new_position_does_not_inherit_confirmation(self):
        engine = FusionEngine()
        for _ in range(PHONE_PERSIST_FRAMES):
            engine.update([detection()], {})
        self.assertFalse(engine.update([detection(bbox=(200, 200, 300, 300))], {})['events'])

    def test_allowed_object_never_alerts(self):
        det = detection('cell phone')
        det['is_cheat'] = False
        engine = FusionEngine()
        for _ in range(10):
            self.assertEqual(engine.update([det], {})['score'], 0)

    def test_score_decays_and_reset_clears_history(self):
        engine = FusionEngine()
        engine.update([], {'looking_away': True})
        for _ in range(SCORE_DECAY_FRAMES + 30):
            engine.update([], {})
        self.assertEqual(engine.current_score, 0)
        engine.update([detection()], {})
        engine.reset()
        self.assertFalse(engine.update([detection()], {})['events'])

    def test_phone_confirmation_does_not_remove_earphones(self):
        class EmptyResult:
            boxes = None
        detector = YOLODetector.__new__(YOLODetector)
        detector.phone_confirm_model = lambda *args, **kwargs: [EmptyResult()]
        earphone = detection('earphone')
        result = detector._confirm_phones(None, [earphone, detection()])
        self.assertEqual(result, [earphone])

    def test_product_class_is_not_used_to_confirm_phone(self):
        class ProductBox:
            cls = [0]
        class Result:
            boxes = [ProductBox()]
        class Model:
            names = {0: 'ProductRecog', 1: 'phone'}
            def __call__(self, *args, **kwargs):
                return [Result()]
        detector = YOLODetector.__new__(YOLODetector)
        detector.phone_confirm_model = Model()
        self.assertEqual(detector._confirm_phones(None, [detection()]), [])


if __name__ == '__main__':
    unittest.main()
