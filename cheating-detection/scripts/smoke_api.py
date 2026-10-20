"""Technical integration check against a local backend configured with a test VIDEO file."""
import json
from pathlib import Path
import time
import cv2
import httpx
import numpy as np
from websockets.sync.client import connect

ROOT = Path(__file__).resolve().parents[1]


def main():
    report = {'input': 'Repeated validation image; not an exam recording',
              'mode': 'YOLO-World + YOLO-Pose; untrusted phone_v1 disabled'}
    with httpx.Client(base_url='http://127.0.0.1:8000', timeout=20) as client:
        with connect('ws://127.0.0.1:8000/ws/alerts', open_timeout=10) as ws:
            assert json.loads(ws.recv(timeout=10))['heartbeat']
            try:
                client.post('/start').raise_for_status()
                deadline = time.monotonic() + 45
                report['received_alert_types'] = []
                while time.monotonic() < deadline:
                    data = json.loads(ws.recv(timeout=10))
                    if data.get('error'):
                        raise RuntimeError(data['error'])
                    if data.get('type'):
                        report['received_alert_types'].append(data['type'])
                        break
                assert report['received_alert_types'], 'No alert received on the test fixture'
                report['metrics_samples'] = []
                for _ in range(5):
                    report['metrics_samples'].append(client.get('/status').json())
                    time.sleep(1)
                with client.stream('GET', '/video_feed') as response:
                    response.raise_for_status()
                    raw = b''
                    for chunk in response.iter_bytes():
                        raw += chunk
                        start, end = raw.find(b'\xff\xd8'), raw.find(b'\xff\xd9')
                        if start >= 0 and end > start:
                            break
                    frame = cv2.imdecode(np.frombuffer(raw[start:end+2], dtype=np.uint8), cv2.IMREAD_COLOR)
                    assert frame is not None
                    report['decoded_frame_shape'] = list(frame.shape)
            finally:
                report['stop_response'] = client.post('/stop').json()
            assert report['stop_response']['status'] == 'stopped'
            assert report['stop_response']['fps'] == 0
    output = ROOT / 'artifacts/integration-smoke-current.json'
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    print(output)


if __name__ == '__main__':
    main()
