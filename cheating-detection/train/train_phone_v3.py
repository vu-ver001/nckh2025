"""Bounded CPU run followed by validation and same-set checkpoint comparison."""
import datetime
import argparse
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
os.environ.setdefault('YOLO_CONFIG_DIR', str(ROOT / 'artifacts'))
from audit_dataset import audit_dataset


def status(state, **fields):
    path = ROOT / 'artifacts/phone-v3-pipeline.json'
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(dict(status=state, updated_at=datetime.datetime.now().isoformat(),
                                   epochs_requested=40, device='cpu', **fields), indent=2))
    temp.replace(path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--resume', action='store_true', help='Continue this interrupted run from last.pt')
    args = parser.parse_args()
    from ultralytics import YOLO
    import torch
    torch.set_num_threads(6)
    dataset = ROOT / 'dataset/phone_detection_v3'
    assert audit_dataset(dataset)['ready_for_evaluation']
    if args.resume:
        assert (ROOT / 'models/phone_v3/weights/last.pt').exists(), 'No checkpoint to resume'
    else:
        assert not (ROOT / 'models/phone_v3').exists(), 'Preserve existing run'
    try:
        status('training')
        model = YOLO(str(ROOT / ('models/phone_v3/weights/last.pt' if args.resume else 'yolov8n.pt')))
        model.add_callback('on_train_epoch_end', lambda trainer: status(
            'training', epoch_completed=trainer.epoch + 1))
        if args.resume:
            model.train(resume=True, device='cpu', workers=0)
        else:
            model.train(data=str(dataset / 'data.yaml'), epochs=40, patience=10,
                    imgsz=640, batch=8, workers=0, device='cpu', seed=42,
                    project=str(ROOT / 'models'), name='phone_v3', exist_ok=False)
        status('evaluating')
        best = YOLO(str(ROOT / 'models/phone_v3/weights/best.pt'))
        metrics = best.val(data=str(dataset / 'data.yaml'), imgsz=640, batch=8,
                           device='cpu', workers=0, project=str(ROOT / 'artifacts'),
                           name='phone-v3-validation')
        result = dict(precision=float(metrics.box.mp), recall=float(metrics.box.mr),
                      map50=float(metrics.box.map50), map50_95=float(metrics.box.map),
                      speed_ms=metrics.speed)
        (ROOT / 'artifacts/phone-v3-validation-summary.json').write_text(json.dumps(result, indent=2))
        from compare_phone_v3 import main as compare
        compare(['--models', str(ROOT / 'models/phone_v2/weights/best.pt'),
                 str(ROOT / 'models/phone_v3/weights/best.pt'),
                 '--output', str(ROOT / 'artifacts/phone-v3-comparison.json')])
        status('complete', metrics=result, activated=False,
               note='Validation and same-set comparison completed. Independent exam videos still required.')
    except BaseException as exc:
        status('failed', error=str(exc))
        raise


if __name__ == '__main__':
    main()
