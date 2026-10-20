# ============================================================
# resume_phone.py - Tiếp tục training YOLOv8 từ checkpoint
# ============================================================
# Cách dùng:
#   venv\Scripts\python.exe train\resume_phone.py
# ============================================================

import os
from ultralytics import YOLO

# Đường dẫn tới file checkpoint cuối cùng (last.pt)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHECKPOINT_PATH = os.path.join(BASE_DIR, "models", "phone_v1", "weights", "last.pt")

def resume_training():
    if not os.path.exists(CHECKPOINT_PATH):
        print(f"[Error] Khong tim thay file checkpoint tai: {CHECKPOINT_PATH}")
        print("Hay dam bao ban da chay train_phone.py it nhat 1 epoch.")
        return

    print(f"[Resume] Dang tiep tuc training tu: {CHECKPOINT_PATH}...")
    
    # Load model tu checkpoint
    model = YOLO(CHECKPOINT_PATH)
    
    # Tiep tuc train (YOLOv8 tu dong tim data.yaml va cac config cu)
    model.train(resume=True)

    print("\n[Resume] ✅ Training da hoan tat hoac bi dung.")

if __name__ == "__main__":
    resume_training()
