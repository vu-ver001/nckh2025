> Tài liệu trước đợt tích hợp MediaPipe và chuẩn hóa thời gian ngày 06/09. Các mô tả YOLO-Pose/đếm frame và số kiểm thử dưới đây là lịch sử. Xem REPORT_REVISED_2026-09-06.md và NEXT_STEPS_2026-09-07.md cho phiên bản hiện hành.

# Hồ sơ thực nghiệm — bản làm việc 06/09/2026

**Cập nhật từ người dùng:** hạn cấp Trường áp dụng cho nhóm là 09/09/2026; báo cáo đã qua cấp Khoa có nội dung/số liệu tự tạo hoặc phóng đại. Ưu tiên đính chính theo bằng chứng và trao đổi với GVHD về hồ sơ đã nghiệm thu; kết quả thực nghiệm mới phải ghi đúng ngày và điều kiện, không dùng để hợp thức hóa số liệu cũ. Phần ghi chưa xác nhận hạn bên dưới là trạng thái trước câu trả lời này.

Đã nhận báo cáo của nhóm và thông báo giải thưởng ngày 06/09; tên đề tài có hai biến thể, yêu cầu MediaPipe chưa khớp mã hiện tại. Hạn hồ sơ trong thông báo là 09/09/2026, chưa xác nhận áp dụng cho nhóm. Thành phần hồ sơ, thông tin nhóm/GVHD và các chênh lệch được ghi tại `docs/DOCUMENT_REVIEW_2026-09-06.md`. Tài liệu này ghi phương pháp và bằng chứng hiện có, không thay cho đề cương được giảng viên phê duyệt.

## Câu hỏi và phạm vi

Mục tiêu kỹ thuật đã chốt là demo một nguồn video, một người. Hệ thống phát hiện vật thể/hành vi cần xem xét, không chứng minh một người gian lận. YOLO-World cung cấp vật thể, checkpoint phone xác nhận điện thoại, YOLO-Pose cung cấp keypoint, quy tắc fusion tích lũy điểm và cảnh báo. Những thành phần này không phải thuật toán mới do đề tài tự phát minh.

Hai câu hỏi cần tách biệt:

1. Checkpoint điện thoại nào phù hợp hơn với tập ảnh đang đánh giá? Đã có so sánh v2/Colab cùng điều kiện.
2. Hệ thống đầy đủ có phát hiện các sự kiện mục tiêu trên video quay thử, với bao nhiêu bỏ sót/cảnh báo nhầm và độ trễ? Chưa có dữ liệu thực tế để trả lời.

## Bằng chứng đã có

| Thực nghiệm | Đơn vị và chỉ số | Kết quả / phạm vi kết luận |
|---|---|---|
| So sánh checkpoint | 214 ảnh, 262 phone; micro P/R/F1 ở conf 0,30, IoU 0,50 | Colab P/R/F1 = 61,39/47,33/53,45%; riêng detector, không phải hệ thống cảnh báo |
| Bootstrap ghép cặp | 2.000 lần lấy lại mẫu theo ảnh, seed 42 | Khoảng thăm dò có điều kiện; không khắc phục thiên lệch chọn model trên validation |
| Tích hợp model thật | Ảnh validation được chọn rồi lặp thành video | Đã xác minh video/cảnh báo/snapshot/dashboard; không phải đo độ chính xác độc lập |
| Hồi quy mã | 39 kiểm thử và build frontend | Chứng minh các tình huống phần mềm được kiểm thử, không chứng minh hiệu quả nhận diện trong phòng thi |
| Sáu clip thực tế | Mỗi clip khoảng 30 giây, một người | Còn thiếu video và nhãn; không có kết quả để điền |

Hồ sơ máy đọc được, bảng CSV, biểu đồ PNG/PDF và hướng dẫn chạy lại nằm tại `artifacts/research`. Checksum checkpoint/dữ liệu, phiên bản runtime, bbox và TP/FP/FN từng ảnh được lưu trong `phone-comparison.json`. Phép so sánh mới tái tạo đúng TP/FP/FN của lần trước. Chỉ train trên Colab nếu sau đánh giá có căn cứ cần train; không tự resume các lượt CPU cũ.

