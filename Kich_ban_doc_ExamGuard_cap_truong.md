# KỊCH BẢN THUYẾT TRÌNH EXAMGUARD — CẤP TRƯỜNG

**Đối tượng:** Hội đồng gồm cả thành viên không thuộc Công nghệ thông tin  
**Thời lượng:** khoảng 6–7 phút  
**Lưu ý:** Nội dung trong *[ngoặc vuông]* là chỉ dẫn, không đọc thành tiếng.

---

## Slide 1 — Trang bìa

*[Nhìn hội đồng]*

Kính thưa quý thầy cô trong hội đồng!

Em xin đại diện nhóm trình bày đề tài **“Nghiên cứu ứng dụng thuật toán YOLO và framework MediaPipe trong hệ thống giám sát phát hiện gian lận thi cử”**, với tên gọi **ExamGuard**.

Đề tài được thực hiện dưới sự hướng dẫn của Thạc sĩ Cao Thị Thoa. Trong phần trình bày, em xin tập trung vào ba nội dung: bài toán, cách hệ thống hoạt động và kết quả thực nghiệm.

---

## Slide 2 — Vấn đề đặt ra

Trong một ca thi, giám thị phải quan sát nhiều thí sinh cùng lúc nên có thể bỏ qua những diễn biến xảy ra trong thời gian ngắn.

Nhóm đặt ra câu hỏi: **Trí tuệ nhân tạo có thể giúp giám thị tìm nhanh những thời điểm cần chú ý hay không?**

ExamGuard được xây dựng để phát hiện điện thoại, tài liệu và một số tín hiệu tư thế đáng chú ý, sau đó gửi cảnh báo kèm ảnh chụp để giám thị xem lại.

Hệ thống **không tự kết luận thí sinh gian lận**. Một người cúi đầu có thể chỉ đang viết bài. Vì vậy, máy chỉ hỗ trợ sàng lọc; con người luôn đưa ra quyết định cuối cùng.

---

## Slide 3 — Hệ thống hoạt động như thế nào?

Có thể hình dung ExamGuard gồm ba phần: **camera quan sát, bộ phận phân tích và màn hình cảnh báo**.

Camera cung cấp hình ảnh cho hai nhánh xử lý. Nhánh thứ nhất tìm các đồ vật như điện thoại hoặc tài liệu. Nhánh thứ hai tạo một “bộ khung ảo” từ các điểm trên cơ thể và bàn tay để quan sát quay đầu, cúi đầu hoặc đưa tay gần tai.

Hệ thống kết hợp hai nguồn thông tin và theo dõi chúng theo thời gian. Khi đủ điều kiện, cảnh báo cùng thời điểm và ảnh chụp được gửi lên dashboard để giám thị kiểm tra.

---

## Slide 4 — Công nghệ cốt lõi

Hệ thống sử dụng hai nhóm công nghệ chính là **YOLO** và **MediaPipe**.

YOLO giúp máy tính khoanh vùng và nhận diện đồ vật trong ảnh. Nhóm kết hợp một model nhận diện nhiều vật thể với một model được huấn luyện riêng cho điện thoại.

MediaPipe xác định 33 điểm trên cơ thể và 21 điểm trên mỗi bàn tay. Từ đó, hệ thống tạo tín hiệu về tư thế; đây không phải công nghệ đọc suy nghĩ hay tự xác định hành vi gian lận.

Để giảm nhiễu, điện thoại phải xuất hiện ít nhất ba lần quan sát và kéo dài tối thiểu 0,2 giây mới tạo sự kiện.

---

## Slide 5 — Dữ liệu và thử nghiệm

Model điện thoại được huấn luyện từ tập dữ liệu CITW, có nguồn từ COCO 2017. Dữ liệu gồm **1.600 ảnh huấn luyện** và **214 ảnh dùng để đánh giá trong quá trình phát triển**. Điện thoại trong ảnh được đánh dấu bằng khung chữ nhật để model học vị trí.

Nhóm cũng sử dụng sáu video thử nghiệm với các tình huống bình thường, viết bài, dùng máy tính, dùng hộp bút và hai tình huống có điện thoại.

