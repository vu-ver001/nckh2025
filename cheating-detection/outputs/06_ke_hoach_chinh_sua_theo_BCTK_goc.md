# Kế hoạch chỉnh sửa báo cáo tổng kết theo bản gốc

Ngày lập: 08/09/2026. Đây là kế hoạch biên tập, chưa phải bản BCTK đã sửa hoặc hồ sơ được phê duyệt.

## 1 Tài liệu tham chiếu và kết quả cần bàn giao

Tài liệu gốc: [NH8_1-VN_BCTK_HUNRE_NH_2026_11_30_Cao_Thi_Thoa.md](<C:/Users/T14s Gen 3/Downloads/NH8_1-VN_BCTK_HUNRE_NH_2026_11_30_Cao_Thi_Thoa.md>). Các số dòng dưới đây chỉ vị trí trong Markdown hiện tại, không phải số trang PDF đã nghiệm thu. Khi chỉnh, tìm theo cả tên mục và số bảng vì mục lục và thân bài có chỗ đánh số chưa thống nhất.

Giữ bố cục BCTK: phần thông tin kết quả, Mở đầu, Chương 1 Tổng quan, Chương 2 Mục tiêu và phương pháp, Chương 3 Cơ sở lý thuyết, Chương 4 Thiết kế, Chương 5 Thực nghiệm, Kết luận và kiến nghị, tài liệu tham khảo. Không dùng bản Word 11 trang ngày 06/09 để coi là đã sửa đầy đủ BCTK gốc: bản Word trong outputs hiện là bản sao của bản rà soát đó.

Bản sửa đầy đủ sẽ là file mới `BCTK_sua_theo_ban_goc_de_GVHD_ra_soat.md` và `.docx` trong outputs, kèm bảng đối chiếu từng thay đổi. Giữ nguyên BCTK nguồn và các output trước. Chỉ tạo PDF nộp sau khi nhận hướng dẫn xử lý hồ sơ từ GVHD/Khoa.

Đích biên tập: người đọc hiểu mục tiêu ban đầu, phần thực sự đã làm, kết quả nào có dữ liệu kiểm tra, phần nào mới bổ sung và giới hạn áp dụng. Không tự đổi tên đề tài, hạ mục tiêu rồi kết luận đạt toàn bộ, hoặc ghi lùi ngày kết quả mới.

## 2 Nguồn kết quả dùng cho việc sửa

Giữ mã theo [danh mục minh chứng hiện có](02_danh_muc_minh_chung.md), không đánh lại mã khi biên tập:

| Mã | Nguồn trong dự án | Dùng cho phần nào |
|---|---|---|
| MC01 | `dataset/phone_detection_v3/provenance/manifest.json`; `artifacts/phone-v3-data-audit.json` | Nguồn dữ liệu; 1.600 ảnh train và 214 validation, 2.177 và 262 box |
| MC02 | `models/phone_v3_colab/args.yaml`, `results.csv`, `weights/best.pt`; `artifacts/phone-v3-colab-import.json` | Cấu hình, đường cong lượt train, checkpoint và checksum |
| MC03 | `artifacts/phone-colab-comparison.json`; `artifacts/research/phone-comparison.json`, `RESULTS.md`, `phone-benchmark.png` | So sánh checkpoint trên ảnh validation và khoảng bootstrap có giới hạn |
| MC04 | `artifacts/research/error-analysis/summary.json`, `ASSISTANT_REVIEW.md` | Phân tích lỗi theo kích thước và phiếu lỗi có nguồn |
| MC05 | `artifacts/research/detector-variants-validation.json`; `detector-variants-validation-fixed.json` cùng thư mục | Đối chứng detector và kết quả trước/sau sửa ghép box |
| MC06 | `artifacts/mediapipe-check/summary.json`, `pose-hands-overlay.jpg`; `models/mediapipe/provenance.json` | Kiểm tra tích hợp MediaPipe thật và nguồn asset |
| MC07 | `artifacts/phone-colab-check-1788700181192987400/summary.json` và snapshot/log cùng thư mục | Kiểm thử model thật qua video, cảnh báo, snapshot và dừng |
| MC08 | `artifacts/improvement-tests-20260908.log`; `artifacts/stability-30min-mediapipe.json` | 57 kiểm thử phần mềm; kiểm tra thành phần 30 phút ngày 06/09 |
| MC09 | `dataset/phone_negative_candidates/manifest.json`; `artifacts/research/negative-diagnosis/summary.json` | 280 ảnh ứng viên và 75 ảnh kích hoạt model, chưa phải tập âm tính được duyệt |
| MC10 | `demo/recordings/manifest.json`; `artifacts/research/video-ablation-20260908-pending.json` | Trạng thái video bổ sung; hiện 0 clip sẵn sàng, chưa có kết quả |

