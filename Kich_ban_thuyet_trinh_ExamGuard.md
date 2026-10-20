# KỊCH BẢN THUYẾT TRÌNH — ĐỀ TÀI EXAMGUARD
### Ứng dụng YOLO và MediaPipe trong hệ thống giám sát phát hiện gian lận thi cử
**Thời lượng mục tiêu:** 5–7 phút | **Số slide:** 8 | **Đối tượng:** Hội đồng cấp trường

> Toàn bộ số liệu trong kịch bản này lấy trực tiếp từ `TONG_QUAN_HE_THONG.md`. Không thêm số liệu suy đoán — nếu hội đồng hỏi điều gì ngoài tài liệu, hãy trả lời trung thực là "chưa có minh chứng" thay vì đoán, xem mục Q&A ở cuối file.

---

## CÁCH DÙNG FILE NÀY

1. Đọc phần **"Lời thuyết trình"** để luyện nói — có thể diễn đạt lại theo giọng văn của bạn, miễn giữ đúng số liệu.
2. Copy phần **"Prompt cho Canva AI"** dán vào ô nhập của Canva AI (Magic Design / trình tạo bài thuyết trình bằng AI) để tạo bố cục & hình minh họa cho từng slide.
3. Có **1 prompt tổng** ở mục dưới đây — dùng để tạo cả bộ slide cùng lúc bằng Canva AI. Sau đó dùng các prompt riêng từng slide để tinh chỉnh/tạo lại hình minh họa nếu cần.

---

## PROMPT TỔNG (dán vào Canva AI để tạo cả bộ slide 1 lần)

```
Tạo bài thuyết trình khoa học 8 slide, phong cách học thuật - công nghệ, tối giản,
tông màu xanh navy + trắng + cam nhấn (màu cảnh báo), font sans-serif hiện đại,
dùng icon flat-design, biểu đồ/sơ đồ đơn giản, không dùng ảnh người thật.

Chủ đề: ExamGuard - Nghiên cứu ứng dụng thuật toán YOLO và framework MediaPipe
trong hệ thống giám sát hỗ trợ phát hiện gian lận thi cử. Đây là hệ thống HỖ TRỢ
giám thị, không tự động kết luận hay xử lý kỷ luật thí sinh.

Cấu trúc 8 slide:
1. Trang bìa: tên đề tài, tên nhóm/tác giả, đơn vị, GVHD
2. Đặt vấn đề: khó khăn của giám thị khi coi thi, mục tiêu hệ thống hỗ trợ
3. Kiến trúc hệ thống: sơ đồ luồng camera -> YOLO + MediaPipe -> Fusion Engine -> cảnh báo -> dashboard
4. Thuật toán & model: YOLO-World zero-shot, YOLOv8n fine-tuned phát hiện điện thoại,
   MediaPipe Pose 33 điểm + Hands 21 điểm/tay
5. Dataset & thực nghiệm: dữ liệu CITW/COCO cho điện thoại, 6 video tự quay 1 người/1 camera
6. Kết quả: bảng so sánh 2 checkpoint (precision/recall/F1), kết quả 6 video test
7. Hạn chế & hướng phát triển: liệt kê ngắn gọn 4-5 hạn chế chính và hướng cải thiện
8. Kết luận: tóm tắt đóng góp, lời cảm ơn hội đồng

Giữ chữ trên mỗi slide tối đa ~40 từ, ưu tiên số liệu và sơ đồ hơn văn bản dài.
```

---

## SLIDE 1 — TRANG BÌA

**Nội dung hiển thị:**
- Tên đề tài: *Nghiên cứu ứng dụng thuật toán YOLO và framework MediaPipe trong hệ thống giám sát phát hiện gian lận thi cử*
- Tên hệ thống: **ExamGuard**
- Nhóm thực hiện / Sinh viên thực hiện: `[điền tên]`
- Giảng viên hướng dẫn: `[điền tên]`
- Đơn vị: Khoa Công nghệ thông tin — Trường Đại học Tài nguyên và Môi trường Hà Nội

