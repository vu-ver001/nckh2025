# BỘ MINH CHỨNG KẾT QUẢ NGHIÊN CỨU

**Mã dự Giải:** HUNRE.NH.2026.11.30  
**Tên đề tài:** Nghiên cứu ứng dụng thuật toán YOLO và MediaPipe trong hệ thống giám sát phát hiện gian lận thi cử  
**Khoa:** Công Nghệ Thông Tin  
**Sinh viên đại diện nhóm:** Vương Anh Vũ  
**Các thành viên:** Nguyễn Ngọc Anh; Vũ Duy Tiến; Nguyễn Thị Khánh Vân; Nguyễn Thị Kim Tuyến  
**Giảng viên hướng dẫn:** ThS. Cao Thị Thoa  
**Giải:** Giải thưởng Sinh viên nghiên cứu khoa học cấp Trường năm học 2025–2026  
**Ngày lập danh mục:** 08/09/2026  
**Phạm vi của danh mục:** Các kết quả và sản phẩm kỹ thuật đã có trong workspace; chưa thay thế báo cáo đã nộp hoặc biên bản nghiệm thu.

## 1. Cách sử dụng danh mục

Tệp này là danh mục để khai trên Google Form và để nhóm, GVHD, Khoa đối chiếu. Tệp hướng dẫn được dùng làm tiêu chí lập danh mục tại `C:\Users\T14s Gen 3\Downloads\files (1)\02_Huong_dan_Bo_Minh_chung_2026.md`; nội dung hướng dẫn không phải là minh chứng của đề tài.

Mỗi mã MC chỉ đại diện cho một nội dung cần kiểm tra. Mã chính thức đã được cập nhật là `HUNRE.NH.2026.11.30`; giữ nguyên mã này khi khai trên biểu mẫu. Các tệp nguồn được giữ nguyên tên và vị trí trong workspace để bảo toàn provenance; chưa tự đổi tên hoặc đóng gói chúng.

Tên tệp đề xuất theo hướng dẫn:

`HUNRE.NH.2026.11.30_MCxx_Ten-minh-chung`

## 2. Bộ minh chứng nên nộp cùng hồ sơ