Mọi số mới phải ghi là phép đo tương ứng trong đợt bổ sung, không phải chứng cứ hồi tố cho số đã ghi trong báo cáo nghiệm thu.

## 3 Kế hoạch theo đúng phần và chương của BCTK

### 3.1 Bìa và Thông tin kết quả nghiên cứu

Vị trí: đầu tệp; các mục Mục tiêu đề tài, Tính mới và sáng tạo, Kết quả nghiên cứu từ dòng 95, 102 và 111.

- Giữ tên trên bìa ở bản làm việc; ghi vào bảng cần xác nhận rằng phần Thông tin chung có biến thể tên khác. Chỉ thống nhất tên/mã theo quyết định hoặc phản hồi GVHD/Khoa.
- Giữ tên thành viên và GVHD theo nguồn; không tự thêm chữ ký, xếp loại, mã dự Giải hoặc lời xác nhận của GVHD.
- Viết lại Kết quả nghiên cứu sau khi Chương 5 hoàn tất. Thay câu đạt Accuracy trên 90% và đã kiểm thử thực tế bằng kết quả cụ thể tại MC03, MC06–MC08 cùng giới hạn.
- Tính mới và sáng tạo: mô tả đóng góp triển khai, xác nhận theo thời gian, công cụ đối chứng và phân tích lỗi. Không coi việc dùng YOLO và MediaPipe là bằng chứng tự đủ của thuật toán mới.
- Khả năng ứng dụng: chuyển các kết luận giảm gian lận/giảm tải thành mục đích hoặc tiềm năng chưa đo được. Công bố: giữ thông tin chưa có công bố tại thời điểm báo cáo, chờ nhóm xác nhận cập nhật nếu có.
- Ngày trên nội dung gốc không được dùng để ký cho bản bổ sung; bản sửa ghi ngày biên tập thật và trạng thái rà soát.

### 3.2 Mở đầu

Vị trí: dòng 420, MỞ ĐẦU.

Giữ vấn đề hỗ trợ giám thị và lý do nghiên cứu. Rà từng nhận định định lượng về gian lận hoặc lợi ích giám sát: có nguồn phù hợp thì giữ; thiếu nguồn thì bỏ con số hoặc viết ở mức vấn đề cần khảo sát. Kết đoạn bằng phạm vi đã triển khai một người/một nguồn video và mục đích kiểm chứng, không hứa xử lý toàn phòng hoặc thời gian thực nếu chưa đo.

### 3.3 Chương 1 Tổng quan các vấn đề nghiên cứu

Vị trí: dòng 464–650; Bảng 1.1 ở dòng 543.

- Kiểm tra từng công trình: tác giả, năm, tên bài, đường dẫn/DOI, nhiệm vụ, dataset, metric và phần cứng. Chỉ giữ nội dung khi tìm được bài gốc hoặc nguồn chính thức; chưa tìm được thì đánh dấu trong bảng rà soát, không sử dụng làm chứng cứ so sánh.
- Bảng 1.1 dùng các cột Công trình, Bài toán, Dữ liệu, Phương pháp, Giới hạn liên quan. Chỉ giữ số metric khi rõ cách đo; không xếp hạng các nghiên cứu khác dataset.
- Phần khoảng trống nghiên cứu tập trung vào khó phân biệt vật giống phone, phone nhỏ/che và tác động quy tắc thời gian. Ghi đây là vấn đề thực nghiệm cần kiểm tra, không tuyên bố chưa ai làm hoặc hệ thống đã giải quyết hoàn toàn.
- Nội dung so sánh công trình ở Bảng 5.5 được chuyển về đây nếu nguồn xác minh được, tránh lặp hai bảng tổng quan.

### 3.4 Chương 2 Mục tiêu đối tượng phạm vi nội dung và phương pháp

Vị trí: dòng 653–833; mục tiêu ở dòng 655, phạm vi 681, phương pháp 810.

Giữ các mục tiêu ban đầu như dấu vết nghiên cứu; thêm bảng Mục tiêu ban đầu và mức thực hiện để tránh hiểu rằng đã đạt toàn bộ:

