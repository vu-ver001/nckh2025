"""Train only the corrected dataset; preserve legacy checkpoints for audit."""
import argparse
import os
from pathlib import Path
import sys
import datetime
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
os.environ.setdefault('YOLO_CONFIG_DIR', str(ROOT / 'artifacts'))
from audit_dataset import audit_dataset


def write_status(status, **details):
    output = ROOT / 'artifacts' / 'phone-v2-pipeline.json'
    output.parent.mkdir(exist_ok=True)
    data = dict(status=status, updated_at=datetime.datetime.now().isoformat(),
                output_model=str(ROOT / 'models/phone_v2/weights/best.pt'), **details)
    temporary = output.with_suffix('.tmp')
    temporary.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
    temporary.replace(output)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--epochs', type=int, default=80)
    parser.add_argument('--device', default='cpu')
    parser.add_argument('--batch', type=int, default=8)
    args = parser.parse_args()
    dataset = ROOT / 'dataset/phone_detection_v2'
    if not dataset.exists():
        raise SystemExit('Run scripts/prepare_corrected_dataset.py first.')
    audit = audit_dataset(dataset)
    if not audit['ready_for_evaluation'] or audit['names'].get(1) != 'phone':
        raise SystemExit('Dataset must pass audit with original class 1 = phone.')
    if (ROOT / 'models/phone_v2').exists():
        raise SystemExit('models/phone_v2 exists. Preserve it; explicitly choose a new run before retraining.')
    if args.epochs <= 0 or args.batch <= 0:
        parser.error('epochs and batch must be positive')
    from ultralytics import YOLO
    model = YOLO(str(ROOT / 'yolov8n.pt'))
    write_status('training', epochs_requested=args.epochs, device=args.device)
    try:
        model.train(data=str(dataset / 'data.yaml'), epochs=args.epochs, batch=args.batch,
            imgsz=640, device=args.device, workers=0, seed=42,
            project=str(ROOT / 'models'), name='phone_v2', exist_ok=False, patience=20)
        write_status('evaluating', epochs_requested=args.epochs, device=args.device)
        subprocess.run([sys.executable, str(ROOT / 'scripts/evaluate_phone.py')], check=True)
        write_status('complete', epochs_requested=args.epochs, device=args.device,
                     note='Training and validation finished; checkpoint is not activated for alerts.')
    except BaseException as exc:
        write_status('failed', error=str(exc), error_type=type(exc).__name__)
        raise


if __name__ == '__main__':
    main()