**Lời thuyết trình (~15 giây):**
> "Kính thưa hội đồng, em xin trình bày đề tài: Nghiên cứu ứng dụng thuật toán YOLO và framework MediaPipe trong hệ thống giám sát phát hiện gian lận thi cử, với tên gọi hệ thống là ExamGuard."

**Prompt Canva AI:**
```
Slide bìa thuyết trình khoa học, nền navy gradient tối giản, biểu tượng camera
giám sát cách điệu góc dưới, tiêu đề lớn ở giữa "ExamGuard", phụ đề nhỏ hơn:
"Nghiên cứu ứng dụng YOLO và MediaPipe trong giám sát hỗ trợ phát hiện
gian lận thi cử". Khoảng trống cho tên nhóm, GVHD, đơn vị ở góc dưới.
```

---

## SLIDE 2 — ĐẶT VẤN ĐỀ

**Nội dung hiển thị:**
- Giám thị phải quan sát nhiều vị trí cùng lúc, khó theo dõi liên tục mọi chi tiết
- ExamGuard: nguyên mẫu **hỗ trợ** — không thay thế giám thị, không tự kết luận
- Mục tiêu: phát hiện vật thể (điện thoại, tài liệu) + tín hiệu tư thế bất thường → cảnh báo kèm ảnh chụp để con người xem lại

**Lời thuyết trình (~45 giây):**
> "Trong một ca thi, giám thị phải quan sát đồng thời nhiều vị trí và rất khó theo dõi liên tục mọi chi tiết trên video. Xuất phát từ thực tế đó, nhóm em xây dựng ExamGuard như một **nguyên mẫu hỗ trợ giám sát**: hệ thống tiếp nhận hình ảnh từ camera hoặc video, phát hiện vật thể và tư thế đáng chú ý, sau đó gửi cảnh báo kèm thời điểm và ảnh chụp để con người xem lại. Em xin nhấn mạnh: hệ thống chỉ tạo tín hiệu để giám thị kiểm tra, **không tự động kết luận hay xử lý kỷ luật thí sinh**."

**Prompt Canva AI:**
```
Slide đặt vấn đề, layout 2 cột. Cột trái: icon giám thị đứng giữa nhiều bàn thi
với các mũi tên tỏa ra thể hiện "khó quan sát cùng lúc". Cột phải: 3 bullet point
ngắn về mục tiêu hệ thống (phát hiện vật thể, phát hiện tư thế, gửi cảnh báo cho
con người xác minh). Có 1 dòng nhấn mạnh dạng badge màu cam: "Hệ thống HỖ TRỢ,
không thay thế giám thị". Tông màu navy - trắng - cam.
```

---

## SLIDE 3 — KIẾN TRÚC HỆ THỐNG

**Nội dung hiển thị (sơ đồ luồng, 6 bước):**
1. Camera/video → OpenCV đọc khung hình
2. YOLO-World + YOLOv8n phone detector (song song với) MediaPipe Pose + Hands
3. Fusion Engine: kết hợp bằng chứng, tính điểm rủi ro theo thời gian
4. FastAPI backend
5. Video MJPEG + cảnh báo WebSocket + CSV/snapshot
6. Dashboard React — giám thị xác minh và quyết định cuối cùng

**Lời thuyết trình (~60 giây):**
> "Về kiến trúc, hệ thống gồm sáu bước. Đầu tiên, OpenCV đọc khung hình từ webcam hoặc video. Hai nhánh xử lý chạy song song: một bên là YOLO-World kết hợp YOLOv8n chuyên biệt để phát hiện vật thể như điện thoại, sách, tài liệu; bên còn lại là MediaPipe Pose và Hands trích xuất ba mươi ba điểm cơ thể và hai mươi mốt điểm mỗi bàn tay. Hai luồng bằng chứng này được đưa vào **Fusion Engine** — nơi áp dụng ngưỡng hình học, tính liên tục theo thời gian và tính điểm rủi ro tổng hợp. Kết quả được FastAPI xử lý, truyền video có chú thích qua MJPEG, gửi cảnh báo qua WebSocket, đồng thời ghi log CSV và ảnh snapshot. Cuối cùng, dashboard React hiển thị tất cả để giám thị xác minh — **quyết định cuối cùng luôn thuộc về con người**."

