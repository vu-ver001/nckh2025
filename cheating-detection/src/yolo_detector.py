# ============================================================
# yolo_detector.py - YOLO Object Detection Module
# Hỗ trợ 2 chế độ:
#   1. YOLO-World (Zero-shot) — Nhận diện bằng ngôn ngữ tự nhiên
#   2. YOLO COCO (Fallback)   — Nhận diện bằng class ID cố định
# ============================================================

import cv2
import os
import numpy as np
from ultralytics import YOLO
from detection_labels import is_phone_label

from config import (
    YOLO_DET_MODEL, YOLO_CUSTOM_MODEL, YOLO_PHONE_CONFIRM_MODEL,
    YOLO_CONF_THRESHOLD, YOLO_IOU_THRESHOLD,
    PHONE_CONF_THRESHOLD, PHONE_CONFIRM_IOU, PHONE_CONFIRM_CONF,
    COCO_CLASSES, CUSTOM_CLASSES,
    COLOR_ALERT, COLOR_WARN,
    USE_YOLO_WORLD, YOLO_WORLD_MODEL,
    YOLO_WORLD_CHEAT_CLASSES, YOLO_WORLD_ALLOWED_CLASSES,
)


# ── Tính IoU giữa 2 bounding boxes ──────────────────────────
def _compute_iou(box_a, box_b):
    """Tính Intersection over Union giữa 2 bbox (x1,y1,x2,y2)."""
    xa = max(box_a[0], box_b[0])
    ya = max(box_a[1], box_b[1])
    xb = min(box_a[2], box_b[2])
    yb = min(box_a[3], box_b[3])

    inter = max(0, xb - xa) * max(0, yb - ya)
    if inter == 0:
        return 0.0

    area_a = (box_a[2] - box_a[0]) * (box_a[3] - box_a[1])
    area_b = (box_b[2] - box_b[0]) * (box_b[3] - box_b[1])
    union = area_a + area_b - inter

    return inter / union if union > 0 else 0.0


# ── Mapping: YOLO-World label → loại sự kiện cho Fusion Engine ──
def _classify_world_label(label: str, cheat_classes: list, allowed_classes: list):
    """
    Phân loại label từ YOLO-World thành:
      - ('cheat', normalized_label) nếu là vật thể gian lận
      - ('allowed', normalized_label) nếu là vật thể được phép
      - ('unknown', label) nếu không xác định
    """
    label_lower = label.lower().strip()

    # Kiểm tra allowed TRƯỚC → ưu tiên vật thể được phép
    for allowed in allowed_classes:
        if allowed.lower().strip() == label_lower:
            return "allowed", label_lower

    for cheat in cheat_classes:
        if cheat.lower().strip() == label_lower:
            # Normalize sang label chuẩn cho fusion engine
            if is_phone_label(label_lower):
                return "cheat", "cell phone"
            elif any(kw in label_lower for kw in ["earphone", "earbud", "wireless earphone"]):
                return "cheat", "earphone"
            elif any(kw in label_lower for kw in ["cheat sheet", "hidden note"]):
                return "cheat", "cheat_sheet"
            elif "book" in label_lower:
                return "cheat", "book"
            else:
                return "cheat", label_lower

    return "unknown", label_lower


