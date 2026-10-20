# ============================================================
# display_ui.py - Overlay UI Renderer
# Vẽ HUD, thanh trạng thái, cảnh báo lên frame
# ============================================================

import cv2
import numpy as np
import datetime

from config import (
    ALERT_LEVEL_COLORS, COLOR_OK, COLOR_INFO,
    FONT_SCALE, FONT_THICK,
    ALERT_SCORE_LOW, ALERT_SCORE_MEDIUM, ALERT_SCORE_HIGH,
)


class DisplayUI:
    """Render HUD (heads-up display) overlay lên video frame."""

    def __init__(self, frame_width: int, frame_height: int):
        self.W = frame_width
        self.H = frame_height

    def render(self, frame: np.ndarray, fusion_result: dict, fps: float,
               yolo_detections: list, mp_analysis: dict) -> np.ndarray:
        """Render tất cả UI elements lên frame."""
        frame = self._draw_top_bar(frame, fusion_result, fps)
        frame = self._draw_score_bar(frame, fusion_result)
        frame = self._draw_behavior_alerts(frame, mp_analysis)  # Phân bổ vị trí mới
        frame = self._draw_events_panel(frame, fusion_result)
        frame = self._draw_yolo_boxes(frame, yolo_detections)
        frame = self._draw_timestamp(frame)
        return frame

    def _draw_top_bar(self, frame, fusion_result, fps):
        """Thanh trạng thái phía trên."""
        level = fusion_result["level"]
        color = ALERT_LEVEL_COLORS.get(level, COLOR_OK)

        # Background bar
        cv2.rectangle(frame, (0, 0), (self.W, 50), (20, 20, 20), -1)
        cv2.line(frame, (0, 50), (self.W, 50), color, 2)

        # Status text
        status_text = {
            "OK":       "✓ BINH THUONG",
            "LOW":      "! CANH BAO NHE",
            "MEDIUM":   "!! CANH BAO",
            "HIGH":     "!!! NGHI NGO",
            "CRITICAL": "!!!! CANH BAO CAO",
        }.get(level, level)

        cv2.putText(frame, f"TRANG THAI: {status_text}",
                    (10, 35), cv2.FONT_HERSHEY_SIMPLEX,
                    0.8, color, 2)

        # FPS
        cv2.putText(frame, f"FPS: {fps:.1f}",
                    (self.W - 130, 35), cv2.FONT_HERSHEY_SIMPLEX,
                    0.7, COLOR_INFO, 2)
        return frame

    def _draw_score_bar(self, frame, fusion_result):
        """Thanh điểm rủi ro hình chữ nhật."""
        score = fusion_result["score"]
        max_score = ALERT_SCORE_HIGH * 2  # max = 20
        ratio = min(score / max_score, 1.0)

        BAR_X, BAR_Y = 10, 60
        BAR_W, BAR_H = 200, 18

        # Background
        cv2.rectangle(frame, (BAR_X, BAR_Y),
                      (BAR_X + BAR_W, BAR_Y + BAR_H), (50, 50, 50), -1)

        # Fill
        fill_w = int(BAR_W * ratio)
        if ratio < 0.35:
            bar_color = (0, 200, 0)
        elif ratio < 0.65:
            bar_color = (0, 165, 255)
        else:
            bar_color = (0, 0, 255)

        if fill_w > 0:
            cv2.rectangle(frame, (BAR_X, BAR_Y),
                          (BAR_X + fill_w, BAR_Y + BAR_H), bar_color, -1)

        cv2.rectangle(frame, (BAR_X, BAR_Y),
                      (BAR_X + BAR_W, BAR_Y + BAR_H), (200, 200, 200), 1)
        cv2.putText(frame, f"RUI RO: {score}/{max_score}",
                    (BAR_X + BAR_W + 8, BAR_Y + 14),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLOR_INFO, 1)
        return frame

    def _draw_behavior_alerts(self, frame, mp_analysis):
        """Vẽ các cảnh báo hành vi (quay đầu, nhìn xuống) có background."""
        alerts = []
        if mp_analysis.get("looking_away"):
            alerts.append(("QUAY DAU SANG NGANG", (0, 0, 255)))
        if mp_analysis.get("head_down"):
            alerts.append(("NHIN XUONG QUA LAU", (0, 165, 255)))
        if mp_analysis.get("hand_near_ear"):
            alerts.append(("TAY GAN VUNG TAI - CAN KIEM TRA", (0, 165, 255)))
        if mp_analysis.get("hand_suspicious"):
            alerts.append(("TAY O VI TRI BAT THUONG", (0, 165, 255)))

        if not alerts:
            return frame

        # Bắt đầu vẽ từ dưới thanh score bar (khoảng y=90)
        start_y = 105
        for text, color in alerts:
            (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
            
            # Draw semi-transparent background
            overlay = frame.copy()
            cv2.rectangle(overlay, (8, start_y - th - 5), (15 + tw, start_y + 5), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
            
            cv2.putText(frame, text, (10, start_y), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            start_y += 35
            
        return frame

    def _draw_events_panel(self, frame, fusion_result):
        """Danh sách sự kiện đang diễn ra (bottom left)."""
        events = fusion_result.get("events", [])
        if not events:
            return frame

        panel_x, panel_y = 10, self.H - 30 * len(events) - 10
        for i, event in enumerate(events[-5:]):  # max 5 lines
            color = ALERT_LEVEL_COLORS.get(event.level, COLOR_INFO)
            y = panel_y + i * 28

            # Semi-transparent background
            overlay = frame.copy()
            cv2.rectangle(overlay, (panel_x - 5, y - 18),
                          (panel_x + 420, y + 5), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)

            cv2.putText(frame, f"[{event.level}] {event.event_type}: {event.detail}",
                        (panel_x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2)
        return frame

    def _draw_yolo_boxes(self, frame, detections):
        """Vẽ bounding boxes từ YOLO detections."""
        for det in detections:
            x1, y1, x2, y2 = det["bbox"]
            label = det["label"].upper()
            conf = det["confidence"]

            is_earphone = any(keyword in det["label"].lower() for keyword in ("earphone", "earbud"))
            if is_earphone:
                box_color = (0, 165, 255)
                prefix = "REVIEW"
            elif det["is_cheat"]:
                box_color = (0, 0, 255)
                prefix = "ALERT"
            else:
                box_color = (0, 200, 0)     # Xanh lá cho vật thể được phép
                prefix = "OK"

            # Animated border (thicker)
            cv2.rectangle(frame, (x1, y1), (x2, y2), box_color, 3)
            # Corner decorations for premium look
            clen = 15
            for cx, cy in [(x1, y1), (x2, y1), (x1, y2), (x2, y2)]:
                dx = clen if cx == x1 else -clen
                dy = clen if cy == y1 else -clen
                cv2.line(frame, (cx, cy), (cx + dx, cy), box_color, 4)
                cv2.line(frame, (cx, cy), (cx, cy + dy), box_color, 4)

            text = f"[{prefix}] {label} {conf:.1%}"
            (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.65, 2)
            cv2.rectangle(frame, (x1, y1 - th - 10), (x1 + tw + 6, y1), box_color, -1)
            cv2.putText(frame, text, (x1 + 3, y1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
        return frame

    def _draw_timestamp(self, frame):
        """Timestamp góc phải dưới."""
        ts = datetime.datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
        cv2.putText(frame, ts, (self.W - 240, self.H - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)
        return frame

    def draw_alert_flash(self, frame, level: str) -> np.ndarray:
        """Flash border khi có alert HIGH/CRITICAL."""
        if level in ("HIGH", "CRITICAL"):
            color = ALERT_LEVEL_COLORS[level]
            cv2.rectangle(frame, (0, 0), (self.W - 1, self.H - 1), color, 8)
        return frame