**Prompt Canva AI:**
```
Sơ đồ luồng (flowchart) ngang, phong cách flat-design tối giản, 6 khối nối bằng
mũi tên: [Camera/Video] -> [OpenCV đọc khung hình] -> hai nhánh song song
[YOLO phát hiện vật thể] và [MediaPipe Pose+Hands] -> hợp lại tại [Fusion Engine
- tính điểm rủi ro] -> [FastAPI Backend] -> [Dashboard React - giám thị xác minh].
Mỗi khối là hình chữ nhật bo góc, icon nhỏ minh họa bên trong, màu navy/xanh dương
nhạt, mũi tên màu cam. Không dùng ảnh người thật.
```

---

## SLIDE 4 — THUẬT TOÁN VÀ MODEL

**Nội dung hiển thị (bảng tóm tắt):**

| Thành phần | Model | Vai trò |
|---|---|---|
| YOLO-World | `yolov8s-worldv2.pt` | Phát hiện zero-shot vật thể cần rà soát |
| Phone detector | YOLOv8n fine-tuned (`phone_v3_colab`) | Phát hiện điện thoại, conf ≥ 0,30 |
| MediaPipe Pose | Pose Landmarker Lite, 33 điểm | Quay đầu, cúi đầu, tay bất thường |
| MediaPipe Hands | Hand Landmarker, 21 điểm/tay | Tay gần tai |

- Một điện thoại chỉ tạo cảnh báo sau ≥ 3 quan sát, kéo dài ≥ 0,2 giây (tránh nhiễu 1 khung hình)
- **Không dùng** Face Mesh trong pipeline hiện hành

**Lời thuyết trình (~70 giây):**
> "Về mặt thuật toán, nhóm em dùng bốn model chính. YOLO-World — phiên bản `yolov8s-worldv2` — phát hiện vật thể theo kiểu zero-shot dựa trên danh sách prompt, ví dụ cell phone, cheat sheet, hidden note. Song song, một model YOLOv8n được fine-tune riêng để phát hiện điện thoại với độ tin cậy tối thiểu ba mươi phần trăm. Về phần tư thế, MediaPipe Pose Landmarker trích xuất ba mươi ba điểm cơ thể để nhận diện quay đầu, cúi đầu; MediaPipe Hands trích xuất hai mươi mốt điểm mỗi bàn tay để nhận diện tay gần tai. Một điểm quan trọng: để tránh cảnh báo giả do nhiễu một khung hình, hệ thống chỉ xác nhận sự kiện điện thoại sau **ít nhất ba lần quan sát liên tục**, kéo dài tối thiểu không phẩy hai giây. Hệ thống hiện **chưa dùng Face Mesh**."

**Prompt Canva AI:**
```
Slide dạng bảng so sánh 4 hàng, mỗi hàng có icon minh họa riêng: icon mắt/camera
cho YOLO-World, icon điện thoại cho phone detector, icon người với các chấm nối
xương (pose skeleton) cho MediaPipe Pose, icon bàn tay với chấm khớp ngón cho
MediaPipe Hands. Bên dưới bảng, 1 callout box nhỏ ghi "Cảnh báo chỉ kích hoạt
sau ≥3 lần quan sát liên tục - tránh nhiễu 1 khung hình". Tông màu navy - cam.
```

---

## SLIDE 5 — DATASET & THỰC NGHIỆM

**Nội dung hiển thị:**
- **Dữ liệu huấn luyện điện thoại:** nguồn CITW (tập con từ COCO 2017)
  - Train: 1.600 ảnh, 2.177 bounding box
  - Validation: 214 ảnh, 262 bounding box
  - Huấn luyện: YOLOv8n pretrained, 40 epoch, batch 16, Google Colab
