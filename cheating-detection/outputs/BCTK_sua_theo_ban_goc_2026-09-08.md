# BÁO CÁO TỔNG KẾT ĐỀ TÀI NGHIÊN CỨU KHOA HỌC SINH VIÊN

## BẢN SỬA PHỤC VỤ RÀ SOÁT VÀ XÁC NHẬN

**Năm học:** 2025–2026  
**Tên đề tài theo báo cáo gốc:** Nghiên cứu sử dụng thuật toán YOLO và framework MediaPipe trong hệ thống giám sát gian lận thi cử  
**Tên dùng thống nhất trong phần kỹ thuật:** Nghiên cứu ứng dụng thuật toán YOLO và framework MediaPipe trong hệ thống giám sát phát hiện gian lận thi cử  
**Ngành/lĩnh vực:** Công nghệ thông tin / Máy tính và Công nghệ thông tin  
**Đơn vị:** Khoa Công nghệ thông tin, Trường Đại học Tài nguyên và Môi trường Hà Nội  
**Sinh viên:** Vương Anh Vũ, Vũ Duy Tiến, Nguyễn Ngọc Anh, Nguyễn Thị Kim Tuyến, Nguyễn Thị Khánh Vân (ĐH13C8)  
**Giảng viên hướng dẫn:** ThS. Cao Thị Thoa  
**Ngày lập bản sửa:** 08/09/2026  

> **Tư cách của tài liệu.** Đây là bản sửa làm việc được đối chiếu từ tệp `C:\Users\T14s Gen 3\Downloads\NH8_1-VN_BCTK_HUNRE_NH_2026_11_30_Cao_Thi_Thoa.md` và các minh chứng đang có trong workspace. Tài liệu này chưa thay thế bản đã nộp hoặc biên bản nghiệm thu. Các con số trong bản gốc nhưng chưa truy được nguồn được hạ trạng thái, ghi là **chưa được xác nhận**, và không được dùng như kết quả của nghiên cứu.

## TÓM TẮT ĐIỀU HÀNH

Đề tài xây dựng một nguyên mẫu giám sát video một camera, kết hợp detector YOLO nhận diện điện thoại với MediaPipe Pose + Hands để trích xuất tín hiệu tư thế và bàn tay. Phiên bản có thể kiểm tra trong workspace hiện sử dụng checkpoint `phone_v3_colab` do nhóm nhập từ Google Colab, ngưỡng confidence 0,30, và pipeline xác nhận cảnh báo theo thời gian. Trên **214 ảnh validation**, checkpoint Colab đạt 124 TP, 73 FP, 138 FN ở IoU 0,50, tương ứng Precision 62,94%, Recall 47,33%, F1 54,03% theo phép ghép đã sửa. Phân tích theo kích thước cho thấy vật thể nhỏ hơn 0,25% diện tích ảnh chỉ đạt recall 24,18%; vì vậy chưa thể tuyên bố hệ thống đạt độ chính xác trên 90% hoặc sẵn sàng nghiệm thu thực địa.

Luồng kỹ thuật đã được kiểm tra bằng fixture lặp từ ảnh validation: nạp model, xử lý 24 frame, phát sự kiện `PHONE_DETECTED`, chụp snapshot HTTP 200 và dừng phiên. Bộ kiểm thử phần mềm hiện có đạt 57/57; một thử nghiệm ổn định 1.800,259 giây xử lý 6.460 frame trong 269 vòng lặp không lỗi. Đây là bằng chứng về tính đúng của nguyên mẫu, không phải đánh giá chất lượng trên camera phòng thi. Sáu video độc lập dự kiến quay cùng nhóm chưa có tệp và nhãn trong workspace, nên các mục về sự kiện phát hiện/bỏ sót, cảnh báo nhầm, độ trễ và FPS thực tế được để trạng thái **chưa đo**.

**Kết luận mức độ hoàn thành tại ngày 08/09/2026:** hoàn thành nguyên mẫu kỹ thuật và đánh giá detector trên validation; chưa hoàn thành đánh giá video độc lập, chưa có xác nhận nghiệm thu mới, chưa đủ căn cứ cho các tuyên bố triển khai phòng thi hoặc các số liệu trong báo cáo gốc chưa truy được nguồn.

## TÍNH MỚI VÀ SÁNG TẠO ĐƯỢC GHI NHẬN

Điểm mới của bản nguyên mẫu là ghép detector vật thể với MediaPipe Pose + Hands trong một pipeline có lưu vết model, nguồn video, sự kiện và snapshot. Điểm có giá trị phương pháp là thiết kế phép đối chứng để tách detector điện thoại, YOLO-World và luật fusion; đồng thời ghi rõ điều kiện đo và giới hạn của fixture. Bản sửa không gọi đây là một thuật toán mới, không khẳng định đã giải quyết đầy đủ nhận diện hành vi, và không nâng nguyên mẫu thành sản phẩm triển khai phòng thi.

## MỞ ĐẦU

### 1. Bối cảnh và vấn đề nghiên cứu

Giám sát thi cử bằng camera thường tạo ra lượng video lớn, trong khi giám thị phải đồng thời quan sát nhiều vị trí. Một hệ thống hỗ trợ có thể sàng lọc các khung hình nghi vấn để con người xem lại. Bài toán của đề tài là kiểm tra khả năng ghép hai loại tín hiệu: (i) vật thể có thể là điện thoại trong ảnh và (ii) các dấu hiệu hình học từ pose/hand landmarks. Tín hiệu đầu ra được thiết kế như cảnh báo hỗ trợ, không phải kết luận thí sinh gian lận.

### 2. Tính cần thiết

Giải pháp có ý nghĩa nghiên cứu ở việc xây dựng pipeline có thể lặp lại, ghi lại nguồn checkpoint, điều kiện đo và minh chứng. Giá trị của đề tài ở giai đoạn này là chứng minh nguyên mẫu và định lượng giới hạn; không gán cho mô hình quyền tự động xử lý kỷ luật hay thay thế giám thị.

### 3. Câu hỏi nghiên cứu

