# Phone v3 — lượt huấn luyện dữ liệu công khai

Theo yêu cầu tự tìm dữ liệu và train ngày 2026-09-05.

- Nguồn: https://huggingface.co/datasets/ridgerun-ai/citw-v0.1
- Revision: `f31df211860010059745ba29de06d06f16055c6e`.
- Dataset card ghi giấy phép CC-BY-NC-2.0; sử dụng cho nghiên cứu phi thương mại. README nguồn được lưu trong thư mục provenance.
- CITW được lọc từ COCO 2017, chỉ có nhãn điện thoại. Chọn ngẫu nhiên 1.600 ảnh train với seed 42 và giữ nguyên 214 ảnh validation nguồn trước lọc trùng. Class 0 = phone.
- Kiểm tra giải mã ảnh, chuyển bbox pixel sang YOLO có cắt biên, loại trùng ID/SHA256 và audit cấu trúc. Đã xem mẫu 6 ảnh validation có vẽ bbox. Chưa chứng nhận toàn bộ nhãn hoặc ảnh gần trùng.
- Không trộn nhãn ProductRecog không rõ nghĩa trong dữ liệu cũ vào lượt này.
- YOLOv8n pretrained, CPU, 640 px, batch 8, tối đa 40 epoch, patience 10. Kết quả riêng tại `models/phone_v3`.
- Sau train tự validate checkpoint tốt nhất; so sánh v2/v3 trên cùng ảnh ở confidence 0,30 và IoU 0,50, chỉ tính class phone. Script so sánh có matching một-một để tránh đếm trùng true positive.
- Tệp theo dõi: `artifacts/phone-v3-prepare.log`, `artifacts/phone-v3-train.log`, `artifacts/phone-v3-pipeline.json`; kết quả: `phone-v3-validation-summary.json`, `phone-v3-comparison.json`.

Giới hạn: bộ validation chỉ gồm ảnh có điện thoại, chưa đo báo động nhầm trên cảnh không có điện thoại; không phải video phòng thi. Pretrained YOLO đã dùng COCO nên đây không phải bộ dữ liệu hoàn toàn mới đối với quá trình pretraining. Không tự kích hoạt checkpoint trong dashboard chỉ dựa trên việc train hoàn tất.