- **Dữ liệu video tự thu thập:** 6 video, 1 người/1 camera, 720×1280, 30 FPS, tổng ~193,63 giây (bình thường, viết bài, dùng máy tính, hộp bút/sổ, điện thoại rõ, điện thoại khó)
- ⚠️ Nhãn video đang ở trạng thái **provisional** (sơ bộ, chưa duyệt chính thức)

**Lời thuyết trình (~45 giây):**
> "Về dữ liệu, phần phát hiện điện thoại được huấn luyện trên tập CITW — một tập con điện thoại trích từ COCO 2017 — gồm một nghìn sáu trăm ảnh huấn luyện và hai trăm mười bốn ảnh validation. Bên cạnh đó, nhóm tự quay sáu video một người một camera để kiểm thử toàn bộ pipeline, gồm các tình huống bình thường, viết bài, dùng máy tính, và hai video có điện thoại. Em xin lưu ý trung thực: nhãn thời gian trên các video này hiện đang ở trạng thái **sơ bộ**, nhóm cần xác nhận lại trước khi dùng làm kết quả nghiệm thu chính thức."

**Prompt Canva AI:**
```
Slide 2 khối dữ liệu song song. Khối trái "Dữ liệu ảnh" với icon ảnh/dataset,
số liệu lớn nổi bật "1.600 ảnh train / 214 ảnh validation". Khối phải "Dữ liệu
video tự quay" với icon camera/video, số liệu "6 video - 1 người/1 camera -
~193 giây". Thêm 1 nhãn nhỏ màu vàng/cam dạng cảnh báo: "Nhãn video: provisional
- chưa duyệt chính thức" để thể hiện sự trung thực khoa học.
```

---

## SLIDE 6 — KẾT QUẢ THỰC NGHIỆM

**Nội dung hiển thị (bảng so sánh checkpoint):**

| Checkpoint | Precision | Recall | F1 |
|---|---:|---:|---:|
| phone v2 | 23,03% | 15,65% | 18,64% |
| **phone v3 (đang dùng)** | **61,39%** | **47,33%** | **53,45%** |

**Kết quả trên 6 video thử nghiệm:**
- Phát hiện **4/4 episode điện thoại** (theo nhãn sơ bộ)
- Độ trễ cảnh báo đầu tiên: **0,75–2,05 giây**
- Tốc độ xử lý: **9,65–10,95 FPS**
- 6 cảnh báo điện thoại ngoài khoảng nhãn (cảnh báo nhầm)
- **63/63** kiểm thử hồi quy phần mềm đạt

**Lời thuyết trình (~70 giây):**
> "Về kết quả, checkpoint đang dùng — phone v3 Colab — đạt precision sáu mươi mốt phẩy ba chín phần trăm, recall bốn mươi bảy phẩy ba ba phần trăm, cải thiện rõ rệt so với checkpoint v2 trước đó. Trên sáu video thử nghiệm, hệ thống phát hiện được bốn trên bốn episode có điện thoại theo nhãn sơ bộ, với độ trễ cảnh báo đầu tiên khoảng không phẩy bảy mươi lăm đến hai phẩy không năm giây. Tốc độ xử lý đạt khoảng mười khung hình mỗi giây trên máy kiểm thử CPU. Em cũng xin báo cáo trung thực: có sáu cảnh báo điện thoại ngoài khoảng nhãn, tức là còn cảnh báo nhầm cần cải thiện. Về phần mềm, sáu mươi ba trên sáu mươi ba kiểm thử hồi quy đã đạt, luồng video-phát hiện-cảnh báo-dashboard chạy ổn định end-to-end."

