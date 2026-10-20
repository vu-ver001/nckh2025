"""Real asset inference on existing validation images; technical smoke check only."""
from pathlib import Path
import sys
import json
import hashlib
import time
import cv2
import numpy as np
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from mediapipe_tasks_analyzer import MediaPipeTasksAnalyzer


def main():
    output = ROOT/'artifacts/mediapipe-check'
    output.mkdir(exist_ok=True)
    records = []
    analyzer = MediaPipeTasksAnalyzer()
    try:
        blank = analyzer.analyze(np.zeros((480,640,3), dtype=np.uint8), timestamp=0)
        assert not any(blank[k] for k in ('head_down','looking_away','hand_near_ear','hand_suspicious'))
        paths = sorted((ROOT/'dataset/phone_detection_v3/images/val').glob('*.jpg'))[:25]
        for i, path in enumerate(paths):
            frame = cv2.imread(str(path))
            started = time.perf_counter()
            result = analyzer.analyze(frame, timestamp=i+1.)
            poses = result['mp_pose_result'].pose_landmarks
            hands = result['hand_result'].hand_landmarks
            record = dict(image=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                pose_landmarks=[len(p) for p in poses], hand_landmarks=[len(h) for h in hands],
                processing_seconds=time.perf_counter()-started)
            records.append(record)
            if poses and hands:
                image_path = output/'pose-hands-overlay.jpg'
                assert cv2.imwrite(str(image_path), analyzer.draw(frame.copy(), result))
                record['overlay'] = str(image_path)
                break
        assert any(r['pose_landmarks'] for r in records), 'No actual pose output'
        assert any(r['hand_landmarks'] for r in records), 'No actual hand output'
        report = dict(result='passed', backend=analyzer.model_status(), records=records,
            limitation='Selected validation images, not independent behavior recognition evaluation.')
        (output/'summary.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
        print(output/'summary.json')
    finally:
        analyzer.close()


if __name__ == '__main__':
    main()