| Mục tiêu trong bản gốc | Cách trình bày mức thực hiện |
|---|---|
| Nghiên cứu CNN, YOLOv7/v8, MediaPipe | Phân biệt nội dung tổng quan với công nghệ thực sự triển khai; bản đang dùng là YOLO-World và YOLOv8n phone, MediaPipe Tasks |
| Xây dữ liệu phone và tai nghe trong phòng thi | Bộ được kiểm tra hiện là dữ liệu phone công khai; chưa chứng minh hoàn tất dữ liệu tai nghe/phòng thi |
| Huấn luyện đạt độ chính xác trên 90% | Giữ là mục tiêu ban đầu; metric Accuracy chưa được định nghĩa/đo phù hợp, chưa có căn cứ kết luận đạt. Không đổi F1 thành Accuracy |
| MediaPipe phát hiện hành vi theo thời gian thực | Đã tích hợp Pose/Hands ngày 06/09; chưa đánh giá định lượng hành vi và chưa xác nhận đạt yêu cầu tốc độ |
| Đánh giá P/R/FPS, so sánh công trình | Có đánh giá checkpoint và đối chứng nội bộ; chưa có test video độc lập/benchmark cùng điều kiện với công trình khác |

Câu hỏi nghiên cứu dùng cho phần bổ sung: checkpoint v2 và Colab khác nhau ra sao trên cùng validation; sửa ghép box tác động thế nào; xác nhận theo thời gian và phủ quyết vật được phép ảnh hưởng cảnh báo ra sao trên video có nhãn. Câu hỏi cuối để trạng thái chưa trả lời nếu MC10 chưa hoàn thành.

Phương pháp bổ sung mô tả ghép prediction–ground truth một-một, metric ở mức box và event tách biệt, validation đã dùng chọn checkpoint, video pilot riêng. Không coi hàng nghìn frame liên tiếp là hàng nghìn mẫu độc lập.

### 3.5 Chương 3 Cơ sở lý thuyết

Vị trí: dòng 835–1355.

- Rút gọn CNN và YOLOv7 ở mức cần cho bối cảnh; bổ sung YOLO-World vào phần mô hình thực sự sử dụng. Đối chiếu mô tả grid/anchor với đúng phiên bản, không áp cơ chế YOLO đời đầu cho mọi YOLO.
- Giữ nguyên lý Pose 33 điểm và Hands 21 điểm nhưng phân biệt landmark, luật hình học và bộ phân loại hành vi. MediaPipe Hands hiện không phải một classifier trao đổi bài.
- Mục FPS chỉ giải thích định nghĩa; số tốc độ từ tài liệu bên ngoài cần nguồn/phần cứng và không được coi là tốc độ hệ thống của nhóm.
- Bổ sung TP/FP/FN cho detection; không dùng Accuracy dựa trên true negative chưa định nghĩa. Tách F1 tại ngưỡng cố định với mAP tích phân theo confidence.
- Hình 3.9 là confusion matrix kết quả thực nghiệm: nếu có file gốc đúng checkpoint thì chuyển sang Chương 5 với nguồn; nếu chỉ minh họa thì ghi minh họa và bỏ nhãn kết quả đề tài; không có file thì bỏ.
- Sửa chú thích Hình 2.9 trong phần MediaPipe Hands cho đúng Chương 3; cập nhật danh mục hình sau khi chốt.

### 3.6 Chương 4 Thiết kế và xây dựng hệ thống

Vị trí: dòng 1357–1748. Đây là phần cần viết lại theo mã và dữ liệu hiện có.

