# Nghiên cứu sử dụng thuật toán YOLO và framework MediaPipe trong hệ thống giám sát gian lận thi cử

BẢN SỬA PHỤC VỤ RÀ SOÁT VỚI GIẢNG VIÊN HƯỚNG DẪN

Trường Đại học Tài nguyên và Môi trường Hà Nội — Khoa Công nghệ thông tin

Nhóm thực hiện theo tài liệu cung cấp: Vương Anh Vũ, Vũ Duy Tiến, Nguyễn Ngọc Anh, Nguyễn Thị Kim Tuyến, Nguyễn Thị Khánh Vân. Lớp ĐH13C8.

Người hướng dẫn theo tài liệu cung cấp: ThS. Cao Thị Thoa.

Ngày cập nhật 06/09/2026. Tên trên lấy theo bìa báo cáo đã cung cấp; cần đối chiếu tên đăng ký vì phần thông tin chung trong bản cũ có cách viết khác. Bản này chưa thay thế hồ sơ đã nộp và chưa được xác nhận nghiệm thu. Nhóm cần thống nhất với giảng viên cách đính chính hoặc bổ sung theo quy trình của Khoa và Trường.

## Tóm tắt

Nghiên cứu xây dựng một nguyên mẫu hỗ trợ giám sát một người qua một nguồn video. Phần mềm kết hợp YOLO-World, checkpoint YOLOv8n chuyên phát hiện điện thoại, MediaPipe Pose và Hands, các quy tắc theo thời gian và dashboard. Cảnh báo là tín hiệu để người giám sát xem xét, không phải kết luận một người đã gian lận.

Trong phép đánh giá detector trên cùng 214 ảnh validation chứa 262 điện thoại, tại confidence 0,30 và IoU ghép nhãn 0,50, checkpoint Colab đạt precision 61,39%, recall 47,33% và F1 53,45%. Checkpoint v2 đạt lần lượt 23,03%, 15,65% và 18,64%. Đây là kết quả validation đã được dùng chọn checkpoint, không phải phép đánh giá độc lập trên video phòng thi. Kiểm thử kỹ thuật xác nhận nạp MediaPipe, trích xuất landmark, truyền video, phát cảnh báo điện thoại và phục vụ snapshot. Công cụ so sánh bốn cấu hình đã chạy thử trên video lặp ảnh validation. Bộ sáu video độc lập của nhóm chưa có, vì vậy chưa báo cáo độ chính xác hành vi hoặc chất lượng cảnh báo trong phòng thi.

Từ khóa: phát hiện điện thoại, YOLO World, MediaPipe, xác nhận theo thời gian, giám sát thi, đánh giá thực nghiệm.

## 1 Mục tiêu và phạm vi nghiên cứu

Mục tiêu của phiên bản hiện tại là phát hiện sự xuất hiện của điện thoại và hiển thị một số quan sát tư thế để hỗ trợ giám thị. Output gồm video có chú thích, loại cảnh báo, thời điểm, mức điểm theo quy tắc và ảnh chụp sự kiện. Phạm vi thử nghiệm được giới hạn ở một người và một nguồn video; chưa có tracking danh tính, phân công cảnh báo theo nhiều thí sinh hoặc triển khai toàn phòng thi.

So với mục tiêu rộng trong báo cáo trước, các nội dung nhận diện tai nghe, tài liệu và hành vi bàn tay chưa có đánh giá định lượng độc lập. Không coi giấy trên bàn, cúi đầu viết, chạm tai hoặc nhìn sang bên là bằng chứng đủ để kết luận gian lận. Các nhãn này cần được định nghĩa theo quy định của bài thi và ngữ cảnh quan sát.

Câu hỏi thực nghiệm chính là: kết hợp detector điện thoại chuyên dụng và xác nhận liên tục theo thời gian có giảm cảnh báo nhầm hay không, với đánh đổi nào về bỏ sót, độ trễ và tốc độ xử lý? Phép so sánh checkpoint trả lời một câu hỏi hẹp hơn: hai checkpoint hiện có khác nhau thế nào trên cùng tập ảnh validation.

Đóng góp hiện có nằm ở nguyên mẫu tích hợp, logic kiểm tra bằng chứng theo thời gian và công cụ đánh giá có lưu nguồn gốc. Chưa có kết quả chứng minh một thuật toán phát hiện mới, ưu thế tổng quát so với các nghiên cứu khác hoặc tác động giảm gian lận thực tế.

