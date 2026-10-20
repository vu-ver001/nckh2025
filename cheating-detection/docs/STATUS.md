# Trạng thái thực tế — cập nhật 08/09/2026

## Bổ sung ngày 08/09/2026

Đã triển khai bộ bảng rà soát trong thư mục `outputs/`: bảng đính chính, danh mục minh chứng, trạng thái đánh giá video và các câu hỏi cần GVHD/Khoa xác nhận. Chạy lại hai công cụ đánh giá video cho thấy 0/6 clip sẵn sàng, 0 lượt chạy; không tạo số liệu giả. Bản Word rà soát được sao chép nguyên vẹn vào `outputs/04_bao_cao_sua_de_GVHD_ra_soat.docx` với checksum trùng bản trong `deliverables/`. Chưa tìm thấy sáu video hoặc nhãn trong workspace.

Đã hoàn thiện bản BCTK sửa theo bố cục báo cáo gốc tại `outputs/BCTK_sua_theo_ban_goc_2026-09-08.md` và bản Word `outputs/BCTK_sua_theo_ban_goc_2026-09-08.docx`. Bản này có các chương mục tiêu/phạm vi/phương pháp, cơ sở lý thuyết, thiết kế hệ thống, thực nghiệm, kết luận và năm phụ lục; các số liệu thiếu nguồn được rút khỏi kết luận, còn sáu video độc lập vẫn ghi `chưa đo`. Word đã được kết xuất PDF và kiểm tra trực quan 19 trang; không thay thế báo cáo gốc hay biên bản nghiệm thu.

Đã bổ sung nguồn **Webcam trực tiếp** cho dashboard. Backend nhận camera 0, giữ nguyên pipeline YOLO-World + phone_v3_colab + MediaPipe, hiển thị nguồn đang dùng và trả lỗi nếu camera không mở được. Logic tay gần vùng tai hiện chuẩn hóa theo bề rộng vai, yêu cầu giữ khoảng 2 giây hoặc lặp 3 lần trong 20 giây; nhãn tai nghe từ YOLO-World chỉ giữ để quan sát, không tự tạo cảnh báo. Kiểm thử hồi quy hiện tại: 63/63 đạt; frontend build đạt. Chưa thay thế kiểm thử camera vật lý trên buổi thi thật.

## Hiện tại sau triển khai ngày 06/09/2026

Đã tích hợp MediaPipe Pose + Hands thật và checkpoint Colab, chuyển logic thời gian sang timestamp nguồn video, sửa ghép trùng box điện thoại. 57/57 kiểm thử đạt; frontend build đạt; model thật qua video → cảnh báo → snapshot → API đạt. Dashboard đã xác nhận hai model, video và cảnh báo, bắt đầu/dừng hoạt động.

Kiểm thử thành phần 30 phút hoàn tất: 6.460 frame, không lỗi, trước sửa ghép box cuối cùng; không phải thử camera/WebSocket cả buổi thi. Sau sửa đã kiểm thử đơn vị/tích hợp riêng.

Đối chứng 214 ảnh: World TP112/FP69/FN150; phone TP124/FP73/FN138; kết hợp trước sửa FP109, sau sửa FP73 với TP124. Không có bằng chứng World giúp phone tốt hơn; C sau sửa tương đương B khi tắt phủ quyết vật được phép. Không trộn bảng pipeline này với đánh giá checkpoint thô FP78.

Đã chuẩn bị 280 ảnh ứng viên từ COCO, 75 ảnh kích hoạt model cần review. Chưa tạo nhãn train hoặc train mới. Mọi train tiếp theo chỉ trên Google Colab.

Báo cáo sửa có nguồn đối chiếu: [Markdown](REPORT_REVISED_2026-09-06.md), [Word](../deliverables/Bao_cao_sua_de_GVHD_ra_soat_2026-09-06.docx). Chưa thay thế hồ sơ đã nộp. Kế hoạch thao tác sau quay: [NEXT_STEPS_2026-09-07.md](NEXT_STEPS_2026-09-07.md).

Còn thiếu sáu video độc lập và nhãn đã review, xác nhận GVHD/Khoa về hồ sơ đính chính, tên đăng ký và mẫu chính thức. Hạn người dùng xác nhận: 09/09/2026. Chưa hoàn thành thực nghiệm phòng thi hoặc toàn bộ hồ sơ dự giải.

## Nhật ký trước đợt triển khai (giữ để đối chiếu)

Đã lập kế hoạch chi tiết đến 09/09 tại `docs/IMPROVEMENT_PLAN_2026-09-09.md`: phân công, quyết định MediaPipe/hồ sơ, chuẩn hóa thời gian, đối chứng, video độc lập, kiểm thử và báo cáo; có nhánh mở rộng sau hạn nếu được phép. Đây là kế hoạch, chưa triển khai các thay đổi kỹ thuật hoặc chạy thêm thực nghiệm trong lượt lập kế hoạch.

