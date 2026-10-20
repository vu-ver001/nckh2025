"""Exploratory image-level A/B/C comparison; temporal ablation requires real video."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
os.environ.setdefault('YOLO_CONFIG_DIR',str(ROOT/'artifacts'))
from compare_phone_v3 import count_matches
from phone_experiment import PhoneExperimentDetector


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    import cv2
    import ultralytics
    parser=argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    output=parser.parse_args().output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        raise FileExistsError('Preserve previous report; choose another --output')
    parent_path=ROOT/'artifacts/research/phone-comparison.json'
    parent=json.loads(parent_path.read_text())
    checkpoint=ROOT/'models/phone_v3_colab/weights/best.pt'
    world=ROOT/'yolov8s-worldv2.pt'
    inputs=[parent_path,checkpoint,world,Path(__file__),ROOT/'src/phone_experiment.py',ROOT/'src/yolo_detector.py',ROOT/'src/config.py']
    hashes={str(path.relative_to(ROOT)):digest(path) for path in inputs}
    records=next(iter(parent['models'].values()))['per_image']
    manifest={row['image']:row for row in parent['validation_manifest']}
    report=dict(created_at=datetime.now(timezone.utc).isoformat(),inputs_sha256=hashes,
        validation_manifest=parent['validation_manifest'],ultralytics=ultralytics.__version__,
        settings=dict(world_conf=.4,phone_conf=.3,nms_iou=.45,matching_iou=.5,imgsz=640,
                      device='cpu',allowed_filter=False,pose=False),
        limitations=['Same model-selection validation, not independent exam test.',
            'Actual detector pipeline boxes are integer coordinates; counts can differ from raw float-box checkpoint evaluation.',
            'World/phone thresholds retain configured values; confidences are not calibrated across models.',
            'Concurrent work on this computer: no inference speed benchmark is reported.',
            'No temporal model comparison on still images.'],variants={})
    for variant in ('world','phone','combined'):
        detector=PhoneExperimentDetector(variant,checkpoint)
        rows=[]
        for index,row in enumerate(records):
            image=ROOT/'dataset/phone_detection_v3/images/val'/row['image']
            label=ROOT/'dataset/phone_detection_v3/labels/val'/(image.stem+'.txt')
            if digest(image)!=manifest[row['image']]['image_sha256'] or digest(label)!=manifest[row['image']]['label_sha256']:
                raise ValueError('Validation changed')
            detections=detector.detect(cv2.imread(str(image)))
            predictions=[(d['bbox'],d['confidence']) for d in detections]
            tp,fp,fn=count_matches(predictions,row['ground_truth_xyxy'])
            rows.append(dict(image=row['image'],tp=tp,fp=fp,fn=fn,predictions=predictions))
            if (index+1)%50==0:
                print(f'{variant}: {index+1}/{len(records)}',flush=True)
        tp,fp,fn=(sum(row[key] for row in rows) for key in ('tp','fp','fn'))
        report['variants'][variant]=dict(tp=tp,fp=fp,fn=fn,precision=tp/max(1,tp+fp),
            recall=tp/max(1,tp+fn),f1=2*tp/max(1,2*tp+fp+fn),per_image=rows)
        del detector
    if hashes!={str(path.relative_to(ROOT)):digest(path) for path in inputs}:
        raise ValueError('Inputs changed while running')
    temporary=output.with_suffix('.tmp')
    temporary.write_text(json.dumps(report,indent=2),encoding='utf-8')
    temporary.replace(output)
    print(json.dumps({k:{a:b for a,b in v.items() if a!='per_image'} for k,v in report['variants'].items()},indent=2))


if __name__=='__main__':
    main()