def _filter_overlapping_detections(detections: list[dict], iou_threshold: float = 0.15) -> list[dict]:
    """
    Lọc các detection chồng lấn (cùng vùng ảnh).
    Nguyên tắc: Nếu một vật thể 'allowed' và 'cheat' chồng lấn nhau (IoU > threshold),
    thì ƯU TIÊN giữ 'allowed' và loại bỏ 'cheat'.
    
    Ngoài IoU, còn kiểm tra "chứa nhau": nếu box cheat nằm gần như hoàn toàn
    trong box allowed (diện tích chồng > 60% box cheat) thì coi là cùng vật thể.
    
    Lý do: YOLO-World có thể bắt cùng 1 vật (hộp bút, máy tính Casio) thành cả
    "calculator"/"pencil case" lẫn "cell phone". Khi đó "allowed" đáng tin hơn.
    """
    if len(detections) <= 1:
        return detections

    # Tách thành 2 nhóm
    allowed_dets = [d for d in detections if not d["is_cheat"]]
    cheat_dets = [d for d in detections if d["is_cheat"]]

    # Với mỗi cheat detection, kiểm tra xem có chồng lấn với allowed nào không
    filtered_cheat = []
    for cheat in cheat_dets:
        is_overlapping_with_allowed = False
        for allowed in allowed_dets:
            iou = _compute_iou(cheat["bbox"], allowed["bbox"])
            if iou > iou_threshold:
                is_overlapping_with_allowed = True
                print(f"[YOLODetector] Loại bỏ nhầm: '{cheat['label']}' chồng lấn với '{allowed['label']}' (IoU={iou:.2f})")
                break

            # Kiểm tra chứa nhau: box cheat nằm trong box allowed (hoặc ngược lại)
            c_x1, c_y1, c_x2, c_y2 = cheat["bbox"]
            a_x1, a_y1, a_x2, a_y2 = allowed["bbox"]
            c_area = max(1, (c_x2 - c_x1) * (c_y2 - c_y1))
            a_area = max(1, (a_x2 - a_x1) * (a_y2 - a_y1))
            inter_x1, inter_y1 = max(c_x1, a_x1), max(c_y1, a_y1)
            inter_x2, inter_y2 = min(c_x2, a_x2), min(c_y2, a_y2)
            if inter_x2 > inter_x1 and inter_y2 > inter_y1:
                inter_area = (inter_x2 - inter_x1) * (inter_y2 - inter_y1)
                # >60% diện tích box cheat nằm trong box allowed
                if inter_area / c_area > 0.6 or inter_area / a_area > 0.6:
                    is_overlapping_with_allowed = True
                    print(f"[YOLODetector] Loại bỏ nhầm: '{cheat['label']}' chứa trong '{allowed['label']}' (cover={inter_area / c_area:.0%})")
                    break

        if not is_overlapping_with_allowed:
            filtered_cheat.append(cheat)

    return allowed_dets + filtered_cheat


