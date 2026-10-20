# Demo một nguồn video hoặc webcam — model Google Colab

Không chạy train cục bộ. Checkpoint dùng cho demo là `models/phone_v3_colab/weights/best.pt`, SHA256 `e54b53aa88083d9e047227a7a6db4fc313c400ad81443d03bca50064cc8ed857`. Checkpoint CPU tại `models/phone_v3` được giữ nguyên.

## Chạy demo

Backend mặc định là MediaPipe Pose + Hands. Model đã tải trong `models/mediapipe`; máy mới chạy `venv\Scripts\python.exe scripts/prepare_mediapipe.py`. Chọn `-PoseBackend yolo` khi cần đối chiếu YOLO-Pose. `/status` trả `model.pose` và dashboard hiển thị backend thực tế; lỗi nạp MediaPipe làm phiên báo lỗi.

Từ thư mục dự án chứa `src`, chạy backend trong PowerShell với đường dẫn video thật:

```powershell
.\scripts\start_demo.ps1 -Video .\video\01_binh_thuong.mp4.mp4
```

Khi cần trình bày trực tiếp bằng webcam, chạy không truyền `-Video`:

```powershell
.\scripts\start_demo.ps1
```

Nếu máy có nhiều camera và camera cần dùng không ở chỉ số 0, chỉ định chỉ số đó:

```powershell
.\scripts\start_demo.ps1 -CameraIndex 1
```

Chỉ dùng một trong `-Video` và `-CameraIndex`.

Backend thử lần lượt DirectShow, Media Foundation và lựa chọn tự động trên Windows. Nếu cả ba đều không mở được, kiểm tra **Camera access**, **Let desktop apps access your camera**, màn trập/privacy mode của laptop và đóng Camera/Teams/Zoom/OBS trước khi khởi động lại backend.

Trong terminal thứ hai:

```powershell
cd dashboard
npm run dev -- --host 127.0.0.1
```

Mở http://127.0.0.1:5173. Trong mục **Nguồn demo**, chọn **Webcam trực tiếp** để dùng camera 0 của máy hoặc chọn một trong sáu video, sau đó bấm **Bắt đầu**. Khi cần đổi nguồn, bấm **Dừng**, chọn nguồn mới rồi bấm **Bắt đầu**; nút **Chạy lại từ đầu** phát lại video đang chọn hoặc khởi động lại webcam. **Dừng** đóng nguồn và đưa FPS về 0. Không cần khởi động lại backend khi chuyển giữa webcam và sáu video trong thư mục `video/`. Nếu máy không có camera hoặc camera đang bị ứng dụng khác khóa, dashboard giữ nguyên lỗi thực tế từ backend. Nếu cổng 8000 đã có backend, dừng backend cũ trước khi chạy. Backend hiện được khởi động cho kiểm thử bằng `artifacts/technical-fixture.avi` — video lặp ảnh validation, không phải video phòng thi.

Danh sách video được lấy từ `video/` và chỉ cho phép sáu kịch bản đã chuẩn bị: bình thường, viết bài, máy tính, hộp bút/sổ, điện thoại rõ và điện thoại khó. Backend kiểm tra tên tệp và không cho dashboard mở tệp ngoài thư mục demo; webcam dùng camera chỉ số 0. Trạng thái trên dashboard luôn hiển thị model đã nạp, nguồn hiện tại (webcam hay video) và lỗi/fallback thực tế.

Thông tin model trong `/status` và heartbeat WebSocket gồm `configured_phone`, `loaded_phone`, `phone_name`, `detector`, `status`, `error`. `not_loaded` là chưa nạp hoặc đã dừng; `loaded` là nạp thành công; `fallback` là đang dùng detector nền thiếu model xác nhận. Tồn tại file không được xem là đã nạp model. Lỗi toàn phiên được trả qua `error` như trước.

## So sánh checkpoint

```powershell
.\venv\Scripts\python.exe scripts/compare_phone_v3.py --models models/phone_v2/weights/best.pt models/phone_v3_colab/weights/best.pt
.\venv\Scripts\python.exe scripts/check_trained_phone.py --model models/phone_v3_colab/weights/best.pt
```

Cùng 214 ảnh, 262 điện thoại được gán nhãn; confidence 0,30, IoU matching 0,50, NMS IoU 0,45, imgsz 640:

| Model | TP | FP | FN | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|---:|
| phone_v2 | 41 | 137 | 221 | 23,03% | 15,65% | 18,64% |
| phone_v3_colab | 124 | 78 | 138 | 61,39% | 47,33% | 53,45% |

Kết quả nằm trong `artifacts/phone-colab-comparison.json`. Đây là detector riêng trên ảnh COCO có điện thoại, không phải precision toàn hệ thống hoặc báo động nhầm/giờ trong phòng thi. Metrics trong ZIP Colab dùng điểm vận hành validation khác, nên không bằng bảng này.

