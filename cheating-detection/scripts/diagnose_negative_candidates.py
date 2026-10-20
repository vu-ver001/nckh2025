"""Find phone-model activations on unreviewed COCO candidates; not false-positive ground truth."""
import csv
import hashlib
import json
import os
from pathlib import Path
import sys
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
os.environ.setdefault('YOLO_CONFIG_DIR',str(ROOT/'artifacts'))


def main():
    from ultralytics import YOLO
    source=ROOT/'dataset/phone_negative_candidates'
    manifest=json.loads((source/'manifest.json').read_text())
    checkpoint=ROOT/'models/phone_v3_colab/weights/best.pt'
    output=ROOT/'artifacts/research/negative-diagnosis'
    output.mkdir(parents=True,exist_ok=True)
    model=YOLO(str(checkpoint))
    records=[]
    for row in manifest['images']:
        path=source/'images'/row['split']/row['file']
        if hashlib.sha256(path.read_bytes()).hexdigest()!=row['sha256']:
            raise ValueError('Candidate image changed')
        result=model(str(path),conf=.3,iou=.45,imgsz=640,device='cpu',verbose=False)[0]
        predictions=[]
        for box in result.boxes:
            if model.names[int(box.cls[0])]=='phone':
                predictions.append(dict(bbox=box.xyxy[0].tolist(),confidence=float(box.conf[0])))
        records.append(dict(**row,predictions=predictions))
    active=[r for r in records if r['predictions']]
    active.sort(key=lambda r:max(p['confidence'] for p in r['predictions']),reverse=True)
    for i,row in enumerate(active[:12],1):
        path=source/'images'/row['split']/row['file']
        with Image.open(path) as original:
            original=original.convert('RGB')
            display=original.copy()
            draw=ImageDraw.Draw(display)
            for pred in row['predictions']:
                draw.rectangle(pred['bbox'],outline='red',width=3)
            display.thumbnail((780,600))
            sheet=Image.new('RGB',(800,950),'white')
            sheet.paste(display,((800-display.width)//2,35))
            pred=row['predictions'][0]
            x1,y1,x2,y2=pred['bbox']
            padding=max(x2-x1,y2-y1)*.25
            crop=original.crop((max(0,x1-padding),max(0,y1-padding),min(original.width,x2+padding),min(original.height,y2+padding)))
            crop.thumbnail((760,280))
            sheet.paste(crop,((800-crop.width)//2,650))
            text=ImageDraw.Draw(sheet)
            text.text((12,10),f"{i:02d} {row['split']}/{row['file']} phone conf={pred['confidence']:.3f}",fill='black')
            text.text((12,625),'Unreviewed candidate: no annotated phone does not prove no phone. Crop below.',fill='black')
            sheet.save(output/f'review-{i:02d}.jpg')
    report=dict(model=str(checkpoint),model_sha256=hashlib.sha256(checkpoint.read_bytes()).hexdigest(),
        source_manifest_sha256=hashlib.sha256((source/'manifest.json').read_bytes()).hexdigest(),
        candidates=len(records),activated_images=len(active),predicted_boxes=sum(len(r['predictions']) for r in records),
        settings=dict(conf=.3,nms=.45,imgsz=640,device='cpu'),
        limitation='Source annotations contain no phone. Human scene review pending; activations are NOT a measured false-positive rate. No training labels created.',
        records=records,review_order=[r['split']+'/'+r['file'] for r in active[:12]])
    (output/'summary.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    review=output/'review.csv'
    if not review.exists():
        with review.open('w',encoding='utf-8-sig',newline='') as stream:
            writer=csv.writer(stream)
            writer.writerow(['split','file','model_boxes','review_status','actual_phone_present','notes'])
            for row in records:
                writer.writerow([row['split'],row['file'],len(row['predictions']),'pending','',''])
    print(json.dumps({k:report[k] for k in ('candidates','activated_images','predicted_boxes')}))


if __name__=='__main__':
    main()