## 2 Cơ sở và công nghệ kế thừa

YOLO-World là phương pháp phát hiện vật thể theo tập nhãn mở [1]. Dự án dùng checkpoint có sẵn và khai báo tên đối tượng cần quan sát; kiến trúc này là thành phần kế thừa. Checkpoint phone là YOLOv8n được fine-tune, không phải YOLOv8m như bản báo cáo trước.

MediaPipe Pose Landmarker cung cấp 33 điểm cơ thể, còn Hand Landmarker cung cấp 21 điểm trên mỗi bàn tay được phát hiện [2, 3]. Phiên bản này chạy hai task thật trên các khung hình và hiển thị kết quả. Các landmark bàn tay hiện phục vụ quan sát và minh chứng tích hợp; chưa có bộ phân loại cử chỉ tay được huấn luyện và đánh giá. Các luật hành vi đang dùng mũi, mắt, vai, cổ tay, tai và hông từ bộ điểm cơ thể.

Dữ liệu CITW được nguồn cung cấp mô tả là tập con điện thoại từ COCO 2017 [4]. COCO chứa vật thể trong cảnh đời thường [5]; không thể xem các ảnh này là dữ liệu phòng thi do nhóm tự quay. Vì khác góc camera, khoảng cách và ngữ cảnh, hiệu năng validation không tự suy ra chất lượng trong phòng thi.

## 3 Dữ liệu và cấu hình huấn luyện

| Thành phần | Bằng chứng hiện có |
|---|---|
| Bộ dữ liệu v3 cục bộ | 1.600 ảnh train, 214 ảnh validation; lớp phone |
| Nguồn | CITW từ COCO; giữ phân chia nguồn và manifest |
| Checkpoint đang dùng | phone_v3_colab với lớp 0 là phone |
| Kiến trúc và huấn luyện | YOLOv8n pretrained, 40 epoch, imgsz 640, batch 16, seed 42 |
| Nơi huấn luyện | Google Colab theo người dùng và cấu hình lưu trong kết quả |
| Thời gian trong CSV | 994,254 giây cho lượt 40 epoch |
| GPU huấn luyện | Chưa xác định loại GPU; device 0 không đủ để suy ra RTX 3060 |
| Bộ test video độc lập | Chưa có tại thời điểm lập bản sửa |

Checkpoint tốt nhất lưu chỉ số tương ứng epoch 39. ZIP kết quả được nhập vào thư mục riêng và kiểm tra SHA256. Bản CPU trước đó được giữ để đối chiếu, không tự tiếp tục huấn luyện cục bộ.

Manifest cục bộ ghi checksum ảnh/nhãn và nguồn dữ liệu. Kiểm tra byte trùng không thay thế việc kiểm tra ảnh gần trùng, cảnh chụp hoặc danh tính người. ZIP Colab chưa cung cấp manifest đầy đủ của tập train trên Colab, nên chưa khẳng định toàn bộ ảnh train trên hai môi trường giống nhau từng byte.

Số liệu khoảng 2.690 ảnh gốc, 8.990 ảnh sau augmentation và tập test 270 ảnh trong bản cũ không có bộ dữ liệu tương ứng để xác minh trong hồ sơ hiện có. Bản sửa không dùng các số đó để mô tả lượt huấn luyện Colab này.

## 4 Thiết kế và triển khai hệ thống

Luồng chính gồm đọc video, chạy detector vật thể, trích xuất landmark, áp dụng quy tắc, tạo cảnh báo và hiển thị trên dashboard. FastAPI phục vụ video MJPEG, WebSocket truyền trạng thái và cảnh báo, snapshot được phục vụ qua HTTP. Dashboard hiển thị checkpoint phone và backend tư thế thực tế, có nút bắt đầu và dừng.

### 4.1 Phát hiện và xác nhận điện thoại

YOLO-World chạy các prompt vật thể được cấu hình. Điện thoại của World được xét ở confidence từ 0,40; model phone chạy ở confidence từ 0,30. Đầu ra điện thoại dùng tọa độ và confidence của model phone. Box World chỉ bổ sung thông tin hỗ trợ khi IoU từ 0,20 hoặc tâm box World nằm trong box phone; mỗi box World chỉ ghép một lần. Loại trùng box phone ở IoU trên 0,30. Phone được giữ ngay cả khi World không phát hiện, nếu không bị bộ lọc vật được phép loại. Cơ chế này đã sửa lỗi nhiều box World cùng được một box phone xác nhận. Các quy tắc ghép và loại trùng là heuristic, cần kiểm thử riêng trong cảnh nhiều vật đặt gần nhau.

