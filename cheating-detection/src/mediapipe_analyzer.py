# ============================================================
# mediapipe_analyzer.py - Pose & Hands Analyzer
# Legacy class name; this implementation explicitly uses YOLOv8-Pose.
# ============================================================

import cv2
import numpy as np
from ultralytics import YOLO
from temporal import GestureEpisodeTracker, HoldTimer

from config import (
    YOLO_POSE_MODEL,
    HEAD_TURN_RATIO_THRESHOLD, HEAD_TURN_FRAMES_NEEDED,
    HEAD_DOWN_RATIO_THRESHOLD, HEAD_DOWN_FRAMES_NEEDED,
    HAND_EAR_DISTANCE_THRESHOLD, HAND_EAR_SHOULDER_RATIO_THRESHOLD,
    HAND_EAR_HOLD_SECONDS, HAND_EAR_MAX_GAP_SECONDS,
    HAND_EAR_REPEAT_WINDOW_SECONDS, HAND_EAR_REPEAT_COUNT,
    HAND_EAR_MIN_EPISODE_SECONDS,
    COLOR_WARN, COLOR_ALERT,
)

# ── YOLOv8-Pose Keypoint Indices ───────────────────────────
# 0=nose, 1=L eye, 2=R eye, 3=L ear, 4=R ear
# 5=L shoulder, 6=R shoulder
# 7=L elbow, 8=R elbow
# 9=L wrist, 10=R wrist
# 11=L hip, 12=R hip
KP_NOSE    = 0
KP_L_EYE  = 1
KP_R_EYE  = 2
KP_L_EAR  = 3
KP_R_EAR  = 4
KP_L_SHLDR = 5
KP_R_SHLDR = 6
KP_L_WRIST = 9
KP_R_WRIST = 10
KP_L_HIP   = 11
KP_R_HIP   = 12


