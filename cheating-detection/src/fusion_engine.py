# ============================================================
# fusion_engine.py - Kết hợp kết quả YOLO + MediaPipe
# Rule-based scoring system để đưa ra cảnh báo tổng hợp
# ============================================================

import time
import math
from temporal import PhoneTracker
from detection_labels import is_phone_label
from config import (
    SCORE_WEIGHTS, ALERT_SCORE_LOW, ALERT_SCORE_MEDIUM, ALERT_SCORE_HIGH,
    SCORE_DECAY_FRAMES, PHONE_PERSIST_FRAMES,
    HAND_EAR_HOLD_SECONDS, HAND_EAR_REPEAT_WINDOW_SECONDS,
    HAND_EAR_REPEAT_COUNT,
)


def _boxes_overlap(box_a, box_b, iou_threshold: float = 0.3) -> bool:
    """Kiểm tra 2 bbox (x1,y1,x2,y2) có chồng lấn đáng kể không."""
    xa = max(box_a[0], box_b[0])
    ya = max(box_a[1], box_b[1])
    xb = min(box_a[2], box_b[2])
    yb = min(box_a[3], box_b[3])
    inter = max(0, xb - xa) * max(0, yb - ya)
    if inter == 0:
        return False
    area_a = max(1, (box_a[2] - box_a[0]) * (box_a[3] - box_a[1]))
    area_b = max(1, (box_b[2] - box_b[0]) * (box_b[3] - box_b[1]))
    return inter / (area_a + area_b - inter) >= iou_threshold


class AlertEvent:
    """Đại diện cho một sự kiện cảnh báo đơn lẻ."""
    def __init__(self, event_type: str, detail: str, score: int, level: str):
        self.event_type = event_type
        self.detail = detail
        self.score = score
        self.level = level
        self.timestamp = time.time()


