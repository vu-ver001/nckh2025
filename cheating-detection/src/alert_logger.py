# ============================================================
# alert_logger.py - Ghi nhật ký cảnh báo ra file CSV + console
# ============================================================

import csv
import os
import datetime
from config import LOG_TO_FILE, LOG_FILE_PATH, LOG_DIR


class AlertLogger:
    def __init__(self):
        self.events = []  # In-memory log
        self.session_start = datetime.datetime.now()

        if LOG_TO_FILE:
            os.makedirs(LOG_DIR, exist_ok=True)
            self._init_csv()

    def _init_csv(self):
        """Tạo file CSV với header nếu chưa có."""
        file_exists = os.path.isfile(LOG_FILE_PATH)
        self._csv_file = open(LOG_FILE_PATH, "a", newline="", encoding="utf-8")
        self._writer = csv.writer(self._csv_file)
        if not file_exists:
            self._writer.writerow([
                "timestamp", "elapsed_sec", "event_type",
                "detail", "score", "alert_level"
            ])
            self._csv_file.flush()

    def log(self, event_type: str, detail: str = "", score: int = 0, level: str = "LOW"):
        """Ghi một sự kiện cảnh báo."""
        now = datetime.datetime.now()
        elapsed = (now - self.session_start).total_seconds()
        ts = now.strftime("%Y-%m-%d %H:%M:%S")

        record = {
            "timestamp": ts,
            "elapsed_sec": round(elapsed, 2),
            "event_type": event_type,
            "detail": detail,
            "score": score,
            "alert_level": level,
        }
        self.events.append(record)
        print(f"[ALERT][{level}] {ts} | {event_type}: {detail} (score={score})")

        if LOG_TO_FILE:
            self._writer.writerow([
                ts, round(elapsed, 2), event_type, detail, score, level
            ])
            self._csv_file.flush()

    def get_recent_events(self, n: int = 5):
        """Trả về N sự kiện gần nhất."""
        return self.events[-n:]

    def close(self):
        if LOG_TO_FILE and hasattr(self, "_csv_file"):
            self._csv_file.close()
