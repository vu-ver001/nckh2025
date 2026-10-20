# KỊCH BẢN ĐỌC THUYẾT TRÌNH EXAMGUARD

**Thời lượng:** khoảng 6–7 phút  
**Cách dùng:** đọc phần dưới mỗi slide; nội dung trong *[ngoặc vuông]* là chỉ dẫn, không đọc thành tiếng.

---

## Slide 1 — Trang bìa

*[Nhìn hội đồng]*

Kính thưa quý thầy cô trong hội đồng!

Em xin đại diện nhóm trình bày đề tài **“Nghiên cứu ứng dụng thuật toán YOLO và framework MediaPipe trong hệ thống giám sát phát hiện gian lận thi cử”**, với tên hệ thống là **ExamGuard**.

Đề tài được thực hiện bởi các sinh viên Vương Anh Vũ, Vũ Duy Tiến, Nguyễn Ngọc Anh, Nguyễn Thị Kim Tuyến và Nguyễn Thị Khánh Vân, dưới sự hướng dẫn của Thạc sĩ Cao Thị Thoa.

---

## Slide 2 — Đặt vấn đề

Trong một ca thi, giám thị phải quan sát đồng thời nhiều vị trí nên rất khó theo dõi liên tục tất cả chi tiết.

Từ thực tế đó, nhóm xây dựng ExamGuard như một **công cụ hỗ trợ giám sát**. Hệ thống nhận hình ảnh từ camera hoặc video, phát hiện điện thoại, sách, tài liệu và một số tín hiệu tư thế đáng chú ý, sau đó gửi cảnh báo kèm thời điểm và ảnh chụp để giám thị kiểm tra.

Nhóm xin nhấn mạnh rằng ExamGuard **không tự kết luận thí sinh gian lận và không thay thế giám thị**. Quyết định cuối cùng luôn thuộc về con người.

---

## Slide 3 — Kiến trúc hệ thống

Về kiến trúc, đầu tiên OpenCV đọc từng khung hình từ webcam hoặc video. Hình ảnh sau đó được đưa vào hai nhánh xử lý song song.

Nhánh thứ nhất sử dụng YOLO-World kết hợp YOLOv8n chuyên biệt để phát hiện vật thể, đặc biệt là điện thoại. Nhánh thứ hai sử dụng MediaPipe Pose và Hands để trích xuất 33 điểm cơ thể và 21 điểm trên mỗi bàn tay.

Kết quả được đưa vào **Fusion Engine** để kiểm tra tính liên tục theo thời gian và tính điểm rủi ro. FastAPI tiếp nhận kết quả, truyền video qua MJPEG, gửi cảnh báo qua WebSocket, ghi log và lưu ảnh sự kiện. Cuối cùng, dashboard React hiển thị thông tin để giám thị xác minh.

---

## Slide 4 — Thuật toán và model

Hệ thống sử dụng bốn thành phần chính.

YOLO-World, với checkpoint `yolov8s-worldv2`, phát hiện zero-shot các vật thể cần rà soát. Một model YOLOv8n được fine-tune riêng cho điện thoại, với ngưỡng confidence tối thiểu là 0,30.

MediaPipe Pose Landmarker cung cấp 33 điểm cơ thể để tạo tín hiệu quay đầu, cúi đầu và vị trí tay. MediaPipe Hand Landmarker cung cấp 21 điểm mỗi bàn tay để hỗ trợ phát hiện tay gần tai.

Để giảm nhiễu, điện thoại chỉ tạo sự kiện sau ít nhất 3 quan sát, kéo dài tối thiểu 0,2 giây và có vị trí tương đối liên tục. Các tín hiệu quay đầu, cúi đầu hay tay gần tai chỉ là dấu hiệu cần xem lại, không phải bằng chứng đủ để kết luận gian lận.

---

## Slide 5 — Dataset và thực nghiệm

Dữ liệu huấn luyện điện thoại được lấy từ CITW, được mô tả là tập con điện thoại của COCO 2017.

Tập dữ liệu gồm **1.600 ảnh train**, với 2.177 bounding box, và **214 ảnh validation**, với 262 bounding box điện thoại. Model YOLOv8n được huấn luyện 40 epoch, batch size 16 trên Google Colab.