| Mã | Tên minh chứng và tên tệp đề xuất | Kết quả/nội dung được chứng minh | Tệp hoặc đường dẫn kiểm tra | Trạng thái nộp | Giới hạn cần ghi kèm |
|---|---|---|---|---|---|
| MC01 | Nguồn dữ liệu và kiểm toán tập dữ liệu  (`HUNRE.NH.2026.11.30_MC01_Nguon-du-lieu-va-kiem-toan`) | 1.600 ảnh train, 214 ảnh validation; 2.177 và 262 bounding box; không phát hiện trùng ảnh giữa hai split trong lần kiểm toán | `artifacts/phone-v3-data-audit.json`; `dataset/phone_detection_v3/provenance/manifest.json`; `dataset/phone_detection_v3/provenance/SOURCE_README.md` | Nên nộp | Chưa xác nhận toàn bộ tập Colab giống byte với bản cục bộ; cần xác nhận license/quyền dùng ảnh |
| MC02 | Checkpoint Colab và provenance (`HUNRE.NH.2026.11.30_MC02_Checkpoint-Colab-va-provenance`) | Model một lớp `phone`, checkpoint nạp được, SHA-256 và cấu hình huấn luyện có thể kiểm tra | `models/phone_v3_colab/weights/best.pt`; `models/phone_v3_colab/args.yaml`; `models/phone_v3_colab/results.csv`; `artifacts/phone-v3-colab-import.json` | Nên nộp khi biểu mẫu cho phép tệp lớn hoặc cung cấp đường dẫn kiểm tra | Checkpoint import ghi nhận metrics validation P 59,457%, R 51,497%, mAP@0.5 50,806%, mAP@0.5:0.95 30,615%; chưa phải test độc lập; GPU Colab cần nhóm xác nhận |
| MC03 | So sánh `phone_v2` và `phone_v3_colab` trên cùng validation (`HUNRE.NH.2026.11.30_MC03_So-sanh-checkpoint-validation`) | Với 214 ảnh, confidence 0,30, IoU ghép 0,50: v2 = TP/FP/FN 41/137/221, P/R/F1 23,03%/15,65%/18,64%; Colab = 124/78/138, 61,39%/47,33%/53,45% | `artifacts/phone-colab-comparison.json`; `artifacts/research/phone-comparison.json`; `artifacts/research/RESULTS.md` | Nên nộp | Đây là validation có ảnh điện thoại, không phải test độc lập hoặc độ chính xác cảnh báo trong phòng thi |
| MC04 | Phân tích lỗi theo kích thước (`HUNRE.NH.2026.11.30_MC04_Phan-tich-loi-theo-kich-thuoc`) | Recall của nhóm điện thoại <0,25% diện tích ảnh là 24,18%; nhóm 0,25–1% là 52,70%; nhóm ≥1% là 64,95% | `artifacts/research/error-analysis/summary.json`; `artifacts/research/error-analysis/ASSISTANT_REVIEW.md` | Minh chứng phụ; nộp khi Research Brief dùng nhận định này | Phiếu review là phân tích hỗ trợ, chưa thay cho xác nhận nhãn của nhóm |
| MC05 | Đối chứng detector và logic ghép box (`HUNRE.NH.2026.11.30_MC05_Doi-chung-detector`) | Fixed comparison: YOLO-World 112/69/150; `phone_v3_colab` 124/73/138; `combined` 124/73/138 theo TP/FP/FN | `artifacts/research/detector-variants-validation-fixed.json`; mã phiên bản được ghi trong `inputs_sha256` của JSON | Nên nộp nếu hồ sơ trình bày so sánh phương án | Chưa chứng minh YOLO-World cải thiện detector điện thoại; đây không phải đánh giá hành vi |
| MC06 | MediaPipe Pose + Hands (`HUNRE.NH.2026.11.30_MC06_MediaPipe-Pose-Hands`) | Backend MediaPipe Pose + Hands nạp thành công; tạo 33 landmark pose và hai bộ 21 landmark tay trên ảnh kỹ thuật | `artifacts/mediapipe-check/summary.json`; `artifacts/mediapipe-check/pose-hands-overlay.jpg`; `models/mediapipe/provenance.json` | Nên nộp ảnh overlay và summary | Ảnh kiểm tra lấy từ validation; chưa có nhãn hành vi và chưa có Precision/Recall/F1/FP Rate cho hành vi |
| MC07 | Luồng tích hợp model thật (`HUNRE.NH.2026.11.30_MC07_Luong-tich-hop-model-dashboard`) | Xử lý 24 frame 640×480; phát `PHONE_DETECTED`; snapshot HTTP 200; phiên dừng với `error=null` | `artifacts/phone-colab-check-1788700181192987400/summary.json`; thư mục `snapshots/` và `logs/` cùng phiên | Nên nộp nếu cần chứng minh sản phẩm hệ thống | Video là fixture lặp ảnh validation; không phải video phòng thi độc lập |
| MC08 | Kiểm thử phần mềm và ổn định thành phần (`HUNRE.NH.2026.11.30_MC08_Kiem-thu-va-on-dinh`) | 57/57 kiểm thử đạt; thử nghiệm thành phần 1.800,259 giây, 6.460 frame, 269 vòng lặp, không ghi lỗi runtime | `artifacts/improvement-tests-final.log`; `artifacts/stability-30min-mediapipe.json` | Nên nộp bản log/summary trích xuất | Không thay thế benchmark camera vật lý, WebSocket cả buổi hoặc đánh giá chất lượng thực địa |
| MC11 | Hình minh họa kết quả huấn luyện và đánh giá (`HUNRE.NH.2026.11.30_MC11_Hinh-huan-luyen-va-confusion-matrix`) | Đường cong huấn luyện, Precision/Recall/PR/F1 và confusion matrix do run Colab lưu | `models/phone_v3_colab/results.png`; `models/phone_v3_colab/BoxP_curve.png`; `models/phone_v3_colab/BoxR_curve.png`; `models/phone_v3_colab/BoxPR_curve.png`; `models/phone_v3_colab/BoxF1_curve.png`; `models/phone_v3_colab/confusion_matrix.png`; `models/phone_v3_colab/confusion_matrix_normalized.png` | Nộp khi Research Brief/Poster sử dụng các hình này | Các hình là đầu ra validation của run Colab; phải ghi rõ tập `val`, không gọi là test độc lập và không suy ra Accuracy tổng thể |
| MC10 | Sáu video độc lập và đánh giá luồng cảnh báo (`HUNRE.NH.2026.11.30_MC10_Video-doc-lap-va-danh-gia-luong-canh-bao`) | Sáu video một người, một camera; nhãn sơ bộ điện thoại; 4/4 episode điện thoại được phát hiện; 6 cảnh báo `PHONE_DETECTED` ngoài khoảng nhãn; tốc độ xử lý 9,65–10,95 FPS trên máy kiểm thử | `video/01_binh_thuong.mp4.mp4` đến `video/06_dien_thoai_kho.mp4.mp4`; `artifacts/video-intake/manifest-eval.json`; `artifacts/video-intake/evaluation-final.json`; `artifacts/video-intake/evaluation-summary.md` | Nên nộp sau khi nhóm xác nhận người review và quyền sử dụng video | Đây là kiểm thử một người, một nguồn video; nhãn hành vi chưa đầy đủ; không gọi 4/4 là độ chính xác 100% |

