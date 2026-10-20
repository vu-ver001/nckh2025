# Kế hoạch cải thiện đề tài đến hạn 09/09/2026

Ngày lập: 06/09/2026. Đây là kế hoạch đề xuất, chưa phải công việc đã hoàn thành hoặc cam kết đạt các chỉ tiêu trong báo cáo cũ. Phạm vi được người dùng chốt: một người trong một nguồn video; chỉ huấn luyện trên Google Colab. Video dự kiến quay thứ Hai 07/09 cùng các thành viên.

## 1. Kết quả cần bàn giao và điểm xuất phát

Đích trước hạn: một demo có thể chạy lại, một phép đánh giá có dữ liệu và log kiểm tra được, một bản báo cáo mô tả đúng phần thực hiện, cùng danh sách nội dung cần đính chính của bản đã nghiệm thu. Không đặt các số tự tạo 91,2%, 85,3%, 52 FPS thành kết quả bắt buộc phải đạt.

Hiện có: Colab YOLOv8n 40 epoch; luồng video–cảnh báo–snapshot–dashboard đã kiểm thử kỹ thuật; 41 kiểm thử ở lần chạy đã lưu gần nhất. So sánh phone trên 214 ảnh validation/262 đối tượng, confidence 0,30, matching IoU 0,50: precision 61,39%, recall 47,33%, F1 53,45%. Validation này đã dùng chọn checkpoint, không phải test phòng thi. Chưa có sáu video, chưa có đối chứng bốn cấu hình, chưa có MediaPipe trong luồng chạy thật.

Nguồn: [đối chiếu báo cáo](DOCUMENT_REVIEW_2026-09-06.md), [kết quả detector](../artifacts/phone-colab-comparison.json), [phân tích lỗi](../artifacts/research/error-analysis/summary.json).

## 2. Phân công và quyết định cần chốt

| Vai trò | Trách nhiệm |
|---|---|
| Trợ lý | Sửa mã, công cụ đo, kiểm thử; soạn bảng kết quả, bản sửa báo cáo và danh sách thay đổi |
| Người dùng / đầu mối nhóm | Xác nhận bản nào đã nộp cho ai, tập hợp file, liên hệ GVHD/Khoa, điều phối buổi quay |
| Thành viên quay | Quay video gốc, ghi điều kiện và mã phiên; không xem output model để lựa cảnh có lợi |
| Thành viên gán nhãn + người kiểm tra thứ hai | Đánh dấu thời điểm và đối tượng; giải quyết bất đồng, khóa nhãn trước đo |
| GVHD / Khoa | Thống nhất phạm vi học thuật, tên đề tài và hướng xử lý MediaPipe; hướng dẫn đính chính/bổ sung bản đã nghiệm thu, xác nhận hồ sơ nộp |

Chưa phân công tên cụ thể cho các vai trò trong nhóm. Hạn cấp Trường 09/09 do người dùng xác nhận; giờ đóng cổng/hạn nội bộ, xếp loại và tình trạng đề cử chưa được xác minh. Người dùng nói có thể một thành viên đã nộp; chưa biết nộp Khoa hay Trường. Cần xác nhận ngay ngày 06/09, không chờ có model tốt hơn.

Quyết định MediaPipe: vì tên báo cáo có MediaPipe, ưu tiên kiểm tra khả năng tích hợp thật trong một cấu hình riêng. Nếu tên/phạm vi bắt buộc giữ, đây là việc bắt buộc phải thực hiện hoặc công khai chưa đạt. Chỉ giữ YOLO-Pose làm phương pháp chính khi nhóm/GVHD thống nhất mô tả phù hợp. Không tự đổi tên đề tài đăng ký và không coi tên tệp `mediapipe_analyzer.py` là bằng chứng dùng MediaPipe.

## 3. Lịch thực hiện và phụ thuộc

Các hạn dưới đây là mục tiêu điều phối theo ngày Việt Nam, phụ thuộc giờ có video và phản hồi GVHD. Khối lượng ước tính là giờ làm việc tập trung, không phải thời gian chạy máy hoặc bảo đảm hoàn thành.