**Prompt Canva AI:**
```
Slide kết quả, nửa trên là biểu đồ cột (bar chart) so sánh Precision/Recall/F1
giữa 2 checkpoint "phone v2" và "phone v3", cột phone v3 nổi bật màu cam cao
hơn hẳn, cột phone v2 màu xám nhạt. Nửa dưới là 4 ô số liệu (stat cards) dạng
lưới 2x2: "4/4 episode phát hiện", "0,75-2,05s độ trễ", "~10 FPS xử lý",
"63/63 test đạt". Tông màu navy - trắng - cam, số liệu in đậm cỡ lớn.
```

---

## SLIDE 7 — HẠN CHẾ & HƯỚNG PHÁT TRIỂN

**Nội dung hiển thị (chọn lọc, không liệt kê hết 10 mục để tránh rối):**

**Hạn chế chính:**
- Chưa thử nghiệm tại phòng thi thật (mới pilot 1 người/1 camera)
- Chưa hỗ trợ nhiều thí sinh cùng lúc (chưa có ID tracking)
- Dữ liệu huấn luyện lệch miền (ảnh đời thường, không phải ảnh phòng thi)
- Còn cảnh báo nhầm; vật thể nhỏ recall còn thấp (24,18%)

**Hướng phát triển:**
- Thu thập dữ liệu đúng bối cảnh phòng thi thật
- Thêm multi-object tracking cho nhiều thí sinh
- Xây dựng mô hình hành vi theo chuỗi thời gian
- Bổ sung quy trình bảo vệ dữ liệu cá nhân

**Lời thuyết trình (~45 giây):**
> "Nhóm em nhìn nhận rõ các hạn chế hiện tại. Thứ nhất, hệ thống chưa được thử nghiệm tại phòng thi thật, mới dừng ở quy mô một người một camera. Thứ hai, chưa hỗ trợ nhiều thí sinh cùng lúc do chưa có cơ chế theo dõi danh tính riêng biệt. Thứ ba, dữ liệu huấn luyện điện thoại đến từ ảnh đời thường nên có độ lệch miền so với môi trường phòng thi thực tế. Hướng phát triển tiếp theo, nhóm sẽ thu thập dữ liệu đúng bối cảnh phòng thi, bổ sung tính năng theo dõi nhiều thí sinh, xây dựng mô hình hành vi theo chuỗi thời gian thay vì chỉ dựa trên ngưỡng từng khung hình, và bổ sung quy trình bảo vệ dữ liệu cá nhân cho người dự thi."

**Prompt Canva AI:**
```
Slide 2 cột đối xứng, cột trái tiêu đề "Hạn chế" nền màu nhạt với icon cảnh báo,
4 bullet ngắn. Cột phải tiêu đề "Hướng phát triển" nền màu xanh lá nhạt với icon
mũi tên đi lên, 4 bullet ngắn tương ứng. Layout tối giản, không quá nhiều chữ,
tông màu navy - trắng, điểm nhấn cam cho cột trái và xanh lá cho cột phải.
```

---

## SLIDE 8 — KẾT LUẬN

**Nội dung hiển thị:**
- ExamGuard: nguyên mẫu hỗ trợ giám sát 1 người/1 camera, kết hợp YOLO + MediaPipe
- Đã chứng minh: pipeline hoạt động end-to-end, cải thiện rõ rệt qua các checkpoint
- Còn nhiều việc cần làm trước khi triển khai thực tế — đây là **bước đầu** có cơ sở khoa học
- Lời cảm ơn hội đồng

**Lời thuyết trình (~20 giây):**
> "Tóm lại, ExamGuard là một nguyên mẫu hỗ trợ giám sát ở quy mô một người một camera, kết hợp YOLO và MediaPipe với một Fusion Engine tính điểm rủi ro theo thời gian. Nhóm đã chứng minh được pipeline hoạt động ổn định end-to-end và có cải thiện rõ rệt qua các checkpoint, đồng thời cũng nhìn nhận thẳng thắn các hạn chế cần giải quyết trước khi triển khai thực tế. Em xin cảm ơn hội đồng đã lắng nghe và rất mong nhận được góp ý ạ."

