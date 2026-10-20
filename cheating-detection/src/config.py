# ============================================================
# config.py - Centralized Configuration
# Cheating Detection System v2.0
# ============================================================

import os

# ─── Paths ────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, "models")
DATASET_DIR = os.path.join(BASE_DIR, "dataset")
LOG_DIR = os.path.abspath(os.environ.get("EXAMGUARD_LOG_DIR", os.path.join(BASE_DIR, "logs")))

# YOLO Model paths
YOLO_POSE_MODEL = os.path.join(BASE_DIR, "yolov8n-pose.pt")
YOLO_DET_MODEL  = os.path.join(BASE_DIR, "yolov8n.pt")

# Custom trained model (after training)
YOLO_CUSTOM_MODEL = os.path.join(MODEL_DIR, "cheating_best.pt")

# Phone confirmation model (trained riêng cho phone — giảm false positive)
# phone_v1 was trained with an incorrect class mapping. Keep it for audit only.
# Colab checkpoint passed isolated integration; CPU training artifacts stay separate.
YOLO_PHONE_CONFIRM_MODEL = os.path.abspath(os.environ.get(
    "EXAMGUARD_PHONE_CONFIRM_MODEL", os.path.join(MODEL_DIR, "phone_v3_colab", "weights", "best.pt")))

# ─── Camera / Video ───────────────────────────────────────
CAMERA_INDEX = 0          # 0 = laptop webcam, 1 = external
_video_source = os.environ.get("EXAMGUARD_VIDEO_SOURCE", str(CAMERA_INDEX))
VIDEO_SOURCE = int(_video_source) if _video_source.isdecimal() else os.path.abspath(_video_source)
FRAME_WIDTH  = 1280
FRAME_HEIGHT = 720
TARGET_FPS   = 30

# ─── YOLO Detection ───────────────────────────────────────
YOLO_CONF_THRESHOLD = 0.25      # Lowered from 0.45 for maximum sensitivity
YOLO_IOU_THRESHOLD  = 0.45      # NMS IoU threshold

# Ngưỡng confidence riêng cho "cell phone" từ YOLO-World (giảm false positive
# với vật chữ nhật như hộp bút). YOLO-World không chuẩn hóa confidence tốt,
# nên nâng nhẹ thay vì nâng cao — dựa chủ yếu vào model xác nhận.
PHONE_CONF_THRESHOLD = 0.4

# ─── Phone Confirmation (giảm false positive) ─────────────
# Mọi detection "cell phone" từ YOLO-World phải được checkpoint cấu hình xác nhận
# (chồng lấn IoU >= PHONE_CONFIRM_IOU hoặc tâm box nằm trong box phone)
PHONE_CONFIRM_IOU  = 0.2     # IoU tối thiểu giữa box world và box xác nhận
PHONE_CONFIRM_CONF = 0.3     # Conf tối thiểu của model xác nhận

# Số lần YOLO liên tiếp phone phải xuất hiện (cùng vị trí) trước khi cộng điểm
PHONE_PERSIST_FRAMES = 3

# COCO class IDs we care about (default model)
COCO_CLASSES = {
    67: "cell phone",
    73: "book",
    26: "backpack",
    27: "umbrella",   # Sometimes confused with earphone wire
}

# Custom trained classes (your model after training)
CUSTOM_CLASSES = {
    0: "earphone",
    1: "phone",
    2: "cheat_sheet",
}

# ─── YOLO-World (Zero-shot Detection) ─────────────────────
USE_YOLO_WORLD = True       # True = dùng YOLO-World, False = dùng COCO cũ
YOLO_WORLD_MODEL = os.path.join(BASE_DIR, "yolov8s-worldv2.pt")

# Vật thể CẦN CẢNH BÁO (nghi gian lận)
YOLO_WORLD_CHEAT_CLASSES = [
    "cell phone",
    "smartphone",
    "earphone",
    "earbud",
    "wireless earphone",
    "cheat sheet",
    "hidden note",
    "book",             # Sách không được phép mang vào phòng thi
]

