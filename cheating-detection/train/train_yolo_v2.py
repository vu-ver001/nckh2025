# ============================================================
# train_yolo_v2.py - Script huấn luyện YOLOv8 với 5 classes
# Cải tiến: Thêm các class gây nhiễu để giảm False Positive
# ============================================================

from ultralytics import YOLO
import os
import yaml

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 1. Định nghĩa bộ Dataset mới
dataset_config = {
    "path": os.path.join(BASE_DIR, "dataset", "cheating_v2").replace("\\", "/"),
    "train": "images/train",
    "val":   "images/val",
    "nc":    5,
    "names": {
        0: "earphone",
        1: "phone",
        2: "cheat_sheet",
        3: "calculator",
        4: "pencil_case",
    },
}

yaml_path = os.path.join(BASE_DIR, "dataset", "data_v2.yaml")
with open(yaml_path, "w") as f:
    yaml.dump(dataset_config, f, default_flow_style=False, allow_unicode=True)

print(f"[Train] Created config: {yaml_path}")

# 2. Huấn luyện với kiến trúc YOLOv8s (Small) để có độ chính xác cao hơn Nano
# Nếu máy yếu, hãy đổi lại thành "yolov8n.pt"
model = YOLO("yolov8s.pt") 

# 3. Chạy huấn luyện
# Chú ý: Cần bật augment để AI học tốt hơn trong điều kiện phòng thi
model.train(
    data=yaml_path,
    epochs=150,
    imgsz=640,
    batch=16,
    device="cpu", # Đổi thành 0 nếu có GPU
    project=os.path.join(BASE_DIR, "models"),
    name="examguard_v2_improved",
    save=True,
    augment=True,
    mosaic=1.0,  # Ghép ảnh để nhận diện vật thể nhỏ (tai nghe) tốt hơn
    mixup=0.2,
    patience=50, # Đợi lâu hơn trước khi dừng sớm
)
