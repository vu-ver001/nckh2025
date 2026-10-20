# Kết quả video bổ sung

Ngày kiểm tra workspace: 08/09/2026  
Trạng thái: **CHƯA THỰC HIỆN — thiếu video và nhãn được review**.

## Dữ liệu hiện có

`demo/recordings/manifest.json` mô tả sáu clip dự kiến và ghi rõ mục đích không đưa video vào train:

| Clip | Kịch bản dự kiến | File trong workspace | Nhãn thời gian |
|---|---|---|---|
| normal_01.mp4 | Ngồi làm bài | Không tìm thấy | `null` |
| normal_02.mp4 | Viết và nhìn xuống giấy | Không tìm thấy | `null` |
| objects_01.mp4 | Máy tính Casio | Không tìm thấy | `null` |
| objects_02.mp4 | Hộp bút hoặc sổ | Không tìm thấy | `null` |
| phone_01.mp4 | Điện thoại rõ | Không tìm thấy | `null` |
| phone_02.mp4 | Điện thoại xa hoặc bị che | Không tìm thấy | `null` |

Các file `.avi` trong `artifacts/` là fixture hoặc input được tạo cho kiểm thử kỹ thuật, không phải sáu video độc lập và không được dùng làm dữ liệu nghiên cứu phòng thi.

## Kết quả kiểm tra tự động ngày 08/09

`artifacts/research/video-ablation-20260908-pending.json` ghi `status=missing_video_or_labels`, `ready_clips=0`, `runs=0`. `artifacts/research/full-pipeline-20260908-pending.json` ghi cả sáu clip là `missing_video_or_labels`. Hai file này là bằng chứng trạng thái thiếu dữ liệu; không phải kết quả đánh giá chất lượng.

## Chưa được phép điền

Chưa điền TP, FP, FN, precision, recall, F1 sự kiện, false alarms/minute, độ trễ hoặc FPS video nhóm. Không dùng `null` để đại diện cho “không có điện thoại”; chỉ đổi thành `[]` sau khi người review xem và xác nhận clip âm tính.

## Quy trình khi nhận video

1. Giữ bản gốc, ghi người quay, mã người/phiên, ngày, góc camera, độ phân giải, FPS và SHA256.
2. Kiểm tra video đọc được và cập nhật metadata; không đưa video vào train.
3. Người review gán khoảng `PHONE_DETECTED` theo thời điểm điện thoại nhìn thấy; người thứ hai kiểm tra trước khi xem dự đoán.
4. Khóa checkpoint/ngưỡng hiện tại trước khi chạy: phone Colab, World, combined và temporal. Nếu chỉnh ngưỡng theo video này, đổi vai trò thành tập hiệu chỉnh.
5. Chạy `scripts/evaluate_phone_ablation.py` và `scripts/evaluate_demo_videos.py`, lưu output với tên mới; không ghi đè các kết quả cũ.
6. Tách lỗi detector (không có box điện thoại) khỏi lỗi luật (có box nhưng không tạo cảnh báo hoặc ngược lại). Nếu không có bbox ground truth, chỉ báo phân loại lỗi theo review thủ công.

## Kết quả sẽ được cập nhật theo bảng này

| Clip | Thời lượng | Sự kiện thật | Sự kiện phát hiện | Bỏ sót | Cảnh báo nhầm | Độ trễ đầu tiên | FPS | Trạng thái review |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| normal_01 | Chưa có | Chưa có | Chưa có | Chưa có | Chưa có | Chưa có | Chưa có | Chờ video/nhãn |
| normal_02 | Chưa có | Chưa có | Chưa có | Chưa có | Chưa có | Chưa có | Chưa có | Chờ video/nhãn |
| objects_01 | Chưa có | Chưa có | Chưa có | Chưa có | Chưa có | Chưa có | Chưa có | Chờ video/nhãn |
| objects_02 | Chưa có | Chưa có | Chưa có | Chưa có | Chưa có | Chưa có | Chưa có | Chờ video/nhãn |
| phone_01 | Chưa có | Chưa có | Chưa có | Chưa có | Chưa có | Chưa có | Chưa có | Chờ video/nhãn |
| phone_02 | Chưa có | Chưa có | Chưa có | Chưa có | Chưa có | Chưa có | Chưa có | Chờ video/nhãn |

Tập này chỉ đủ làm pilot một người/một nguồn video. Không suy rộng thành hiệu năng cho nhiều thí sinh hoặc phòng thi thật.