1. Checkpoint điện thoại được huấn luyện trên Google Colab có nạp và chạy ổn định trong pipeline cục bộ hay không?
2. Với cùng 214 ảnh validation và cùng điều kiện `confidence=0,30`, IoU ghép nhãn 0,50, checkpoint Colab cải thiện thế nào so với checkpoint `phone_v2`?
3. MediaPipe Pose + Hands có được nạp thật và tạo được landmark để cung cấp tín hiệu hỗ trợ hay không?
4. Luồng video → xác nhận điện thoại → cảnh báo → snapshot → dashboard có hoạt động liên tục, có lỗi dừng hoặc làm nghẽn client hay không?
5. Những trường hợp thất bại hiện tập trung ở vật thể nhỏ, bị che, sai nhãn hay ở luật cảnh báo?

### 4. Cách đọc bản sửa

- **Đã xác nhận:** có tệp kết quả, điều kiện đo và đường dẫn để mở lại.
- **Đã thực hiện nhưng giới hạn:** có kiểm tra kỹ thuật nhưng đầu vào là fixture hoặc không đại diện cho phòng thi.
- **Chưa đo/chưa xác nhận:** chưa có tệp hoặc chưa có người có thẩm quyền xác nhận; không được suy diễn thành đạt.
- **Cần nhóm/GVHD xác nhận:** nội dung hành chính, tình trạng nghiệm thu, quyền sử dụng dữ liệu, danh sách thành viên và việc sử dụng AI.

# CHƯƠNG 1. TỔNG QUAN CÁC VẤN ĐỀ NGHIÊN CỨU

## 1.1. Các công trình và hướng tiếp cận liên quan

Báo cáo gốc đã đặt vấn đề trong ba hướng: phát hiện vật thể bằng YOLO, trích xuất tư thế/hành vi bằng MediaPipe, và giám sát video có người kiểm tra cuối. Bản sửa giữ khung này nhưng thay cách trình bày từ tuyên bố hiệu quả sang câu hỏi có thể kiểm chứng.

### 1.1.1. Phát hiện vật thể trong video

YOLO là detector một giai đoạn, dự đoán bounding box và lớp trong một lần suy luận. Ưu điểm là pipeline gọn và có thể chạy gần thời gian thực; nhược điểm của nguyên mẫu này là vật thể điện thoại rất nhỏ trong ảnh, bị che hoặc có hình dạng tương tự vật dụng học tập. Vì vậy một dự đoán có confidence cao vẫn chỉ là ứng viên cần xem lại.

### 1.1.2. Pose và hand landmarks

MediaPipe Pose + Hands cung cấp các điểm hình học cho đầu, vai, khuỷu, cổ tay và bàn tay. Các điểm này được dùng để tạo biến quan sát như hướng quay đầu tương đối, tay đưa lên vùng mặt và trạng thái landmark không ổn định. Chúng không trực tiếp chứng minh hành vi gian lận; camera, ánh sáng, tư thế ngồi và độ che khuất có thể làm thay đổi điểm.

### 1.1.3. Kiến trúc lai và human-in-the-loop

Kiến trúc lai có thể giảm việc cảnh báo từ một frame đơn. Detector phát hiện điện thoại được ưu tiên làm tín hiệu vật thể; pose/hand chỉ làm tín hiệu hỗ trợ. Dashboard hiển thị bằng chứng (khung hình, confidence, thời điểm và snapshot) để người xem quyết định. Bản sửa không dùng cụm “tự động kết luận gian lận”.

## 1.2. Khoảng trống cần giải quyết

Các vấn đề thực tế của nguyên mẫu cần được đo riêng:

- Chưa có video độc lập đã gán mốc điện thoại xuất hiện/biến mất.
- Validation hiện có 214 ảnh và không đại diện cho mọi góc camera.
- Recall giảm mạnh với điện thoại rất nhỏ; một số box lệch nhẹ có thể bị tính là FN.
- Các ảnh âm tính do công cụ đề xuất mới là ứng viên, chưa được con người duyệt và chưa được đưa vào train.
- `YOLO-World` đang được dùng như nhánh cảnh báo/vật thể hỗ trợ trong dashboard; kết quả fixed ablation chưa chứng minh nó cải thiện nhận diện điện thoại so với checkpoint Colab.

## 1.3. Lý do chọn đề tài và đóng góp dự kiến

Đề tài phù hợp với một nghiên cứu nguyên mẫu vì có thể tái lập bằng checkpoint, manifest, cấu hình và log. Đóng góp được xác nhận ở giai đoạn này gồm: (i) pipeline kết hợp detector và landmarks, (ii) quy tắc cảnh báo có chống lặp theo thời gian, (iii) bộ đối chiếu detector có cùng điều kiện, và (iv) tài liệu hóa giới hạn để định hướng thu thập video và train tiếp. Hiệu quả sử dụng trong phòng thi là mục tiêu tiếp theo, chưa phải kết luận hiện tại.

# CHƯƠNG 2. MỤC TIÊU, ĐỐI TƯỢNG, PHẠM VI, NỘI DUNG VÀ PHƯƠNG PHÁP

## 2.1. Mục tiêu tổng quát

Xây dựng và kiểm chứng một nguyên mẫu một camera có khả năng phát hiện ứng viên điện thoại trong video, kết hợp tín hiệu pose/hand để tạo cảnh báo có bằng chứng và hiển thị trên dashboard.

## 2.2. Mục tiêu cụ thể và tiêu chí kiểm chứng