Luồng ứng dụng hiện giữ bộ lọc vật được phép từ phiên bản trước. Bộ lọc có thể loại điện thoại thật nếu chồng lên hộp bút hoặc máy tính. Công cụ thực nghiệm cho phép tắt bộ lọc để đo ảnh hưởng; chưa có dữ liệu thực tế để kết luận nên bật hay tắt. Đã sửa đường xử lý để model phone vẫn được gọi khi World không trả box.

### 4.2 Thời gian và trạng thái cảnh báo

API và công cụ video dùng thời gian nguồn: timestamp từ decoder khi hợp lệ, dự phòng theo FPS cho video có tốc độ khung hình cố định; camera dùng đồng hồ đơn điệu. Detector được lấy mẫu theo chu kỳ 0,1 giây nguồn. Số lần dùng phương án dự phòng được ghi trong báo cáo thực nghiệm để người đọc biết giới hạn của thời gian video.

Điện thoại cần ít nhất ba quan sát mới, kéo dài ít nhất 0,2 giây, ghép một-một theo vị trí. Khoảng gián đoạn lớn hơn 0,5 giây làm mất tính liên tục. Kết quả detector được cache để hiển thị không làm tăng số lần xác nhận. Các tham số thời gian là cấu hình ban đầu, chưa được hiệu chỉnh trên dữ liệu phòng thi.

Điểm được cộng theo trọng số cấu hình, với mỗi loại sự kiện tối đa một lần trong một giây nguồn; phone có trọng số 12. Khi không có bằng chứng sự kiện mới, điểm giảm theo số giây sạch đã trôi qua. Giới hạn tổng điểm là 30. Thông báo cùng loại cách nhau ít nhất 10 giây nguồn; số quan sát dương tính, số đợt sự kiện và số thông báo sau cooldown cần được báo riêng. Điểm chưa được hiệu chuẩn thành xác suất gian lận.

### 4.3 MediaPipe và các luật tư thế

Backend mặc định của demo FastAPI là MediaPipe Pose và Hands. YOLO-Pose vẫn có thể chọn rõ ràng bằng cấu hình để đối chiếu. Nếu MediaPipe không nạp được, phiên báo lỗi; không âm thầm đổi backend rồi tiếp tục ghi là MediaPipe.

Điểm cơ thể MediaPipe được ánh xạ sang các vị trí mà luật hiện có sử dụng. Quay đầu và cúi đầu cần điểm đủ confidence và duy trì theo thời gian. Thiếu mắt, mũi, vai hoặc mất người không được dùng làm bằng chứng hành vi. Các luật này chỉ mô tả hình học từ camera, chưa được kiểm chứng bằng nhãn hành vi độc lập. Việc trích xuất và vẽ 21 điểm bàn tay không đồng nghĩa đã nhận diện đúng trao đổi bài hoặc dùng tai nghe.

### 4.4 Giao diện và lỗi vận hành

Giao diện phân biệt model chưa nạp, model đang dùng và fallback detector phone. Backend tư thế được công bố riêng. Gửi WebSocket có giới hạn thời gian và xử lý lỗi để một client chậm không làm dừng detection. Khi dừng hoặc hết video, tài nguyên được đóng, FPS trở về 0 và phiên mới khởi tạo lại trạng thái. Tốc độ xử lý vẫn có thể giảm do tải tính toán hoặc chờ gửi dữ liệu; không mô tả hệ thống như một pipeline không có độ trễ.

## 5 Thực nghiệm và kết quả đã kiểm chứng

### 5.1 Phép so sánh checkpoint trên ảnh

Hai checkpoint được đánh giá trên cùng 214 ảnh chứa 262 nhãn phone. Ngưỡng confidence là 0,30; NMS IoU 0,45; ghép prediction với ground truth ở IoU 0,50. Mỗi box dự đoán và mỗi nhãn khớp tối đa một lần, ưu tiên confidence cao. Precision là TP chia TP cộng FP; recall là TP chia TP cộng FN; F1 là trung bình điều hòa của precision và recall. Đây là chỉ số tại một ngưỡng, không phải Accuracy chung hoặc mAP.

