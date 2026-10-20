# ExamGuard — Hệ Thống Hỗ Trợ Giám Sát Phát Hiện Gian Lận Thi Cử

> **Đề tài NCKH 2025:** Nghiên cứu ứng dụng thuật toán YOLO và framework MediaPipe trong hệ thống giám sát phát hiện gian lận thi cử  
> **Đơn vị:** Khoa Công nghệ thông tin, Trường Đại học Tài nguyên và Môi trường Hà Nội (HUNRE)

---

## 📌 Giới thiệu dự án

**ExamGuard** là hệ thống AI hỗ trợ giám thị phát hiện các hành vi gian lận và vật thể nghi vấn trong phòng thi theo thời gian thực. Hệ thống kết hợp:
- **YOLOv8s-WorldV2 & YOLO Custom:** Phát hiện vật thể cấm (điện thoại, tài liệu, vật thể mở).
- **MediaPipe Pose & Hand Landmark:** Phân tích tư thế đầu (quay đầu, cúi gục), cử chỉ tay (tay gần tai, tay dưới gầm bàn).
- **Temporal Fusion Engine:** Kết hợp các tín hiệu không gian và thời gian để tính toán điểm rủi ro, giảm thiểu báo động giả (false positive).
- **Web Dashboard & FastAPI:** Trực quan hóa luồng video kèm bounding box, cảnh báo WebSocket thời gian thực, lưu trữ snapshot vi phạm.

---

## 📁 Cấu trúc thư mục

```text
├── cheating-detection/               # Thư mục mã nguồn chính của ứng dụng
│   ├── src/                          # Backend FastAPI, detector, tracking, fusion engine
│   ├── dashboard/                    # Giao diện Web Dashboard (React + Vite + TailwindCSS)
│   ├── models/                       # Trọng số mô hình (YOLO, MediaPipe tasks)
│   ├── video/                        # Các video kịch bản mẫu phục vụ kiểm thử
│   ├── scripts/                      # Script khởi chạy và chuẩn bị dữ liệu (start_demo.ps1, ...)
│   ├── docs/                         # Báo cáo kỹ thuật chi tiết & hướng dẫn Colab
│   ├── tests/                        # Unit test và integration test
│   └── requirements.txt              # Danh sách thư viện Python cần thiết
│
├── CAU_HOI_PHAN_BIEN_EXAMGUARD.md     # Bộ câu hỏi và trả lời phản biện hội đồng NCKH
├── ExamGuard Science Presentation.pptx # Slide thuyết trình báo cáo đề tài
├── Kich_ban_doc_ExamGuard.md          # Kịch bản thuyết trình chi tiết
├── Kich_ban_doc_ExamGuard_cap_truong.md# Kịch bản thuyết trình cấp trường
├── Kich_ban_thuyet_trinh_ExamGuard.md # Hướng dẫn thuyết minh đề tài
├── TONG_QUAN_HE_THONG.md              # Báo cáo tổng quan kiến trúc kỹ thuật hệ thống
└── outputs/                          # Báo cáo tóm tắt đề tài
```

---

## 🚀 Hướng dẫn chạy thử nghiệm nhanh (Quickstart)

### 1. Khởi chạy Backend (FastAPI)

Mở PowerShell tại thư mục `cheating-detection/`:

```powershell
# Chạy demo với video mẫu
.\scripts\start_demo.ps1 -Video .\video\01_binh_thuong.mp4.mp4

# Hoặc chạy trực tiếp với Webcam
.\scripts\start_demo.ps1
```

### 2. Khởi chạy Dashboard (Frontend)

Mở một cửa sổ Terminal mới:

```powershell
cd cheating-detection/dashboard
npm install
npm run dev
```

Truy cập trình duyệt tại địa chỉ: `http://localhost:5173`

---

## 📜 Tài liệu báo cáo & Thuyết trình

- [Tổng quan hệ thống kỹ thuật](TONG_QUAN_HE_THONG.md)
- [Bộ câu hỏi phản biện hội đồng](CAU_HOI_PHAN_BIEN_EXAMGUARD.md)
- [Kịch bản thuyết minh](Kich_ban_thuyet_trinh_ExamGuard.md)
- [Hướng dẫn chi tiết trong thư mục code](cheating-detection/README.md)
