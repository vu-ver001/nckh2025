"""Prepare COCO images without annotated phones as review candidates, not training data."""
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import random
import zipfile
from PIL import Image, ImageDraw
from prepare_phone_v3 import fetch

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dataset/phone_negative_candidates'
TARGETS = {'book', 'remote', 'laptop', 'mouse', 'bottle', 'backpack'}


def select_candidates(data, limit):
    names = {c['id']: c['name'] for c in data['categories']}
    categories = defaultdict(set)
    for annotation in data['annotations']:
        categories[annotation['image_id']].add(names[annotation['category_id']])
    # Exclude annotated phones including crowd annotations. Keep source split.
    rows = [im for im in data['images'] if 'cell phone' not in categories[im['id']]
            and categories[im['id']] & TARGETS and im.get('license')]
    rows.sort(key=lambda im: im['id'])
    return random.Random(42).sample(rows, min(limit, len(rows))), categories


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    archive = ROOT / 'artifacts/coco-annotations-trainval2017.zip'
    provenance = dict(source='http://images.cocodataset.org/annotations/annotations_trainval2017.zip',
                      annotation_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),
                      purpose='Candidate negatives for manual review and false-detection diagnosis; not approved training labels.',
                      seed=42, images=[])
    seen = set()
    with zipfile.ZipFile(archive) as z:
        for split, limit in [('val', 80), ('train', 200)]:
            data = json.loads(z.read(f'annotations/instances_{split}2017.json'))
            rows, categories = select_candidates(data, limit)
            licenses = {lic['id']: lic for lic in data['licenses']}
            folder = OUT / 'images' / split
            folder.mkdir(parents=True, exist_ok=True)
            def download(row):
                assert Path(row['file_name']).name == row['file_name']
                path = folder / row['file_name']
                fetch(row['coco_url'], path)
                with Image.open(path) as image:
                    image.load()
                return row, hashlib.sha256(path.read_bytes()).hexdigest()
            with ThreadPoolExecutor(max_workers=8) as pool:
                for index, (row, digest) in enumerate(pool.map(download, rows), 1):
                    assert digest not in seen, 'Duplicate candidate across source splits'
                    seen.add(digest)
                    provenance['images'].append(dict(file=row['file_name'], split=split,
                        image_id=row['id'], sha256=digest, source_url=row['coco_url'],
                        flickr_url=row.get('flickr_url'), license=licenses[row['license']],
                        annotated_classes=sorted(categories[row['id']]), review='pending'))
                    if index % 20 == 0:
                        print(f'{split}: {index}/{len(rows)} verified', flush=True)
    (OUT / 'manifest.json').write_text(json.dumps(provenance, indent=2))
    for split in ('train', 'val'):
        files = sorted((OUT / 'images' / split).glob('*.jpg'))
        for page in range((len(files) + 19) // 20):
            sheet = Image.new('RGB', (1200, 1050), 'white')
            for n, path in enumerate(files[page*20:(page+1)*20]):
                with Image.open(path) as im:
                    im = im.convert('RGB')
                    im.thumbnail((300, 185))
                    x, y = (n % 4)*300, (n // 4)*210
                    sheet.paste(im, (x, y))
                    ImageDraw.Draw(sheet).text((x, y+187), path.name, fill='black')
            sheet.save(OUT / f'review-{split}-{page+1}.jpg')
    print('Candidate manifest and review contact sheets ready; no training labels created.', flush=True)


if __name__ == '__main__':
    main()
