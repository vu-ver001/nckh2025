# Việc tiếp theo trước hạn 09/09/2026

## Những việc đã làm

MediaPipe Pose + Hands thật; checkpoint Colab; thời gian theo video; ghép box không nhân bản; công cụ đối chứng; 57 kiểm thử; build dashboard; luồng model thật → cảnh báo → snapshot. Thành phần chạy ổn định 30 phút trên video kỹ thuật trước sửa ghép box cuối cùng. Báo cáo Word sửa dùng bằng chứng thật đã được chuẩn bị.

## Lịch và người phụ trách

| Hạn đề xuất | Việc | Người phụ trách | Điều kiện hoàn thành |
|---|---|---|---|
| 07/09 trước quay | Xác nhận tên đề tài, nơi đã nộp và cách đính chính | Đại diện nhóm + GVHD/Khoa | Có câu trả lời của người phụ trách hồ sơ |
| 07/09 | Quay sáu clip khoảng 30 giây | Nhóm | Video gốc, cùng góc camera dự kiến, một người mỗi clip |
| 07/09 sau quay | Ghi nhãn thời điểm, người quay, người kiểm tra | Hai thành viên nhóm | Khoảng xuất hiện/biến mất đã review |
| Sau khi có video và nhãn | Chạy đối chứng A/B/C/D và luồng đầy đủ | Trợ lý | JSON thô, checksum, bảng số đếm và lỗi mỗi clip |
| 08/09 | Review lỗi, cập nhật báo cáo/slide theo số thật | Trợ lý + nhóm + GVHD | Mọi kết luận truy được đến dữ liệu; bỏ kết quả không có bằng chứng |
| Trước hạn 09/09 | Hoàn thiện và nộp hồ sơ đúng mẫu | Đại diện nhóm + GVHD/Khoa | Xác nhận đủ giấy tờ và đã tiếp nhận |

Các ngày này là kế hoạch, không phải việc đã hoàn thành. Chưa biết giờ chốt ngày 09/09; nhóm cần kiểm tra đầu mối nhận hồ sơ.

## Chuẩn bị video và nhãn

Đặt file trong `demo/recordings/`: normal_01.mp4, normal_02.mp4, objects_01.mp4, objects_02.mp4, phone_01.mp4, phone_02.mp4. Giữ cả bản gốc. Góc nhìn cần thấy mặt, hai tay và mặt bàn theo vị trí camera định dùng. Hai clip đầu ngồi viết/nhìn xuống giấy; hai clip tiếp Casio/hộp bút/sổ; hai clip cuối phone rõ và phone xa/che. Không đưa các clip này vào train.

Sửa `demo/recordings/manifest.json`: chỉ đổi `events: null` thành danh sách sau khi xem và gán nhãn. `[]` nghĩa đã review và không có sự kiện cần chấm, không có nghĩa chưa biết. Ví dụ cấu trúc dưới đây chỉ minh họa, phải thay bằng mốc thật:

```json
{"type":"PHONE_DETECTED","start":5.2,"end":12.8}
```

Ghi thêm `recorded_by`, `reviewed_by`, `session_id`, `participant_id`, góc và độ phân giải vào từng clip. Nhãn PHONE_DETECTED là điện thoại nhìn thấy, không phải kết luận gian lận. Đánh giá hành vi cần bảng định nghĩa nhãn và gán nhãn riêng đầy đủ; thiếu nhãn hành vi thì không gọi cảnh báo hành vi là false positive chắc chắn.

## Chạy sau khi có nhãn

Mở PowerShell tại thư mục chứa `src`, `scripts`, `venv`. Các lệnh sau chỉ suy luận/đánh giá, không train:

```powershell
venv\Scripts\python.exe scripts/evaluate_phone_ablation.py --output artifacts/research/video-ablation-20260907.json
venv\Scripts\python.exe scripts/evaluate_phone_ablation.py --variants combined temporal --allowed-filter --output artifacts/research/video-allowed-filter-20260907.json
$env:EXAMGUARD_POSE_BACKEND='mediapipe'
venv\Scripts\python.exe scripts/evaluate_demo_videos.py --output artifacts/research/full-pipeline-20260907.json
```

Chạy tuần tự, tắt các tác vụ AI khác nếu đo tốc độ. Giữ output từng lần, dùng tên mới khi chạy lại. Đối chứng chính tắt pose và phủ quyết vật được phép; B và C sau sửa tương đương về box phone, nên tác động cần kiểm chứng là temporal và phủ quyết, không được khẳng định kết hợp hai model tốt hơn. Latency trong JSON theo thời gian video, chưa bao gồm mạng/hiển thị. Tính FP trên phút video âm tính và số TP/FP/FN từng clip; không dùng số frame làm cỡ mẫu độc lập.

## Quyết định train

Chưa cần bắt đầu lượt train mới trước khi có video và review lỗi. Đã có 280 ảnh ứng viên COCO trong `dataset/phone_negative_candidates`; 75 ảnh kích hoạt checkpoint ở confidence 0,30 cần review. Không tự coi ảnh thiếu annotation phone là âm tính chuẩn. Nếu lỗi thuộc model, review nhãn rồi tạo phiên bản dataset mới, loại trùng và giữ split theo phiên/nguồn. Train bằng notebook Colab hiện có, nhập ZIP/checkpoint riêng và kiểm tra checksum. Không train trên máy này.

## Hồ sơ học thuật

Đọc bản sửa `deliverables/Bao_cao_sua_de_GVHD_ra_soat_2026-09-06.docx` với GVHD. Các số cũ 91,2%, 85,3%, 52 FPS chưa có bằng chứng nên không dùng. Kết quả mới không xác nhận ngược các số đã nêu trước đây. Chưa có mẫu poster/cam kết chính thức hoặc xác nhận hồ sơ đã gửi tới đâu; người trong nhóm cần lấy các thông tin này. Trợ lý chưa gửi hay nộp tài liệu cho bên ngoài.
