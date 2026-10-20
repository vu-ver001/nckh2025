# Danh mục minh chứng kết quả nghiên cứu

Ngày lập: 08/09/2026  
Mã MC chỉ là mã tổ chức nội bộ cho bộ rà soát này; chưa phải mã do Trường cấp.

| Mã | Nội dung chứng minh | Tệp và vị trí kiểm tra | Trạng thái và giới hạn |
|---|---|---|---|
| MC01 | Nguồn dữ liệu và phân chia | `dataset/phone_detection_v3/provenance/manifest.json`; `dataset/phone_detection_v3/provenance/SOURCE_README.md`; `artifacts/phone-v3-data-audit.json`, trường `splits` | Đọc được; 1.600 train, 214 validation, 2.177/262 box; có source/revision/checksum. Chưa chứng minh toàn bộ tập train Colab giống byte với bản cục bộ. |
| MC02 | Checkpoint Colab và cấu hình huấn luyện | `models/phone_v3_colab/weights/best.pt`; `models/phone_v3_colab/args.yaml`; `models/phone_v3_colab/results.csv`; `artifacts/phone-v3-colab-import.json` | Đọc/nạp được; class `phone`; SHA256 checkpoint khớp biên nhận. GPU Colab chưa xác minh. |
| MC03 | So sánh checkpoint trên validation | `artifacts/phone-colab-comparison.json`; `artifacts/research/phone-comparison.json`; `artifacts/research/RESULTS.md`; `artifacts/research/phone-benchmark.png` | JSON/PNG đọc được. Colab TP124/FP78/FN138, P61,39%, R47,33%, F1 53,45%; v2 TP41/FP137/FN221, P23,03%, R15,65%, F1 18,64%. Validation đã dùng chọn model. |
| MC04 | Phân tích lỗi theo kích thước | `artifacts/research/error-analysis/summary.json`; `artifacts/research/error-analysis/ASSISTANT_REVIEW.md` | Có đếm theo ba nhóm diện tích và phiếu review. Review của trợ lý không thay xác nhận nhãn của nhóm. |
| MC05 | Đối chứng World/phone/combined và sửa logic ghép box | `artifacts/research/detector-variants-validation-fixed.json`; bản trước sửa `detector-variants-validation.json` | Sau sửa: World 112/69/150; phone 124/73/138; combined 124/73/138. Chưa chứng minh World cải thiện phone; pose và phủ quyết vật được phép tắt trong phép tách thành phần. |
| MC06 | MediaPipe Pose + Hands thật | `artifacts/mediapipe-check/summary.json`; `artifacts/mediapipe-check/pose-hands-overlay.jpg`; `models/mediapipe/provenance.json` | Có 33 pose points và hai bộ 21 hand points trên ảnh kỹ thuật; ảnh nguồn từ validation, không phải video phòng thi. |
| MC07 | Luồng tích hợp model thật | `artifacts/phone-colab-check-1788700181192987400/summary.json`; thư mục `snapshots` và `logs` cùng thư mục | `result=passed`; video 24 frame, cảnh báo `PHONE_DETECTED`, snapshot HTTP 200, video/snapshot giải mã được, dừng phiên thành công. Đây là fixture lặp ảnh validation. |
| MC08 | Kiểm thử phần mềm và ổn định thành phần | `artifacts/improvement-tests-final.log`; `artifacts/stability-30min-mediapipe.json` | 57/57 test đạt; 1.800,259 giây, 6.460 frame, 269 vòng lặp không lỗi. Không phải thử camera vật lý, WebSocket cả buổi hoặc độ chính xác độc lập. |
| MC09 | Ứng viên dữ liệu bổ sung | `dataset/phone_negative_candidates/manifest.json`; `artifacts/research/negative-diagnosis/summary.json`; `.../ASSISTANT_REVIEW.md` | 280 ảnh có source/license/checksum; model kích hoạt 90 box trên 75 ảnh. Chưa phải nhãn âm tính, chưa đưa vào train. |
| MC10 | Video độc lập của nhóm | `demo/recordings/manifest.json` | Chưa đủ: manifest có sáu kịch bản nhưng `events` đều `null`; không tìm thấy file video tương ứng trong workspace ngày 08/09. |

## Bộ minh chứng tối thiểu nên gửi xin xác nhận

Đề xuất dùng MC01–MC03, MC05–MC08 cho phần kết quả kỹ thuật; MC04 làm phân tích lỗi phụ; MC09 chỉ dùng khi nhóm đã review và được phép đưa vào hồ sơ. MC10 chỉ thêm sau khi video được gán nhãn và chạy đánh giá. Không mặc định gửi toàn bộ mã nguồn, toàn bộ ảnh hoặc các file train cũ.

## Các số liệu phải đi cùng điều kiện

Mọi bảng detector phải ghi checkpoint, tập 214 ảnh validation, confidence 0,30, NMS IoU 0,45, IoU ghép nhãn 0,50 và giới hạn “không phải test phòng thi độc lập”. Mọi bảng video phải ghi số clip đã gán nhãn, người review, mã phiên, checksum và thời gian đo.
