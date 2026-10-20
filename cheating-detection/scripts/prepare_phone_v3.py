"""Download a pinned CITW research subset; preserve source splits and provenance."""
import concurrent.futures
import hashlib
import json
from pathlib import Path
import random
import time

from PIL import Image
import requests
import yaml
from audit_dataset import audit_dataset

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dataset/phone_detection_v3'
REV = 'f31df211860010059745ba29de06d06f16055c6e'
BASE = f'https://huggingface.co/datasets/ridgerun-ai/citw-v0.1/resolve/{REV}'


def fetch(url, path):
    if path.exists():
        return
    for attempt in range(5):
        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            temp = path.with_suffix(path.suffix + '.part')
            temp.write_bytes(response.content)
            temp.replace(path)
            return
        except requests.RequestException:
            if attempt == 4:
                raise
            time.sleep(2 ** attempt)


def box_row(box, width, height):
    x, y, w, h = box
    if w <= 0 or h <= 0:
        raise ValueError('Non-positive source bbox')
    x1, y1 = max(0, x), max(0, y)
    x2, y2 = min(width, x + w), min(height, y + h)
    if x2 <= x1 or y2 <= y1:
        raise ValueError('Source bbox outside image')
    return f'0 {(x1+x2)/2/width:.8f} {(y1+y2)/2/height:.8f} {(x2-x1)/width:.8f} {(y2-y1)/height:.8f}'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    provenance = OUT / 'provenance'
    provenance.mkdir(exist_ok=True)
    fetch(BASE + '/README.md', provenance / 'SOURCE_README.md')
    manifest = []
    seen_ids, seen_hashes = set(), set()
    for split in ('val', 'train'):
        metadata = provenance / f'{split}.jsonl'
        fetch(BASE + f'/data/{split}/metadata.jsonl', metadata)
        rows = [json.loads(line) for line in metadata.read_text().splitlines()]
        rows.sort(key=lambda row: row['image_id'])
        if split == 'train':
            rows = random.Random(42).sample(rows, min(1600, len(rows)))
        images, labels = OUT / 'images' / split, OUT / 'labels' / split
        images.mkdir(parents=True, exist_ok=True)
        labels.mkdir(parents=True, exist_ok=True)
        def download(row):
            name = row['file_name']
            if Path(name).name != name:
                raise ValueError('Unsafe source filename')
            fetch(BASE + f'/data/{split}/{name}', images / name)
            return row
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            for index, row in enumerate(pool.map(download, rows), 1):
                path = images / row['file_name']
                digest = hashlib.sha256(path.read_bytes()).hexdigest()
                if row['image_id'] in seen_ids or digest in seen_hashes:
                    path.unlink()
                    continue
                seen_ids.add(row['image_id'])
                seen_hashes.add(digest)
                with Image.open(path) as im:
                    im.load()
                    width, height = im.size
                obj = row['objects']
                assert len(obj['bbox']) == len(obj['category']) and set(obj['category']) == {0}
                label_rows = [box_row(box, width, height) for box in obj['bbox']]
                (labels / (path.stem + '.txt')).write_text('\n'.join(label_rows) + '\n')
                manifest.append(dict(split=split, image_id=row['image_id'], file=path.name,
                                     sha256=digest, boxes=len(label_rows)))
                if index % 100 == 0:
                    print(f'{split}: {index}/{len(rows)} downloaded and verified', flush=True)
    (OUT / 'data.yaml').write_text(yaml.safe_dump(dict(train='images/train', val='images/val',
                                                      nc=1, names={0: 'phone'})))
    report = audit_dataset(OUT)
    (provenance / 'manifest.json').write_text(json.dumps(dict(
        source='https://huggingface.co/datasets/ridgerun-ai/citw-v0.1', revision=REV,
        license='CC-BY-NC-2.0 (source dataset card)', seed=42, images=manifest,
        limitations='COCO-derived positives only; no exam-domain or negative-only benchmark. Exact hashes and IDs deduplicated; near-duplicates not certified.'), indent=2))
    (ROOT / 'artifacts/phone-v3-data-audit.json').write_text(json.dumps(report, indent=2))
    assert report['ready_for_evaluation']
    print(json.dumps(report, indent=2), flush=True)


if __name__ == '__main__':
    main()