**Xác nhận mới của người dùng:** bản báo cáo đã dùng để qua nghiệm thu Khoa, có số liệu/nội dung phóng đại hoặc tự tạo; hạn cấp Trường của nhóm là **09/09/2026**. Ưu tiên sửa theo minh chứng thật và trao đổi với GVHD về việc đính chính bản đã nghiệm thu; không tái sử dụng các kết quả thiếu bằng chứng trong hồ sơ dự giải. Chưa có biên bản xếp loại/danh sách đề cử để kiểm tra. Cập nhật này thay các ghi chú chưa biết hạn/tình trạng bản báo cáo bên dưới.

Đã nhận thông báo giải thưởng và báo cáo tổng kết Markdown của nhóm ngày 06/09. Báo cáo có tên nhóm/GVHD nhưng tên đề tài có hai biến thể; nội dung MediaPipe và một số kết quả chưa khớp bằng chứng mã/Colab hiện có. Thông báo ghi hạn hồ sơ 09/09/2026; chưa xác nhận nhóm thuộc đợt này hoặc đã nghiệm thu/đề cử. Chi tiết và phân công tiếp theo tại `docs/DOCUMENT_REVIEW_2026-09-06.md`. Người dùng tạm hoãn quay video đến thứ Hai 07/09. So sánh bốn cấu hình chưa được triển khai.

Đã soạn bản thảo kỹ thuật tại `docs/RESEARCH_DRAFT.md`, gồm phương pháp, thực nghiệm ảnh, phân tích lỗi và giới hạn. Tiêu đề là mô tả tạm; chưa thống nhất tên đăng ký/phạm vi với báo cáo được cung cấp, chưa có mẫu poster/cam kết hoặc video độc lập. Không coi bản thảo là hoàn thành đề tài.

Phân tích lỗi Colab đã hoàn tất trên kết quả 214 ảnh: phone dưới 0,25% diện tích ảnh đạt recall 22/91 = 24,18%; nhóm ≥1% đạt 63/97 = 64,95%. Đã xem 12 phiếu lỗi nhiều nhất và ghi quan sát tại `artifacts/research/error-analysis/ASSISTANT_REVIEW.md`. Review này do trợ lý thực hiện, chưa thay người kiểm tra nhãn; không sửa nhãn/test hoặc bắt đầu train mới.

Hồ sơ nghiên cứu đã bổ sung dữ liệu dự đoán từng ảnh, checksum/phiên bản môi trường, bootstrap ghép cặp và xuất bảng/biểu đồ tại `artifacts/research`. Quy trình và giới hạn trong `docs/RESEARCH_PROTOCOL.md`. Tổng kiểm thử mới nhất: 41 đạt. Các kết quả validation không phải test độc lập vì checkpoint Colab đã được chọn trên chính validation.

Demo đã chuyển sang `models/phone_v3_colab/weights/best.pt` sau kiểm thử model thật → video MJPEG → cảnh báo → snapshot thành công. Trình duyệt đã xác nhận model Colab đang nạp, video hiển thị, cảnh báo điện thoại, nút Dừng đưa phiên về chưa giám sát. Video kỹ thuật là ảnh validation được chọn rồi lặp, không phải video phòng thi. 35 kiểm thử đạt và frontend build thành công. Không chạy hoặc tự resume train CPU.

So sánh cùng 214 ảnh/262 điện thoại, confidence 0,30, IoU matching 0,50: v2 TP/FP/FN = 41/137/221, precision/recall = 23,03%/15,65%; Colab = 124/78/138, precision/recall = 61,39%/47,33%. Bằng chứng `artifacts/phone-colab-comparison.json`; integration `artifacts/phone-colab-check-1788630321422196900/summary.json`; kiểm thử `artifacts/demo-tests.log`.

Đã chuẩn bị manifest 6 video tại `demo/recordings/manifest.json`, công cụ `scripts/evaluate_demo_videos.py` và hướng dẫn `docs/DEMO_COLAB.md`. Hiện 6/6 video/nhãn còn thiếu. Chưa quyết định train thêm, chưa đo báo động nhầm/giờ hoặc độ trễ trên video phòng thi. Scope demo đã chốt: một nguồn video, một người; người dùng quay video. Báo cáo được cung cấp có mục tiêu chất lượng rộng hơn demo; chưa xác nhận khả năng áp dụng hạn giải thưởng hoặc tiêu chí nghiệm thu chính thức cho phiên bản hiện tại.

## Lịch sử trước khi tích hợp Colab (không phải cấu hình hiện hành)