| Checkpoint | TP | FP | FN | Precision | Recall | F1 |
|---|---|---|---|---|---|---|
| phone v2 | 41 | 137 | 221 | 23,03% | 15,65% | 18,64% |
| phone v3 Colab | 124 | 78 | 138 | 61,39% | 47,33% | 53,45% |

![Kết quả detector trên validation](../artifacts/research/phone-benchmark.png)

Hình 1. So sánh P, R và F1 trên validation. Khoảng bootstrap trong hình là phân tích thăm dò theo ảnh, không loại bỏ thiên lệch chọn checkpoint trên validation.

Checkpoint Colab tốt hơn v2 trên phép đánh giá này. Tuy nhiên, dữ liệu train và cấu hình huấn luyện hai lượt khác nhau, nên không quy toàn bộ chênh lệch cho một thành phần thuật toán. Không so các số trên với các công trình khác dùng dữ liệu, metric hoặc phần cứng khác để kết luận ưu thế.

### 5.2 Phân tích lỗi theo kích thước điện thoại

| Diện tích box so với ảnh | Nhãn thật | Phát hiện đúng | Bỏ sót | Recall |
|---|---|---|---|---|
| Dưới 0,25% | 91 | 22 | 69 | 24,18% |
| Từ 0,25% đến dưới 1% | 74 | 39 | 35 | 52,70% |
| Từ 1% trở lên | 97 | 63 | 34 | 64,95% |

Các nhóm trên do nghiên cứu đặt để chẩn đoán, không phải định nghĩa small/medium/large chính thức của COCO. Kết quả cho thấy đối tượng nhỏ là điểm yếu đáng chú ý. Review một số ảnh nhiều lỗi ghi nhận phone bị che, box không khớp toàn vật và nhầm các vật chữ nhật. Review do trợ lý thực hiện chưa thay thế việc nhóm kiểm tra nhãn, đặc biệt ở các thiết bị có hình dạng giống điện thoại.

### 5.3 Kiểm thử tích hợp và phần mềm

MediaPipe Tasks phiên bản 0.10.32 đã được nạp với model Pose Lite và Hand Landmarker. Trên ảnh validation được chọn để kiểm tra kỹ thuật, hệ thống trả một bộ 33 điểm cơ thể và hai bộ 21 điểm bàn tay. Kiểm thử ảnh trống không tạo cảnh báo tư thế. Kết quả này chứng minh task chạy và trả dữ liệu đúng cấu trúc; không dùng làm thống kê nhận diện hành vi.

![MediaPipe trên ảnh kiểm thử kỹ thuật](../artifacts/mediapipe-check/pose-hands-overlay.jpg)

Hình 2. Overlay MediaPipe trên ảnh validation 000000001296.jpg từ CITW/COCO. Đây là ảnh kỹ thuật được chọn, không phải ảnh nhóm tự quay trong phòng thi.

Kiểm thử model thật qua API đã nhận cảnh báo PHONE_DETECTED, giải mã video, tải và giải mã snapshot thành công, sau đó dừng phiên. Video là ảnh validation được lặp 24 frame. Không dùng video này để báo recall sự kiện, cảnh báo nhầm hoặc chất lượng trong phòng thi. Bộ kiểm thử tự động mới nhất trước khi biên tập tài liệu có 57 ca đạt; số ca kiểm thử phản ánh kiểm tra phần mềm, không phải cỡ mẫu thực nghiệm AI.

Kiểm tra thành phần decode, model, fusion, vẽ và JPEG đã chạy 1.800,259 giây, xử lý 6.460 frame qua 269 lần phát lại video kỹ thuật, kết thúc không có lỗi. Đây là phiên MediaPipe trước sửa ghép box cuối cùng; bản sửa ghép box đã được kiểm thử đơn vị và tích hợp riêng. Tốc độ trung bình khoảng 3,59 FPS trong lúc máy chạy tác vụ khác, không dùng làm benchmark tốc độ. Kết quả không thay thế kiểm tra camera vật lý, WebSocket dài hạn hoặc một buổi thi thực tế.

### 5.4 Thiết kế thí nghiệm video đang chờ dữ liệu

| Cấu hình | Thành phần |
|---|---|
| A | YOLO World cho điện thoại |
| B | Checkpoint phone Colab |
| C | World kết hợp phone, không xác nhận liên tục |
| D | C với xác nhận liên tục theo thời gian |

