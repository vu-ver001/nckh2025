import sys
from pathlib import Path
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from audit_dataset import audit_dataset
from prepare_corrected_dataset import box_row


class DatasetAuditTests(unittest.TestCase):
    def test_polygon_conversion_preserves_phone_class(self):
        self.assertEqual(box_row('1 0.2 0.3 0.6 0.3 0.6 0.9'),
                         '1 0.40000000 0.60000000 0.40000000 0.60000000')
    def make_dataset(self, root, train='0 0.5 0.5 0.2 0.2', val='0 0.5 0.5 0.2 0.2'):
        for split, label in [('train', train), ('val', val)]:
            (root / 'images' / split).mkdir(parents=True)
            (root / 'labels' / split).mkdir(parents=True)
            (root / 'images' / split / 'image.jpg').write_bytes(split.encode())
            (root / 'labels' / split / 'image.txt').write_text(label)

    def test_unknown_class_blocks_evaluation_without_rewriting(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            label = '1 0.5 0.5 0.2 0.2'
            self.make_dataset(root, val=label)
            result = audit_dataset(root)
            self.assertFalse(result['ready_for_evaluation'])
            self.assertEqual(result['splits']['val']['affected_images'], 1)
            self.assertEqual((root / 'labels/val/image.txt').read_text(), label)

    def test_clean_dataset_passes_and_duplicate_split_blocks(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.make_dataset(root)
            self.assertTrue(audit_dataset(root)['ready_for_evaluation'])
            (root / 'images/val/image.jpg').write_bytes(b'train')
            self.assertFalse(audit_dataset(root)['ready_for_evaluation'])

    def test_invalid_coordinate_detected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.make_dataset(root, val='0 1.5 0.5 0.2 0.2')
            self.assertEqual(audit_dataset(root)['splits']['val']['issues'][0]['reason'],
                             'coordinate_out_of_range')