| Mốc | Công việc | Người làm | Đầu ra / điều kiện chuyển bước |
|---|---|---|---|
| 06/09, ưu tiên đầu | Xác nhận hồ sơ đã nộp, thông báo sai lệch, xin hướng dẫn đính chính; lấy tên đăng ký và mẫu hồ sơ | Nhóm + GVHD/Khoa | Biết bản gốc nào cần đối chiếu, đường xử lý hồ sơ và yêu cầu MediaPipe |
| 06/09 | Đóng gói phiên bản hiện tại, lưu hash code/model/config; lập bảng tuyên bố–bằng chứng (1–2 giờ) | Trợ lý | Baseline có thể khôi phục; giữ nguyên file đã nộp |
| 06/09 đến trước đánh giá 07/09 | Kiểm tra MediaPipe trong cấu hình riêng; thống nhất đồng hồ video và công cụ bốn cấu hình (ước tính 6–10 giờ, có thể vượt) | Trợ lý | Kết quả khả thi MediaPipe; evaluator có bài kiểm tra tính công bằng |
| 07/09, buổi quay | Sáu clip độc lập, metadata, nhãn hai người kiểm tra | Nhóm | File đọc được, nhãn khóa, biết clip nào để đánh giá/hiệu chỉnh |
| 07/09 sau nhận dữ liệu → sáng 08/09 | Chạy cấu hình đã khóa, xem lỗi, sửa lỗi phần mềm có thể tái hiện; chỉ chạy lại phần bị ảnh hưởng | Trợ lý + người review | Kết quả thô, bảng từng clip, phân loại lỗi và giới hạn |
| 08/09 trước phiên review | Chốt phiên bản; kiểm tra demo, độ ổn định; sửa báo cáo, tóm tắt và minh chứng | Trợ lý | Bản sửa gắn nguồn, bảng thay đổi so với bản đã nộp |
| 08/09 cuối ngày | Review với GVHD; hoàn thiện poster khi có mẫu, hồ sơ và lời trình bày | Nhóm + GVHD, trợ lý hỗ trợ | Các tuyên bố thống nhất, phần thiếu được ghi rõ, hình thức hồ sơ đúng mẫu |
| 09/09 trước hạn thực tế của Khoa | Nộp/thay thế/bổ sung theo hướng dẫn, lưu xác nhận nhận hồ sơ | Người được nhóm phân công | File cuối và xác nhận gửi/nhận |

Nếu thiếu thời gian: ưu tiên sửa tuyên bố và tính đúng của phép đo, sau đó demo ổn định; giảm số thí nghiệm và ghi rõ phần chưa làm. Không bỏ giới hạn, không tạo số liệu để điền bảng. Không phát triển thêm camera, nhận diện danh tính, nhận diện toàn phòng hoặc chức năng giao diện ngoài nhu cầu demo.

## 4. Gói kỹ thuật A — thời gian và logic cảnh báo

Tệp dự kiến: `src/fusion_engine.py`, `src/fastapi_server.py`, `src/mediapipe_analyzer.py`, `src/config.py`, `scripts/evaluate_demo_videos.py`.

1. Truyền thời gian nguồn vào quy tắc cảnh báo. Video dùng timestamp trình chiếu nếu đọc được; CFR có thể dùng chỉ số frame/FPS đã xác minh; camera dùng đồng hồ đơn điệu. Thời điểm ghi log lịch và thời gian đo xử lý là trường riêng. Kiểm tra timestamp tăng, gap lớn, EOF và reset phiên.
2. Persistence, decay và cooldown dùng cùng cơ sở thời gian. Timestamp của kết quả mới quyết định quan sát; dữ liệu cache không làm tăng xác nhận. Khi bị mất quan sát quá lâu phải reset/giảm trạng thái theo quy tắc ghi rõ.
3. Lưu số sự kiện trước cooldown và thông báo sau cooldown. Không coi giảm thông báo do cooldown dài là detector chính xác hơn. Cố định lịch lấy mẫu theo thời gian nguồn cho mọi cấu hình so sánh; ghi số frame xử lý/bỏ qua.
4. Chuẩn hóa tọa độ hoặc khoảng cách theo kích thước cơ thể cho các luật tay/tư thế nếu có lỗi tái hiện. Cúi xuống viết và chạm tai là quan sát hành vi, không tự xác nhận gian lận.
5. Rà soát quy tắc ưu tiên vật được phép trong `src/yolo_detector.py`. Tạo ca phone thật cạnh Casio/hộp bút và ca chỉ có vật dễ nhầm. Thử thay đổi quy tắc bằng một tùy chọn riêng; chỉ đưa vào bản chính khi kiểm tra được đánh đổi FP/FN. Không bỏ toàn bộ bộ lọc theo suy đoán.

Tiêu chí hoàn thành: cùng chuỗi detection/keypoint có cùng timestamp phải tạo cùng sự kiện dù thêm độ trễ xử lý; bắt đầu/dừng reset trạng thái; frame cache không tạo bằng chứng; mất người/keypoint không kích hoạt cảnh báo giả; hai box không chia sẻ sai bộ đếm. Với video lấy mẫu khác nhau, không hứa kết quả tuyệt đối giống nhau vì thông tin quan sát có thể khác.

