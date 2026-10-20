"""Re-run phone validation into a separate artifact directory, never overwrite training."""
import os
from pathlib import Path
import json
import argparse
from audit_dataset import audit_dataset

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault('YOLO_CONFIG_DIR', str(ROOT / 'artifacts'))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=Path, default=ROOT / 'models/phone_v2/weights/best.pt')
    args = parser.parse_args()
    if not args.model.is_file():
        raise SystemExit('Corrected checkpoint not found. Train phone_v2 first; phone_v1 has invalid label semantics.')
    audit = audit_dataset(ROOT / 'dataset/phone_detection_v2')
    if not audit['ready_for_evaluation']:
        raise SystemExit('Dataset audit failed. Resolve labels before evaluation.')
    from ultralytics import YOLO
    model = YOLO(str(args.model))
    if model.names != audit['names']:
        raise SystemExit('Model class mapping does not match the corrected dataset.')
    metrics = model.val(data=str(ROOT / 'dataset/phone_detection_v2/data.yaml'),
        split='val', imgsz=640, batch=8, workers=0, device='cpu',
        project=str(ROOT / 'artifacts'), name='phone-validation', exist_ok=False)
    per_class = {model.names[int(cls)]: dict(zip(
        ['precision', 'recall', 'map50', 'map50_95'],
        [float(v) for v in metrics.box.class_result(i)]))
        for i, cls in enumerate(metrics.box.ap_class_index)}
    report = dict(dataset='phone_detection_v2/val', model=str(args.model), per_class=per_class,
        speed_ms=metrics.speed, dataset_audit=audit,
        limitation='Phone detection validation only; not end-to-end cheating alert accuracy.')
    output = Path(metrics.save_dir) / 'summary.json'
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    print(output)


if __name__ == '__main__':
    main()