class FusionEngine:
    """
    Kết hợp output từ YOLO và MediaPipe để tính điểm rủi ro
    và phân loại mức độ cảnh báo.

    Scoring system:
    
    - Mỗi loại sự kiện có điểm (weight) riêng
    - Tổng điểm quyết định mức cảnh báo: LOW / MEDIUM / HIGH / CRITICAL
    - Điểm tự giảm dần theo thời gian nếu không có sự kiện mới
    """

    def __init__(self):
        self.current_score = 0
        self.active_events: list[AlertEvent] = []
        self._frame_count = 0
        self._last_decay_frame = 0
        self._consecutive_clean_frames = 0
        # Temporal persistence cho phone (giảm false positive chập chờn)
        self._phone_tracks = []
        self._timed_phone = PhoneTracker()
        self._source_time = None
        self._last_scored = {}
        self._last_evidence = None
        self._decayed_units = 0

    def update(self, yolo_detections: list[dict], mp_analysis: dict, *, yolo_fresh: bool = True, timestamp=None) -> dict:
        """
        Cập nhật trạng thái fusion với kết quả detection mới.

        Returns:
        {
          'score': int,
          'level': str ('OK'|'LOW'|'MEDIUM'|'HIGH'|'CRITICAL'),
          'events': list[AlertEvent],
          'should_alert': bool,
        }
        """
        if timestamp is not None:
            if not math.isfinite(timestamp) or (self._source_time is not None and timestamp <= self._source_time):
                raise ValueError('Fusion requires strictly increasing finite source time')
            self._source_time = timestamp
        self._frame_count += 1
        frame_events = []
        frame_score = 0

        # ── Temporal persistence cho PHONE ──────────────────
        # Detection phone phải xuất hiện liên tục (cùng vị trí) qua
        # PHONE_PERSIST_FRAMES lần YOLO mới được tính điểm.
        # False positive thường chập chờn 1-2 frame → bị lọc.
        phone_observations = [
            (index, det["bbox"]) for index, det in enumerate(yolo_detections)
            if det.get("is_cheat", True) and is_phone_label(det["label"])
        ]

        confirmed_indices = set()
        if yolo_fresh and timestamp is not None:
            confirmed_indices = self._timed_phone.update(phone_observations, timestamp)
        elif yolo_fresh:
            # One previous observation can confirm at most one current box.
            # Prefer the closest overlapping centers when multiple boxes overlap.
            pairs = []
            for index, box in phone_observations:
                for previous, (old_box, count) in enumerate(self._phone_tracks):
                    if _boxes_overlap(box, old_box):
                        distance = sum((box[k] + box[k+2] - old_box[k] - old_box[k+2]) ** 2
                                       for k in (0, 1))
                        pairs.append((distance, index, previous))
            matches, used_previous = {}, set()
            for _, index, previous in sorted(pairs):
                if index not in matches and previous not in used_previous:
                    matches[index] = previous
                    used_previous.add(previous)
            tracks = []
            for index, box in phone_observations:
                count = self._phone_tracks[matches[index]][1] + 1 if index in matches else 1
                tracks.append((box, count))
                if count >= PHONE_PERSIST_FRAMES:
                    confirmed_indices.add(index)
            self._phone_tracks = tracks

        # ── Xử lý YOLO detections ─────────────────────────
        for index, det in enumerate(yolo_detections):
            if not yolo_fresh:
                break
            label = det["label"]
            conf = det["confidence"]

            # Bỏ qua vật thể được phép (calculator, pen, v.v.)
            if not det.get("is_cheat", True):
                continue

            # Phân loại label → sự kiện cảnh báo
            if is_phone_label(label):
                if index not in confirmed_indices:
                    continue   # Chưa đủ PHONE_PERSIST_FRAMES liên tục → bỏ qua
                score = SCORE_WEIGHTS["phone_detected"]
                e = AlertEvent("PHONE_DETECTED", f"Phone conf={conf:.1%}", score, "HIGH")
                frame_events.append(e)
                frame_score += score

            elif any(kw in label for kw in ["earphone", "earbud"]):
                # A tiny AirPod-like object is not reliable evidence from this
                # zero-shot detector. Keep the raw box for inspection, but do
                # not turn it into a demo alert.
                continue

            elif any(kw in label for kw in ["book", "cheat_sheet", "cheat sheet", "hidden note"]):
                score = SCORE_WEIGHTS["cheat_sheet_detected"]
                e = AlertEvent("CHEAT_SHEET", f"Document {label} conf={conf:.1%}", score, "MEDIUM")
                frame_events.append(e)
                frame_score += score

        # ── Xử lý MediaPipe analysis ──────────────────────
        if mp_analysis.get("looking_away"):
            score = SCORE_WEIGHTS["looking_away"]
            e = AlertEvent("LOOKING_AWAY", "Head turned sideways", score, "LOW")
            frame_events.append(e)
            frame_score += score

        if mp_analysis.get("head_down"):
            score = SCORE_WEIGHTS["head_down_long"]
            e = AlertEvent("HEAD_DOWN", "Looking down excessively", score, "LOW")
            frame_events.append(e)
            frame_score += score

        hand_near_ear_event = mp_analysis.get("hand_near_ear_event")
        if hand_near_ear_event is None:
            hand_near_ear_event = mp_analysis.get("hand_near_ear")
        if hand_near_ear_event:
            score = SCORE_WEIGHTS["hand_near_ear"]
            duration = float(mp_analysis.get("hand_near_ear_duration") or 0.0)
            episodes = int(mp_analysis.get("hand_near_ear_episodes") or 0)
            if duration >= HAND_EAR_HOLD_SECONDS:
                detail = f"Tay gần vùng tai liên tục {duration:.1f}s; cần kiểm tra"
            elif episodes >= HAND_EAR_REPEAT_COUNT:
                detail = (f"Tay gần vùng tai lặp {episodes} lần trong "
                          f"{HAND_EAR_REPEAT_WINDOW_SECONDS:.0f}s; cần kiểm tra")
            else:
                detail = "Tay gần vùng tai; cần kiểm tra"
            e = AlertEvent("HAND_NEAR_EAR", detail, score, "LOW")
            frame_events.append(e)
            frame_score += score

        if mp_analysis.get("hand_suspicious"):
            score = SCORE_WEIGHTS["hand_suspicious"]
            e = AlertEvent("HAND_SUSPICIOUS", "Hand in suspicious position", score, "LOW")
            frame_events.append(e)
            frame_score += score

        # ── Score accumulation with decay ─────────────────
        if timestamp is not None:
            # Add each event type at most once per source second. Cached phone
            # results never refresh evidence. This score is still heuristic.
            frame_score = 0
            for event in frame_events:
                if timestamp - self._last_scored.get(event.event_type, float('-inf')) >= 1 - 1e-9:
                    frame_score += event.score
                    self._last_scored[event.event_type] = timestamp
                event.source_seconds = timestamp
            if frame_events:
                self.current_score += frame_score
                self._last_evidence = timestamp
                self._decayed_units = 0
            elif self._last_evidence is not None:
                units = max(0, math.floor(timestamp - self._last_evidence + 1e-9))
                self.current_score = max(0, self.current_score - max(0, units - self._decayed_units))
                self._decayed_units = units
        elif frame_events:
            self.current_score += frame_score
            self._consecutive_clean_frames = 0
        else:
            self._consecutive_clean_frames += 1
            # Decay score after SCORE_DECAY_FRAMES clean frames
            if self._consecutive_clean_frames >= SCORE_DECAY_FRAMES:
                self.current_score = max(0, self.current_score - 1)

        # Cap score to prevent runaway accumulation
        self.current_score = min(self.current_score, 30)
        self.active_events = frame_events

        # ── Determine alert level ──────────────────────────
        level = self._get_level(self.current_score)

        return {
            "score": self.current_score,
            "level": level,
            "events": frame_events,
            "should_alert": len(frame_events) > 0,
            "frame_score": frame_score,
        }

    def _get_level(self, score: int) -> str:
        if score >= ALERT_SCORE_HIGH * 2:
            return "CRITICAL"
        elif score >= ALERT_SCORE_HIGH:
            return "HIGH"
        elif score >= ALERT_SCORE_MEDIUM:
            return "MEDIUM"
        elif score >= ALERT_SCORE_LOW:
            return "LOW"
        return "OK"

    def reset(self):
        """Reset khi bắt đầu phiên mới."""
        self.__init__()
