# Checklist nghiệm thu đề xuất

Ngày lập: 05/09/2026. Chưa được owner/reviewer phê duyệt; không phải cam kết deadline.

| Mã | Tiêu chí / bằng chứng cần có | Trạng thái |
|---|---|---|
| T01 | Dashboard build thành công | Đạt trên máy hiện tại |
| T02 | API startup, status và WebSocket hoạt động | Đạt kiểm thử |
| T03 | Phân biệt tai nghe/điện thoại; không dùng detection cũ để xác nhận liên tiếp | Đạt kiểm thử hồi quy |
| T04 | Start không tạo trùng worker; lỗi camera/model được báo và tài nguyên được đóng | Đạt kiểm thử |
| T05 | Video → model thật → cảnh báo → dashboard; MJPEG giải mã được; Dừng về FPS 0 | Kiểm tra tích hợp với video ghép ảnh validation; không thay cho kiểm thử phòng thi |
| T06 | Model Colab và fallback phản ánh đúng trạng thái nạp, không dựa vào tồn tại file | Đạt kiểm thử API/constructor; thấy tên Colab trên dashboard khi chạy |
| T07 | Kiểm thử hồi quy và build dashboard | 35 tests pass, npm run build thành công ngày 06/09 |
| D01 | Mapping dataset đúng; nhãn hợp lệ và không trộn box/polygon | Bản v2 đạt kiểm tra cấu trúc |
| D02 | Review chất lượng nhãn bằng mắt, kiểm tra rò rỉ theo người/video gốc | Chưa thực hiện; hash không phát hiện ảnh gần giống |
| M01 | Train model phone_v2; đánh giá riêng class phone | Xong 80/80 epoch, validation 17:54 ngày 05/09/2026; P 70,44%, R 73,17%, mAP50 80,37% cho phone |
| M02 | Đánh giá độc lập trên video phòng thi có nhãn | Thiếu video và nhãn |
| M03 | So sánh v2/Colab trên cùng 214 ảnh, confidence 0,30, IoU 0,50 | Hoàn tất; xem artifacts/phone-colab-comparison.json |
| M04 | Chuẩn bị bộ đo 6 video một người, ghi nhận thiếu dữ liệu trung thực | Có manifest/công cụ/hướng dẫn; chưa có 6 video thực tế |
| U01 | Reviewer chạy và xác nhận checklist bản bàn giao | Chưa có reviewer |

## Quyết định cần chốt

1. Deadline demo/nghiệm thu; owner, reviewer và người phê duyệt.
2. Đã chốt phạm vi demo: một nguồn video quay thử, một người; chưa có tracking nhiều thí sinh.
3. Đã chuyển demo sang checkpoint Colab sau kiểm thử tích hợp; không train cục bộ.
4. Tiêu chí định lượng: precision/recall từng cảnh báo, báo động nhầm/giờ, FPS tối thiểu và độ trễ cảnh báo.

## Bộ video đánh giá cần chuẩn bị

Lập danh sách video bình thường và video có hành vi mục tiêu, gồm nhiều người/góc quay/ánh sáng; tách người hoặc phiên quay khỏi dữ liệu train. Mỗi đoạn cần nhãn loại sự kiện và thời gian bắt đầu/kết thúc. Chưa có bộ này nên không đặt số lượng tối thiểu hoặc ngưỡng đạt thay người phê duyệt.

Thứ tự đề xuất: review dữ liệu → train/evaluate model đúng mapping → đo toàn hệ thống trên video độc lập → điều chỉnh ngưỡng → reviewer xác nhận. Người thực hiện và hạn từng bước đang chờ phân công.
