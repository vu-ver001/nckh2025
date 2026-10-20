import sys
from pathlib import Path
import unittest
from types import SimpleNamespace
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from phone_experiment import EpisodeBuilder, episode_metrics, validate_events
from yolo_detector import YOLODetector

PHONE = dict(label='cell phone', confidence=.8, bbox=(0,0,100,100), is_cheat=True)


class ExperimentTests(unittest.TestCase):
    def test_duplicate_episode_does_not_inflate_true_positives(self):
        expected = [dict(type='PHONE_DETECTED', start=1,end=5)]
        predictions = [dict(type='PHONE_DETECTED',start=t,end=t+.1) for t in (2,3)]
        result = episode_metrics(expected, predictions)
        self.assertEqual((result['tp'],result['fp'],result['fn']), (1,1,0))

    def test_early_episode_cannot_match_two_later_events(self):
        expected = [dict(type='PHONE_DETECTED',start=1,end=2), dict(type='PHONE_DETECTED',start=3,end=4)]
        result = episode_metrics(expected,[dict(type='PHONE_DETECTED',start=0,end=5)])
        self.assertEqual((result['tp'],result['fp'],result['fn']), (0,1,2))

    def test_temporal_changes_only_confirmation(self):
        plain, timed = EpisodeBuilder('combined'), EpisodeBuilder('temporal')
        for t in (0,.1,.2,.3):
            plain.update([PHONE], t)
            timed.update([PHONE], t)
        self.assertEqual(plain.episodes[0]['start'], 0)
        self.assertEqual(timed.episodes[0]['start'], .2)
        timed.update([], .4)
        self.assertFalse(timed.update([PHONE], .5))

    def test_invalid_ground_truth_rejected(self):
        with self.assertRaises(ValueError):
            validate_events([dict(type='PHONE_DETECTED', start=float('nan'), end=2)])
        with self.assertRaises(ValueError):
            validate_events([dict(type='PHONE_DETECTED', start=1,end=3),dict(type='PHONE_DETECTED',start=2,end=4)])

    def test_phone_only_can_survive_empty_world(self):
        core = YOLODetector.__new__(YOLODetector)
        core.world_model = lambda *a, **kw: [SimpleNamespace(boxes=None)]
        core._confirm_phones = lambda *a, **kw: [PHONE]
        self.assertEqual(core._detect_world(None), [PHONE])
        self.assertEqual(core._detect_world(None,confirm=False), [])

    def test_overlap_veto_is_explicit_experiment_option(self):
        class Model:
            names = {0:'phone'}
            def __call__(self, *args, **kwargs):
                return [SimpleNamespace(boxes=[SimpleNamespace(cls=[0],conf=[.8],xyxy=[[0,0,100,100]])])]
        core = YOLODetector.__new__(YOLODetector)
        core.phone_confirm_model = Model()
        allowed = dict(label='pencil case', confidence=.8, bbox=(0,0,100,100), is_cheat=False)
        self.assertEqual(core._confirm_phones(None,[allowed]), [allowed])
        result = core._confirm_phones(None,[allowed],allow_overlap=True)
        self.assertEqual(len(result),2)
        self.assertEqual(result[1]['source'],'phone_confirm')

    def test_world_duplicates_share_one_canonical_specialist_box(self):
        class Model:
            names = {0: 'phone'}
            def __call__(self, *args, **kwargs):
                return [SimpleNamespace(boxes=[SimpleNamespace(cls=[0], conf=[.7], xyxy=[[40,40,60,60]])])]
        core = YOLODetector.__new__(YOLODetector)
        core.phone_confirm_model = Model()
        other = dict(label='earphone', confidence=.9, bbox=(200,200,220,220), is_cheat=True)
        worlds = [dict(PHONE, bbox=box) for box in ((0,0,100,100),(30,30,70,70),(300,300,320,320))]
        result = core._confirm_phones(None, worlds+[other], allow_overlap=True)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], other)
        self.assertEqual(result[1]['bbox'], (40,40,60,60))
        self.assertEqual(result[1]['confidence'], .7)
        self.assertTrue(result[1]['world_supported'])

    def test_world_phone_without_specialist_evidence_is_removed(self):
        core = YOLODetector.__new__(YOLODetector)
        core.phone_confirm_model = lambda *a, **kw: [SimpleNamespace(boxes=None)]
        self.assertEqual(core._confirm_phones(None, [PHONE]), [])

    def test_allowed_veto_also_applies_to_world_supported_phone(self):
        class Model:
            names = {0:'phone'}
            def __call__(self, *args, **kwargs):
                return [SimpleNamespace(boxes=[SimpleNamespace(cls=[0],conf=[.8],xyxy=[[0,0,100,100]])])]
        core = YOLODetector.__new__(YOLODetector)
        core.phone_confirm_model = Model()
        allowed = dict(label='book',confidence=.8,bbox=(0,0,100,100),is_cheat=False)
        self.assertEqual(core._confirm_phones(None,[allowed, PHONE]), [allowed])
