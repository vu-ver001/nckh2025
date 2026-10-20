"""Isolated real-model integration check; never activates the default dashboard model."""
import json
import os
from pathlib import Path
import sys
import time
import argparse
import yaml

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--model', type=Path, required=True)
parser.add_argument('--dataset', type=Path, default=ROOT / 'dataset/phone_detection_v3')
args = parser.parse_args()
assert args.model.is_file(), 'Missing checkpoint'
OUTPUT = ROOT / 'artifacts' / f'phone-colab-check-{time.time_ns()}'
OUTPUT.mkdir(parents=True)
os.environ['YOLO_CONFIG_DIR'] = str(ROOT / 'artifacts')
os.environ['EXAMGUARD_PHONE_CONFIRM_MODEL'] = str(args.model.resolve())
os.environ['EXAMGUARD_VIDEO_SOURCE'] = str(OUTPUT / 'input.avi')
os.environ['EXAMGUARD_LOG_DIR'] = str(OUTPUT / 'logs')
os.environ['EXAMGUARD_SNAPSHOT_DIR'] = str(OUTPUT / 'snapshots')
sys.path.insert(0, str(ROOT / 'src'))

import cv2
import numpy as np
from fastapi.testclient import TestClient
import fastapi_server as server
from yolo_detector import _compute_iou
from detection_labels import is_phone_label


def main():
    detector, analyzer = server.create_components()
    assert detector.phone_confirm_model is not None
    assert 'phone' in detector.phone_confirm_model.names.values()
    dataset = args.dataset.resolve()
    names = yaml.safe_load((dataset / 'data.yaml').read_text())['names']
    names = dict(enumerate(names)) if isinstance(names, list) else names
    phone_id = next(i for i, name in names.items() if name == 'phone')
    selected = None
    candidates = 0
    for label in sorted((dataset / 'labels/val').glob('*.txt')):
        rows = [list(map(float, line.split())) for line in label.read_text().splitlines() if line.strip()]
        phones = [row for row in rows if row[0] == phone_id]
        if not phones:
            continue
        candidates += 1
        image = dataset / 'images/val' / f'{label.stem}.jpg'
        frame = cv2.imread(str(image))
        if frame is None:
            continue
        frame = cv2.resize(frame, (640, 480))
        boxes = [((x-w/2)*640, (y-h/2)*480, (x+w/2)*640, (y+h/2)*480)
                 for _, x, y, w, h in phones]
        detections = detector.detect(frame)
        if any(is_phone_label(d['label']) and d['is_cheat'] and
               any(_compute_iou(d['bbox'], b) >= 0.3 for b in boxes) for d in detections):
            selected = image
            break
    if selected is None:
        raise RuntimeError('No labeled phone fixture survived the complete detector. Review confirmation/filtering.')
    writer = cv2.VideoWriter(str(OUTPUT / 'input.avi'), cv2.VideoWriter_fourcc(*'MJPG'), 10, (640, 480))
    assert writer.isOpened()
    for _ in range(24):
        writer.write(frame)
    writer.release()
    # Reuse actual models already loaded; no fabricated detections or behavior outputs.
    server.create_components = lambda: (detector, analyzer)
    with TestClient(server.app) as client:
        with client.websocket_connect('/ws/alerts') as ws:
            assert ws.receive_json()['heartbeat']
            client.post('/start').raise_for_status()
            video = client.get('/video_feed')
            video.raise_for_status()
            server.state.worker.join(30)
            assert not server.state.worker.is_alive()
            assert server.state.error is None, server.state.error
            # Once decoding has ended all expected alerts have been sent.
            messages = []
            for _ in range(40):
                message = ws.receive_json()
                messages.append(message)
                if message.get('type') == 'PHONE_DETECTED':
                    break
                if message.get('heartbeat') and message.get('status') in {'stopped', 'error'}:
                    break
            phone_alert = next((m for m in messages if m.get('type') == 'PHONE_DETECTED'), None)
            assert phone_alert, 'No PHONE_DETECTED event from real model pipeline'
            snapshot = client.get(phone_alert['image'])
            assert snapshot.status_code == 200
            assert cv2.imdecode(np.frombuffer(snapshot.content, np.uint8), cv2.IMREAD_COLOR) is not None
            start, end = video.content.find(b'\xff\xd8'), video.content.find(b'\xff\xd9')
            assert start >= 0 and end > start
            decoded = cv2.imdecode(np.frombuffer(video.content[start:end+2], np.uint8), cv2.IMREAD_COLOR)
            assert decoded is not None
            status = client.post('/stop').json()
            assert status['status'] == 'stopped' and status['fps'] == 0
    report = dict(result='passed', model=os.environ['EXAMGUARD_PHONE_CONFIRM_MODEL'],
                  class_names=detector.phone_confirm_model.names, pose=analyzer.model_status(), source_image=str(selected),
                  candidates_checked=candidates, frames=24, decoded_shape=list(decoded.shape),
                  phone_alert=phone_alert, snapshot_http_status=snapshot.status_code,
                  final_status=status, activated_in_default_dashboard=False,
                  limitation='Selected repeated validation image. Technical integration only; not independent accuracy or false-alarm evaluation.')
    (OUTPUT / 'summary.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    print(OUTPUT / 'summary.json')


if __name__ == '__main__':
    main()