Ngoài ra, workspace có 6 video thử nghiệm gồm các tình huống: bình thường, viết bài, dùng máy tính, dùng hộp bút hoặc sổ, điện thoại rõ và điện thoại khó. Tổng thời lượng khoảng 194 giây, ở phạm vi một người và một camera.

Nhãn thời gian của video hiện vẫn là nhãn sơ bộ, chưa phải kết quả nghiệm thu tại phòng thi thật.

---

## Slide 6 — Kết quả thực nghiệm

Trên cùng 214 ảnh validation, checkpoint phone v2 đạt precision 23,03%, recall 15,65% và F1 18,64%.

Checkpoint phone v3 đang sử dụng đạt **precision 61,39%, recall 47,33% và F1 53,45%**. Kết quả này cho thấy phone v3 cải thiện rõ rệt so với phiên bản trước trong cùng điều kiện đánh giá.

Trên 6 video thử nghiệm, hệ thống phát hiện được **4 trên 4 episode có điện thoại** theo nhãn sơ bộ. Độ trễ cảnh báo đầu tiên từ 0,75 đến 2,05 giây. Tốc độ xử lý đạt từ 9,65 đến 10,95 FPS trên máy CPU kiểm thử.

Tuy nhiên, hệ thống còn tạo ra **6 cảnh báo điện thoại ngoài khoảng nhãn**. Vì dữ liệu còn ít và nhãn chưa được duyệt chính thức, nhóm không gọi kết quả 4 trên 4 là độ chính xác 100%.

Về phần mềm, 63 trên 63 kiểm thử hồi quy đã đạt và pipeline đã hoạt động end-to-end.

---

## Slide 7 — Hạn chế và hướng phát triển

Hệ thống hiện còn bốn hạn chế chính.

Thứ nhất, hệ thống chưa được kiểm thử trong phòng thi thật, mà mới ở quy mô một người và một camera. Thứ hai, hệ thống chưa hỗ trợ theo dõi nhiều thí sinh. Thứ ba, dữ liệu huấn luyện chủ yếu là ảnh đời thường nên còn khác với bối cảnh phòng thi. Thứ tư, cảnh báo nhầm vẫn xảy ra và khả năng phát hiện điện thoại rất nhỏ còn thấp.

Trong thời gian tới, nhóm định hướng thu thập dữ liệu đúng bối cảnh phòng thi, bổ sung multi-object tracking, xây dựng mô hình hành vi theo chuỗi thời gian, tối ưu tốc độ xử lý và hoàn thiện quy trình bảo vệ dữ liệu cá nhân.

---

## Slide 8 — Kết luận

*[Nói chậm lại]*

Tóm lại, ExamGuard là nguyên mẫu hỗ trợ giám sát một người, một camera, kết hợp YOLO, MediaPipe và Fusion Engine để phát hiện vật thể, phân tích tín hiệu tư thế và tạo cảnh báo theo thời gian.

Nhóm đã xây dựng được pipeline hoạt động end-to-end và ghi nhận sự cải thiện rõ rệt của checkpoint phone v3. Tuy nhiên, hệ thống vẫn cần thêm dữ liệu và thử nghiệm thực tế trước khi triển khai trong phòng thi.

Phần trình bày của nhóm em đến đây là kết thúc. Em xin trân trọng cảm ơn quý thầy cô đã lắng nghe và rất mong nhận được ý kiến đóng góp!

---

## Năm ý cần nhớ nếu không đọc nguyên văn

1. ExamGuard chỉ **hỗ trợ**, không tự kết luận gian lận.
2. Phạm vi hiện tại là **một người, một camera**.
3. Phone v3 đạt Precision **61,39%**, Recall **47,33%**, F1 **53,45%**.
4. Video pilot phát hiện **4/4 episode**, nhưng có **6 cảnh báo ngoài khoảng nhãn**.
5. Nếu chưa có minh chứng, trả lời: **“Nhóm chưa có đủ dữ liệu để kết luận và xác định đây là nội dung cần đánh giá tiếp.”**