**Prompt Canva AI:**
```
Slide kết luận, nền navy đậm, tiêu đề lớn "Cảm ơn hội đồng đã lắng nghe" ở giữa,
phía trên là 1 dòng tóm tắt ngắn về ExamGuard, icon check-mark hoặc icon bắt tay
cách điệu. Có thể thêm QR code placeholder hoặc dòng chữ nhỏ "Câu hỏi & góp ý"
ở góc dưới. Phong cách tối giản, đồng bộ với slide bìa.
```

---

## MẸO TRÌNH BÀY

- **Tốc độ nói:** ~150 từ/phút, dừng 1 nhịp sau mỗi số liệu quan trọng để hội đồng kịp ghi nhận.
- **Số liệu:** đọc tròn số khi nói (ví dụ "khoảng sáu mươi mốt phần trăm") thay vì đọc từng chữ số thập phân rườm rà.
- **Giữ thái độ trung thực khoa học** giống văn phong tài liệu gốc — đây là điểm cộng lớn với hội đồng cấp trường, vì thể hiện tư duy phản biện chứ không tô hồng kết quả.
- Tập luyện với đồng hồ bấm giờ 2–3 lần trước khi bảo vệ để không vượt quá 7 phút.

---

## DỰ TRÙ CÂU HỎI PHẢN BIỆN & GỢI Ý TRẢ LỜI

| Câu hỏi khả năng cao | Hướng trả lời (dựa trên tài liệu, không suy đoán thêm) |
|---|---|
| Hệ thống đã thử ở phòng thi thật chưa? | Chưa. Mới pilot 1 người/1 camera trên 6 video tự quay; đây là hạn chế đã nêu rõ trong nghiên cứu, hướng tiếp theo là thu thập dữ liệu đúng bối cảnh phòng thi. |
| Độ chính xác bao nhiêu %? | Không dùng "accuracy" vì bài toán detection cần đánh giá theo bounding box. Cụ thể: checkpoint v3 đạt precision 61,39%, recall 47,33%, F1 53,45% trên tập validation 214 ảnh. |
| Hệ thống có tự động phạt thí sinh không? | Không. Hệ thống chỉ tạo tín hiệu/cảnh báo kèm ảnh chụp để giám thị xem lại và ra quyết định cuối cùng. |
| Nếu nhiều thí sinh trong 1 khung hình thì sao? | Hiện MediaPipe chỉ lấy 1 người/khung hình, chưa có ID tracking cho nhiều người — đây là hạn chế đã nêu, hướng phát triển là thêm multi-object tracking. |
| Vấn đề quyền riêng tư/đạo đức khi giám sát bằng camera? | Nhóm nhận thức đây là vấn đề cần giải quyết; hướng phát triển có đề cập bổ sung quy trình bảo vệ dữ liệu cá nhân: thông báo ghi hình, thời hạn lưu trữ, kiểm soát truy cập và xóa dữ liệu theo quy định. |
| Tại sao không dùng Face Mesh để nhận diện gương mặt/ánh mắt? | Pipeline hiện tại chưa tích hợp Face Mesh; nhóm ưu tiên Pose + Hands trước để xử lý tư thế và vị trí tay, Face Mesh là hướng có thể mở rộng sau. |
| Tốc độ xử lý có đáp ứng thời gian thực không? | Đạt 9,65–10,95 FPS trên máy CPU kiểm thử (Ryzen 5 PRO 6650U), chưa đo độ trễ end-to-end qua trình duyệt; đây là điểm cần tối ưu thêm, hướng phát triển có đề cập ONNX/TensorRT hoặc quantization. |
| Tập validation có đáng tin cậy không, có bị overfitting không? | Cần lưu ý trung thực: tập 214 ảnh validation cũng được dùng để chọn checkpoint, nên không phải tập test độc lập — đây là hạn chế đã nêu, hướng khắc phục là xây tập test độc lập riêng theo người/phòng/phiên. |

