# ============================================================
# train_yolo.py - Script huấn luyện YOLOv8 custom model
# Phát hiện: tai nghe (earphone), phao thi (cheat_sheet)
# ============================================================
# Cách dùng:
#   python train/train_yolo.py
#
# Yêu cầu:
#   - Dataset đã label theo format YOLO (xem dataset/README.md)
#   - datasets/cheating/
#       ├── images/
#       │   ├── train/   (ảnh train)
#       │   └── val/     (ảnh validate)
#       └── labels/
#           ├── train/   (.txt annotations)
#           └── val/     (.txt annotations)
# ============================================================

from ultralytics import YOLO
import os
import yaml

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ─────────────────────────────────────────────────────────
# 1. Tạo file data.yaml mô tả dataset
# ─────────────────────────────────────────────────────────
dataset_config = {
    "path": os.path.join(BASE_DIR, "dataset", "cheating").replace("\\", "/"),
    "train": "images/train",
    "val":   "images/val",
    "nc":    3,          # Số class
    "names": {           # Tên class (khớp với thứ tự label)
        0: "earphone",
        1: "phone",
        2: "cheat_sheet",
    },
}

yaml_path = os.path.join(BASE_DIR, "dataset", "data.yaml")
os.makedirs(os.path.dirname(yaml_path), exist_ok=True)

with open(yaml_path, "w") as f:
    yaml.dump(dataset_config, f, default_flow_style=False, allow_unicode=True)

print(f"[Train] data.yaml created: {yaml_path}")

# ─────────────────────────────────────────────────────────
# 2. Load pretrained model (transfer learning từ YOLOv8n)
# ─────────────────────────────────────────────────────────
# YOLOv8n = nano (nhanh, phù hợp CPU/GPU yếu)
# YOLOv8s = small (tốt hơn, cần GPU)
# Khuyến nghị: bắt đầu bằng yolov8n để thử, rồi dùng yolov8s khi có GPU
model = YOLO("yolov8n.pt")   # Tải pretrained weights từ COCO

# ─────────────────────────────────────────────────────────
# 3. Training
# ─────────────────────────────────────────────────────────
results = model.train(
    data=yaml_path,
    epochs=100,             # Số epoch (tăng lên 150-200 nếu cần)
    imgsz=640,              # Kích thước ảnh input
    batch=16,               # Batch size (giảm xuống 8 nếu hết RAM/VRAM)
    lr0=0.01,               # Learning rate ban đầu
    lrf=0.01,               # Final LR ratio
    momentum=0.937,
    weight_decay=0.0005,
    warmup_epochs=3,
    patience=30,            # Early stopping nếu không cải thiện 30 epoch
    device="cpu",           # Đổi thành "0" nếu có GPU CUDA
    workers=4,
    project=os.path.join(BASE_DIR, "models"),
    name="cheating_v1",
    save=True,
    save_period=10,         # Lưu checkpoint mỗi 10 epoch
    val=True,
    plots=True,             # Tạo biểu đồ loss/mAP
    augment=True,           # Data augmentation
    # Augmentation params
    flipud=0.0,             # Không lật dọc (người không đứng ngược)
    fliplr=0.5,             # Lật ngang 50%
    mosaic=1.0,             # Mosaic augmentation
    mixup=0.1,              # Mixup
    copy_paste=0.1,
    hsv_h=0.015,            # Hue augmentation
    hsv_s=0.7,              # Saturation
    hsv_v=0.4,              # Brightness
    degrees=5.0,            # Rotation ±5°
    translate=0.1,
    scale=0.5,
)

print("\n[Train] Training complete!")
print(f"[Train] Best model: models/cheating_v1/weights/best.pt")

# ─────────────────────────────────────────────────────────
# 4. Validate và in metrics
# ─────────────────────────────────────────────────────────
best_model = YOLO(os.path.join(BASE_DIR, "models", "cheating_v1", "weights", "best.pt"))
metrics = best_model.val(data=yaml_path)

print("\n── Kết quả Validate ──────────────────────────────")
print(f"  mAP@0.5:      {metrics.box.map50:.4f}")
print(f"  mAP@0.5:0.95: {metrics.box.map:.4f}")
print(f"  Precision:    {metrics.box.mp:.4f}")
print(f"  Recall:       {metrics.box.mr:.4f}")

# Per-class results
class_names = ["earphone", "phone", "cheat_sheet"]
if hasattr(metrics.box, 'ap_class_index'):
    for i, cls_idx in enumerate(metrics.box.ap_class_index):
        name = class_names[cls_idx] if cls_idx < len(class_names) else f"class_{cls_idx}"
        ap = metrics.box.ap50[i] if metrics.box.ap50 is not None else 0
        print(f"  [{name}] AP@0.5: {ap:.4f}")

print("\n[Train] Chạy lệnh sau để theo dõi training:")
print("  tensorboard --logdir models/cheating_v1")