## 5. Gói kỹ thuật B — MediaPipe có bằng chứng sử dụng

Thử theo MediaPipe Tasks API: [Pose Landmarker](https://developers.google.com/edge/mediapipe/solutions/vision/pose_landmarker/python) và [Hand Landmarker](https://developers.google.com/edge/mediapipe/solutions/vision/hand_landmarker/python). Hai API cung cấp landmark ảnh/video; việc suy luận hành vi vẫn phải thiết kế và kiểm thử riêng. Kiểm tra môi trường đang cài, nạp asset và suy luận thật theo [hướng dẫn Python](https://developers.google.com/edge/mediapipe/solutions/setup_python), không kết luận chỉ từ việc import thành công.

- Kiểm tra khả thi ban đầu giới hạn khoảng 2 giờ làm việc: tạo model task, đọc ảnh/video kiểm thử, lấy landmark, đo thời gian và kiểm tra khả năng tích hợp. Nếu lỗi môi trường, ghi rõ; thử môi trường riêng phù hợp thay vì phá môi trường demo đang chạy.
- Adapter thống nhất output hành vi, confidence, backend đang dùng; dashboard và log hiển thị `MediaPipe` hay `YOLO-Pose` thực tế. Không fallback im lặng.
- Tách kiểm thử cơ thể và bàn tay, xử lý mất landmark; lưu ảnh minh chứng và cấu hình. Chỉ chọn backend sau kiểm thử tích hợp.
- Nếu GVHD yêu cầu chứng minh hành vi: cần video/nhãn hành vi riêng, gồm hành vi mục tiêu và cử chỉ tự nhiên dễ nhầm. Sáu video phone không đủ để báo F1 cho quay đầu/tay. Có thể đề xuất thêm bốn clip 30 giây trong buổi quay nếu nhóm thu xếp được; đây là phát sinh tùy chọn, chưa được coi đã có dữ liệu.
- Tích hợp MediaPipe thành công chỉ chứng minh thành phần hoạt động, không chứng minh F1 85,3%, tốc độ 52 FPS hoặc khả năng suy luận gian lận.

## 6. Gói nghiên cứu C — đối chứng bốn cấu hình

Câu hỏi: xác nhận điện thoại bằng model chuyên dụng và tính liên tục theo thời gian có giảm cảnh báo nhầm, với đánh đổi nào về bỏ sót, độ trễ và tốc độ?

| Mã | Cấu hình | Mục đích |
|---|---|---|
| A | YOLO-World, nhãn điện thoại | Baseline detector mở |
| B | Checkpoint phone Colab | Baseline detector chuyên dụng |
| C | World + phone, không persistence | Kiểm tra tác động kết hợp detector |
| D | C + persistence theo thời gian | So C/D để đo tác động xác nhận liên tục |

Khóa trước đo: video/nhãn, checkpoint/hash, prompt, confidence từng model (khởi đầu World phone 0,40; phone 0,30 như cấu hình hiện tại), NMS, matching, kích thước đầu vào, lịch lấy mẫu, cooldown và cách gom sự kiện. Dùng cùng ngưỡng của mỗi detector ở mọi cấu hình chứa detector đó; không giả định confidence hai model đã được hiệu chuẩn tương đương.

Trong thí nghiệm phone chính, tắt đóng góp pose và điểm hành vi để tách đúng tác động. A/B/C có cùng bộ chuyển observation thành sự kiện, D chỉ thay điều kiện persistence. Vật được phép không được lọc khác nhau giữa A–D mà không ghi rõ: đề xuất tắt bộ phủ quyết allowed trong thí nghiệm chính, đánh giá nó riêng dưới một tùy chọn C/D cùng điều kiện. Luồng ứng dụng đầy đủ được đo riêng với cấu hình thực tế. Không dùng kết quả biến thể ablation để gắn nhãn là kết quả hệ thống sản xuất đầy đủ.

Đo từng video: số sự kiện thật, phát hiện, bỏ sót; số cảnh báo sai/clip; tổng thời gian video; thời điểm cảnh báo đầu tiên so với bắt đầu sự kiện; FPS xử lý sau warm-up và thời gian nạp model tách riêng. Nhãn đúng loại và khoảng thời gian, mỗi sự kiện thật khớp tối đa một sự kiện dự đoán; thông báo lặp thống kê riêng. Nếu tính event precision/F1 phải định nghĩa đơn vị event, cách nối/kết thúc và ghép một-một; không lấy tất cả thông báo cùng khoảng nhãn thành nhiều TP.

Để phân biệt lỗi detector/rule trên video: bổ sung bbox phone ở các frame lấy mẫu cố định, ví dụ 1 frame/giây cho sáu clip (~180 frame), kèm frame quanh chuyển cảnh để chẩn đoán. Nếu chưa gán bbox, chỉ báo phân loại lỗi bằng review thủ công, không tuyên bố detector precision/recall từ nhãn thời gian đơn thuần.

Lưu prediction thô giúp so lại quy tắc công bằng, nhưng FPS phải đo chạy thật từng cấu hình, không đo từ cache. Không suy ra độ trễ camera→dashboard từ FPS hoặc trễ theo thời gian video. Sáu clip chỉ là pilot; ưu tiên số đếm và kết quả từng clip, không trình bày khoảng tin cậy mạnh từ hàng nghìn frame phụ thuộc nhau.

## 7. Gói dữ liệu D — buổi quay và chống rò rỉ đánh giá

Sáu clip × khoảng 30 giây: hai bình thường, hai Casio/hộp bút/sổ, hai điện thoại rõ/xa/che. Một người mỗi lượt, cùng camera/góc dự kiến. Nếu thay người giữa các clip, lưu mã người và phiên; không tuyên bố so sánh cấu hình camera hoặc tổng quát nhiều người từ thiết kế này.

Giữ video gốc, metadata độ phân giải/FPS/ánh sáng/khoảng cách, SHA256, nhãn thời gian bắt đầu–kết thúc. Người thứ hai kiểm tra nhãn độc lập với dự đoán. Clip âm tính được xác nhận dùng `[]`; chưa review dùng `null`.

Phương án mặc định: khóa cấu hình trước khi xem kết quả sáu clip và dùng cả sáu để đánh giá pilot. Nếu cần chỉnh ngưỡng theo lỗi của chúng, đổi vai trò thành hiệu chỉnh; đề nghị một phiên quay độc lập khác cho đánh giá cuối. Không chia frame cùng một clip sang train/test; không đưa sáu clip hoặc crop validation hiện có vào train rồi tiếp tục báo chất lượng trên chính chúng.

## 8. Gói kiểm thử E — chốt demo

- Chạy lại 41 kiểm thử đã có; thêm kiểm thử có ý nghĩa cho đồng hồ thời gian, ghép sự kiện một-một, bỏ sót do overlap và backend MediaPipe nếu triển khai. Số test tăng không phải chỉ tiêu chất lượng nghiên cứu.
- Kiểm thử model thật qua start → video → cảnh báo → snapshot → stop, tiếp đó start lại; xác nhận trạng thái model/backend/fallback đúng.
- Client WebSocket chậm hoặc mất kết nối không làm dừng detection; thiếu file/model/video báo lỗi rõ. Tách log fixture kỹ thuật với video độc lập.
- Chạy liên tục tối thiểu 30 phút như mục tiêu kiểm tra ổn định đề xuất, lưu CPU/RAM/lỗi/FPS. Nếu muốn giữ tuyên bố 90 phút, phải chạy đủ 90 phút và ghi đúng nguồn video (kể cả video lặp); đây không phải 90 phút dữ liệu phòng thi độc lập.
- Chạy build frontend và đóng gói cấu hình, model hash, lệnh chạy, kết quả. Chỉ sửa lỗi nghiêm trọng sau khi chốt ngày 08/09; mọi sửa sau đo phải xác định phần kết quả bị ảnh hưởng.

Tiêu chí kỹ thuật đề xuất: cảnh phone rõ phát ít nhất một cảnh báo đúng khoảng thời gian, snapshot tương ứng xem được, phiên chạy/dừng/khởi động lại được; lỗi client không làm dừng luồng. Nếu chưa đạt, ghi demo chưa đạt. Không ép kết quả âm tính thành 0 báo nhầm; báo số đo thật. Không dùng các tiêu chí này thay tiêu chí nghiệm thu chính thức của Khoa/Trường.

## 9. Gói hồ sơ F — bản sửa và minh chứng

1. Lập bảng từng tuyên bố cũ: giữ có nguồn, sửa theo phép đo mới, hoặc bỏ/đánh dấu chưa thực hiện. Ghi lượt đo, ngày, dataset, model, phần cứng và phạm vi kết luận.
2. Sửa Chương 4 theo kiến trúc thực tế; Chương 5 theo bảng kết quả và hình có nguồn; viết lại tóm tắt và kết luận sau cùng để thống nhất. Phân biệt mục tiêu đăng ký với mức đã hoàn thành.
3. Rà soát tài liệu tham khảo theo bản gốc/DOI/URL; chưa tìm được nguồn thì không dựa vào nó để khẳng định tính mới. Không so trực tiếp MOTA với Accuracy hoặc FPS trên máy khác để tuyên bố vượt trội.
4. Chuẩn bị PDF báo cáo và tóm tắt; poster khi có mẫu của Phòng; bảng minh chứng, checksum và hướng dẫn demo. Cần Word/PDF/ảnh gốc nếu muốn giữ bố cục, các tham chiếu ảnh trong Markdown chưa đủ.
5. Nhóm/GVHD review nội dung đính chính và thủ tục hồ sơ đã nộp. Cam kết phải phù hợp nội dung đã kiểm tra; không tự ký hoặc gửi thay người có trách nhiệm. Theo dõi phiên bản cuối, nơi nộp và xác nhận nhận hồ sơ.

## 10. Phát triển sau hạn nộp — chỉ khi quy trình cho phép bổ sung

Không coi nghiên cứu sau 09/09 mặc nhiên được đưa vào hồ sơ đã nộp. Thông báo có mốc trình bày 23/09; cần Khoa xác nhận tài liệu nào được cập nhật trước buổi đó.

Giai đoạn tiếp theo đề xuất 1–2 tuần: mở rộng sang ít nhất ba người, hai phiên quay tách biệt và hai điều kiện camera/ánh sáng, có đủ tình huống bình thường; lập số clip cụ thể theo nguồn lực, giữ tách theo phiên/người. Đây là mục tiêu thu thập, không tự coi cỡ mẫu này đủ cho kết luận tổng quát.

Chỉ train khi lỗi model được review: ảnh âm tính thật (Casio/hộp bút/hoa văn chữ nhật), phone nhỏ/xa/che, nhãn đủ và đúng. Kiểm tra quyền sử dụng, trùng lặp, nguồn gốc; chuẩn bị dataset và notebook Colab. Giữ một tập hiệu chỉnh và test độc lập trước train. Lưu seed, môi trường, args, manifest, CSV và checksum checkpoint nhập về. So với checkpoint cũ cùng dữ liệu, báo cả FP/FN và tốc độ; không mặc định model lớn hơn hoặc train lâu hơn là tốt hơn.

Nếu model thấy phone nhưng rule bỏ: sửa logic trước; nếu confidence sai ngưỡng: hiệu chỉnh trên tập riêng; nếu keypoint/hành vi sai: không train detector phone để sửa. Đánh giá lại nhiều người/tracking là giai đoạn mở rộng riêng.

## 11. Rủi ro và cách giảm phạm vi

| Rủi ro | Mức | Cách xử lý |
|---|---|---|
| Hồ sơ cũ đã gửi, chưa biết cách thay/đính chính | Cao | Nhóm liên hệ GVHD/Khoa ngay; trợ lý chuẩn bị bản sửa riêng và bảng đối chiếu |
| MediaPipe không tích hợp kịp hoặc không đúng phạm vi đăng ký | Cao | Kiểm tra khả thi sớm, không fallback giả; báo mức thực hiện và chốt với GVHD |
| Video/nhãn đến muộn | Cao | Chuẩn bị công cụ trước; không dùng ảnh lặp thay thực nghiệm thực tế; ghi phần video thiếu nếu chưa làm được |
| Sửa logic làm tăng FP hoặc đổi ý nghĩa benchmark | Cao | Lưu baseline; một thay đổi mỗi so sánh; tách phép đo hệ thống khỏi ablation |
| Xem test rồi tối ưu và báo test là độc lập | Cao | Theo dõi vai trò clip; thêm phiên mới hoặc ghi rõ kết quả là hiệu chỉnh |
| Không đủ thời gian bốn cấu hình / kiểm tra dài hạn | Vừa | Ưu tiên đo đúng cấu hình chính và một baseline, ghi rõ phần chưa thực hiện; không bỏ bước sửa báo cáo |
| Train không kịp hoặc model mới kém hơn | Vừa | Train ngoài đường bắt buộc trước 09/09; giữ Colab hiện tại làm baseline |

Việc bắt đầu ngay sau khi triển khai kế hoạch: lưu baseline, chuẩn bị bản sửa có bảng bằng chứng, kiểm tra khả thi MediaPipe và xây công cụ thời gian/đối chứng. Các quyết định hồ sơ do nhóm/GVHD xử lý song song; không cần chờ video để làm các việc này.