class MediaPipeAnalyzer:
    """
    Phân tích tư thế và cử chỉ bằng YOLOv8-Pose.
    Thay thế MediaPipe Pose bằng YOLO (không cần model download thêm).
    """

    def __init__(self):
        print("[PoseAnalyzer] Loading YOLOv8-Pose model...")
        self.pose_model = YOLO(YOLO_POSE_MODEL)

        # Frame counters
        self._head_turn_counter = 0
        self._head_down_counter = 0
        self._hand_ear_tracker = None
        print("[PoseAnalyzer] Ready.")

    def _get_kp(self, kps: np.ndarray, idx: int):
        """
        Lấy keypoint tại index idx.
        kps shape: (N_kp, 3) → [x_norm, y_norm, confidence]
        Trả về (x, y, conf) normalized 0-1.
        """
        if idx >= len(kps):
            return (0.0, 0.0, 0.0)
        return float(kps[idx][0]), float(kps[idx][1]), float(kps[idx][2])

    def model_status(self):
        return dict(backend='YOLO-Pose', status='loaded', model=YOLO_POSE_MODEL, error=None)

    def analyze(self, frame: np.ndarray, *, timestamp=None) -> dict:
        """
        Phân tích 1 frame bằng YOLOv8-Pose.
        Trả về dict kết quả tương thích với fusion_engine.
        """
        h, w = frame.shape[:2]

        output = {
            "looking_away":    False,
            "head_down":       False,
            "hand_near_ear":   False,
            "hand_near_ear_event": False,
            "hand_near_ear_duration": 0.0,
            "hand_near_ear_episodes": 0,
            "hand_near_ear_distance": None,
            "hand_suspicious": False,
            "pose_result":     None,   # raw YOLO result
            "hand_result":     None,
            "head_turn_score": 0.0,
        }

        # Chạy YOLO Pose
        results = self.pose_model(frame, verbose=False)
        output["pose_result"] = results

        if results[0].keypoints is None or len(results[0].keypoints.data) == 0:
            self._head_turn_counter = 0
            self._head_down_counter = 0
            if timestamp is not None:
                self._apply_timers(output, False, False, timestamp)
                self._set_hand_ear_output(output, False, timestamp, None)
            return output

        # Lấy person đầu tiên (confidence cao nhất)
        kps_raw = results[0].keypoints.data[0]  # shape: (17, 3) [x_px, y_px, conf]

        # Normalize về 0-1
        kps = kps_raw.cpu().numpy().copy()
        kps[:, 0] /= w
        kps[:, 1] /= h

        return self.analyze_keypoints(kps, output, timestamp=timestamp)

    def _apply_timers(self, output, turned, down, timestamp):
        if not hasattr(self, '_turn_timer'):
            self._turn_timer = HoldTimer(8 / 30)
            self._down_timer = HoldTimer(12 / 30)
        output['looking_away'] = self._turn_timer.update(turned, timestamp)
        output['head_down'] = self._down_timer.update(down, timestamp)

    def _set_hand_ear_output(self, output, active, timestamp, distance):
        output['hand_near_ear_distance'] = distance
        if timestamp is None:
            output['hand_near_ear'] = bool(active)
            output['hand_near_ear_event'] = bool(active)
            return
        if getattr(self, '_hand_ear_tracker', None) is None:
            self._hand_ear_tracker = GestureEpisodeTracker(
                duration=HAND_EAR_HOLD_SECONDS,
                max_gap=HAND_EAR_MAX_GAP_SECONDS,
                repeat_window=HAND_EAR_REPEAT_WINDOW_SECONDS,
                repeat_count=HAND_EAR_REPEAT_COUNT,
                min_episode=HAND_EAR_MIN_EPISODE_SECONDS,
            )
        state = self._hand_ear_tracker.update(bool(active), timestamp)
        qualified = state['duration'] + 1e-9 >= HAND_EAR_HOLD_SECONDS
        repeated = state['episodes'] >= HAND_EAR_REPEAT_COUNT
        output['hand_near_ear'] = bool(state['active'] and (qualified or repeated))
        output['hand_near_ear_event'] = bool(state['event'])
        output['hand_near_ear_duration'] = state['duration']
        output['hand_near_ear_episodes'] = state['episodes']

    def analyze_keypoints(self, kps, output, *, timestamp=None, hand_points=None):
        """Shared 17-keypoint rules; duration thresholds are provisional, not calibrated."""
        turned = down = False

        nose_x,   nose_y,   nose_c   = self._get_kp(kps, KP_NOSE)
        l_eye_x,  l_eye_y,  l_eye_c  = self._get_kp(kps, KP_L_EYE)
        r_eye_x,  r_eye_y,  r_eye_c  = self._get_kp(kps, KP_R_EYE)
        l_ear_x,  l_ear_y,  l_ear_c  = self._get_kp(kps, KP_L_EAR)
        r_ear_x,  r_ear_y,  r_ear_c  = self._get_kp(kps, KP_R_EAR)
        l_wr_x,   l_wr_y,   l_wr_c   = self._get_kp(kps, KP_L_WRIST)
        r_wr_x,   r_wr_y,   r_wr_c   = self._get_kp(kps, KP_R_WRIST)
        l_hip_x,  l_hip_y,  l_hip_c  = self._get_kp(kps, KP_L_HIP)
        r_hip_x,  r_hip_y,  r_hip_c  = self._get_kp(kps, KP_R_HIP)
        l_sh_x,   l_sh_y,   l_sh_c   = self._get_kp(kps, KP_L_SHLDR)
        r_sh_x,   r_sh_y,   r_sh_c   = self._get_kp(kps, KP_R_SHLDR)

        # ── Head Turn Detection ────────────────────────────
        if l_eye_c > 0.5 and r_eye_c > 0.5:
            eye_center_x = (l_eye_x + r_eye_x) / 2
            eye_dist = abs(l_eye_x - r_eye_x)
            if eye_dist > 0.01 and nose_c > 0.4:
                turn_ratio = abs(nose_x - eye_center_x) / eye_dist
                output["head_turn_score"] = turn_ratio
                if turn_ratio > HEAD_TURN_RATIO_THRESHOLD:
                    turned = True
                    self._head_turn_counter += 1
                else:
                    self._head_turn_counter = max(0, self._head_turn_counter - 2)
            else:
                self._head_turn_counter = 0
        else:
            # Missing/occluded eyes do not establish head direction.
            self._head_turn_counter = 0

        if self._head_turn_counter >= HEAD_TURN_FRAMES_NEEDED:
            output["looking_away"] = True

        # ── Head Down Detection ────────────────────────────
        if l_eye_c > 0.4 and r_eye_c > 0.4 and nose_c > 0.4 and l_sh_c > 0.4:
            eye_avg_y = (l_eye_y + r_eye_y) / 2
            shoulder_dist = abs(l_sh_y - nose_y) + 1e-5
            if nose_y - eye_avg_y > HEAD_DOWN_RATIO_THRESHOLD * shoulder_dist:
                down = True
                self._head_down_counter += 1
            else:
                self._head_down_counter = max(0, self._head_down_counter - 1)
        else:
            self._head_down_counter = 0

        if self._head_down_counter >= HEAD_DOWN_FRAMES_NEEDED:
            output["head_down"] = True

        if timestamp is not None:
            self._apply_timers(output, turned, down, timestamp)

        # ── Hand Near Ear Detection ────────────────────────
        # Prefer MediaPipe Hands landmarks when available. A wrist alone is
        # too coarse for a small earbud gesture, so fingertips are considered
        # as well. Pose wrists remain a fallback when Hands loses the hand.
        ears = [(l_ear_x, l_ear_y, l_ear_c), (r_ear_x, r_ear_y, r_ear_c)]
        ears = [(x, y, c) for x, y, c in ears if c > 0.4]
        candidates = list(hand_points or [])
        if not candidates:
            candidates = [(l_wr_x, l_wr_y, l_wr_c), (r_wr_x, r_wr_y, r_wr_c)]
        candidates = [(x, y, c) for x, y, c in candidates if c > 0.5]
        nearest_distance = None
        hand_near_ear = False
        if ears and candidates:
            shoulder_width = None
            if l_sh_c > 0.4 and r_sh_c > 0.4:
                shoulder_width = float(np.hypot(l_sh_x - r_sh_x, l_sh_y - r_sh_y))
            for hand_x, hand_y, _ in candidates:
                for ear_x, ear_y, _ in ears:
                    distance = float(np.hypot(hand_x - ear_x, hand_y - ear_y))
                    normalized = distance / shoulder_width if shoulder_width and shoulder_width > 0.03 else None
                    measured = normalized if normalized is not None else distance
                    nearest_distance = measured if nearest_distance is None else min(nearest_distance, measured)
            if nearest_distance is not None:
                threshold = (HAND_EAR_SHOULDER_RATIO_THRESHOLD
                             if shoulder_width and shoulder_width > 0.03
                             else HAND_EAR_DISTANCE_THRESHOLD)
                hand_near_ear = nearest_distance < threshold
        self._set_hand_ear_output(output, hand_near_ear, timestamp, nearest_distance)

        # ── Suspicious Hand Position ───────────────────────
        if l_hip_c > 0.3 and r_hip_c > 0.3:
            hip_avg_y = (l_hip_y + r_hip_y) / 2
            for wr_y, wr_c in [(l_wr_y, l_wr_c), (r_wr_y, r_wr_c)]:
                if wr_c > 0.5 and wr_y > hip_avg_y + 0.15:
                    output["hand_suspicious"] = True

        return output

    def draw(self, frame: np.ndarray, analysis: dict) -> np.ndarray:
        """Vẽ pose skeleton từ YOLO result lên frame."""
        pose_result = analysis.get("pose_result")

        if pose_result is not None and len(pose_result) > 0:
            # Dùng YOLO built-in annotator (vẽ skeleton tự động)
            annotated = pose_result[0].plot(
                boxes=False,     # Không vẽ bounding box người
                labels=False,
                conf=False,
            )
            # Copy skeleton lên frame gốc (blend nhẹ nhàng)
            frame = cv2.addWeighted(frame, 0.7, annotated, 0.3, 0)

        return frame

    def close(self):
        """Cleanup (không cần gì với YOLO)."""
        pass
