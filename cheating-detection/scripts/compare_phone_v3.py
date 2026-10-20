"""Compare phone-only detections at fixed confidence .30 / IoU .50 on identical images."""
import json
from pathlib import Path
import os
import argparse
import hashlib
import yaml
import platform
import datetime
import importlib.metadata

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault('YOLO_CONFIG_DIR', str(ROOT / 'artifacts'))


def iou(a, b):
    intersection = max(0, min(a[2], b[2]) - max(a[0], b[0])) * max(0, min(a[3], b[3]) - max(a[1], b[1]))
    union = (a[2]-a[0])*(a[3]-a[1]) + (b[2]-b[0])*(b[3]-b[1]) - intersection
    return intersection / union if union > 0 else 0


def match_predictions(predictions, targets):
    """Confidence-ordered, one-to-one matches; indices refer to original lists."""
    matched = set()
    pairs = []
    for prediction_index, (box, confidence) in sorted(enumerate(predictions), key=lambda item: item[1][1], reverse=True):
        candidates = [(iou(box, gt), i) for i, gt in enumerate(targets) if i not in matched]
        overlap, index = max(candidates, default=(0, -1))
        if overlap >= .5:
            matched.add(index)
            pairs.append((prediction_index, index))
    used = {p for p, _ in pairs}
    return pairs, [p for p in range(len(predictions)) if p not in used], [i for i in range(len(targets)) if i not in matched]


def count_matches(predictions, targets):
    pairs, false_predictions, missed_targets = match_predictions(predictions, targets)
    return len(pairs), len(false_predictions), len(missed_targets)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--models', nargs='+', type=Path, required=True)
    parser.add_argument('--dataset', type=Path, default=ROOT / 'dataset/phone_detection_v3')
    parser.add_argument('--output', type=Path, default=ROOT / 'artifacts/phone-colab-comparison.json')
    args = parser.parse_args(argv)
    from ultralytics import YOLO
    dataset = args.dataset.resolve()
    from audit_dataset import audit_dataset
    assert audit_dataset(dataset)['ready_for_evaluation'], 'Dataset audit failed'
    names = yaml.safe_load((dataset / 'data.yaml').read_text())['names']
    names = dict(enumerate(names)) if isinstance(names, list) else names
    target_id = next(i for i, name in names.items() if name == 'phone')
    images = sorted((dataset / 'images/val').glob('*.jpg'))
    assert images, 'No validation images'
    def data_manifest():
        return [dict(image=path.name, image_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                     label_sha256=hashlib.sha256((dataset / 'labels/val' / (path.stem + '.txt')).read_bytes()).hexdigest())
                for path in images]
    manifest = data_manifest()
    config_sha = hashlib.sha256((dataset / 'data.yaml').read_bytes()).hexdigest()
    report = dict(confidence=.30, iou=.50, images=len(images), models={},
                  dataset=str(dataset), nms_iou=.45,
                  created_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  environment=dict(python=platform.python_version(), platform=platform.platform(),
                      packages={name: importlib.metadata.version(name) for name in ('ultralytics', 'torch', 'numpy')}),
                  imgsz=640, device='cpu', validation_manifest=manifest, dataset_config_sha256=config_sha,
                  evaluator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  limitations='Phone-positive COCO-derived validation; not an independent exam or negative-only benchmark.')
    for checkpoint in args.models:
        checkpoint = checkpoint.resolve()
        assert checkpoint.is_file(), f'Missing checkpoint: {checkpoint}'
        checkpoint_sha = hashlib.sha256(checkpoint.read_bytes()).hexdigest()
        model = YOLO(str(checkpoint))
        class_id = next(i for i, name in model.names.items() if name == 'phone')
        totals = [0, 0, 0]
        per_image = []
        for path in images:
            result = model.predict(str(path), conf=.30, classes=[class_id], imgsz=640,
                                   iou=.45, device='cpu', verbose=False)[0]
            h, w = result.orig_shape
            targets = []
            for line in (dataset / 'labels/val' / (path.stem + '.txt')).read_text().splitlines():
                cls, x, y, bw, bh = map(float, line.split())
                if cls != target_id:
                    continue
                targets.append([(x-bw/2)*w, (y-bh/2)*h, (x+bw/2)*w, (y+bh/2)*h])
            predictions = [(box.xyxy[0].tolist(), float(box.conf[0])) for box in result.boxes]
            counts = count_matches(predictions, targets)
            totals = [a+b for a, b in zip(totals, counts)]
            per_image.append(dict(image=path.name, tp=counts[0], fp=counts[1], fn=counts[2],
                                  ground_truth_xyxy=targets, predictions=predictions))
        assert hashlib.sha256(checkpoint.read_bytes()).hexdigest() == checkpoint_sha, 'Checkpoint changed during evaluation'
        tp, fp, fn = totals
        report['models'][str(checkpoint)] = dict(sha256=checkpoint_sha, phone_class_id=class_id, per_image=per_image,
                                         tp=tp, fp=fp, fn=fn, precision=tp/max(1,tp+fp),
                                         recall=tp/max(1,tp+fn), f1=2*tp/max(1,2*tp+fp+fn))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    assert manifest == data_manifest(), 'Validation data changed during evaluation'
    assert hashlib.sha256((dataset / 'data.yaml').read_bytes()).hexdigest() == config_sha, 'Dataset config changed'
    temporary = args.output.with_suffix('.tmp')
    temporary.write_text(json.dumps(report, indent=2))
    temporary.replace(args.output)
    print(json.dumps({name: {k: v for k, v in result.items() if k != 'per_image'}
                      for name, result in report['models'].items()}, indent=2), flush=True)
    print(f'Reproducible per-image report: {args.output}', flush=True)


if __name__ == '__main__':
    main()