| Mục trong BCTK | Nội dung chỉnh sửa cụ thể | Căn cứ |
|---|---|---|
| Yêu cầu chức năng và phi chức năng | Tách yêu cầu dự kiến với chức năng đã kiểm tra; ngưỡng tốc độ/mức chính xác là yêu cầu, không gắn dấu đạt khi chưa đo | MC07–MC08 |
| Hình 4.1 và Hình 4.2 | Vẽ lại khi biên tập: nguồn video → đồng hồ nguồn → detector phone/World và MediaPipe → fusion → cảnh báo/snapshot → dashboard. Không gọi hai nhánh là chạy song song nếu mã thực thi tuần tự | `src/fastapi_server.py`, MC07 |
| Fusion Logic, dòng 1453 | Bỏ mô tả chỉ một nhánh thì chỉ cảnh báo thấp. Mô tả điểm theo trọng số: phone 12, tối đa tổng 30, mỗi loại tối đa một lần/giây nguồn; cooldown 10 giây nguồn. Điểm không phải xác suất gian lận | `src/fusion_engine.py`, `src/config.py` |
| Debouncing | Thay N=5–10 frame bằng ít nhất ba quan sát mới kéo dài 0,2 giây; gián đoạn trên 0,5 giây reset, lấy mẫu detector theo 0,1 giây nguồn. Cache không tính thành bằng chứng mới | `src/temporal.py`, MC08 |
| Xác nhận phone | Dùng box/confidence model phone; World chỉ ghi hỗ trợ ghép; loại trùng. Nêu rõ phủ quyết vật được phép có thể làm bỏ sót và cần đối chứng | MC05, `src/yolo_detector.py` |
| Thu thập, gán nhãn, augmentation | Mô tả dữ liệu kế thừa từ CITW/COCO và chuyển định dạng/kiểm tra nhãn. Không khẳng định nhóm đã dùng LabelImg/Roboflow để tạo toàn bộ dữ liệu nếu thiếu lịch sử dự án tương ứng | MC01 |
| Bảng 4.1 | Thay bằng train 1.600 ảnh/2.177 box; validation 214 ảnh/262 box; một lớp phone; test video chưa đánh giá. Không tính online augmentation thành 8.990 file độc lập | MC01 |
| Bảng 4.2 | Thay toàn bộ trường theo args: YOLOv8n, pretrained yolov8n.pt, 40 epoch, batch16, imgsz640, seed42. Optimizer ghi `auto` nếu chỉ có args; chưa suy ra SGD thực tế. Các lr, workers, augmentation phải đọc giá trị lưu, không giữ số mẫu từ bảng cũ | MC02 |
| Bảng 4.3 và các luật tư thế | Lập lại bảng tín hiệu đầu vào, điều kiện, thời gian duy trì, trường hợp thiếu landmark, nhãn cảnh báo. Ghi chưa hiệu chỉnh/đánh giá hành vi độc lập | MC06 và mã analyzer/fusion |
| Giao diện | Chỉ chụp giao diện thật, ghi checkpoint/backend và nguồn video; phân biệt ảnh fixture với video nhóm. Mô tả start/stop, MJPEG, WebSocket, snapshot, lỗi/fallback đúng kiểm thử | MC07–MC08 |

### 3.7 Chương 5 Thực nghiệm và đánh giá kết quả

Vị trí: dòng 1750–1980. Ưu tiên sửa chương này trước các phần tóm tắt và kết luận.

| Bảng hoặc mục gốc | Phương án thay thế |
|---|---|
| Bảng 5.1 Môi trường | Tách môi trường Colab từ log và máy đánh giá cục bộ từ artifact; ghi ngày, phiên bản, checkpoint. Không giữ thông số RTX3060 nếu chưa xác nhận. Máy mạnh mới chỉ có tên trong bảng sau khi đã thực sự đo |
| Kết quả huấn luyện, Hình 5.1–5.2 | Dùng đồ thị có sẵn từ đúng run hoặc dựng lại từ results.csv; chú thích 40 epoch. Các chỉ số checkpoint lưu và đánh giá lại là hai phép đo khác nhau, không tráo cột |
| Bảng 5.2 Theo ba lớp | Thay bằng So sánh checkpoint phone trên 214 ảnh validation. Bỏ kết quả định lượng tai nghe/tài liệu không có model, nhãn và phép đo tương ứng |
| Bảng 5.3 Hành vi | Thay bảng P/R/F1 chưa có căn cứ bằng Trạng thái kiểm chứng mô-đun tư thế: nạp asset, trả landmark, hiển thị và luật đã test; cột độ chính xác ghi chưa đánh giá. Không dùng số test làm số mẫu hành vi |
| Bảng 5.4 Tổng thể | Đổi thành Mức đạt các yêu cầu hệ thống: chức năng đã test, nguồn kiểm thử, giới hạn, yêu cầu chưa đo. Rút dấu đạt đi kèm 91,2%, 85,3%, 52 FPS, 19 ms và 90 phút |
| Bảng 5.5 So với công trình | Thay bằng Đối chứng các cấu hình trên cùng validation, lấy MC05. Nội dung nghiên cứu liên quan chuyển về Chương 1, không so MOTA với Accuracy |
| Bảng 5.6 mới | Phân tích lỗi theo kích thước từ MC04, định nghĩa diện tích tương đối và số GT/TP/FN |
| Bảng 5.7 mới nếu có dữ liệu | Kết quả video pilot từng clip/từng cấu hình; chỉ lập khi MC10 có nhãn review và output thật. Nếu thiếu thì giữ mục thiết kế và trạng thái, không tạo bảng số liệu |