**Cập nhật 06/09 — người dùng huấn luyện trên Google Colab:** đã dừng train CPU theo yêu cầu; không được tự resume. ZIP `phone_v3_results.zip` có đủ 40 epoch (994,254 giây). Đã nhập riêng tại `models/phone_v3_colab`, giữ nguyên bản CPU tại `models/phone_v3`. SHA256 best Colab: `e54b53aa88083d9e047227a7a6db4fc313c400ad81443d03bca50064cc8ed857`. Nạp và inference ảnh trống thành công, class 0 = phone. Metrics lưu trong checkpoint tốt nhất (epoch 39): precision 59,457%, recall 51,497%, mAP50 50,806%, mAP50–95 30,615%; đây là kết quả validation Colab, chưa phải đo chất lượng phòng thi. Cấu hình dashboard chưa chuyển sang bản Colab. Báo cáo nhập: `artifacts/phone-v3-colab-import.json`.

**Sửa logic 06/09:** phân loại book/notebook bằng khớp nhãn chính xác; bộ đếm điện thoại riêng theo box với ghép một-một; không suy ra quay đầu từ mắt mất confidence, reset khi mất người/keypoint; timeout gửi WebSocket không làm dừng detection. 29 kiểm thử đạt. Ghép box chưa phải tracking định danh người và hành vi vẫn phân tích người đầu tiên trong frame.

**20:19 — khôi phục phone_v3:** dữ liệu đã audit đạt (1.600 train, 214 val). Tiến trình train dừng lúc 19:37 giữa epoch 12, không có traceback trong log; chưa xác định nguyên nhân. Đã sao lưu checkpoint và CSV epoch 11 tại `artifacts/phone-v3-interrupted-20260905-1937`, tiếp tục cùng lượt bằng `--resume` và xác nhận batch epoch 12 đang tăng. Log hiện hành: `artifacts/phone-v3-resume.log`, `artifacts/phone-v3-resume-error.log`. Chưa có kết quả cuối.

**Lượt mới phone_v3:** đang tải và chuẩn bị dữ liệu CITW công khai theo yêu cầu tự tìm và train. Mục tiêu 1.600 ảnh train, 214 ảnh validation trước lọc trùng; pipeline chờ audit thành công rồi tự train tối đa 40 epoch và so sánh với v2. Chi tiết nguồn, giấy phép và giới hạn trong `PHONE_V3.md`; trạng thái hiện hành xem `artifacts/phone-v3-prepare.log` và `artifacts/phone-v3-pipeline.json`. Đã tạo lịch kiểm tra tiếp khi hoàn tất. Chưa có kết quả v3.

**Cập nhật sau huấn luyện ngày 05/09/2026:** phone_v2 đã chạy đủ 80/80 epoch trên CPU và hoàn tất validation lúc 17:54:28. Tổng thời gian từ khi bắt đầu khoảng 5 giờ 58 phút. Không còn tiến trình train/evaluate. Checkpoint được kiểm thử tích hợp trong tiến trình riêng, chưa kích hoạt vào dashboard mặc định. Lượt kiểm tra khởi động trước đó được lưu riêng tại `models/phone_v2-startup-check`.

**Kết luận:** đã huấn luyện và kiểm thử model đúng mapping. Precision riêng phone đạt 70,44%, recall 73,17%, mAP50 80,37%, mAP50–95 65,65%. Chưa có tiêu chí nghiệm thu được thống nhất hoặc video phòng thi độc lập; cần review nhãn và đánh giá báo động nhầm trước khi kết luận chất lượng sử dụng thực tế.

## Đã thực hiện và xác minh

| Hạng mục | Kết quả | Bằng chứng |
|---|---|---|
| Khôi phục frontend | Bổ sung package.json, lockfile, index.html, Vite/proxy; build thành công | dashboard/dist; npm run build |
| Sửa nhận diện và scoring | Tai nghe không bị phân loại thành điện thoại; detection cũ không được tính thành nhiều lần xác nhận | tests/test_detection.py |
| Ổn định backend | Startup async đúng; start/stop có khóa; đóng camera khi lỗi/hết video; phục vụ snapshot | tests/test_api.py |
| Dashboard dùng số liệu thực | Bỏ FPS ngẫu nhiên, lịch sử/camera/thống kê giả; thêm start/stop và trạng thái lỗi; khóa cài đặt chưa áp dụng | Kiểm tra trực tiếp trình duyệt |
| Kiểm thử tự động | 18/18 đạt | artifacts/tests.txt |
| Kiểm thử với model thật | YOLO-World + YOLO-Pose, nhận cảnh báo LOOKING_AWAY qua WebSocket; MJPEG giải mã được 640×480; stop trả stopped, FPS 0 | artifacts/integration-smoke-current.json |
| Sửa dữ liệu | Tạo riêng v2: 977 train + 245 val, giữ đúng hai class, thống nhất bounding box | dataset/phone_detection_v2/provenance.json |
| Audit v2 | 0 ảnh lỗi nhãn theo kiểm tra cấu trúc; 0 cặp ảnh trùng byte giữa train/val | artifacts/dataset-audit-v2.json |
| Chuẩn bị train/evaluate | Có script chặn dataset/model sai mapping; train mới không ghi đè run cũ | train/train_phone.py; scripts/evaluate_phone.py |
| Train/evaluate phone_v2 | 80/80 epoch, validation đầy đủ 245 ảnh; chỉ số riêng phone trên 31 ảnh có phone / 41 đối tượng | artifacts/phone-validation2/summary.json |
| Kiểm thử checkpoint mới | Model thật và video 24 frame ghép ảnh validation; nhận PHONE_DETECTED, giải mã MJPEG, snapshot HTTP 200, stop về FPS 0 | artifacts/phone-v2-check-1788606103330677300/summary.json |