Tổng thời lượng video khoảng 194 giây, ở quy mô một người và một camera. Nhãn video mới được đánh dấu sơ bộ, nên chưa thể xem đây là thử nghiệm chính thức trong phòng thi thật.

---

## Slide 6 — Kết quả đạt được

Model điện thoại đang dùng đạt **precision 61,39%**. Có thể hiểu là trong các lần hệ thống dự đoán có điện thoại, khoảng 61% khớp với nhãn theo điều kiện đánh giá.

**Recall đạt 47,33%**, nghĩa là hệ thống mới tìm được gần một nửa số điện thoại đã được đánh dấu và vẫn còn bỏ sót. Chỉ số tổng hợp F1 đạt **53,45%**, cao hơn phiên bản cũ là 18,64%.

Trên sáu video, hệ thống phát hiện được **4 trên 4 khoảng có điện thoại** theo nhãn sơ bộ, với độ trễ từ 0,75 đến 2,05 giây và tốc độ khoảng 10 khung hình mỗi giây.

Tuy nhiên, hệ thống cũng tạo **6 cảnh báo ngoài khoảng đã đánh dấu**. Vì vậy, nhóm không gọi kết quả 4 trên 4 là độ chính xác 100%. Kết luận trung thực là model đã có tiến bộ nhưng vẫn còn cả bỏ sót và cảnh báo nhầm.

---

## Slide 7 — Hạn chế và hướng phát triển

Nguyên mẫu hiện mới hoạt động ở quy mô **một người và một camera**, chưa theo dõi riêng nhiều thí sinh trong một phòng. Dữ liệu huấn luyện chủ yếu là ảnh đời thường nên chưa phản ánh đầy đủ góc quay, ánh sáng và che khuất trong phòng thi. Điện thoại nhỏ còn khó phát hiện và cảnh báo nhầm vẫn tồn tại.

Hướng tiếp theo là thu thập dữ liệu đúng bối cảnh phòng thi, bổ sung khả năng theo dõi nhiều người, phân tích hành vi theo chuỗi thời gian và tối ưu tốc độ. Nếu triển khai thực tế, hệ thống cũng phải có quy định rõ về thông báo ghi hình, quyền truy cập và thời hạn lưu dữ liệu.

---

## Slide 8 — Kết luận

*[Nói chậm lại]*

Tóm lại, ExamGuard là nguyên mẫu sử dụng trí tuệ nhân tạo để hỗ trợ giám thị tìm những thời điểm cần chú ý trong video thi.

Nhóm đã xây dựng được quy trình hoàn chỉnh từ tiếp nhận hình ảnh đến phát cảnh báo trên giao diện, đồng thời ghi nhận model mới cải thiện rõ rệt so với phiên bản trước.

Tuy nhiên, đây mới là bước đầu và chưa phải sản phẩm có thể triển khai ngay trong phòng thi. Hệ thống vẫn cần thêm dữ liệu, thử nghiệm độc lập và đánh giá về quyền riêng tư.

Em xin trân trọng cảm ơn quý thầy cô đã lắng nghe và rất mong nhận được ý kiến đóng góp!

---

## Giải thích nhanh thuật ngữ khi được hỏi

| Thuật ngữ | Cách giải thích dễ hiểu |
|---|---|
| YOLO | Công cụ khoanh vùng và nhận diện đồ vật trong ảnh |
| MediaPipe | Công cụ xác định các điểm trên cơ thể và bàn tay |
| Model | Chương trình đã học từ dữ liệu để đưa ra dự đoán |
| Precision | Trong các lần máy báo có điện thoại, tỷ lệ khớp với nhãn thật |
| Recall | Trong số điện thoại có trong dữ liệu, tỷ lệ máy tìm thấy |
| FPS | Số khung hình được xử lý trong một giây |

## Ba điều cần nhớ

1. Nói **“hỗ trợ giám thị”**, không nói “tự động xác định gian lận”.
2. Không nói “độ chính xác 100%”; báo cáo cả kết quả đúng, bỏ sót và cảnh báo nhầm.
3. Nếu chưa có bằng chứng, trả lời: **“Trong phạm vi hiện tại, nhóm chưa có đủ dữ liệu để kết luận và xác định đây là nội dung cần đánh giá tiếp.”**
