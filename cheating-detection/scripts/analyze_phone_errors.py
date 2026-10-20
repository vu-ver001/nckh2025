"""Diagnose saved validation detections and render review sheets without retraining."""
import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from compare_phone_v3 import iou, match_predictions

ROOT = Path(__file__).resolve().parents[1]


def size_bin(box, width, height):
    fraction = (box[2]-box[0])*(box[3]-box[1])/(width*height)
    return '<0.25%' if fraction < .0025 else '0.25%-1%' if fraction < .01 else '>=1%'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=Path, default=ROOT / 'artifacts/research/phone-comparison.json')
    parser.add_argument('--output', type=Path, default=ROOT / 'artifacts/research/error-analysis')
    args = parser.parse_args()
    source = args.input.read_bytes()
    report = json.loads(source)
    assert report['confidence'] == .3 and report['iou'] == .5, 'This diagnosis uses conf .30 and IoU .50'
    checkpoint, model = next((k, v) for k, v in report['models'].items() if Path(k).parent.parent.name == 'phone_v3_colab')
    hashes = {r['image']: r['image_sha256'] for r in report['validation_manifest']}
    folder = Path(report['dataset']) / 'images/val'
    bins = {k: Counter(gt=0, detected=0, missed=0) for k in ('<0.25%', '0.25%-1%', '>=1%')}
    missed_reasons, fp_reasons = Counter(), Counter()
    errors = []
    args.output.mkdir(parents=True, exist_ok=True)
    for row in model['per_image']:
        image_path = folder / row['image']
        assert hashlib.sha256(image_path.read_bytes()).hexdigest() == hashes[row['image']], 'Image changed'
        with Image.open(image_path) as im:
            width, height = im.size
        pairs, fp, fn = match_predictions(row['predictions'], row['ground_truth_xyxy'])
        assert (len(pairs), len(fp), len(fn)) == (row['tp'], row['fp'], row['fn']), 'Matching semantics changed'
        for index, box in enumerate(row['ground_truth_xyxy']):
            item = bins[size_bin(box, width, height)]
            item['gt'] += 1
            item['missed' if index in fn else 'detected'] += 1
        for index in fn:
            overlap = max((iou(row['ground_truth_xyxy'][index], b) for b, _ in row['predictions']), default=0)
            missed_reasons['no_nearby_prediction_at_conf_030' if overlap < .1 else
                           'localization_iou_010_to_050' if overlap < .5 else 'one_to_one_matching_conflict'] += 1
        for index in fp:
            overlap = max((iou(row['predictions'][index][0], b) for b in row['ground_truth_xyxy']), default=0)
            fp_reasons['no_nearby_ground_truth' if overlap < .1 else
                       'localization_iou_010_to_050' if overlap < .5 else 'duplicate_or_matching_conflict'] += 1
        if fp or fn:
            errors.append(dict(image=row['image'], tp=row['tp'], fp=row['fp'], fn=row['fn'],
                               predictions=row['predictions'], ground_truth_xyxy=row['ground_truth_xyxy'],
                               unmatched_predictions=fp, unmatched_targets=fn))
    for values in bins.values():
        values['recall'] = values['detected']/values['gt'] if values['gt'] else None
    selected = sorted(errors, key=lambda r: (-(r['fp']+r['fn']), r['image']))[:12]
    font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 18)
    small = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 14)
    for number, row in enumerate(selected, 1):
        with Image.open(folder / row['image']) as im:
            original = im.convert('RGB')
        annotated = original.copy()
        draw = ImageDraw.Draw(annotated)
        for index, box in enumerate(row['ground_truth_xyxy']):
            color = '#eab308' if index in row['unmatched_targets'] else '#16a34a'
            draw.rectangle(box, outline=color, width=3)
        for index, (box, confidence) in enumerate(row['predictions']):
            color = '#ef4444' if index in row['unmatched_predictions'] else '#06b6d4'
            draw.rectangle(box, outline=color, width=2)
            draw.text((box[0], max(0, box[1]-16)), f'{confidence:.2f}', fill=color, font=small)
        sheet = Image.new('RGB', (1200, 700), 'white')
        draw = ImageDraw.Draw(sheet)
        draw.text((15, 10), f"{number:02d}  {row['image']}  TP={row['tp']} FP={row['fp']} FN={row['fn']}", font=font, fill='black')
        draw.text((15, 40), 'GT: green=matched / yellow=missed. Prediction: cyan=matched / red=unmatched.', font=small, fill='black')
        annotated.thumbnail((780, 610))
        sheet.paste(annotated, (15, 75))
        crops = [('Missed GT', row['ground_truth_xyxy'][i]) for i in row['unmatched_targets']]
        crops += [('Unmatched prediction', row['predictions'][i][0]) for i in row['unmatched_predictions']]
        for n, (label, box) in enumerate(crops[:2]):
            padding = max(20, (box[2]-box[0])*.75, (box[3]-box[1])*.75)
            bounds = (max(0, int(box[0]-padding)), max(0, int(box[1]-padding)),
                      min(original.width, int(box[2]+padding)), min(original.height, int(box[3]+padding)))
            crop = original.crop(bounds)
            crop.thumbnail((380, 260))
            # Enlarge small crops for human review; leave originals unchanged.
            ratio = min(380/crop.width, 260/crop.height)
            crop = crop.resize((round(crop.width*ratio), round(crop.height*ratio)))
            draw.text((810, 80+n*300), label, font=font, fill='black')
            sheet.paste(crop, (810, 110+n*300))
        sheet.save(args.output / f'review-{number:02d}.png')
    fields = ['image', 'tp', 'fp', 'fn', 'human_review', 'confirmed_cause', 'suggested_action']
    # Never overwrite annotations a reviewer may already have entered.
    if not (args.output / 'review-queue.csv').exists():
        with (args.output / 'review-queue.csv').open('w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(dict(image=r['image'], tp=r['tp'], fp=r['fp'], fn=r['fn'], human_review='pending') for r in selected)
    summary = dict(checkpoint=checkpoint, input_sha256=hashlib.sha256(source).hexdigest(),
                   size_definition='GT bbox area / original image area. Diagnostic bins, not COCO small/medium/large categories.',
                   by_size=bins, unmatched_ground_truth=missed_reasons, unmatched_predictions=fp_reasons,
                   images_with_errors=len(errors), total_images=len(model['per_image']),
                   selected_images=[r['image'] for r in selected],
                   limitations='Geometric diagnosis at conf .30/IoU .50, not confirmed semantic causes. An unmatched prediction may be an unlabeled true phone. Review sheets are selected worst cases, not a representative random sample.')
    (args.output / 'summary.json').write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