Lần kiểm thử YOLO-World trước khi phone_v2 hoàn tất đo 5 mẫu FPS: **6,8; 9,3; 9,3; 9,2; 9,4** trên CPU và video ghép lặp một ảnh validation. Các số này không phải tốc độ toàn hệ thống khi dùng phone_v2. Kiểm thử phone_v2 sau huấn luyện dùng một ảnh validation được chọn vì model nhận được phone, rồi ghép lặp thành video: chỉ chứng minh tích hợp kỹ thuật, không phải phép đo recall hoặc báo động nhầm độc lập.

## Phát hiện quan trọng về dữ liệu

YAML export gốc tại `C:/Users/T14s Gen 3/Downloads/Phone Detection.yolov8/data.yaml` định nghĩa:

- Class 0: `ProductRecog - v2 2024-11-05 7:03am`.
- Class 1: `phone`.

Script cũ khai báo `nc: 1`, đổi tên class 0 thành phone nhưng giữ nguyên các nhãn. Audit bản cũ phát hiện **116/977 ảnh train và 31/245 ảnh val có nhãn ngoài cấu hình**, đồng thời trộn box/polygon. Validation cũ chạy trên 214 ảnh còn lại trả precision 86,32%, recall 80,24%, mAP50 88,84%; **không được trình bày các số này là chất lượng điện thoại** do sai ý nghĩa class. Báo cáo legacy đã được đánh dấu không hợp lệ về ngữ nghĩa.

`phone_v1` được giữ nguyên để đối chiếu, đã loại khỏi cấu hình xác nhận mặc định. `phone_v2/weights/best.pt` đã train, validate và kiểm thử kỹ thuật. Checkpoint chưa được lưu thành `reviewed.pt` hoặc cấu hình vào dashboard đang dùng; chế độ mặc định vẫn là YOLO-World.

## Việc còn lại và phụ thuộc

| Ưu tiên | Việc | Người phụ trách / hạn |
|---|---|---|
| 1 | Xác nhận scope bản đầu, deadline, người nghiệm thu và ngưỡng chất lượng | Chưa được cung cấp |
| 2 | Review bằng mắt nhãn v2; kiểm tra ảnh gần trùng và rò rỉ theo người/video | ML/data reviewer chưa được phân công |
| 3 | Review checkpoint và chọn chế độ sử dụng thử | Train/evaluate đã hoàn tất; chưa có tiêu chí chấp nhận chất lượng |
| 4 | Cung cấp video phòng thi độc lập có nhãn thời gian/sự kiện, đo báo động nhầm và độ trễ | Chưa có bộ video/nhãn |
| 5 | Hiệu chuẩn điểm/ngưỡng, review và nghiệm thu | Sau bước 3–4 |

Không tính % hoàn thành tổng dự án hoặc số ngày chậm vì chưa có kế hoạch được phê duyệt. Không có cơ sở xác định blocker do ai hay ngày bàn giao cụ thể.

## Giới hạn kiểm tra

Chưa test camera vật lý, nhiều camera/nhiều thí sinh, tải dài hạn, cài mới toàn bộ môi trường hoặc triển khai công khai. Tư thế hiện lấy người đầu tiên model trả về. Điểm theo frame chưa được hiệu chuẩn với FPS. Lịch sử lâu dài và cài đặt backend vẫn chưa được triển khai trên dashboard.

Bản sao mã nguồn trước sửa: `artifacts/before-improvements-20260905.zip`. Ảnh và nhãn dataset cũ, weights cũ không bị ghi đè; cache validation được công cụ dựng lại. Logs/snapshots từ smoke test nằm riêng trong artifacts.