# Vật thể ĐƯỢC PHÉP — bắt để LOẠI TRỪ khỏi cảnh báo nhầm
# Mô tả chi tiết giúp YOLO-World phân biệt tốt hơn
YOLO_WORLD_ALLOWED_CLASSES = [
    "scientific calculator",
    "Casio calculator",
    "pencil case",
    "pencil box",
    "pencil holder",
    "pen holder",
    "notebook",
    "folder",
    "box",
    "pen",
    "eraser",
    "ruler",
    "water bottle",
]

# ─── MediaPipe ────────────────────────────────────────────
MP_POSE_CONFIDENCE      = 0.5   # Lowered from 0.6
MP_POSE_TRACKING        = 0.4   # Lowered from 0.5
MP_HANDS_MAX_NUM        = 2     
MP_HANDS_CONFIDENCE     = 0.5
MP_FACE_MAX_NUM         = 1
MP_FACE_CONFIDENCE      = 0.6

# ─── Alert Thresholds (Behavior Rules) ────────────────────
# Head turn: ratio of nose offset to eye distance
HEAD_TURN_RATIO_THRESHOLD = 0.58   # Increased from 0.45 (Need more turn to trigger)
HEAD_TURN_FRAMES_NEEDED   = 8      # Increased from 3 (Must hold turn for ~0.3s)

# Head tilt DOWN: nose below eyes baseline
HEAD_DOWN_RATIO_THRESHOLD = 0.5    # Increased from 0.4
HEAD_DOWN_FRAMES_NEEDED   = 12     # Increased from 5 (Avoid alert on blinking/brief look down)

# Hand near ears (earphone gesture). This is a review cue, not proof of an
# earbud: require a body-size-normalized distance and temporal persistence.
HAND_EAR_DISTANCE_THRESHOLD = 0.18  # fallback when shoulder landmarks are missing
HAND_EAR_SHOULDER_RATIO_THRESHOLD = 0.45
HAND_EAR_HOLD_SECONDS = 2.0
HAND_EAR_MAX_GAP_SECONDS = 0.5
HAND_EAR_REPEAT_WINDOW_SECONDS = 20.0
HAND_EAR_REPEAT_COUNT = 3
HAND_EAR_MIN_EPISODE_SECONDS = 0.35

# Looking away (one eye significantly less visible than other)
EYE_VISIBILITY_DIFF = 0.35          # Increased from 0.25

# ─── Scoring / Fusion ─────────────────────────────────────
# Points assigned to each event
SCORE_WEIGHTS = {
    "phone_detected":       12,     # Increased from 10
    "cheat_sheet_detected": 8,      # Increased from 7
    "looking_away":         5,      # Increased from 4
    "head_down_long":       4,      # Increased from 3
    "hand_near_ear":        4,      # Review cue; not proof of an earbud
    "hand_suspicious":      4,      # Increased from 3
}

ALERT_SCORE_LOW    = 2    # Lowered from 3
ALERT_SCORE_MEDIUM = 6    # Lowered from 7
ALERT_SCORE_HIGH   = 9    # Lowered from 10

# Score decays over time (frames) to avoid persistent false alerts
SCORE_DECAY_FRAMES = 30   # Reset score after 1 sec if no events

# ─── UI Display ───────────────────────────────────────────
FONT_SCALE   = 0.65
FONT_THICK   = 2

COLOR_OK     = (0, 200, 0)      # Green
COLOR_WARN   = (0, 165, 255)    # Orange
COLOR_ALERT  = (0, 0, 255)      # Red
COLOR_INFO   = (200, 200, 200)  # Gray

ALERT_LEVEL_COLORS = {
    "LOW":      (0, 165, 255),   # Orange
    "MEDIUM":   (0, 60, 255),    # Deep orange-red
    "HIGH":     (0, 0, 255),     # Red
    "CRITICAL": (180, 0, 255),   # Purple-red
}

# ─── Logging ──────────────────────────────────────────────
LOG_TO_FILE    = True
LOG_FILE_PATH  = os.path.join(LOG_DIR, "cheating_log.csv")
LOG_VIDEO_PATH = os.path.join(LOG_DIR, "session_record.avi")
SAVE_VIDEO     = False   # Set True to record session