| Mục tiêu | Tiêu chí kiểm chứng | Trạng thái 08/09/2026 |
|---|---|---|
| Nạp checkpoint Colab | Model nạp được, ghi tên/đường dẫn/checksum, không âm thầm fallback | Đạt trong MC02, MC07; trạng thái dashboard cần nhóm xác nhận khi chạy phiên cuối |
| Định lượng detector | Cùng 214 ảnh validation, confidence 0,30, IoU 0,50; có TP/FP/FN/P/R/F1 | Đạt; MC03 và MC05 |
| Nạp Pose + Hands | Có model thật, version và số landmark | Đạt kiểm tra kỹ thuật; MC06 |
| Luồng tích hợp | Video → cảnh báo → snapshot → dashboard → dừng phiên | Đạt bằng fixture; MC07 |
| Kiểm thử phần mềm | Tất cả test hiện có và lỗi model/snapshot được kiểm tra | 57/57 đạt; MC08 |
| Đánh giá thực tế | Sáu video độc lập, mốc sự kiện, FP/FN, latency, FPS | Chưa bắt đầu vì thiếu video/nhãn; MC10 |
| Tuyên bố sẵn sàng phòng thi | Có đánh giá độc lập và người duyệt xác nhận | Chưa đạt, không được ghi là đã nghiệm thu |

## 2.3. Đối tượng nghiên cứu

Đối tượng kỹ thuật là pipeline xử lý video một camera gồm detector điện thoại `phone_v3_colab`, nhánh YOLO-World hỗ trợ, MediaPipe Pose + Hands, lớp fusion theo thời gian, dịch vụ snapshot/dashboard và kênh truyền trạng thái. Đối tượng đánh giá là box điện thoại trên tập validation và các sự kiện cảnh báo trong video kiểm thử.

## 2.4. Phạm vi

**Trong phạm vi:** một người trong một nguồn video; phát hiện điện thoại; pose/hand landmarks; cảnh báo và snapshot; dashboard kỹ thuật; đánh giá trên 214 ảnh validation; kiểm thử fixture và ổn định thành phần.

**Ngoài phạm vi của bản này:** nhận diện danh tính; theo dõi nhiều thí sinh; kết luận kỷ luật; đánh giá phòng thi thật; tai nghe khi chưa có nhãn và metric riêng; triển khai nhiều camera; huấn luyện mới trên máy cục bộ; tuyên bố thay thế giám thị; hồ sơ nghiệm thu chính thức nếu chưa có biên bản.

## 2.5. Nội dung thực hiện

1. Kiểm kê và checksum checkpoint Colab.
2. Kiểm toán dataset và tách train/validation.
3. So sánh `phone_v2` và `phone_v3_colab` trên cùng validation.
4. Phân tích lỗi theo kích thước và kiểm tra logic ghép box.
5. Chuẩn bị/nạp MediaPipe Pose + Hands.
6. Chạy luồng tích hợp, snapshot, dashboard và test.
7. Chuẩn bị giao thức video độc lập; giữ kết quả trống cho đến khi có tệp và nhãn.

## 2.6. Phương pháp nghiên cứu

- **Thực nghiệm có kiểm soát:** khóa checkpoint, danh sách ảnh, ngưỡng và quy tắc ghép để các phiên so sánh chỉ khác model hoặc logic cần kiểm tra.
- **Kiểm toán dữ liệu:** đọc manifest, đếm split/box, kiểm tra checksum và trùng ảnh giữa train/validation.
- **Đánh giá detector:** TP/FP/FN theo IoU 0,50; Precision = TP/(TP+FP); Recall = TP/(TP+FN); F1 là trung bình điều hòa.
- **Phân tích lỗi:** chia theo diện tích box so với ảnh; tách lỗi không có prediction khỏi lỗi prediction lệch box.
- **Đánh giá tích hợp:** kiểm tra các trạng thái nạp model, xử lý frame, sự kiện, snapshot, dashboard, dừng phiên và lỗi fallback.
- **Đánh giá video sau khi có dữ liệu:** người review đánh dấu thời điểm điện thoại xuất hiện/biến mất; máy ghi sự kiện và latency; đối chiếu hai bảng để tách lỗi detector và lỗi luật.

# CHƯƠNG 3. CƠ SỞ LÝ THUYẾT

## 3.1. Thị giác máy tính và bài toán phát hiện

Video được xem là chuỗi frame `I_t`. Detector biến mỗi frame thành tập ứng viên `D_t = {(box, class, confidence)}`. Hệ thống không quyết định từ một frame duy nhất; lớp fusion giữ lịch sử ngắn để tránh cảnh báo chớp tắt.

## 3.2. CNN và YOLO

CNN học các mẫu không gian qua convolution, activation và downsampling. YOLO dự đoán box/lớp trong một lượt nên có lợi thế về độ trễ. Với bài toán này, độ phân giải ảnh và kích thước điện thoại ảnh hưởng trực tiếp đến recall. NMS loại các box trùng dựa trên IoU; NMS IoU trong phép đo detector là 0,45, còn IoU 0,50 là điều kiện ghép prediction với ground truth.

## 3.3. YOLOv8/Ultralytics và checkpoint Colab

Checkpoint đang được dùng là `models/phone_v3_colab/weights/best.pt`, một model một lớp `phone` nhập từ Google Colab. Cấu hình đi kèm trong `models/phone_v3_colab/args.yaml` ghi model nền YOLOv8n, `epochs=40`, `batch=16`, `imgsz=640`, `seed=42`; thiết bị GPU Colab không được suy ra chỉ từ file và cần nhóm xác nhận nếu hồ sơ yêu cầu. SHA-256 của checkpoint là `e54b53aa88083d9e047227a7a6db4fc313c400ad81443d03bca50064cc8ed857`.

## 3.4. MediaPipe Pose và Hands

MediaPipe trả về landmarks chuẩn hóa theo ảnh. Pipeline hiện dùng Pose Landmarker Lite và Hand Landmarker; lần kiểm tra MC06 ghi nhận 33 điểm pose và hai bộ 21 điểm tay trên ảnh kỹ thuật. Các điểm này được dùng để suy ra tín hiệu hỗ trợ, với điều kiện phải có độ tin cậy/visibility đủ; khi landmark mất, hệ thống không được coi đó là hành vi bất thường.

## 3.5. Chỉ số đánh giá

Với một tập nhãn cố định, TP là prediction ghép được một ground truth chưa ghép; FP là prediction không ghép; FN là ground truth không có prediction. Precision phản ánh tỷ lệ prediction đúng, Recall phản ánh tỷ lệ ground truth được tìm thấy. F1 giúp nhìn cân bằng hai chỉ số. mAP là chỉ số tổng hợp theo ngưỡng confidence; trong bản sửa chỉ dùng các metric có trong artifact, không tự khôi phục mAP hoặc Accuracy từ số liệu khác.