Bảng 5.2 dự kiến dùng đúng số sau:

| Checkpoint | TP | FP | FN | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|---:|
| phone v2 | 41 | 137 | 221 | 23,03% | 15,65% | 18,64% |
| phone v3 Colab | 124 | 78 | 138 | 61,39% | 47,33% | 53,45% |

Điều kiện: confidence 0,30; NMS IoU 0,45; IoU ghép nhãn 0,50; 214 ảnh/262 phone; validation đã dùng chọn checkpoint. Không kết luận đây là chất lượng toàn hệ thống hoặc test phòng thi độc lập.

Bảng 5.5 dự kiến dùng TP/FP/FN: World 112/69/150; phone 124/73/138; kết hợp trước sửa 124/109/138; kết hợp sau sửa 124/73/138. World phone confidence0,40, phone0,30; tắt pose và phủ quyết vật được phép. FP73 khác FP78 ở Bảng5.2 do xử lý pipeline gồm tọa độ nguyên và lọc trùng, không phải số liệu mâu thuẫn cần chọn một.

Thảo luận phải trả lời cả kết quả không như mong muốn: recall phone nhỏ thấp; sửa logic giảm FP nhưng chưa làm World tốt hơn phone riêng; tư thế chưa đánh giá; phiên ổn định 30 phút chỉ là video lặp và diễn ra trước sửa ghép box cuối cùng; không suy độ trễ end-to-end từ FPS.

### 3.8 Kết luận và kiến nghị

Vị trí: dòng 1982–2094.

Viết lại sau khi khóa Chương5. Đóng góp lý luận mô tả phương pháp tích hợp và thiết kế kiểm chứng, không tuyên bố kiến trúc chưa từng được công bố. Đóng góp thực tiễn ghi nguyên mẫu và công cụ có thể kiểm tra. Loại câu hoàn thành hệ thống 91,2%/52FPS và xây bộ phòng thi2.690/8.990 ảnh.

Mục Mức độ đạt mục tiêu dùng lại bảng Chương2, diễn giải mục nào đạt một phần hoặc chưa có dữ liệu. Đề xuất tiếp theo theo lỗi quan sát: video độc lập, review ảnh âm tính, phone nhỏ/xa/che; multi-person, nhận diện danh tính, edge/cloud là hướng sau. Không train thêm trong đợt biên tập để cố đạt số cũ.

### 3.9 Tài liệu tham khảo và phụ lục

Vị trí: TÀI LIỆU THAM KHẢO từ dòng2095; Danh sách hình ảnh cần bổ sung từ dòng2179.

- Kiểm từng trích dẫn với nguồn gốc; bỏ tài liệu không xác minh được khỏi bản nội dung chốt. Bổ sung đúng nguồn YOLO-World, Ultralytics, MediaPipe, CITW/COCO được sử dụng và ngày truy cập khi thực sự kiểm tra.
- Giữ URL/revision/checksum dữ liệu ở phụ lục; ghi giấy phép theo nguồn, không tự kết luận mọi ảnh đều được phép phát hành lại.
- Đưa bảng đính chính sang phụ lục rà soát riêng; không để danh sách hình cần bổ sung hoặc các lệnh hướng dẫn người soạn lẫn trong BCTK nộp.
- Lập bảng nguồn hình: số hình, file gốc, ai tạo, dữ liệu nào, giấy phép/đồng ý sử dụng, chú thích. Hình không có file gốc hoặc quyền sử dụng chưa rõ thì chưa đưa vào bản chốt.
- Nhóm xác nhận khai báo AI: hỗ trợ code, phân tích, review, biên tập; phần nào đã được con người kiểm tra. Phân biệt AI là công cụ nghiên cứu với AI hỗ trợ tạo nội dung báo cáo.

## 4 Xử lý riêng hình ảnh và mục lục

