# ExamGuard — trạng thái và cách chạy

Bản cập nhật 06/09/2026. Demo FastAPI dùng **YOLO-World + phone_v3_colab + MediaPipe Pose và Hands**; đã kiểm tra video, cảnh báo WebSocket, snapshot và start/stop qua API. YOLO-Pose được giữ làm lựa chọn đối chiếu. **Không train cục bộ.** Hướng dẫn hiện hành: [Demo Colab](docs/DEMO_COLAB.md). Bản sửa báo cáo theo bằng chứng: [REPORT_REVISED_2026-09-06.md](docs/REPORT_REVISED_2026-09-06.md).

**Chưa nghiệm thu chất lượng nhận diện.** Trên cùng 214 ảnh validation có điện thoại, tại confidence 0,30 và IoU 0,50: Colab đạt precision 61,39%, recall 47,33%; v2 đạt 23,03% và 15,65%. Đây không phải chất lượng toàn hệ thống trong phòng thi. Sáu video quay thử độc lập và nhãn vẫn còn thiếu. Các checkpoint CPU/legacy được giữ riêng, không dùng làm mặc định demo.

## Chạy trên máy hiện tại

Mở PowerShell tại thư mục chứa README này. Python và Node đang dùng đã kiểm tra: Python 3.14, Node 24.12.

Terminal 1:

```powershell
.\scripts\start_demo.ps1 -Video .\video\01_binh_thuong.mp4.mp4
```

Terminal 2:

```powershell
cd dashboard
npm.cmd ci
npm.cmd run dev
```

Mở http://127.0.0.1:5173 rồi chọn một nguồn trong mục **Nguồn demo**. Chọn **Webcam trực tiếp** để dùng camera 0 của máy trình diễn, hoặc chọn một trong sáu video. Bấm **Bắt đầu** để chạy, **Dừng** để kết thúc, hoặc **Chạy lại từ đầu** để phát lại video đang chọn. Dashboard không tự bật camera khi chỉ mở trang; webcam chỉ được mở sau khi chọn nguồn và bấm **Bắt đầu**. Có thể đổi nguồn ngay trên dashboard mà không cần khởi động lại backend; `/status` và WebSocket báo lỗi nếu webcam, video hoặc model không hoạt động.

Muốn trình diễn webcam ngay từ đầu, chạy backend không truyền `-Video`:

```powershell
.\scripts\start_demo.ps1
```

Dùng video thay camera: đặt biến sau **trước khi chạy backend**, rồi khởi động lại backend:

```powershell
$env:EXAMGUARD_VIDEO_SOURCE = 'D:\duong-dan\video-kiem-thu.mp4'
```

Không đặt biến thì backend dùng camera 0; tùy chọn **Webcam trực tiếp** trên dashboard cũng chuyển về camera này. Có thể đặt `EXAMGUARD_LOG_DIR`, `EXAMGUARD_SNAPSHOT_DIR` để tách dữ liệu kiểm thử. Khi hết video, phiên tự dừng; webcam tiếp tục chạy cho đến khi bấm **Dừng**.

## Cài lại môi trường

```powershell
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements-dev.txt
cd dashboard
npm.cmd ci
```

Cần Git để cài CLIP theo commit được ghim. Model YOLO-World/Pose và CLIP có thể được tải khi chạy lần đầu. Các gói trực tiếp được ghim; môi trường cài mới hoàn toàn chưa được kiểm thử. Môi trường hiện có đã import, build và chạy tích hợp thành công.

Tải và kiểm tra model MediaPipe trước lần chạy đầu: `venv\Scripts\python.exe scripts/prepare_mediapipe.py`. Script lưu SHA256 và URL nguồn. Dùng `start_demo.ps1 -Video <video> -PoseBackend yolo` để đối chiếu YOLO-Pose; mặc định là `mediapipe` và không fallback âm thầm nếu lỗi. Các entrypoint desktop cũ chưa được chuyển sang pipeline này; dùng hướng dẫn FastAPI ở trên cho demo nghiên cứu.

## Kiểm tra lại

```powershell
$env:PYTHONUTF8 = '1'
$env:YOLO_CONFIG_DIR = "$PWD/artifacts"
.\venv\Scripts\python.exe -m unittest discover -s tests -v
.\venv\Scripts\python.exe scripts/audit_dataset.py --dataset dataset/phone_detection_v2 --output artifacts/dataset-audit-v2.json
cd dashboard
npm.cmd run build
```

`scripts/smoke_api.py` chạy start/stop, đọc video và cảnh báo từ backend. Chỉ chạy khi backend được cấu hình với video kiểm thử; kết quả lưu trong `artifacts/integration-smoke-current.json`.

## Dataset và huấn luyện lại

- `dataset/phone_detection`: giữ nguyên ảnh/nhãn cũ; bỏ đường dẫn máy cũ khỏi YAML.
- `dataset/phone_detection_v2`: bản sao riêng, giữ 2 class và train/val gốc, chuyển polygon thành bounding box để thống nhất định dạng. `provenance.json` ghi nguồn mapping và phép chuyển đổi.
- `scripts/prepare_corrected_dataset.py --source-config <data.yaml-goc>` tái tạo bản sửa; từ chối ghi đè thư mục đã có.
- `models/phone_v1`: không dùng các chỉ số của model này làm độ chính xác điện thoại.

Sau khi review nhãn và chọn tài nguyên tính toán:

```powershell
.\venv\Scripts\python.exe train/train_phone.py --epochs 80 --device cpu
.\venv\Scripts\python.exe scripts/evaluate_phone.py
```

Train mới ghi vào `models/phone_v2`, từ chối ghi đè run đã có. Script kiểm tra cấu trúc dataset trước khi train, tự chạy evaluation sau khi train thành công và ghi trạng thái vào `artifacts/phone-v2-pipeline.json`. Evaluation kiểm tra mapping model và trả chỉ số riêng từng class. Lượt train cũ ghi thời lượng khoảng 3 giờ 36 phút trên CPU; đây chỉ là tham chiếu, chưa dự báo cho dữ liệu sửa.

Checkpoint `weights/best.pt` không tự kích hoạt. Sau khi review kết quả, đặt `EXAMGUARD_PHONE_CONFIRM_MODEL` tới checkpoint được chọn và khởi động lại backend, hoặc lưu checkpoint đã review thành `models/phone_v2/reviewed.pt`. Cách này tránh dùng model chưa train/evaluate xong.

## Giới hạn hiện tại

- Một nguồn video; phân tích tư thế lấy người đầu tiên do model trả về, chưa theo dõi từng thí sinh.
- Điểm cảnh báo là quy tắc theo frame; chưa hiệu chuẩn tỷ lệ báo động nhầm và ảnh hưởng FPS.
- Lịch sử dashboard chỉ giữ 100 sự kiện gần nhất của phiên trình duyệt; log máy chủ lưu riêng trong CSV. Chưa có API truy vấn lịch sử lâu dài.
- Trang cài đặt là bản xem thử đã vô hiệu hóa, chưa chỉnh cấu hình backend.
- FastAPI + React là luồng được kiểm tra. Flask, CLI và script thử cũ được giữ nhưng chưa kiểm tra toàn luồng.
- Chưa triển khai công khai; build frontend không đồng nghĩa đã triển khai.

Xem `docs/STATUS.md` và `docs/ACCEPTANCE.md` để theo dõi việc còn lại.
