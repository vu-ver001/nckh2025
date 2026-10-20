import sys
from pathlib import Path
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from prepare_phone_v3 import box_row
from compare_phone_v3 import count_matches, match_predictions
from analyze_phone_errors import size_bin


class PhoneV3Tests(unittest.TestCase):
    def test_matching_reports_original_prediction_indices(self):
        pairs, fp, fn = match_predictions([([0,0,10,10], .4), ([0,0,10,10], .9)],
                                         [[0,0,10,10], [20,20,30,30]])
        self.assertEqual(pairs, [(1, 0)])
        self.assertEqual(fp, [0])
        self.assertEqual(fn, [1])

    def test_size_bins_are_relative_to_image_area(self):
        self.assertEqual(size_bin([0,0,4,4], 100, 100), '<0.25%')
        self.assertEqual(size_bin([0,0,5,5], 100, 100), '0.25%-1%')
        self.assertEqual(size_bin([0,0,10,10], 100, 100), '>=1%')
    def test_clips_partial_box_to_image(self):
        values = list(map(float, box_row([-10, 20, 30, 20], 100, 100).split()))
        self.assertEqual(values, [0, .1, .3, .2, .2])

    def test_rejects_box_outside_image(self):
        with self.assertRaises(ValueError):
            box_row([110, 0, 10, 10], 100, 100)

    def test_duplicate_predictions_cannot_match_same_phone(self):
        self.assertEqual(count_matches([([0,0,10,10], .9), ([0,0,10,10], .8)],
                                       [[0,0,10,10], [20,20,30,30]]), (1,1,1))