| Hình cũ | Quyết định biên tập |
|---|---|
| Hình4.3 LabelImg, Hình4.4 Roboflow | Chỉ giữ nếu có ảnh dự án thật và chứng minh quy trình đó thuộc dữ liệu báo cáo. Nếu không, thay bằng minh họa nhãn/dữ liệu thực tế với nguồn rõ |
| Hình4.5 phân bố lớp | Dựng lại từ số ảnh/box phone theo split, không giữ biểu đồ ba lớp |
| Hình4.6 giao diện | Ảnh dashboard thật; chú thích video kỹ thuật hoặc clip nhóm cụ thể |
| Hình5.3 phone conf0,90 | Thay bằng snapshot thật với confidence thật; không sửa nhãn trên ảnh để đạt0,90 |
| Hình5.4 tai nghe | Bỏ khỏi nhóm kết quả đã kiểm chứng nếu chưa có ảnh/dữ liệu và kiểm tra nhãn; có thể giữ là ví dụ thăm dò khi ghi rõ giới hạn |
| Hình5.5 cúi đầu, Hình5.6 tay | Dùng overlay thật; chỉ gọi là quan sát landmark/luật cảnh báo, không gọi là hành vi nhận diện đúng khi thiếu nhãn |

Sau biên tập, đánh lại số bảng/hình và cập nhật mục lục theo heading/caption thật. Không dùng số trang ghi trong Markdown gốc làm số trang tài liệu mới.

## 5 Trình tự thực hiện và tiêu chí kết thúc

| Thứ tự | Công việc | Người thực hiện | Đầu ra kiểm tra |
|---|---|---|---|
| 1 | Đóng băng bản gốc, ghi checksum; tạo bảng thay đổi theo mục/bảng/dòng và MC | Trợ lý | Không đổi nguồn; mỗi sửa đổi có vị trí và lý do |
| 2 | Sửa Chương5 từ kết quả thô, tiếp theo Chương4 từ mã/cấu hình | Trợ lý | Bảng số liệu cộng khớp; mô tả thực thi đúng nguồn |
| 3 | Đối chiếu mục tiêu Chương2, sửa Mở đầu/Tổng quan/Lý thuyết | Trợ lý; nhóm/GVHD chốt phạm vi | Không hạ mục tiêu âm thầm, không giữ nguồn chưa xác minh |
| 4 | Nhập video và review nhãn khi nhóm cung cấp; nếu chưa có thì khóa trạng thái chưa đánh giá | Trợ lý hỗ trợ; nhóm xác nhận | Chỉ đưa kết quả có video, nhãn và output thực |
| 5 | Viết lại thông tin kết quả, kết luận; rà hình, trích dẫn, AI và quyền sử dụng | Trợ lý; nhóm xác nhận thông tin | Tất cả phần tóm tắt thống nhất Chương5 |
| 6 | Dựng Word theo bố cục BCTK, render và xem từng trang; kiểm liên kết minh chứng | Trợ lý | Không lỗi bảng/hình, không hình placeholder, không dữ liệu giả |
| 7 | Quyết định bản thay thế hay phụ lục bổ sung và hồ sơ nộp | GVHD/Khoa/nhóm | Có hướng dẫn được xác nhận; không tự nộp |

Phần sửa nội dung không phải chờ giấy tờ nếu bằng chứng đã đủ. Phần video phụ thuộc file gốc và nhãn; phần dùng tài liệu để thay báo cáo chính thức phụ thuộc GVHD/Khoa. Hạn09/09 theo thông báo hiện có, chưa biết giờ chốt; không cam kết hoàn tất thực nghiệm mới trước khi nhận đầu vào.

Tiêu chí nghiệm tra bản sửa: mỗi số có nguồn và điều kiện; mỗi mục tiêu có mức đạt; mỗi ảnh có nguồn; không trộn metric hoặc tập dữ liệu; thời điểm bổ sung rõ; tên/mã và phê duyệt chưa có thì chưa giả định; nguồn gốc được giữ; bản sửa theo đủ bố cục BCTK chứ không chỉ sao chép bản rà soát11trang. Các số cũ chỉ được xuất hiện trong bảng đính chính với trạng thái đã rút/chưa xác minh, không nằm trong kết quả đạt được.

## 6 Việc cần nhóm cung cấp để chốt

1. Video gốc đã quay và thông tin phiên; người thứ hai review nhãn.
2. Tài liệu xác nhận tên/mã, bản PDF đã nộp và nghiệm thu; phản hồi GVHD/Khoa về cách đính chính.
3. File ảnh/sơ đồ gốc muốn giữ từ BCTK và nguồn của chúng; bản Markdown hiện tham chiếu `media/image*` không đủ để mặc định ảnh sẵn có.
4. Xác nhận công bố mới nếu có, phạm vi hỗ trợ AI và quyền dùng hình người tham gia.

Các mục này là đầu vào để hoàn thiện những phần phụ thuộc, không phải yêu cầu xin lại quyền soạn bản sửa đã được người dùng cho phép.