FPS trong video là số frame đã xử lý chia cho thời gian xử lý. FPS của fixture hoặc thiết bị hiện tại không đại diện cho FPS camera phòng thi; phải ghi rõ nguồn, độ phân giải, backend và có/không dùng GPU.

# CHƯƠNG 4. THIẾT KẾ VÀ XÂY DỰNG HỆ THỐNG

## 4.1. Yêu cầu chức năng

| Mã | Yêu cầu | Cách kiểm tra | Trạng thái |
|---|---|---|---|
| FR-01 | Chọn nguồn video/camera và bắt đầu phiên | UI/API start; test hiện có | Đã kiểm tra phần mềm |
| FR-02 | Nạp đúng checkpoint Colab và hiển thị tên model | status model + log | Đã kiểm tra MC07; cần xác nhận dashboard phiên cuối |
| FR-03 | Phát hiện box điện thoại | detector/validation | Đã đo trên 214 ảnh |
| FR-04 | Trích xuất pose/hand landmarks | MediaPipe thật | Đã kiểm tra MC06/MC07 |
| FR-05 | Gộp tín hiệu và chống lặp cảnh báo | state/temporal confirmation | Đã có test; cần video độc lập |
| FR-06 | Chụp snapshot kèm sự kiện | endpoint snapshot | HTTP 200 trong MC07 |
| FR-07 | Hiển thị trạng thái trên dashboard | status, level, model, source | Có pipeline; cần người duyệt kiểm tra màn hình cuối |
| FR-08 | Dừng phiên và giải phóng tài nguyên | stop API | Đạt trong MC07 |

## 4.2. Yêu cầu phi chức năng và giới hạn

Hệ thống cần có log đủ để truy ngược model, source, timestamp, confidence và snapshot; lỗi model phải hiển thị rõ thay vì im lặng chuyển sang model khác; client chậm không làm dừng detection; không ghi dữ liệu cá nhân ngoài phần cần cho đánh giá. Các yêu cầu về FPS, độ trễ và độ ổn định chỉ được công bố cùng điều kiện đo. Kết quả hiện có chứng minh ổn định thành phần 30 phút, không chứng minh WebSocket/camera vật lý cả buổi.

## 4.3. Kiến trúc tổng thể

Luồng được triển khai theo các bước:

1. `SourceAdapter` đọc frame từ file video hoặc camera và gắn thời gian nguồn.
2. `PhoneDetector` chạy checkpoint Colab ở confidence 0,30; nhánh YOLO-World là tín hiệu hỗ trợ và được ghi riêng.
3. `MediaPipeAnalyzer` chạy Pose + Hands trên frame hiện tại.
4. `TemporalFusion` giữ lịch sử, xác nhận sự kiện theo điều kiện liên tiếp và chống lặp snapshot.
5. `AlertStore` ghi event, mức cảnh báo, score, source time và đường dẫn snapshot.
6. Dashboard lấy trạng thái phiên, hiển thị model đang nạp, source, FPS, event và lỗi.

Điểm quan trọng của thiết kế là mỗi nhánh có thể tắt trong phép ablation để biết lỗi nằm ở detector hay luật fusion. YOLO-World không được dùng để biến vật thể không liên quan thành điện thoại.

## 4.4. Logic xác nhận cảnh báo

Một box điện thoại đủ ngưỡng là **ứng viên**. Cảnh báo được phát khi ứng viên tồn tại theo quy tắc thời gian đã cấu hình, score được cập nhật và thời gian cooldown không ngăn sự kiện mới. Tín hiệu pose/hand chỉ tăng hoặc giảm mức hỗ trợ; mất landmark không tự tạo cảnh báo. Snapshot lưu frame minh họa cùng event ID. Khi model hoặc source lỗi, dashboard phải ghi `error`/`fallback` và giữ trạng thái quan sát được.

## 4.5. Dữ liệu và provenance

Manifest hiện ghi **1.600 ảnh train, 214 ảnh validation**, với **2.177 box train và 262 box validation**; không phát hiện trùng ảnh giữa hai split trong audit. Dataset có manifest nguồn, revision và checksum tại `dataset/phone_detection_v3/provenance/`. Đây là nguồn đánh giá detector hiện tại; chưa có bằng chứng rằng toàn bộ tập train trên Colab giống byte với bản cục bộ.

## 4.6. Huấn luyện và nhập checkpoint

Nhóm huấn luyện trên Google Colab; lượt này không train trên máy cục bộ. File nhận về được đặt trong `models/phone_v3_colab/weights/best.pt`, kèm args/results. Quy trình tái lập nhập model gồm: sao chép file; tính SHA-256; đọc class names; nạp bằng runtime; chạy một ảnh; ghi artifact import. Checksum là căn cứ nhận diện file, không phải bằng chứng chất lượng model.

## 4.7. MediaPipe và quy tắc hành vi

Các feature hình học được ghi ở dạng trung gian: hướng tương đối đầu/vai, góc tay, khoảng cách cổ tay–mặt và tỷ lệ landmark hợp lệ. Mỗi feature cần được xem trong cửa sổ thời gian; không gắn nhãn “gian lận” cho một tư thế riêng lẻ. Bản sửa chỉ tuyên bố có module landmark và luật hỗ trợ, chưa tuyên bố metric hành vi vì chưa có bộ nhãn hành vi độc lập.

## 4.8. Dashboard và lưu vết

Dashboard cần hiển thị: tên `phone_v3_colab`, model path rút gọn/checksum, detector status, pose status, source kind/name, FPS thực tế, event type/level/score, snapshot và lỗi. Khi fallback xảy ra phải ghi model đã fallback và lý do. Log không nên đưa dữ liệu cá nhân không cần thiết; file video thử nghiệm cần quyền sử dụng rõ.

# CHƯƠNG 5. THỰC NGHIỆM VÀ ĐÁNH GIÁ KẾT QUẢ

