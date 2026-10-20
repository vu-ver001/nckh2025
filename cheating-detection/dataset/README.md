# Dataset Collection & Labeling Guide
# Hướng dẫn thu thập và gán nhãn dữ liệu

## Cấu trúc thư mục

```
dataset/
├── cheating/
│   ├── images/
│   │   ├── train/      ← 80% ảnh train
│   │   └── val/        ← 20% ảnh val
│   └── labels/
│       ├── train/      ← annotations YOLO format
│       └── val/
├── raw/                ← Ảnh gốc chưa label
└── data.yaml           ← Tự động tạo bởi train_yolo.py
```

## Classes cần label

| ID | Tên class     | Mô tả                              | Số ảnh cần |
|----|---------------|-------------------------------------|------------|
| 0  | earphone      | Tai nghe nhét tai, tai nghe không dây | ≥ 500     |
| 1  | phone         | Điện thoại (đang nhìn/cầm)         | ≥ 500      |
| 2  | cheat_sheet   | Phao thi, tờ giấy nhỏ, tài liệu   | ≥ 300      |

## Cách thu thập ảnh

### 1. Quay video giả lập
- Setup giống phòng thi: bàn, ghế, không gian hẹp
- Camera đặt phía trước (góc tương tự camera phòng thi)
- Quay ≥ 30 phút video cho mỗi scenario

### 2. Trích frame từ video
```python
import cv2, os

def extract_frames(video_path, output_dir, interval=10):
    """Trích 1 frame mỗi N frames."""
    os.makedirs(output_dir, exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    count = 0
    saved = 0
    while True:
        ret, frame = cap.read()
        if not ret: break
        if count % interval == 0:
            cv2.imwrite(f"{output_dir}/frame_{saved:05d}.jpg", frame)
            saved += 1
        count += 1
    cap.release()
    print(f"Extracted {saved} frames")

extract_frames("video_gian_lan.mp4", "dataset/raw/earphone", interval=10)
```

### 3. Nguồn ảnh bổ sung
- **Roboflow Universe**: tìm "earphone detection", "phone detection"
  - https://universe.roboflow.com/search?q=earphone
- **Google Images**: download bằng `icrawler`
- **COCO dataset**: đã có phone (class 67) có thể reuse

## Gán nhãn (Labeling)

### Dùng LabelImg (offline, đơn giản)
```bash
pip install labelImg
labelImg dataset/raw/earphone dataset/cheating/labels/train
```
- Chọn format **YOLO** trong LabelImg
- Annotation file .txt cùng tên với ảnh

### Dùng Roboflow (online, mạnh hơn)
1. Upload ảnh lên https://roboflow.com
2. Label bằng web interface
3. Export → **YOLOv8 format**
4. Download về `dataset/cheating/`

## Format annotation YOLO (.txt)

Mỗi dòng: `<class_id> <x_center> <y_center> <width> <height>`
- Tất cả giá trị normalized từ 0 đến 1
- Ví dụ: `0 0.512 0.345 0.123 0.089`  ← earphone ở giữa ảnh

## Data Augmentation (tự động khi train)
Script train đã bật augmentation:
- Flip ngang 50%
- Brightness/Contrast thay đổi
- Mosaic (ghép 4 ảnh)
- Scale thay đổi

## Tips để đạt chất lượng tốt

1. **Đa dạng góc độ**: chụp tai nghe từ trái, phải, front
2. **Đa dạng ánh sáng**: sáng mạnh, thiếu sáng, đèn huỳnh quang
3. **Nhiều người**: tóc dài che tai nghe, kính, mũ
4. **Negative samples**: ảnh không có đối tượng (cần để giảm false positive)
5. **Tỷ lệ TV/V**: nên có ~10-20% ảnh "negative" (không có vật thể nào)
