"""Real MediaPipe Tasks Pose + Hands, with explicit assets and source timestamps."""
from pathlib import Path
import time
import cv2
import numpy as np
from config import MODEL_DIR
from mediapipe_analyzer import MediaPipeAnalyzer


class MediaPipeTasksAnalyzer(MediaPipeAnalyzer):
    # Convert MediaPipe Pose landmarks to the COCO keypoint order used by rules.
    POSE_MAP = (0, 2, 5, 7, 8, 11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28)
    POSE_EDGES = ((11,12),(11,13),(13,15),(12,14),(14,16),(11,23),(12,24),(23,24),(23,25),(25,27),(24,26),(26,28))
    HAND_EDGES = ((0,1),(1,2),(2,3),(3,4),(0,5),(5,6),(6,7),(7,8),(5,9),(9,10),(10,11),(11,12),(9,13),(13,14),(14,15),(15,16),(13,17),(17,18),(18,19),(19,20),(0,17))

    def __init__(self):
        import mediapipe as mp
        from mediapipe.tasks import python
        from mediapipe.tasks.python import vision
        self.mp = mp
        self.pose_path = Path(MODEL_DIR) / 'mediapipe/pose_landmarker_lite.task'
        self.hand_path = Path(MODEL_DIR) / 'mediapipe/hand_landmarker.task'
        for path in (self.pose_path, self.hand_path):
            if not path.is_file():
                raise FileNotFoundError(f'Missing MediaPipe asset: {path}; run scripts/prepare_mediapipe.py')
        self.pose = vision.PoseLandmarker.create_from_options(vision.PoseLandmarkerOptions(
            base_options=python.BaseOptions(model_asset_path=str(self.pose_path)),
            running_mode=vision.RunningMode.VIDEO, num_poses=1))
        try:
            self.hands = vision.HandLandmarker.create_from_options(vision.HandLandmarkerOptions(
                base_options=python.BaseOptions(model_asset_path=str(self.hand_path)),
                running_mode=vision.RunningMode.VIDEO, num_hands=2))
        except Exception:
            self.pose.close()
            raise
        self._head_turn_counter = self._head_down_counter = 0
        self._last_timestamp_ms = -1
        self._origin = time.monotonic()

    def model_status(self):
        return dict(backend='MediaPipe Pose + Hands', status='loaded',
                    model=str(self.pose_path), hands_model=str(self.hand_path),
                    version=self.mp.__version__, error=None)

    def analyze(self, frame, *, timestamp=None):
        timestamp = time.monotonic() - self._origin if timestamp is None else timestamp
        milliseconds = round(timestamp * 1000)
        if milliseconds <= self._last_timestamp_ms:
            raise ValueError('MediaPipe requires increasing source milliseconds')
        self._last_timestamp_ms = milliseconds
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = self.mp.Image(image_format=self.mp.ImageFormat.SRGB, data=rgb)
        pose = self.pose.detect_for_video(image, milliseconds)
        hands = self.hands.detect_for_video(image, milliseconds)
        output = dict(looking_away=False, head_down=False, hand_near_ear=False,
                      hand_suspicious=False, pose_result=None, hand_result=hands,
                      head_turn_score=0., mp_pose_result=pose)
        points = np.zeros((17, 3))
        if pose.pose_landmarks:
            for i, mp_index in enumerate(self.POSE_MAP):
                landmark = pose.pose_landmarks[0][mp_index]
                points[i] = (landmark.x, landmark.y, min(landmark.visibility or 0, landmark.presence or 0))
        else:
            self._set_hand_ear_output(output, False, timestamp, None)
            return output

        # Hands is used as geometric evidence only; there is no trained
        # AirPods classifier. Wrist and fingertip landmarks make the rule
        # useful when the pose wrist is too far from the ear.
        hand_points = []
        for landmarks in getattr(hands, 'hand_landmarks', None) or []:
            for index in (0, 4, 8, 12, 16, 20):
                if index < len(landmarks):
                    landmark = landmarks[index]
                    hand_points.append((landmark.x, landmark.y, 1.0))
        return self.analyze_keypoints(points, output, timestamp=timestamp,
                                      hand_points=hand_points)

    def draw(self, frame, analysis):
        def draw_landmarks(landmarks, edges, color, visibility=False):
            height, width = frame.shape[:2]
            for a, b in edges:
                first, second = landmarks[a], landmarks[b]
                if visibility and min(first.visibility or 0, second.visibility or 0) < .5:
                    continue
                p1 = (int(first.x * width), int(first.y * height))
                p2 = (int(second.x * width), int(second.y * height))
                cv2.line(frame, p1, p2, color, 2)
        for landmarks in getattr(analysis['mp_pose_result'], 'pose_landmarks', None) or []:
            draw_landmarks(landmarks, self.POSE_EDGES, (0, 220, 0), True)
        for landmarks in getattr(analysis['hand_result'], 'hand_landmarks', None) or []:
            draw_landmarks(landmarks, self.HAND_EDGES, (255, 180, 0))
        return frame

    def close(self):
        self.pose.close()
        self.hands.close()