## 5.1. Thiết kế thực nghiệm

| Thành phần | Điều kiện đã khóa |
|---|---|
| Tập detector | 214 ảnh validation từ `phone_detection_v3` |
| Confidence | 0,30 |
| NMS IoU | 0,45 |
| IoU ghép nhãn | 0,50 |
| Checkpoint chính | `phone_v3_colab/best.pt`, SHA-256 nêu tại §3.3 |
| Checkpoint đối chứng | `phone_v2` theo artifact comparison |
| Video độc lập | Sáu kịch bản dự kiến; hiện chưa có file/nhãn |
| Đơn vị kết luận | Box/event có điều kiện; không suy ra kết luận kỷ luật |

## 5.2. Kiểm tra dữ liệu

Audit `artifacts/phone-v3-data-audit.json` xác nhận 1.600 ảnh train và 214 ảnh validation; số box lần lượt 2.177 và 262. Manifest có checksum và nguồn. Đây là kết quả kiểm toán file hiện có, không phải xác nhận quyền sử dụng mọi nguồn ảnh; nhóm cần bổ sung xác nhận license/quyền dùng khi nộp hồ sơ.

## 5.3. So sánh checkpoint `phone_v2` và `phone_v3_colab`

| Checkpoint | TP | FP | FN | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|---:|
| phone_v2 | 41 | 137 | 221 | 23,03% | 15,65% | 18,64% |
| phone_v3_colab | 124 | 78 | 138 | 61,39% | 47,33% | 53,45% |

Bảng trên là kết quả raw comparison tại `artifacts/phone-colab-comparison.json`; phép đo fixed pipeline bên dưới dùng logic ghép đã sửa để tránh đếm box lệch/ghép trùng. Hai bảng không được trộn vào cùng một tuyên bố.

## 5.4. Đối chứng logic detector/fusion

| Biến thể fixed | TP | FP | FN | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|---:|
| YOLO-World | 112 | 69 | 150 | 61,88% | 42,75% | 50,56% |
| phone_v3_colab | 124 | 73 | 138 | 62,94% | 47,33% | 54,03% |
| combined | 124 | 73 | 138 | 62,94% | 47,33% | 54,03% |

Kết quả `combined` không vượt `phone_v3_colab` trong tập này. Vì vậy bản sửa không nói rằng YOLO-World cải thiện detector điện thoại; nó chỉ được giữ như nhánh hỗ trợ/đối chứng trong nguyên mẫu. Phép đo không phải đánh giá hành vi hoặc cảnh báo video.

## 5.5. Phân tích lỗi theo kích thước

| Tỷ lệ diện tích GT/ảnh | GT | Detect | Miss | Recall |
|---|---:|---:|---:|---:|
| <0,25% | 91 | 22 | 69 | 24,18% |
| 0,25%–1% | 74 | 39 | 35 | 52,70% |
| ≥1% | 97 | 63 | 34 | 64,95% |

Có 121 ground truth không có prediction gần ở confidence 0,30; 17 trường hợp có prediction lân cận nhưng IoU chỉ 0,10–0,50. Có 57 prediction không gần ground truth và 21 prediction có overlap 0,10–0,50. Đây là chẩn đoán hình học, không tự kết luận toàn bộ FP là cảnh báo nhầm vì có khả năng nhãn chưa đầy đủ.

## 5.6. Đánh giá mô-đun phân tích tư thế và tay

Trong phiên bản hiện tại, mô-đun này **không phải bộ phân loại hành vi đã huấn luyện với bốn lớp độc lập**. `MediaPipeTasksAnalyzer` nạp Pose Landmarker Lite và Hand Landmarker, sau đó chuyển landmark pose vào các luật hình học và điều kiện duy trì theo thời gian trong `src/mediapipe_analyzer.py`. Landmark bàn tay được nạp và vẽ để quan sát; luật cảnh báo hiện dùng các điểm cổ tay/tai của pose, chưa có bộ phân loại riêng cho “trao đổi cử chỉ tay” hoặc “bàn tay che miệng”.

**Bảng 5.3. Tín hiệu hành vi được triển khai và trạng thái đo lường**

| Tín hiệu thực tế / event | Precision | Recall | F1 | FP Rate | Trạng thái và căn cứ |
|---|---:|---:|---:|---:|---|
| `LOOKING_AWAY` (quay đầu sang ngang) | Chưa đo | Chưa đo | Chưa đo | Chưa đo | Đã triển khai luật; chưa có video hành vi được gán nhãn |
| `HEAD_DOWN` (cúi đầu) | Chưa đo | Chưa đo | Chưa đo | Chưa đo | Đã triển khai luật; chưa có video hành vi được gán nhãn |
| `HAND_NEAR_EAR` (tay gần tai) | Chưa đo | Chưa đo | Chưa đo | Chưa đo | Đã phát event; chưa có nhãn tai nghe/tay gần tai |
| `HAND_SUSPICIOUS` (tay ở vị trí đáng ngờ) | Chưa đo | Chưa đo | Chưa đo | Chưa đo | Đã phát event; không phải nhận diện “che miệng” |
| **Trung bình** | — | — | — | — | Không tính khi chưa có tập nhãn chung và ma trận TP/FP/FN |

Điều kiện luật được khóa trong mã nguồn: `LOOKING_AWAY` dùng tỷ lệ lệch mũi so với tâm hai mắt > 0,58 và yêu cầu duy trì 8 frame (hoặc hold timer 8/30 giây); `HEAD_DOWN` dùng độ lệch dọc mũi–mắt > 0,5 lần khoảng cách mũi–vai và yêu cầu 12 frame (hoặc hold timer 12/30 giây); `HAND_NEAR_EAR` dùng khoảng cách chuẩn hóa cổ tay–tai < 0,22 với landmark đủ độ tin cậy; `HAND_SUSPICIOUS` dùng tung độ cổ tay lớn hơn tung độ hông trung bình ít nhất 0,15 khi các điểm hợp lệ. Các ngưỡng này mô tả luật triển khai, không phải kết quả huấn luyện hay ngưỡng đã được hiệu chuẩn bằng tập hành vi.