Công cụ đã chạy thử đủ bốn cấu hình trên video kỹ thuật. Trong phép so sánh chính, đóng góp pose và bộ phủ quyết vật được phép được tắt để tách tác động detector và thời gian. Bộ lọc vật được phép có thí nghiệm riêng; luồng ứng dụng đầy đủ được đánh giá riêng. Mỗi đợt dự đoán khớp tối đa một sự kiện thật theo thời điểm bắt đầu cảnh báo; các đợt lặp không làm tăng số TP.

Sáu video độc lập dự kiến gồm hai đoạn bình thường, hai đoạn vật dễ nhầm và hai đoạn có điện thoại. Nhãn được người quay và người kiểm tra xác nhận trước khi chạy. Chưa có video tại thời điểm lập bản sửa, nên kết quả A–D trên dữ liệu phòng thi để trống và ghi chưa thực hiện. Nếu các clip được dùng chỉnh ngưỡng, phải ghi là tập hiệu chỉnh và cần phiên khác để đánh giá cuối.

### 5.5 Đối chứng detector trên ảnh và sửa lỗi kết hợp

Đã chạy ba cấu hình trên cùng 214 ảnh. World dùng ngưỡng phone 0,40, model phone dùng 0,30; IoU NMS 0,45, IoU ghép nhãn 0,50, imgsz 640, CPU. Tắt bộ lọc vật được phép và pose để tách đầu ra điện thoại. Đây là phân tích thăm dò trên validation, không phải kết quả test độc lập.

| Cấu hình | TP | FP | FN | Precision | Recall | F1 |
|---|---|---|---|---|---|---|
| World | 112 | 69 | 150 | 61,88% | 42,75% | 50,56% |
| Phone | 124 | 73 | 138 | 62,94% | 47,33% | 54,03% |
| Kết hợp trước sửa | 124 | 109 | 138 | 53,22% | 47,33% | 50,10% |
| Kết hợp sau sửa | 124 | 73 | 138 | 62,94% | 47,33% | 54,03% |

Lỗi ghép xác nhận nhiều box và giữ tọa độ World làm tăng box sai. Sau sửa, số FP của cấu hình kết hợp giảm từ 109 xuống 73, TP giữ 124. Tuy nhiên đầu ra phone của cấu hình kết hợp sau sửa tương đương phone độc lập khi tắt bộ phủ quyết. Vì vậy không kết luận World giúp tăng chất lượng phát hiện điện thoại. World cung cấp các nhãn vật thể khác, nhưng phần đó chưa được đánh giá. C–D sẽ kiểm tra tác động xác nhận theo thời gian; B–C hiện là phép kiểm tra tương đương, không phải bằng chứng hai mô hình bổ trợ nhau.

Số FP 73 của pipeline khác 78 ở đánh giá checkpoint thô mục 5.1 do chuyển tọa độ sang số nguyên và lọc box trùng bổ sung. Hai bảng có đơn vị và cấu hình riêng; không thay thế hoặc trộn số liệu giữa hai phép đo. Chưa đo tốc độ so sánh do máy chạy đồng thời nhiều tác vụ.

### 5.6 Ứng viên dữ liệu bổ sung

Đã tải 280 ảnh COCO không có nhãn cell phone trong annotation nguồn, giữ 200 ảnh thuộc train và 80 thuộc validation nguồn, cùng URL, giấy phép theo ảnh và SHA256. Chạy checkpoint Colab ở confidence 0,30 kích hoạt 90 box trên 75 ảnh. Đây là số dự đoán cần review, không phải 75 ảnh âm tính đã xác nhận hoặc tỷ lệ báo động nhầm.

Review trực quan 12 phiếu ưu tiên ghi nhận nhầm vào chuột máy tính, dập ghim, máy tính khoa học, tay cầm trò chơi và touchpad; một số thiết bị nhỏ còn không rõ loại. Chưa tạo nhãn âm tính, chưa đưa các ảnh này vào train. Chỉ sử dụng sau khi nhóm xác nhận nội dung ảnh, nguồn và phân chia; không dùng tập video đánh giá để huấn luyện.

## 6 Hạn chế và hướng phát triển

Giới hạn chính là chưa có dữ liệu video độc lập, dữ liệu validation có nguồn đời thường và từng tham gia chọn checkpoint, detector bỏ sót nhiều phone nhỏ, các luật hành vi chưa được hiệu chỉnh và bộ lọc chồng lấn có thể loại nhầm phone thật. Phạm vi một người không chứng minh xử lý nhiều thí sinh. Landmark bàn tay chưa được dùng trong bộ phân loại hành vi có đánh giá.