## Vị trí chèn hình để hoàn thiện hồ sơ

Các khung dưới đây cố ý để trống. Khi hoàn thiện Research Brief, Poster hoặc BCTK, thay nguyên khung bằng ảnh tương ứng và giữ nguyên mã minh chứng, nguồn và chú thích. Không chèn ảnh nếu chưa kiểm tra quyền sử dụng hoặc ảnh còn thông tin nhận diện không cần thiết.

### MC01 — Ảnh đại diện dữ liệu và nhãn

> **[CHÈN HÌNH MC01-01 TẠI ĐÂY]**  
> Gợi ý tệp: `artifacts/phone-v3-label-preview.jpg`  
> Chú thích đề xuất: *Một ảnh đại diện của tập validation với bounding box điện thoại; ảnh chỉ minh họa dữ liệu, không phải kết quả đo.*

### MC04 — Ảnh minh họa lỗi theo kích thước

> **[CHÈN HÌNH MC04-01 TẠI ĐÂY]**  
> Gợi ý tệp: `artifacts/research/error-analysis/review-01.png` hoặc một phiếu review đã được nhóm xác nhận  
> Chú thích đề xuất: *Ví dụ trường hợp bỏ sót hoặc định vị chưa khớp; không dùng ảnh này để suy ra tỷ lệ lỗi của toàn bộ tập.*

### MC06 — Overlay Pose + Hands

> **[CHÈN HÌNH MC06-01 TẠI ĐÂY]**  
> Gợi ý tệp: `artifacts/mediapipe-check/pose-hands-overlay.jpg`  
> Chú thích đề xuất: *Kết quả nạp MediaPipe Pose + Hands trên ảnh kiểm tra kỹ thuật; 33 landmark pose và hai bộ 21 landmark tay được tạo ra.*

### MC07 — Ảnh snapshot cảnh báo và dashboard

> **[CHÈN HÌNH MC07-01 TẠI ĐÂY]**  
> Gợi ý tệp: `artifacts/phone-colab-check-1788700181192987400/snapshots/PHONE_DETECTED_1788700201485272900.jpg`  
> Chú thích đề xuất: *Snapshot được tạo khi pipeline phát event `PHONE_DETECTED`; kiểm thử fixture, không phải video phòng thi độc lập.*

### MC11 — Đường cong và confusion matrix

> **[CHÈN HÌNH MC11-01 TẠI ĐÂY]**  
> Gợi ý tệp: `models/phone_v3_colab/results.png` hoặc `models/phone_v3_colab/BoxPR_curve.png`  
> Chú thích đề xuất: *Đường cong kết quả huấn luyện/đánh giá của checkpoint `phone_v3_colab` trên split validation.*