Các giá trị Precision, Recall, F1 và FP Rate trong bảng gốc (0,798–0,912) được rút khỏi kết quả vì workspace chưa có tập kiểm tra hành vi độc lập, nhãn thời gian cho từng loại, hoặc confusion matrix để tái lập chúng. `artifacts/mediapipe-check/summary.json` chỉ xác nhận việc nạp backend MediaPipe Pose + Hands phiên bản 0.10.32 và tạo được 33 landmark pose cùng hai bộ 21 landmark tay trên ảnh kiểm tra; chính artifact ghi rõ đây không phải đánh giá nhận diện hành vi. `artifacts/phone-colab-check-1788700181192987400/summary.json` xác nhận luồng tích hợp phát được event điện thoại, không cung cấp metric hành vi.

Khi chạy đánh giá video, nhóm cần gán nhãn độc lập thời điểm bắt đầu/kết thúc của từng tín hiệu trên cả video dương tính và âm tính, ghi event hệ thống theo source time, rồi tính TP/FP/FN theo một quy tắc giao nhau cố định. Chỉ sau bước đó mới được điền các cột Precision, Recall, F1 và FP Rate. Cần ghi rõ backend: artifact MC06/MC07 dùng `MediaPipe Pose + Hands` qua `pose_factory`; các entrypoint legacy `main.py` và `web_server.py` còn import `MediaPipeAnalyzer` trực tiếp, lớp này thực thi YOLOv8-Pose, nên không được gộp kết quả của hai backend.

## 5.7. Kiểm tra luồng tích hợp

Artifact `artifacts/phone-colab-check-1788700181192987400/summary.json` ghi:

- checkpoint `phone_v3_colab` được nạp;
- pipeline xử lý 24 frame kích thước 640×480;
- phát `PHONE_DETECTED`, detail confidence 68,8%, level HIGH;
- snapshot trả HTTP 200;
- phiên kết thúc với `running=false`, `status=stopped`, `error=null`.

Đầu vào là video fixture lặp một ảnh validation. Do đó đây là kiểm tra đường đi của dữ liệu và giao diện, không phải số đo recall/false alarm trên video độc lập.

## 5.8. Kiểm thử phần mềm và ổn định thành phần

`artifacts/improvement-tests-final.log` ghi **57/57 test đạt**. Thử nghiệm `artifacts/stability-30min-mediapipe.json` chạy 1.800,259 giây, xử lý 6.460 frame trong 269 vòng lặp, không ghi lỗi runtime; tốc độ trung bình theo các mốc dao động khoảng 3,4–3,9 frame/giây trên điều kiện chạy đó. Đây là tốc độ của fixture/backend hiện tại, không thay thế benchmark trên máy khỏe hơn hoặc camera mục tiêu.

## 5.9. Đánh giá video độc lập: trạng thái chờ dữ liệu

Kịch bản đã định nghĩa trong `demo/recordings/manifest.json`:

| Clip | Nội dung dự kiến | File | Mốc sự kiện | Kết quả |
|---|---|---|---|---|
| normal_01 | Ngồi làm bài, viết, nhìn giấy | Chưa có | Chưa có | Chưa đo |
| normal_02 | Ngồi làm bài, viết, nhìn giấy | Chưa có | Chưa có | Chưa đo |
| objects_01 | Máy tính/hộp bút/sổ | Chưa có | Chưa có | Chưa đo |
| objects_02 | Máy tính/hộp bút/sổ | Chưa có | Chưa có | Chưa đo |
| phone_01 | Cầm điện thoại rõ trước camera | Chưa có | Chưa có | Chưa đo |
| phone_02 | Đặt xa hoặc che một phần | Chưa có | Chưa có | Chưa đo |

Lần chạy evaluator ngày 08/09/2026 có trạng thái `missing_video_or_labels`, 0 clip sẵn sàng, 0 run. Không được điền TP/FP/FN, latency hoặc FPS cho sáu clip trước khi nhóm cung cấp file và người review mốc thời gian.

## 5.10. Ứng viên dữ liệu âm tính

`dataset/phone_negative_candidates/manifest.json` có 280 ảnh kèm source/license/checksum; chẩn đoán tìm 90 box trên 75 ảnh ở confidence 0,30. Đây chỉ là danh sách cần người duyệt, chưa phải ảnh âm tính sạch. Chỉ đưa những ảnh đã review vào dataset corrected; giữ manifest phiên bản và lý do loại/giữ.

## 5.11. Đánh giá các tuyên bố từ báo cáo gốc

| Tuyên bố trong bản gốc | Xử lý trong bản sửa |
|---|---|
| Accuracy trên 90% / tổng thể 93,3% | Rút khỏi phần kết quả; chưa có định nghĩa Accuracy và artifact tương ứng |
| YOLOv8m, 100 epoch, 3,5 giờ RTX3060 | Chỉ giữ cấu hình thật có trong `args.yaml`; GPU/100 epoch chưa có bằng chứng trong workspace |
| 52 FPS GPU, 12 FPS CPU, 19 ms | Rút khỏi kết luận; thay bằng số đo fixture có nguồn và điều kiện |
| ổn định 90 phút | Thay bằng 1.800,259 giây/6.460 frame/269 vòng lặp của MC08 |
| MediaPipe phát hiện hành vi với F1 85,3% | Rút; chưa có nhãn hành vi và confusion matrix |
| triển khai phòng thi | Hạ thành khả năng định hướng; chưa có đánh giá camera/phòng thi |

# KẾT LUẬN VÀ KIẾN NGHỊ

## 6.1. Kết luận theo mục tiêu

| Mục tiêu | Kết luận có thể bảo vệ |
|---|---|
| Xây dựng nguyên mẫu YOLO + MediaPipe | Đạt ở mức nguyên mẫu kỹ thuật; detector, landmarks, fusion, snapshot và dashboard đã nối được |
| So sánh model Colab | Đạt trên 214 ảnh validation; Colab tốt hơn phone_v2 theo các bảng có điều kiện |
| Đạt chất lượng trên 90% | Không đạt/không đủ dữ liệu để kết luận; số liệu gốc bị rút |
| Đánh giá hành vi | Mới có module và quy tắc; chưa có metric hành vi độc lập |
| Đánh giá video thực tế | Chưa thực hiện vì thiếu sáu video và nhãn |
| Sẵn sàng phòng thi | Chưa đủ căn cứ; chỉ nên trình diễn kỹ thuật có người giám sát |

