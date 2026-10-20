"""Download official task assets, preserving bytes and provenance. Never trains."""
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
MODELS = {
    'pose_landmarker_lite.task': 'https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/latest/pose_landmarker_lite.task',
    'hand_landmarker.task': 'https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task',
}


def main():
    directory = ROOT / 'models/mediapipe'
    directory.mkdir(parents=True, exist_ok=True)
    manifest_path = directory / 'provenance.json'
    previous = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    assets = {}
    for name, url in MODELS.items():
        path = directory / name
        if not path.exists():
            with urlopen(url, timeout=60) as response:
                data = response.read()
            if len(data) < 100000 or data[:2] != b'\x00\x00' and b'PK' not in data[:8]:
                raise ValueError(f'Unexpected task bundle: {name}')
            temp = path.with_suffix('.part')
            temp.write_bytes(data)
            temp.replace(path)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if name in previous.get('assets', {}) and previous['assets'][name]['sha256'] != digest:
            raise ValueError(f'Existing model checksum changed: {path}')
        assets[name] = dict(url=url, sha256=digest, bytes=path.stat().st_size)
    manifest_path.write_text(json.dumps(dict(checked_at=datetime.now(timezone.utc).isoformat(),
        source='Official Google MediaPipe model bundles; latest URL bytes pinned by SHA256 below',
        assets=assets), indent=2), encoding='utf-8')
    print(manifest_path)


if __name__ == '__main__':
    main()
