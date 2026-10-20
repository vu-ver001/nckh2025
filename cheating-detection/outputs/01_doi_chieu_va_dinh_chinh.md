# Đối chiếu và đính chính báo cáo ban đầu

Ngày lập: 08/09/2026  
Trạng thái: bản làm việc để rà soát với GVHD/Khoa; chưa phải báo cáo thay thế và chưa xác nhận nghiệm thu.

## Nguyên tắc

Báo cáo ban đầu do nhóm cung cấp được giữ nguyên. Bảng này không tự xác định bản nào là PDF đã nghiệm thu. Mỗi tuyên bố được phân loại theo bằng chứng hiện có trong workspace và phải giữ mốc thời gian của phép đo. Kết quả validation, video fixture và video nhóm quay (khi có) không được gộp thành một tập đánh giá.

## Bảng đối chiếu

| Mã | Tuyên bố hoặc nội dung trong báo cáo ban đầu | Bằng chứng hiện có | Quyết định nội dung |
|---|---|---|---|
| DC01 | Accuracy 91,2%; F1 hành vi 85,3% | Chưa có log, nhãn video/hành vi hoặc phép đo tương ứng trong workspace. | **RÚT khỏi kết quả đã đạt.** Chỉ ghi là số liệu chưa xác minh; không thay bằng một metric khác để hợp thức hóa. |
| DC02 | YOLOv8m, 100 epoch, khoảng 3,5 giờ, RTX 3060 | `models/phone_v3_colab/args.yaml` ghi YOLOv8n, 40 epoch, batch 16, imgsz 640, seed 42; loại GPU chưa xác minh. | **SỬA** mô tả lượt Colab theo args/checkpoint. Chỉ giữ RTX3060 nếu có log độc lập chứng minh đúng lượt. |
| DC03 | Khoảng 2.690 ảnh gốc và 8.990 ảnh sau augmentation | `artifacts/phone-v3-data-audit.json` và provenance ghi 1.600 ảnh train, 214 ảnh validation, 2.177/262 box; nguồn CITW/COCO. | **SỬA** theo manifest và audit. Không gọi dữ liệu công khai là dữ liệu phòng thi mô phỏng nếu chưa có căn cứ. |
| DC04 | MediaPipe đã được dùng trong phiên bản báo cáo ban đầu | Mã cũ là YOLO-Pose; MediaPipe Tasks Pose + Hands được tích hợp và kiểm tra ngày 06/09/2026. | **TÁCH MỐC THỜI GIAN.** Ghi MediaPipe là phần tích hợp bổ sung, không hồi tố vào nghiệm thu. |
| DC05 | Mô hình YOLO đạt khoảng 93,4% precision, 92,1% recall, 93,3% mAP | So sánh có kiểm tra trên 214 ảnh validation: phone_v3_colab TP124/FP78/FN138, P61,39%, R47,33%, F1 53,45% ở conf 0,30 và IoU ghép 0,50. | **RÚT số cũ** nếu không có run/log đúng. Giữ bảng mới với tên metric, tập dữ liệu và ngưỡng đầy đủ. |
| DC06 | Hệ thống tích hợp khoảng 52 FPS, độ trễ 19 ms, ổn định 90 phút | Có kiểm tra kỹ thuật 1.800,259 giây/6.460 frame trên video lặp; tốc độ khoảng 3,59 FPS trong lúc máy chạy tác vụ khác; chưa có benchmark 52 FPS/19 ms/90 phút độc lập. | **RÚT hoặc ghi chưa xác minh.** Không suy ra độ trễ từ FPS. Nếu đo lại, ghi máy, backend, phạm vi đo và nguồn video. |
| DC07 | Kiến trúc lai chứng minh hiệu quả hơn | Đối chứng sau sửa trên cùng 214 ảnh: World TP112/FP69/FN150; phone TP124/FP73/FN138; combined TP124/FP73/FN138 khi tắt phủ quyết. | **HẠN CHẾ KẾT LUẬN.** Có thể nói đã xây dựng và đối chứng; chưa nói World cải thiện detector phone. |
| DC08 | Hệ thống đã kiểm thử thực tế/phòng thi | Có kiểm thử API với ảnh validation lặp 24 frame và dashboard; chưa có video nhóm trong workspace, chưa có nhãn độc lập. | **SỬA** thành kiểm thử kỹ thuật; để trống kết quả phòng thi cho đến khi gán nhãn và chạy video. |
| DC09 | Chưa có công bố khoa học | Báo cáo ban đầu ghi chưa có công bố tại thời điểm nộp; workspace không có bài báo, DOI hoặc thư chấp nhận. | **GIỮ** với điều kiện nhóm/GVHD xác nhận có hay không có tài liệu ngoài workspace. |

## Kết quả có thể dùng sau khi xác nhận

- Checkpoint Colab được nạp đúng, SHA256 `e54b53aa88083d9e047227a7a6db4fc313c400ad81443d03bca50064cc8ed857`.
- So sánh v2 và Colab trên cùng 214 ảnh validation: các số trong DC05; đây là validation đã tham gia chọn checkpoint, không phải test độc lập phòng thi.
- Phân tích kích thước: recall dưới 0,25% diện tích ảnh là 22/91 = 24,18%; từ 1% trở lên là 63/97 = 64,95%.
- MediaPipe thật trả 33 pose landmarks và hai bộ 21 hand landmarks trên ảnh kiểm tra; đây là minh chứng tích hợp, không phải đánh giá nhận diện hành vi.
- Luồng model → video → cảnh báo → snapshot → dashboard đạt trong test kỹ thuật; cảnh báo là tín hiệu để người giám sát xem xét, không phải kết luận gian lận.

## Không được làm trong bản sửa

- Không lấy số mới để xác nhận ngược kết quả 91,2%, 85,3%, 52 FPS hoặc 19 ms.
- Không gộp 214 ảnh validation với sáu video nhóm thành một bộ test.
- Không gọi 75/280 ảnh COCO kích hoạt model là 75 false positive; các ảnh đó chưa được review đủ và chưa có nhãn âm tính được duyệt.
- Không ghi bản Word trong `deliverables` là báo cáo đã được GVHD/Khoa phê duyệt.
