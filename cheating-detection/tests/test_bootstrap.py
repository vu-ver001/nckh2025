import sys
from pathlib import Path
import unittest
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from bootstrap_phone_comparison import paired_bootstrap, scores


def model(counts):
    return dict(per_image=[dict(image=str(i), tp=tp, fp=fp, fn=fn)
                          for i, (tp, fp, fn) in enumerate(counts)])


class BootstrapTests(unittest.TestCase):
    def test_micro_scores_use_pooled_counts(self):
        np.testing.assert_allclose(scores([2, 1, 2]), [2/3, 1/2, 4/7])
        np.testing.assert_array_equal(scores([0, 0, 0]), [0, 0, 0])

    def test_identical_models_have_exactly_zero_paired_difference(self):
        a = model([(1, 3, 0), (2, 0, 2), (0, 1, 1)])
        result = paired_bootstrap({'a': a, 'b': a}, repeats=100)
        for row in result['differences'][0]['metrics'].values():
            self.assertEqual(row, dict(estimate=0, low=0, high=0))

    def test_pair_order_and_ground_truth_must_agree(self):
        a = model([(1, 0, 0), (0, 1, 2)])
        b = model([(1, 0, 0), (0, 1, 2)])
        b['per_image'].reverse()
        with self.assertRaises(ValueError):
            paired_bootstrap({'a': a, 'b': b})
        with self.assertRaises(ValueError):
            paired_bootstrap({'a': a, 'b': model([(1, 0, 0), (0, 1, 3)])})

    def test_perfect_candidate_vs_missed_baseline(self):
        result = paired_bootstrap({'a': model([(0, 0, 1)]*4), 'b': model([(1, 0, 0)]*4)})
        self.assertEqual(result['differences'][0]['metrics']['recall'], dict(estimate=1, low=1, high=1))