## Quy trình video độc lập

Theo `docs/DEMO_COLAB.md`: 2 clip làm bài bình thường, 2 clip với vật dễ nhầm, 2 clip có điện thoại rõ/khó. Đây là pilot demo, chưa đủ để suy rộng cho nhiều thí sinh, nhiều camera, nhiều phòng thi.

Trước chạy đánh giá, người quay ghi điều kiện ánh sáng, góc đặt camera, độ phân giải/FPS gốc và mã phiên quay; gán khoảng bắt đầu/kết thúc cho từng sự kiện. Dùng `[]` cho clip được review là không có sự kiện; `null` khi chưa review. Nhãn không lấy từ output model. Nếu dùng clip để chỉnh ngưỡng, đổi vai trò clip đó thành dữ liệu hiệu chỉnh và quay clip/phiên khác cho đánh giá cuối. Không chia các frame cùng phiên sang train và test.

Chạy `scripts/evaluate_demo_videos.py` với manifest để lấy số sự kiện phát hiện/bỏ sót, cảnh báo ngoài khoảng nhãn, trễ theo thời gian video và FPS xử lý. Báo cáo thêm số cảnh báo gốc và thời lượng từng clip; không làm tròn tỷ lệ thành tuyên bố chất lượng khi mẫu ít. Với clip quá ngắn, số cảnh báo/giờ quy đổi không phải phép đo giám sát dài hạn.

Độ trễ hiện đo trên thời gian video, chưa gồm mạng/trình duyệt. Cooldown API dùng thời gian xử lý thực, điểm và ngưỡng tư thế còn phụ thuộc số frame. Phải ghi các giới hạn này khi so sánh tốc độ máy hoặc FPS nguồn. Chưa có tiêu chí nghiệm thu định lượng được thống nhất.

## Chẩn đoán lỗi trước khi bổ sung dữ liệu

- Model không thấy phone thật: review bbox, độ che, kích thước, ánh sáng; đây là ứng viên bổ sung dữ liệu.
- Detector thấy đúng nhưng fusion không cảnh báo: kiểm tra xác nhận, ghép box và persistence trước khi train.
- Vật được phép gây cảnh báo: review nhãn và quy tắc loại chồng lấn; ảnh âm tính chỉ được dùng train sau khi kiểm tra không còn điện thoại bị bỏ nhãn.
- Hành vi bình thường bị báo: kiểm tra keypoint, quy tắc và thời gian, không dùng train detector phone để sửa lỗi tư thế.

V2 và Colab khác dữ liệu/batch/số epoch; kết quả hiện tại không cô lập tác động của một thay đổi thuật toán. Để chứng minh đóng góp từng khối cần ablation trên cùng video độc lập, khóa model/nguồn dữ liệu/ngưỡng trước khi đo. Chưa có ablation nên không viết kết luận về đóng góp định lượng của fusion hay YOLO-World.

## Nguồn phương pháp

- [Cheng và cộng sự, YOLO-World (2024)](https://arxiv.org/abs/2401.17270): phương pháp phát hiện vật thể với tập nhãn mở. Không dùng FPS trong bài báo làm FPS đo trên máy dự án.
- [Lin và cộng sự, Microsoft COCO (2014)](https://arxiv.org/abs/1405.0312): dữ liệu vật thể trong cảnh đời thường; bản thân COCO không phải benchmark phòng thi.
- [SciPy: bootstrap](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html): lấy mẫu ghép cặp và khoảng bootstrap. Triển khai dự án dùng percentile minh bạch cho phân tích thăm dò, không mặc định coi khoảng này là kết luận suy rộng.

## Điều kiện để hoàn tất bài nghiên cứu

Cần tên đề tài/đề cương và quy cách bàn giao; video độc lập có nhãn; kết quả thực nghiệm được kiểm tra; thảo luận giới hạn và đóng góp không vượt bằng chứng; báo cáo/slide theo yêu cầu trường. Các mục này chưa đủ để đánh dấu toàn bộ đề tài hoàn thành.
