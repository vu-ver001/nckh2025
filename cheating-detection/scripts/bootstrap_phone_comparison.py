"""Exploratory paired image-level percentile bootstrap of micro P/R/F1."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
METRICS = ('precision', 'recall', 'f1')


def scores(counts):
    counts = np.asarray(counts, dtype=float)
    tp, fp, fn = np.moveaxis(counts, -1, 0)
    numerators = np.stack([tp, tp, 2*tp], axis=-1)
    denominators = np.stack([tp+fp, tp+fn, 2*tp+fp+fn], axis=-1)
    return np.divide(numerators, denominators, out=np.zeros_like(numerators), where=denominators != 0)


def paired_bootstrap(models, repeats=2000, seed=42):
    if len(models) < 2 or repeats < 1:
        raise ValueError('Need at least two models and positive resampling count')
    ids = None
    arrays = []
    for name, result in models.items():
        rows = result['per_image']
        current = [row['image'] for row in rows]
        if not current or len(set(current)) != len(current):
            raise ValueError('Empty or repeated image IDs')
        if ids is not None and ids != current:
            raise ValueError('Models must use identical image order')
        ids = current
        array = np.array([[row[k] for k in ('tp', 'fp', 'fn')] for row in rows], dtype=float)
        if not np.isfinite(array).all() or (array < 0).any() or (array != np.floor(array)).any():
            raise ValueError('Counts must be finite non-negative integers')
        if arrays and not np.array_equal(array[:, 0] + array[:, 2], arrays[0][:, 0] + arrays[0][:, 2]):
            raise ValueError('Ground-truth counts differ between models')
        arrays.append(array)
    # Whole images are resampled, preserving all boxes and both model outcomes together.
    indices = np.random.default_rng(seed).integers(0, len(ids), size=(repeats, len(ids)))
    samples = np.stack([scores(array[indices].sum(axis=1)) for array in arrays])
    points = np.stack([scores(array.sum(axis=0)) for array in arrays])
    def describe(point, distribution):
        bounds = np.quantile(distribution, [.025, .975], axis=0)
        return {metric: dict(estimate=float(point[i]), low=float(bounds[0, i]), high=float(bounds[1, i]))
                for i, metric in enumerate(METRICS)}
    names = list(models)
    return dict(method='paired image-level percentile bootstrap', confidence_level=.95,
                resamples=repeats, seed=seed, image_count=len(ids),
                zero_denominator='score=0, same convention as comparison evaluator',
                models={name: describe(points[i], samples[i]) for i, name in enumerate(names)},
                differences=[dict(baseline=names[0], candidate=name,
                    metrics=describe(points[i]-points[0], samples[i]-samples[0])) for i, name in enumerate(names[1:], 1)],
                limitations='Exploratory conditional variability on these validation images; assumes images are independent. Does not include training-seed variability, label error, unknown scene clustering, or exam-domain shift.')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=ROOT / 'artifacts/research/phone-bootstrap.json')
    args = parser.parse_args()
    source = args.input.read_bytes()
    result = paired_bootstrap(json.loads(source)['models'])
    result.update(input=str(args.input.resolve()), input_sha256=hashlib.sha256(source).hexdigest())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