## 6.2. Đóng góp

Đóng góp phương pháp là quy trình đo có điều kiện, provenance/checksum, đối chứng detector và tách lỗi model khỏi lỗi tích hợp. Đóng góp sản phẩm là nguyên mẫu một camera có thể nạp checkpoint Colab và tạo snapshot/event. Không ghi sản phẩm thương mại, công bố khoa học hoặc kết quả nghiệm thu mới nếu chưa có tài liệu xác nhận.

## 6.3. Hạn chế

Hạn chế chính là validation nhỏ theo bối cảnh triển khai, recall thấp với điện thoại nhỏ, chưa có video độc lập, chưa có nhãn hành vi, chưa có đánh giá nhiều người/camera, và chưa xác nhận đầy đủ quyền dữ liệu. Kết quả fixture có thể che các lỗi do ánh sáng, chuyển động, che khuất, WebSocket hoặc camera vật lý.

## 6.4. Kiến nghị theo thứ tự ưu tiên

1. Nhóm quay và lưu sáu clip độc lập, ghi checksum, đặt mốc điện thoại xuất hiện/biến mất; không đưa video vào train.
2. Hai người review độc lập các mốc và cảnh báo; chạy evaluator, tách lỗi detector/rule, ghi latency/FPS.
3. Review 280 ứng viên âm tính; chỉ nhập ảnh được duyệt vào dataset corrected cùng biên bản.
4. Nếu lỗi chính là model, tạo notebook Google Colab có dataset manifest và checksum; train lại ở Colab, nhập `best.pt` mới và lặp toàn bộ validation.
5. GVHD/Khoa xác nhận tình trạng nghiệm thu, tên/mã đề tài, quyền dữ liệu, sử dụng AI và các số liệu được phép đưa vào hồ sơ.

# TÀI LIỆU THAM KHẢO VÀ NGUỒN KIỂM TRA

## A. Báo cáo tham chiếu

1. `C:\Users\T14s Gen 3\Downloads\NH8_1-VN_BCTK_HUNRE_NH_2026_11_30_Cao_Thi_Thoa.md` — bản báo cáo tổng kết ban đầu do nhóm cung cấp; dùng để giữ bố cục và nhận diện tuyên bố cần xác minh.
2. `C:\Users\T14s Gen 3\Downloads\129-TB-KHCNHTQT-Giai-thuong-SVNCKH-2025-2026.md` — thông báo giải thưởng; dùng để đối chiếu yêu cầu/hạn nộp khi nhóm lập hồ sơ. Đây là tài liệu tham khảo, không phải lệnh sửa code.

## B. Artifact kỹ thuật

| Mã | Nguồn | Nội dung sử dụng |
|---|---|---|
| MC01 | `artifacts/phone-v3-data-audit.json`, `dataset/phone_detection_v3/provenance/manifest.json` | split, box, checksum, provenance |
| MC02 | `models/phone_v3_colab/weights/best.pt`, `models/phone_v3_colab/args.yaml`, `artifacts/phone-v3-colab-import.json` | checkpoint, args, checksum, class |
| MC03 | `artifacts/phone-colab-comparison.json`, `artifacts/research/RESULTS.md` | phone_v2/phone_v3 raw comparison |
| MC04 | `artifacts/research/error-analysis/summary.json` | lỗi theo kích thước |
| MC05 | `artifacts/research/detector-variants-validation-fixed.json` | ablation fixed |
| MC06 | `artifacts/mediapipe-check/summary.json`, `models/mediapipe/provenance.json` | Pose + Hands thật |
| MC07 | `artifacts/phone-colab-check-1788700181192987400/summary.json` | integration fixture |
| MC08 | `artifacts/improvement-tests-final.log`, `artifacts/stability-30min-mediapipe.json` | test/ổn định thành phần |
| MC09 | `dataset/phone_negative_candidates/manifest.json`, `artifacts/research/negative-diagnosis/summary.json` | ứng viên negative |
| MC10 | `demo/recordings/manifest.json` | trạng thái sáu video độc lập |

## C. Thư mục học thuật kế thừa từ báo cáo gốc

Danh sách dưới đây được trích từ phần tài liệu tham khảo của BCTK gốc để giữ mạch học thuật. Nhóm phải kiểm tra lại tên tác giả, năm, venue, DOI/URL và việc thật sự sử dụng từng tài liệu trước khi nộp; những mục không xác minh được phải bỏ, không dùng để tạo uy tín giả.

1. Bazarevsky, V. và cộng sự (2020), *BlazePose: On-device real-time body pose tracking*, arXiv:2006.10204.
2. Bochkovskiy, A., Wang, C. Y. và Liao, H. Y. M. (2020), *YOLOv4: Optimal speed and accuracy of object detection*, arXiv:2004.10934.
3. Goodfellow, I., Bengio, Y. và Courville, A. (2016), *Deep Learning*, MIT Press.
4. Jocher, G., Chaurasia, A. và Qiu, J. (2023), *Ultralytics YOLOv8*, GitHub/documentation.
5. Redmon, J. và cộng sự (2016), *You Only Look Once: Unified, real-time object detection*, CVPR, 779–788.
6. Wang, C. Y., Bochkovskiy, A. và Liao, H. Y. M. (2022), *YOLOv7: Trainable bag-of-freebies sets new state-of-the-art for real-time object detectors*, arXiv:2207.02696.
7. Zhang, F. và cộng sự (2020), *MediaPipe Hands: On-device real-time hand tracking*, arXiv:2006.10214.
8. Các tài liệu tiếng Việt và các bài về giám sát thi cử được nêu trong BCTK gốc: chỉ giữ sau khi nhóm kiểm tra được bản xuất bản và khả năng truy cập.