> **[CHÈN HÌNH MC11-02 TẠI ĐÂY]**  
> Gợi ý tệp: `models/phone_v3_colab/confusion_matrix.png`  
> Chú thích đề xuất: *Confusion matrix của mô hình YOLOv8 trên validation; các ô và quy ước trục phải giữ nguyên khi đưa vào báo cáo.*

> **[CHÈN HÌNH MC11-03 TẠI ĐÂY — tùy chọn]**  
> Gợi ý tệp: `models/phone_v3_colab/confusion_matrix_normalized.png`  
> Chú thích đề xuất: *Confusion matrix chuẩn hóa; chỉ giữ hình này nếu Research Brief hoặc Poster cần trình bày tỷ lệ theo lớp.*

## 3. Minh chứng bổ sung, chưa nên dùng làm kết quả chính

| Mã | Nội dung | Nguồn | Trạng thái |
|---|---|---|---|
| MC09 | Ứng viên dữ liệu âm tính/vật dễ nhầm | `dataset/phone_negative_candidates/manifest.json`; `artifacts/research/negative-diagnosis/summary.json`; thư mục review cùng phiên | Chỉ dùng sau khi nhóm review, xác nhận quyền dùng và lập nhãn; hiện chưa đưa vào train |
| MC10 | Sáu video độc lập của nhóm, nhãn thời gian và kết quả chạy pipeline | `video/`; `artifacts/video-intake/manifest-eval.json`; `artifacts/video-intake/evaluation-final.json`; `artifacts/video-intake/evaluation-summary.md` | Đã có video và kết quả chạy; cần nhóm xác nhận người review, quyền sử dụng và chốt nhãn trước khi nộp chính thức |

MC09 vẫn là minh chứng bổ sung, chưa đưa vào train khi chưa review và xác nhận quyền dùng. MC10 đã có video và kết quả chạy pipeline; chỉ khai theo phạm vi một người, một camera, các mốc nhãn đã chốt và các giới hạn nêu trong bảng. Không dùng MC10 để tạo thêm thành tích hoặc suy ra chất lượng triển khai thực tế trong phòng thi.

## 4. Danh mục tối thiểu để nhập Google Form

Các cột phải khai đúng theo hướng dẫn: **Mã minh chứng – Tên minh chứng – Nội dung/kết quả được minh chứng – Tệp hoặc đường dẫn tương ứng**.

| Mã | Tên minh chứng | Nội dung/kết quả được minh chứng | Tệp hoặc đường dẫn tương ứng |
|---|---|---|---|
| MC01 | Nguồn dữ liệu và kiểm toán | Quy mô split, số box, manifest và kiểm tra trùng | `artifacts/phone-v3-data-audit.json` |
| MC02 | Checkpoint Colab và provenance | Checksum, class, args, metrics trong checkpoint | `artifacts/phone-v3-colab-import.json` + đường dẫn checkpoint theo yêu cầu |
| MC03 | So sánh checkpoint | Bảng TP/FP/FN và P/R/F1 trên 214 validation | `artifacts/phone-colab-comparison.json` |
| MC05 | Đối chứng detector | Kết quả World/phone/combined sau fixed matching | `artifacts/research/detector-variants-validation-fixed.json` |
| MC06 | MediaPipe Pose + Hands | Model landmark và overlay kiểm tra | `artifacts/mediapipe-check/summary.json` + overlay |
| MC07 | Luồng tích hợp | Event, snapshot, stop và trạng thái lỗi | `artifacts/phone-colab-check-1788700181192987400/summary.json` |
| MC08 | Kiểm thử và ổn định | Test software và stability component | log/JSON tương ứng |
| MC11 | Hình kết quả | Đường cong và confusion matrix khi dùng trong hồ sơ | thư mục `models/phone_v3_colab/` |
| MC10 | Video độc lập và đánh giá luồng | 4/4 episode điện thoại được cảnh báo theo nhãn sơ bộ; 6 cảnh báo điện thoại ngoài khoảng nhãn; 9,65–10,95 FPS | `artifacts/video-intake/evaluation-final.json` + thư mục `video/` |