Sáu clip khoảng 30 giây chỉ đủ làm pilot ban đầu. Cần mở rộng theo phiên quay, người tham gia và điều kiện camera; báo số đếm từng clip trước khi suy rộng. Không dùng hàng nghìn frame gần nhau như hàng nghìn mẫu độc lập để làm kết luận chắc chắn hơn.

Chỉ bổ sung dữ liệu và huấn luyện khi review cho thấy lỗi thuộc model: ưu tiên vật dễ nhầm đã xác nhận không có phone và phone nhỏ, xa, bị che. Ảnh ứng viên chưa được review không tự trở thành nhãn âm tính. Dữ liệu phải giữ nguồn gốc, quyền sử dụng, phân chia và checksum. Mọi huấn luyện tiếp theo thực hiện trên Colab; không huấn luyện trên tập dùng đánh giá cuối.

## Kết luận

Đề tài đã có nguyên mẫu tích hợp YOLO và MediaPipe với luồng video, cảnh báo và snapshot hoạt động trong kiểm thử kỹ thuật. Checkpoint Colab cải thiện P, R và F1 so với v2 trên cùng tập validation. Công cụ so sánh các thành phần và ghi bằng chứng đã được chuẩn bị. Chất lượng giám sát phòng thi, độ chính xác hành vi, tốc độ GPU và độ ổn định cả buổi thi chưa có đủ thực nghiệm để kết luận. Bản sửa giữ các giới hạn này và chỉ dùng những kết quả có nguồn đối chiếu.

## Tài liệu tham khảo

[1] Cheng và cộng sự. YOLO World Real Time Open Vocabulary Object Detection. 2024. https://arxiv.org/abs/2401.17270

[2] Google AI Edge. Pose landmark detection guide và Python guide. https://developers.google.com/edge/mediapipe/solutions/vision/pose_landmarker

[3] Google AI Edge. Hand landmarks detection guide và Python guide. https://developers.google.com/edge/mediapipe/solutions/vision/hand_landmarker

[4] RidgeRun.ai. Cellphones in the Wild v0.1. https://huggingface.co/datasets/ridgerun-ai/citw-v0.1 — revision f31df211860010059745ba29de06d06f16055c6e.

[5] Lin và cộng sự. Microsoft COCO Common Objects in Context. 2014. https://arxiv.org/abs/1405.0312

## Phụ lục nội dung cần đính chính và bằng chứng

| Nội dung bản trước | Nội dung bản sửa |
|---|---|
| Accuracy 91,2%, F1 hành vi 85,3%, khoảng 52 FPS | Chưa có phép đo tương ứng; không dùng làm kết quả đã đạt |
| YOLOv8m, 100 epoch, RTX 3060 | Lượt đang dùng là YOLOv8n, 40 epoch trên Colab; chưa xác minh loại GPU |
| Khoảng 2.690 ảnh gốc, 8.990 ảnh sau tăng cường | Bộ v3 cục bộ có 1.600 train và 214 validation từ nguồn công khai |
| MediaPipe đã dùng trong phiên bản trước | Mã trước dùng YOLO Pose; MediaPipe thật được tích hợp và kiểm tra ngày 06/09/2026 |
| Toàn hệ thống đã kiểm thử thực tế | Đã kiểm thử kỹ thuật; chưa có sáu video độc lập của nhóm |

Bằng chứng trong dự án: artifacts/phone-colab-comparison.json; artifacts/research/phone-comparison.json; artifacts/research/error-analysis/summary.json; artifacts/mediapipe-check/summary.json; artifacts/phone-colab-check-1788700181192987400/summary.json; artifacts/research/technical-ablation.json; artifacts/research/video-ablation-pending.json; artifacts/improvement-tests-final.log; artifacts/stability-30min-mediapipe.json; artifacts/research/detector-variants-validation.json; artifacts/research/detector-variants-validation-fixed.json; artifacts/research/negative-diagnosis/summary.json; models/mediapipe/provenance.json.

Những nội dung cần nhóm và giảng viên xác nhận trước khi sử dụng: tên đăng ký chính thức, phạm vi mục tiêu bắt buộc, kết quả video bổ sung, bản đã nộp và quy trình đính chính, mẫu poster/cam kết. Bản sửa kỹ thuật này không tự thay đổi quyết định nghiệm thu hoặc tình trạng hồ sơ dự giải.