# PHỤ LỤC 1. MA TRẬN KẾT QUẢ – MINH CHỨNG

| Mã kết quả | Tuyên bố được phép dùng | Minh chứng | Cách kiểm tra lại | Điểm còn thiếu |
|---|---|---|---|---|
| R01 | Dataset có 1.600 train/214 val, 2.177/262 box | MC01 | Đọc JSON/manifest | Quyền dùng và đồng nhất với Colab |
| R02 | Checkpoint Colab là model một lớp phone, checksum nêu trên | MC02 | SHA-256 + nạp model | Xác nhận GPU/biên nhận Colab |
| R03 | Colab vượt phone_v2 ở bảng raw | MC03 | Chạy lại cùng validation | Phân biệt raw/fixed khi trích hồ sơ |
| R04 | Fixed phone_v3 đạt P62,94/R47,33/F1 54,03 | MC05 | Kiểm tra JSON và script version | Chưa phải test ngoài mẫu |
| R05 | Điện thoại nhỏ là nhóm bỏ sót nhiều | MC04 | Đọc bảng size | Nguyên nhân semantic cần review người |
| R06 | MediaPipe Pose + Hands nạp thật | MC06 | Mở summary/overlay | Chưa có metric hành vi |
| R07 | Luồng tích hợp tạo event/snapshot và stop được | MC07 | Mở summary/snapshot | Fixture lặp ảnh validation |
| R08 | Bộ test phần mềm 57/57, ổn định thành phần 1.800,259 s | MC08 | Đọc log/JSON | Chưa đại diện camera/WebSocket |
| R09 | Có 280 ứng viên cần review | MC09 | Đọc manifest | Chưa dùng làm negative train |
| R10 | Sáu video độc lập chưa sẵn sàng | MC10 | `events=null`, thiếu file | Cần quay, gán nhãn, chạy đánh giá |

# PHỤ LỤC 2. GIAO THỨC BỔ SUNG VIDEO

## 2.1. Cách quay

Mỗi clip khoảng 30 giây, cùng một người, một camera và độ phân giải mục tiêu. Hai clip bình thường chỉ viết/nhìn giấy; hai clip có máy tính Casio/hộp bút/sổ; hai clip có điện thoại, một clip cầm rõ và một clip để xa hoặc che một phần. Không dùng các clip này để train trong cùng vòng đánh giá.

## 2.2. Phiếu nhãn tối thiểu

Người review ghi `clip_id`, reviewer, checksum, camera, độ phân giải, `phone_onset_s`, `phone_offset_s`, vùng che khuất, và các thời điểm cảnh báo máy. Nếu không chắc thời điểm, ghi khoảng `[start,end]` và lý do. Không ghi tên thật/thông tin nhận diện nếu không cần.

## 2.3. Metric cần xuất

Đếm detection đúng nếu event nằm trong khoảng điện thoại có mặt và box đạt quy tắc IoU/frame đã thống nhất. Báo riêng: missed phone, false alarm trong clip bình thường/đồ vật, thời gian từ onset đến alert, thời gian hết alert sau offset, FPS trung vị/p5 và lỗi pipeline. Người duyệt ký xác nhận bảng trước khi đưa vào hồ sơ.

# PHỤ LỤC 3. QUY TRÌNH TÁI LẬP VÀ QUẢN LÝ PHIÊN BẢN

1. Ghi commit/source version và Python/runtime.
2. Kiểm tra các checksum trong MC01–MC05.
3. Chạy validation với confidence 0,30, NMS IoU 0,45, IoU ghép 0,50.
4. Lưu JSON kết quả, log, ảnh overlay và thời điểm chạy trong thư mục artifact mới.
5. Khi nhập checkpoint mới từ Colab, giữ `best.pt`, `args.yaml`, `results.csv`, checksum và notebook/URL phiên bản; không ghi đè checkpoint cũ.
6. Chỉ thay số liệu trong báo cáo sau khi artifact mở được và một người thứ hai kiểm tra.

# PHỤ LỤC 4. LIÊM CHÍNH, DỮ LIỆU VÀ SỬ DỤNG AI

- Bản sửa không tạo số liệu mới và không dùng số liệu chưa truy nguồn để nâng thành tích.
- Ảnh/video cần có quyền sử dụng, phạm vi đồng ý và quy tắc lưu trữ; nhóm/GVHD phải xác nhận nội dung trước khi ký cam kết.
- Nếu dùng AI để rà soát, lập bảng hoặc sửa diễn đạt, cần khai báo theo biểu mẫu của Trường; AI không được coi là người tạo dữ liệu hay người xác nhận nghiệm thu.
- Người xuất hiện trong video cần được thông báo/đồng ý theo quy định áp dụng; snapshot dùng trong hồ sơ phải che thông tin không cần thiết.

# PHỤ LỤC 5. DANH SÁCH VIỆC CÒN THIẾU VÀ NGƯỜI XÁC NHẬN

| Ưu tiên | Việc | Người cần xác nhận | Bằng chứng đầu ra |
|---|---|---|---|
| P0 | Tình trạng nghiệm thu, mã đề tài, bản chính thức | GVHD/Khoa | quyết định/biên bản |
| P0 | Sáu video + mốc nhãn | Nhóm + người review | video, manifest, label |
| P0 | Số liệu nào được phép đưa vào hồ sơ | GVHD | bảng duyệt số liệu |
| P1 | Quyền dữ liệu, đạo đức, sử dụng AI | Nhóm + Khoa | phiếu xác nhận |
| P1 | Review ứng viên negative | Nhóm | manifest corrected |
| P2 | Train tiếp nếu lỗi model | Nhóm trên Colab | notebook, checkpoint, checksum |

> **Điểm dừng hồ sơ:** chỉ sau khi P0 hoàn tất mới có thể thay các ô “chưa đo/chưa xác nhận” bằng kết quả video và thông tin hành chính. Nếu không hoàn tất trước hạn, báo cáo cần giữ nguyên trạng thái thiếu dữ liệu thay vì điền số ước lượng.
