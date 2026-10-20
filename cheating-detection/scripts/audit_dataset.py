"""Read-only YOLO dataset audit. Never infer class mappings or rewrite labels."""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]


def audit_dataset(dataset):
    config_path = dataset / 'data.yaml'
    config = yaml.safe_load(config_path.read_text(encoding='utf-8-sig')) if config_path.exists() else {'names': {0: 'phone'}}
    names = config['names']
    names = dict(enumerate(names)) if isinstance(names, list) else names
    report = {'dataset': str(dataset), 'names': names, 'splits': {}, 'cross_split_duplicates': []}
    hashes = {}
    for split in ('train', 'val'):
        images = sorted(p for p in (dataset / 'images' / split).iterdir()
                        if p.suffix.lower() in {'.jpg', '.jpeg', '.png'})
        issues, classes, formats = [], Counter(), Counter()
        empty_labels = 0
        for image in images:
            digest = hashlib.sha256(image.read_bytes()).hexdigest()
            if split == 'val' and digest in hashes:
                report['cross_split_duplicates'].append([hashes[digest], str(image)])
            if split == 'train':
                hashes[digest] = str(image)
            label = dataset / 'labels' / split / f'{image.stem}.txt'
            if not label.exists():
                issues.append({'image': image.name, 'reason': 'missing_label'})
                continue
            rows = label.read_text(encoding='utf-8-sig').splitlines()
            if not any(row.strip() for row in rows):
                empty_labels += 1
            for line_number, row in enumerate(rows, 1):
                if not row.strip():
                    continue
                reason = None
                try:
                    values = [float(value) for value in row.split()]
                    cls = values[0]
                    classes[str(cls)] += 1
                    if not all(math.isfinite(value) for value in values):
                        reason = 'non_finite_value'
                    elif cls != int(cls) or int(cls) not in names:
                        reason = 'class_not_in_config'
                    elif len(values) != 5 and not (len(values) >= 7 and len(values) % 2 == 1):
                        reason = 'invalid_row_length'
                    elif any(value < 0 or value > 1 for value in values[1:]):
                        reason = 'coordinate_out_of_range'
                    elif len(values) == 5 and (values[3] <= 0 or values[4] <= 0):
                        reason = 'non_positive_box_size'
                    formats['box' if len(values) == 5 else 'polygon'] += 1
                except (ValueError, IndexError):
                    reason = 'invalid_number'
                if reason:
                    issues.append({'image': image.name, 'label': str(label),
                                   'line': line_number, 'reason': reason})
        report['splits'][split] = dict(images=len(images), empty_labels=empty_labels,
            class_rows=dict(classes), formats=dict(formats), issues=issues,
            affected_images=len({issue['image'] for issue in issues}))
    report['ready_for_evaluation'] = not report['cross_split_duplicates'] and all(
        not item['issues'] and len(item['formats']) <= 1 for item in report['splits'].values())
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', type=Path, default=ROOT / 'dataset/phone_detection')
    parser.add_argument('--output', type=Path, default=ROOT / 'artifacts/dataset-audit.json')
    args = parser.parse_args()
    report = audit_dataset(args.dataset)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    for split, item in report['splits'].items():
        print(f"{split}: {item['images']} images; {item['affected_images']} with label issues; formats={item['formats']}")
    print(f"Cross-split duplicate pairs: {len(report['cross_split_duplicates'])}")
    print(f"Audit: {args.output}")
    return 0 if report['ready_for_evaluation'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