## Sáu video độc lập còn thiếu

Quay một người ở cùng góc camera, khoảng 30 giây mỗi đoạn: 2 cảnh làm bài/viết/nhìn giấy; 2 cảnh dùng Casio/hộp bút/sổ; 2 cảnh điện thoại rõ và xa/bị tay che. Đặt sáu tệp theo tên trong `video/` để dashboard tự hiển thị. Khi đo định lượng, cập nhật manifest đánh giá riêng với tên tệp và nhãn thời gian thực tế.

Sau khi review, thay `events: null` bằng `[]` nếu đoạn không có sự kiện cần cảnh báo, hoặc danh sách như:

```json
[{"type": "PHONE_DETECTED", "start": 5.0, "end": 18.5}]
```

Thời gian tính bằng giây từ đầu video. Ghi đầy đủ các sự kiện thuộc phạm vi kiểm thử; đoạn chỉ viết và nhìn giấy bình thường dùng `[]`. Gộp các khoảng cùng loại bị chồng lấn. Để `null` khi chưa review; không tự suy ra nhãn từ tên file. Không đưa video này vào train.

```powershell
.\venv\Scripts\python.exe scripts/evaluate_demo_videos.py
```

Báo cáo `artifacts/demo-video-evaluation.json` ghi rõ video/nhãn thiếu, số sự kiện phát hiện/bỏ sót, cảnh báo ngoài khoảng nhãn, độ trễ theo thời gian video, FPS xử lý và detections theo từng lần YOLO chạy. FPS này chưa gồm render/dashboard, độ trễ chưa gồm WebSocket/trình duyệt. API và evaluator hiện lấy mẫu detector mỗi 0,1 giây nguồn; xác nhận phone qua ba quan sát trong ít nhất 0,2 giây, reset nếu gap >0,5 giây; cooldown 10 giây nguồn. Score tăng mỗi loại tối đa một lần/giây và giảm theo giây sạch. Các ngưỡng mới chưa được hiệu chỉnh trên video phòng thi. Entry point cũ không truyền timestamp còn dùng chế độ tương thích theo frame.

## Đối chứng phone riêng

Chạy `venv\Scripts\python.exe scripts/evaluate_phone_ablation.py --output artifacts/research/video-ablation-RUN.json` với tên output mới cho từng lần đo. Bốn cấu hình là world, phone, combined, temporal. Không nạp model nếu chưa có video và nhãn. Script giữ checksum code/model/video/manifest, prediction từng mẫu, ghép một-một các đợt sự kiện, số notification sau cooldown và tốc độ. Pose tắt; bộ lọc allowed mặc định tắt cho so sánh chính. Có thể chạy riêng `--variants combined temporal --allowed-filter` để đo bộ lọc mà không trộn với thí nghiệm chính. Không dùng kết quả `technical-ablation.json` làm chất lượng phòng thi.

## Điều kiện hoàn thành và bước sau

Demo kỹ thuật cần: nạp đúng checksum Colab; video, cảnh báo, snapshot hoạt động; bắt đầu/dừng đúng; client chậm không dừng xử lý. Video lặp ảnh được chọn vì model nhận ra chỉ chứng minh kết nối kỹ thuật.

Kiểm chứng ngày 08/09: 63 tests pass, frontend build thành công, API nguồn webcam trả đúng camera 0; dashboard đã kiểm tra tên `phone_v3_colab`, video và cảnh báo điện thoại; nút Dừng trả về chưa giám sát. Logic tay gần vùng tai yêu cầu giữ khoảng 2 giây hoặc lặp 3 lần trong 20 giây; nhãn tai nghe từ YOLO-World không còn tự tạo cảnh báo. Chưa mở camera vật lý trong lượt kiểm thử này. Bộ đo offline được chạy thử trên 24 frame ảnh lặp: 1 sự kiện kỳ vọng/1 phát hiện, 0 cảnh báo ngoài nhãn, trễ 0,6 giây theo video. Tệp `artifacts/technical-video-evaluation.json` chỉ kiểm chứng công cụ đo, không dùng các số này làm kết quả thực nghiệm phòng thi.

Đánh giá thực tế còn chờ sáu video và nhãn. Đối chiếu quan sát detector với sự kiện fusion để phân loại lỗi model, ngưỡng hoặc logic; detections trên frame chưa đủ để xác nhận bbox đúng nếu thiếu bbox ground truth. Chưa quyết định train thêm. Nếu cần, bổ sung dữ liệu âm tính đã review và điện thoại nhỏ/xa/che; train bằng notebook Colab và kiểm tra checksum kết quả nhập về. Chưa hỗ trợ tracking nhiều thí sinh.