class YOLODetector:
    """
    Module phát hiện vật thể.
    - YOLO-World mode: Zero-shot detection, không cần train
    - COCO mode (fallback): Dùng YOLOv8n pretrained trên COCO
    """

    def __init__(self, use_custom_model: bool = False):
        self.use_world = USE_YOLO_WORLD
        self.custom_model = None
        self.phone_confirm_model = None
        self.phone_confirm_error = None

        if self.use_world:
            # ── YOLO-World Mode ──
            print("[YOLODetector] Loading YOLO-World model...")
            self.world_model = YOLO(YOLO_WORLD_MODEL)

            # Khai báo tất cả class cần tìm (cheat + allowed)
            all_classes = YOLO_WORLD_CHEAT_CLASSES + YOLO_WORLD_ALLOWED_CLASSES
            self.world_model.set_classes(all_classes)
            print(f"[YOLODetector] YOLO-World ready — {len(all_classes)} classes configured:")
            print(f"  Cheat items:   {YOLO_WORLD_CHEAT_CLASSES}")
            print(f"  Allowed items: {YOLO_WORLD_ALLOWED_CLASSES}")

            # Model xác nhận phone (giảm false positive: hộp bút ≠ điện thoại)
            try:
                if not os.path.isfile(YOLO_PHONE_CONFIRM_MODEL):
                    raise FileNotFoundError(f"Không tìm thấy checkpoint xác nhận: {YOLO_PHONE_CONFIRM_MODEL}")
                self.phone_confirm_model = YOLO(YOLO_PHONE_CONFIRM_MODEL)
                if "phone" not in self.phone_confirm_model.names.values():
                    raise ValueError("Model xác nhận không có class phone")
                print(f"[YOLODetector] Phone confirm model loaded: {YOLO_PHONE_CONFIRM_MODEL}")
            except Exception as e:
                self.phone_confirm_model = None
                self.phone_confirm_error = str(e)
                print(f"[YOLODetector] WARNING: Không load được phone confirm model: {e}")
                print("[YOLODetector]          Phone sẽ dựa vào YOLO-World thuần (dễ false positive)")

        else:
            # ── COCO Fallback Mode ──
            print("[YOLODetector] Loading COCO detection model (fallback)...")
            self.det_model = YOLO(YOLO_DET_MODEL)
            self.coco_target_classes = list(COCO_CLASSES.keys())

            if use_custom_model:
                try:
                    self.custom_model = YOLO(YOLO_CUSTOM_MODEL)
                    print("[YOLODetector] Custom model loaded.")
                except Exception as e:
                    print(f"[YOLODetector] Custom model not found: {e}")

        print("[YOLODetector] Ready.")

    def model_status(self):
        from pathlib import Path
        return dict(detector='YOLO-World' if self.use_world else 'YOLO COCO',
                    configured_phone=YOLO_PHONE_CONFIRM_MODEL,
                    loaded_phone=YOLO_PHONE_CONFIRM_MODEL if self.phone_confirm_model is not None else None,
                    phone_name=Path(YOLO_PHONE_CONFIRM_MODEL).parent.parent.name,
                    status='loaded' if self.phone_confirm_model is not None else 'fallback',
                    error=self.phone_confirm_error)

    def detect(self, frame: np.ndarray) -> list[dict]:
        """
        Chạy detection trên 1 frame.
        Returns: list of detection dicts:
          {
            'label': str,
            'confidence': float,
            'bbox': (x1,y1,x2,y2),
            'is_cheat': bool,
            'source': 'world' | 'coco' | 'custom'
          }
        """
        if self.use_world:
            return self._detect_world(frame)
        else:
            return self._detect_coco(frame)

    def _detect_world(self, frame: np.ndarray, *, confirm=True, filter_allowed=True) -> list[dict]:
        """Detection bằng YOLO-World (zero-shot)."""
        raw_results = []

        world_results = self.world_model(
            frame,
            conf=YOLO_CONF_THRESHOLD,
            iou=YOLO_IOU_THRESHOLD,
            verbose=False,
            **getattr(self, 'inference_options', {}),
        )

        if world_results[0].boxes is None:
            return self._confirm_phones(frame, [], allow_overlap=not filter_allowed) if confirm else []

        names = world_results[0].names  # {0: "cell phone", 1: "earphone", ...}

        for box in world_results[0].boxes:
            cls_id = int(box.cls[0])
            raw_label = names.get(cls_id, "unknown")
            conf = float(box.conf[0])
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            # Phân loại: cheat hay allowed?
            category, normalized_label = _classify_world_label(
                raw_label,
                YOLO_WORLD_CHEAT_CLASSES,
                YOLO_WORLD_ALLOWED_CLASSES,
            )

            if category == "allowed":
                raw_results.append({
                    "label": normalized_label,
                    "confidence": conf,
                    "bbox": (x1, y1, x2, y2),
                    "is_cheat": False,
                    "source": "world",
                })
            elif category == "cheat":
                # Ngưỡng confidence riêng cho phone (giảm false positive)
                if is_phone_label(normalized_label) and conf < PHONE_CONF_THRESHOLD:
                    continue
                raw_results.append({
                    "label": normalized_label,
                    "confidence": conf,
                    "bbox": (x1, y1, x2, y2),
                    "is_cheat": True,
                    "source": "world",
                })
            # unknown → bỏ qua

        # ── Lọc chồng lấn: ưu tiên allowed khi trùng vùng với cheat ──
        filtered = _filter_overlapping_detections(raw_results, iou_threshold=0.15) if filter_allowed else raw_results

        # ── Xác nhận phone bằng model chuyên dụng (giảm false positive) ──
        if confirm:
            filtered = self._confirm_phones(frame, filtered, allow_overlap=not filter_allowed)
        return filtered

    def _confirm_phones(self, frame: np.ndarray, detections: list[dict], *, allow_overlap=False) -> list[dict]:
        """
        Lớp lọc false positive QUAN TRỌNG nhất:
        Mọi detection "cell phone" từ YOLO-World phải được checkpoint
        xác nhận đã cấu hình xác nhận thì mới giữ lại.

        - phone_confirm chạy mỗi lần detect() để cũng BẮT HỤT các phone mà
          YOLO-World bỏ sót (YOLO-World zero-shot hay miss phone).
        - Độ trễ phụ thuộc checkpoint và phần cứng; đo trên phiên thực tế.
        """
        if self.phone_confirm_model is None:
            return detections

        # Chạy model xác nhận cho cả frame
        results = self.phone_confirm_model(
            frame,
            conf=PHONE_CONFIRM_CONF,
            iou=YOLO_IOU_THRESHOLD,
            verbose=False,
            **getattr(self, 'inference_options', {}),
        )

        confirm_boxes = []
        if results[0].boxes is not None:
            for box in results[0].boxes:
                if self.phone_confirm_model.names.get(int(box.cls[0])) != "phone":
                    continue
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                confirm_boxes.append((x1, y1, x2, y2, float(box.conf[0])))

        # The specialist owns phone geometry and confidence. World support is
        # provenance only: one specialist box must never confirm several boxes.
        world_phones = [d for d in detections if d["is_cheat"] and is_phone_label(d["label"])]
        confirmed = [d for d in detections if not (d["is_cheat"] and is_phone_label(d["label"]))]
        allowed_dets = [d for d in confirmed if not d["is_cheat"]]
        existing_phones = []
        used_world = set()
        for cb in sorted(confirm_boxes, key=lambda box: box[4], reverse=True):
            c_box, c_conf = cb[:4], cb[4]
            if any(_compute_iou(c_box, previous) > 0.3 for previous in existing_phones):
                continue
            if not allow_overlap and any(_compute_iou(c_box, d["bbox"]) > 0.15 for d in allowed_dets):
                continue
            candidates = []
            for index, world_phone in enumerate(world_phones):
                if index in used_world:
                    continue
                box = world_phone["bbox"]
                overlap = _compute_iou(box, c_box)
                cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
                if overlap >= PHONE_CONFIRM_IOU or (c_box[0] <= cx <= c_box[2] and c_box[1] <= cy <= c_box[3]):
                    candidates.append((overlap, world_phone["confidence"], index))
            supported = bool(candidates)
            if supported:
                used_world.add(max(candidates)[2])
            confirmed.append({
                "label": "cell phone", "confidence": c_conf, "bbox": c_box,
                "is_cheat": True, "source": "phone_confirm",
                "world_supported": supported,
            })
            existing_phones.append(c_box)
        return confirmed

    def _detect_coco(self, frame: np.ndarray) -> list[dict]:
        """Detection bằng YOLO COCO (fallback mode)."""
        results = []

        coco_results = self.det_model(
            frame,
            classes=self.coco_target_classes,
            conf=YOLO_CONF_THRESHOLD,
            iou=YOLO_IOU_THRESHOLD,
            verbose=False,
        )

        for box in coco_results[0].boxes:
            cls_id = int(box.cls[0])
            label = COCO_CLASSES.get(cls_id, "unknown")
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            results.append({
                "label": label,
                "confidence": float(box.conf[0]),
                "bbox": (x1, y1, x2, y2),
                "is_cheat": cls_id in [67],
                "source": "coco",
            })

        # Custom model (tai nghe, phao)
        if self.custom_model is not None:
            custom_results = self.custom_model(
                frame,
                conf=YOLO_CONF_THRESHOLD,
                iou=YOLO_IOU_THRESHOLD,
                verbose=False,
            )
            for box in custom_results[0].boxes:
                cls_id = int(box.cls[0])
                label = CUSTOM_CLASSES.get(cls_id, "unknown")
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                results.append({
                    "label": label,
                    "confidence": float(box.conf[0]),
                    "bbox": (x1, y1, x2, y2),
                    "is_cheat": True,
                    "source": "custom",
                })

        return results

    def draw(self, frame: np.ndarray, detections: list[dict]) -> np.ndarray:
        """Vẽ bounding box và nhãn lên frame."""
        for det in detections:
            x1, y1, x2, y2 = det["bbox"]
            label = det["label"].upper()
            conf = det["confidence"]
            is_earphone = any(keyword in det["label"].lower() for keyword in ("earphone", "earbud"))
            color = COLOR_WARN if is_earphone or not det["is_cheat"] else COLOR_ALERT

            # Draw box
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)

            # Label background
            prefix = "XEM LAI" if is_earphone else ("CANH BAO" if det["is_cheat"] else "DUOC PHEP")
            text = f"{prefix}: {label} ({conf:.1%})"
            (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.65, 2)
            cv2.rectangle(frame, (x1, y1 - th - 8), (x1 + tw + 4, y1), color, -1)
            cv2.putText(frame, text, (x1 + 2, y1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
        return frame