Nếu biểu mẫu chỉ cho phép ít tệp, ưu tiên MC01, MC02, MC03, MC06, MC07 và MC08; thêm MC05 hoặc MC11 khi nội dung hồ sơ thực sự dùng các kết quả đó. Không tải toàn bộ mã nguồn, toàn bộ ảnh thô hoặc toàn bộ checkpoint nếu biểu mẫu không yêu cầu.

## 5. Kiểm tra tính toàn vẹn của một số tệp chính

Các hash dưới đây được tính bằng SHA-256 tại ngày lập danh mục. Nếu đóng gói lại, giữ tệp hash kèm gói và kiểm tra lại sau khi tải lên.

| Tệp | SHA-256 |
|---|---|
| `artifacts/phone-v3-data-audit.json` | `CC12705C853C506193B8D9004891C197999F26134D66A769BCBC1B399B99EAB5` |
| `artifacts/phone-v3-colab-import.json` | `4C09E424DC85B0A27D11D6023A03B24CD97549416D58CD8878ED496ACC3DD784` |
| `artifacts/phone-colab-comparison.json` | `9320E9F74687F628452F5B104187C0D74D4A59A6742C17C968AEEBB7B332B6C1` |
| `artifacts/research/detector-variants-validation-fixed.json` | `0A246CDD40B573A9DCEBC755E4E8AE0F97759FB5798D396E9FFD54A3C4961230` |
| `artifacts/mediapipe-check/summary.json` | `3C26331CF20988AFDBAA44ADCA86B8661FA285C1B4833A696E285971E2A847C4` |
| `artifacts/phone-colab-check-1788700181192987400/summary.json` | `FA4B2652A21D8EF2919A5C51AF4D81BFC82CB4BE5D67622EB6380AFBA374EFF8` |

## 6. Nội dung chưa được phép khai báo như kết quả đã đạt

Chưa có minh chứng hợp lệ trong workspace cho các tuyên bố sau: độ chính xác 91,2%; F1 hành vi 85,3%; bộ dữ liệu 2.690 ảnh gốc hoặc 8.990 ảnh sau augmentation; 52 FPS GPU; tập test độc lập; nhận diện riêng các lớp `earphone` và `document` trong checkpoint Colab hiện tại; triển khai nghiệm thu trong phòng thi.

Không điền các số liệu này vào Research Brief, Poster hoặc Google Form nếu chưa có tệp dữ liệu và quy trình đo có thể kiểm tra lại.

## 7. Dữ liệu cần bổ sung trước khi nộp

1. Đường dẫn Google Form, hạn nộp và yêu cầu định dạng tệp do Khoa hoặc Phòng KHCN&HTQT cung cấp; mã dự Giải đã ghi là `HUNRE.NH.2026.11.30`.
2. Xác nhận của nhóm/GVHD về tên đề tài, danh sách thành viên, tình trạng nghiệm thu, quyền sử dụng ảnh/dataset và việc được phép cung cấp checkpoint hoặc ảnh minh chứng.
3. Xác nhận người review, ngày review, quyền sử dụng hình ảnh/video và nhãn thời gian của MC10; nếu hồ sơ khai đánh giá hành vi thì cần thêm nhãn cho từng hành vi và file evaluator tương ứng.
4. Khai báo việc sử dụng AI trong quá trình rà soát/soạn thảo theo biểu mẫu liêm chính của Nhà trường nếu biểu mẫu yêu cầu; không coi nội dung do trợ lý tạo là dữ liệu thực nghiệm.

## 8. Tiền kiểm trước khi gửi

- Mở được từng tệp hoặc đường dẫn bằng tài khoản kiểm tra độc lập.
- Tên tệp dùng tiền tố `HUNRE.NH.2026.11.30` đúng quy ước và mã MC không trùng.
- Research Brief, Poster và BCTK dùng cùng checkpoint, split, ngưỡng và số liệu.
- Ảnh/video có người được kiểm tra quyền sử dụng và che thông tin nhận diện không cần thiết.
- GVHD/Khoa xác nhận các điểm còn thiếu trước khi khai báo chính thức.
