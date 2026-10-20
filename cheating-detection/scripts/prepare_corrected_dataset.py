"""Create a separate two-class, boxes-only dataset from the original annotation mapping."""
import argparse
import json
from pathlib import Path
import shutil
import yaml

ROOT = Path(__file__).resolve().parents[1]


def box_row(row):
    values = [float(value) for value in row.split()]
    cls, coords = int(values[0]), values[1:]
    if values[0] != cls or cls not in {0, 1}:
        raise ValueError(f'Unexpected class: {values[0]}')
    if len(coords) == 4:
        box = coords
    elif len(coords) >= 6 and len(coords) % 2 == 0:
        xs, ys = coords[::2], coords[1::2]
        box = [(min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2,
               max(xs) - min(xs), max(ys) - min(ys)]
    else:
        raise ValueError('Invalid box/polygon annotation')
    if not all(0 <= v <= 1 for v in box) or box[2] <= 0 or box[3] <= 0:
        raise ValueError('Invalid normalized box coordinates')
    return f"{cls} " + ' '.join(f'{value:.8f}' for value in box)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-config', type=Path, required=True,
                        help='Original export data.yaml establishing class IDs')
    parser.add_argument('--input', type=Path, default=ROOT / 'dataset/phone_detection')
    parser.add_argument('--output', type=Path, default=ROOT / 'dataset/phone_detection_v2')
    args = parser.parse_args()
    source = yaml.safe_load(args.source_config.read_text(encoding='utf-8-sig'))
    names = source['names']
    names = dict(enumerate(names)) if isinstance(names, list) else names
    if set(names) != {0, 1} or names[1] != 'phone':
        raise SystemExit('Expected verified original mapping: class 1 = phone, two classes.')
    if args.output.exists():
        raise SystemExit('Output exists; choose another --output. Existing data will not be overwritten.')
    # Validate all rows before creating the output.
    prepared = []
    for split in ('train', 'val'):
        for image in sorted((args.input / 'images' / split).iterdir()):
            if image.suffix.lower() not in {'.jpg', '.jpeg', '.png'}:
                continue
            label = args.input / 'labels' / split / f'{image.stem}.txt'
            if not label.exists():
                raise SystemExit(f'Missing label: {label}')
            rows = [box_row(row) for row in label.read_text().splitlines() if row.strip()]
            prepared.append((split, image, rows))
    for split in ('train', 'val'):
        (args.output / 'images' / split).mkdir(parents=True)
        (args.output / 'labels' / split).mkdir(parents=True)
    for split, image, rows in prepared:
        shutil.copy2(image, args.output / 'images' / split / image.name)
        (args.output / 'labels' / split / f'{image.stem}.txt').write_text(
            '\n'.join(rows) + ('\n' if rows else ''), encoding='utf-8')
    config = dict(nc=2, names=names, train='images/train', val='images/val')
    (args.output / 'data.yaml').write_text(yaml.safe_dump(config, allow_unicode=True), encoding='utf-8')
    (args.output / 'provenance.json').write_text(json.dumps(dict(
        source_config=str(args.source_config), class_names=names, images=len(prepared),
        conversion='Preserve both class IDs and original split; convert polygons to enclosing boxes.'),
        indent=2, ensure_ascii=False), encoding='utf-8')
    print(f'Prepared {len(prepared)} images: {args.output}')


if __name__ == '__main__':
    main()
