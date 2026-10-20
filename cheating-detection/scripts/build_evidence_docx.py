from pathlib import Path
import shutil

from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.shared import Inches, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


ROOT = Path(r"D:\HUNRE\NCKH2025\cheating-detection\cheating-detection")
REFERENCE = Path(r"C:\Users\T14s Gen 3\.codex\plugins\cache\openai-curated-remote\openai-templates\0.1.1\skills\artifact-template-legal-memorandum\assets\reference.docx")
OUTPUT = ROOT / "outputs" / "Bo_minh_chung_HUNRE_NH_2026_11_30.docx"


def clear_paragraph(paragraph):
    p = paragraph._element
    for child in list(p):
        if child.tag != qn("w:pPr"):
            p.remove(child)
    return paragraph


def remove_body_content(doc):
    body = doc._element.body
    sect_pr = body.sectPr
    for child in list(body):
        if child is not sect_pr:
            body.remove(child)


def set_cell_shading(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_cell_border(cell, **kwargs):
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    borders = tc_pr.first_child_found_in("w:tcBorders")
    if borders is None:
        borders = OxmlElement("w:tcBorders")
        tc_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        if edge in kwargs:
            edge_data = kwargs.get(edge)
            tag = "w:{}".format(edge)
            element = borders.find(qn(tag))
            if element is None:
                element = OxmlElement(tag)
                borders.append(element)
            for key in ["sz", "val", "color", "space"]:
                if key in edge_data:
                    element.set(qn("w:{}".format(key)), str(edge_data[key]))


def set_paragraph_border(paragraph, color="B7B7B7", size="8", fill=None):
    p_pr = paragraph._p.get_or_add_pPr()
    borders = p_pr.find(qn("w:pBdr"))
    if borders is None:
        borders = OxmlElement("w:pBdr")
        p_pr.append(borders)
    for edge in ("top", "left", "bottom", "right"):
        tag = qn("w:{}".format(edge))
        item = borders.find(tag)
        if item is None:
            item = OxmlElement("w:{}".format(edge))
            borders.append(item)
        item.set(qn("w:val"), "single")
        item.set(qn("w:sz"), size)
        item.set(qn("w:space"), "6")
        item.set(qn("w:color"), color)
    if fill:
        shd = p_pr.find(qn("w:shd"))
        if shd is None:
            shd = OxmlElement("w:shd")
            p_pr.append(shd)
        shd.set(qn("w:fill"), fill)


def set_run_font(run, size=12, bold=None, italic=None, underline=None, color=None):
    run.font.name = "Garamond"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "Garamond")
    run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold
    if italic is not None:
        run.italic = italic
    if underline is not None:
        run.underline = underline
    if color:
        run.font.color.rgb = RGBColor.from_string(color)


def add_text(paragraph, text, **style):
    run = paragraph.add_run(text)
    set_run_font(run, **style)
    return run


def format_para(paragraph, align=WD_ALIGN_PARAGRAPH.JUSTIFY, line=1.5, before=0, after=0, first=0, left=0):
    pf = paragraph.paragraph_format
    paragraph.alignment = align
    pf.line_spacing = line
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    if first:
        pf.first_line_indent = Inches(first)
    if left:
        pf.left_indent = Inches(left)


def add_para(doc, text="", align=WD_ALIGN_PARAGRAPH.JUSTIFY, line=1.5, before=0, after=0, first=0, left=0, size=12, bold=False, italic=False, underline=False, color=None):
    p = doc.add_paragraph()
    format_para(p, align, line, before, after, first, left)
    if text:
        add_text(p, text, size=size, bold=bold, italic=italic, underline=underline, color=color)
    return p


def add_label_para(doc, label, text, after=0, first=0, align=WD_ALIGN_PARAGRAPH.JUSTIFY):
    p = add_para(doc, align=align, line=1.5, after=after, first=first)
    add_text(p, label, bold=True)
    add_text(p, text)
    return p


def add_heading(doc, text):
    p = add_para(doc, align=WD_ALIGN_PARAGRAPH.CENTER, line=1.5, before=8, after=6)
    p.paragraph_format.keep_with_next = True
    add_text(p, text, bold=True, underline=True)
    return p


def add_bullet(doc, text, after=0, size=12):
    p = add_para(doc, align=WD_ALIGN_PARAGRAPH.JUSTIFY, line=1.35, after=after, left=0.25, first=-0.18, size=size)
    add_text(p, "• ", bold=True, size=size)
    add_text(p, text, size=size)
    return p


def add_numbered(doc, number, text, after=0, size=12):
    p = add_para(doc, align=WD_ALIGN_PARAGRAPH.JUSTIFY, line=1.35, after=after, left=0.28, first=-0.20, size=size)
    add_text(p, f"{number}. ", bold=True, size=size)
    add_text(p, text, size=size)
    return p


def add_code_line(doc, label, value, after=0):
    p = add_para(doc, align=WD_ALIGN_PARAGRAPH.JUSTIFY, line=1.25, after=after, left=0.12, first=-0.12)
    add_text(p, label, bold=True, size=11)
    add_text(p, value, size=11)
    return p


def add_evidence(doc, code, title, result, source, status, limitation):
    p = add_para(doc, align=WD_ALIGN_PARAGRAPH.LEFT, line=1.35, before=3, after=1, left=0.22, first=-0.22)
    p.paragraph_format.keep_with_next = True
    add_text(p, f"{code} — {title}", bold=True)
    add_para(doc, f"Minh chứng/kết quả: {result}", line=1.30, after=0, first=0.18)
    add_para(doc, f"Nguồn kiểm tra: {source}", align=WD_ALIGN_PARAGRAPH.LEFT, line=1.20, after=0, first=0.18)
    add_para(doc, f"Trạng thái: {status}. Giới hạn: {limitation}", line=1.30, after=3, first=0.18)


def add_placeholder(doc, code, source, caption):
    p = add_para(doc, align=WD_ALIGN_PARAGRAPH.CENTER, line=1.0, before=8, after=1)
    p.paragraph_format.left_indent = Inches(0.25)
    p.paragraph_format.right_indent = Inches(0.25)
    set_paragraph_border(p, fill="F3F3F3")
    add_text(p, f"[CHÈN HÌNH {code} TẠI ĐÂY]", bold=True, italic=True, size=12, color="555555")
    q = add_para(doc, align=WD_ALIGN_PARAGRAPH.CENTER, line=1.15, after=1)
    add_text(q, f"Gợi ý tệp: {source}", italic=True, size=10, color="555555")
    r = add_para(doc, align=WD_ALIGN_PARAGRAPH.JUSTIFY, line=1.25, after=5, first=0.18)
    add_text(r, "Chú thích đề xuất: ", bold=True, size=11)
    add_text(r, caption, italic=True, size=11)


def add_page_break(doc):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(0)
    p.add_run().add_break(WD_BREAK.PAGE)


def replace_header_designation(doc):
    for section in doc.sections:
        if section.header.paragraphs:
            p = section.header.paragraphs[0]
            clear_paragraph(p)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            add_text(p, "BỘ MINH CHỨNG • BẢN ĐỐI CHIẾU NỘI BỘ", size=9, bold=True, color="666666")


def set_normal_style(doc):
    style = doc.styles["Normal"]
    style.font.name = "Garamond"
    style._element.rPr.rFonts.set(qn("w:eastAsia"), "Garamond")
    style.font.size = Pt(12)


def build():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(REFERENCE, OUTPUT)
    doc = Document(OUTPUT)
    set_normal_style(doc)
    replace_header_designation(doc)
    remove_body_content(doc)

    # Title block follows the retained legal memorandum title system.
    add_para(doc, "", align=WD_ALIGN_PARAGRAPH.CENTER, line=1.0, after=2)
    title = add_para(doc, align=WD_ALIGN_PARAGRAPH.CENTER, line=1.0, after=10)
    add_text(title, "BỘ MINH CHỨNG", size=24, bold=True)
    subtitle = add_para(doc, align=WD_ALIGN_PARAGRAPH.CENTER, line=1.0, after=14)
    add_text(subtitle, "KẾT QUẢ NGHIÊN CỨU", size=13, bold=True, color="555555")

    add_label_para(doc, "To: ", "Khoa Công Nghệ Thông Tin / Phòng KHCN&HTQT")
    add_label_para(doc, "From: ", "Nhóm nghiên cứu — Vương Anh Vũ")
    add_label_para(doc, "Date: ", "08/09/2026")
    add_label_para(doc, "Re: ", "HUNRE.NH.2026.11.30 — Danh mục minh chứng để chuẩn bị hồ sơ Giải thưởng Sinh viên nghiên cứu khoa học cấp Trường năm học 2025–2026")

    add_heading(doc, "THÔNG TIN ĐỀ TÀI VÀ PHẠM VI")
    add_para(doc, "Danh mục này hệ thống hóa những tệp và kết quả kỹ thuật đã có trong workspace để nhóm, giảng viên hướng dẫn và đơn vị tiếp nhận đối chiếu trước khi khai hồ sơ. Tài liệu không thay thế báo cáo tổng kết đã nộp, quyết định/biên bản nghiệm thu hoặc yêu cầu chính thức của Khoa.", first=0.18)
    add_para(doc, "Thông tin dùng thống nhất trong bộ hồ sơ:", first=0.18, after=1)
    add_bullet(doc, "Mã dự Giải: HUNRE.NH.2026.11.30")
    add_bullet(doc, "Tên đề tài: Nghiên cứu ứng dụng thuật toán YOLO và MediaPipe trong hệ thống giám sát phát hiện gian lận thi cử")
    add_bullet(doc, "Khoa: Công Nghệ Thông Tin; giảng viên hướng dẫn: ThS. Cao Thị Thoa")
    add_bullet(doc, "Sinh viên đại diện: Vương Anh Vũ; thành viên: Nguyễn Ngọc Anh, Vũ Duy Tiến, Nguyễn Thị Khánh Vân, Nguyễn Thị Kim Tuyến")
    add_bullet(doc, "Phạm vi: các kết quả và sản phẩm kỹ thuật có thể mở/kiểm tra trong workspace; sáu video độc lập và nhãn hành vi hiện chưa có")
    add_para(doc, "Nguyên tắc sử dụng: giữ nguyên tên và vị trí tệp nguồn; chỉ khai số liệu có căn cứ; ghi rõ split validation, ngưỡng và giới hạn; không dùng các số liệu cũ chưa có minh chứng hợp lệ.", first=0.18, after=4)

    add_heading(doc, "DANH MỤC MINH CHỨNG VÀ CÁCH KIỂM TRA")
    add_para(doc, "Các mã dưới đây được thiết kế để nhập vào Google Form theo bốn cột: mã minh chứng, tên minh chứng, nội dung/kết quả và tệp hoặc đường dẫn kiểm tra.", first=0.18, after=3)
    add_evidence(doc, "MC01", "Nguồn dữ liệu và kiểm toán tập dữ liệu", "1.600 ảnh train, 214 ảnh validation; 2.177 và 262 bounding box; lần kiểm toán không phát hiện trùng ảnh giữa hai split.", "artifacts/phone-v3-data-audit.json; dataset/phone_detection_v3/provenance/manifest.json; dataset/phone_detection_v3/provenance/SOURCE_README.md", "Nên nộp", "chưa xác nhận toàn bộ tập Colab giống byte với bản cục bộ và cần bổ sung xác nhận license/quyền dùng ảnh.")
    add_evidence(doc, "MC02", "Checkpoint Colab và provenance", "Model một lớp phone nạp được; có SHA-256, args và kết quả validation. Metrics trong artifact import: P 59,457%, R 51,497%, mAP@0.5 50,806%, mAP@0.5:0.95 30,615%.", "models/phone_v3_colab/weights/best.pt; models/phone_v3_colab/args.yaml; models/phone_v3_colab/results.csv; artifacts/phone-v3-colab-import.json", "Nên nộp khi biểu mẫu cho phép tệp lớn hoặc đường dẫn kiểm tra", "đây là validation, chưa phải test độc lập; thông tin GPU Colab cần nhóm xác nhận.")
    add_evidence(doc, "MC03", "So sánh phone_v2 và phone_v3_colab trên cùng validation", "Trên 214 ảnh, confidence 0,30 và IoU ghép 0,50: v2 = TP/FP/FN 41/137/221, P/R/F1 23,03%/15,65%/18,64%; Colab = 124/78/138, P/R/F1 61,39%/47,33%/53,45%.", "artifacts/phone-colab-comparison.json; artifacts/research/phone-comparison.json; artifacts/research/RESULTS.md", "Nên nộp", "là validation có ảnh điện thoại, không phải test độc lập hoặc đánh giá cảnh báo trong phòng thi.")
    add_evidence(doc, "MC04", "Phân tích lỗi theo kích thước", "Recall của nhóm điện thoại <0,25% diện tích ảnh là 24,18%; nhóm 0,25–1% là 52,70%; nhóm ≥1% là 64,95%.", "artifacts/research/error-analysis/summary.json; artifacts/research/error-analysis/ASSISTANT_REVIEW.md", "Minh chứng phụ", "phiếu review là phân tích hỗ trợ và chưa thay cho xác nhận nhãn của nhóm.")

    add_page_break(doc)
    add_heading(doc, "DANH MỤC MINH CHỨNG (TIẾP)")
    add_evidence(doc, "MC05", "Đối chứng detector và logic ghép box", "Fixed comparison: YOLO-World 112/69/150; phone_v3_colab 124/73/138; combined 124/73/138 theo TP/FP/FN.", "artifacts/research/detector-variants-validation-fixed.json; phiên bản mã nằm trong inputs_sha256 của JSON", "Nên nộp nếu hồ sơ trình bày so sánh phương án", "chưa chứng minh YOLO-World cải thiện detector điện thoại và đây không phải đánh giá hành vi.")
    add_evidence(doc, "MC06", "MediaPipe Pose + Hands", "Backend MediaPipe Pose + Hands nạp thành công; tạo 33 landmark pose và hai bộ 21 landmark tay trên ảnh kỹ thuật.", "artifacts/mediapipe-check/summary.json; artifacts/mediapipe-check/pose-hands-overlay.jpg; models/mediapipe/provenance.json", "Nên nộp ảnh overlay và summary", "ảnh lấy từ validation; chưa có nhãn hành vi và chưa có Precision/Recall/F1/FP Rate cho hành vi.")
    add_evidence(doc, "MC07", "Luồng tích hợp model thật", "Xử lý 24 frame 640×480; phát event PHONE_DETECTED; snapshot HTTP 200; phiên dừng với error=null.", "artifacts/phone-colab-check-1788700181192987400/summary.json; thư mục snapshots/ và logs/ cùng phiên", "Nên nộp nếu cần chứng minh sản phẩm hệ thống", "video là fixture lặp ảnh validation, không phải video phòng thi độc lập.")
    add_evidence(doc, "MC08", "Kiểm thử phần mềm và ổn định thành phần", "57/57 kiểm thử đạt; thử nghiệm thành phần 1.800,259 giây, 6.460 frame, 269 vòng lặp, không ghi lỗi runtime.", "artifacts/improvement-tests-final.log; artifacts/stability-30min-mediapipe.json", "Nên nộp bản log/summary trích xuất", "không thay thế benchmark camera vật lý, WebSocket cả buổi hoặc đánh giá chất lượng thực địa.")
    add_evidence(doc, "MC11", "Hình minh họa kết quả huấn luyện và đánh giá", "Đường cong huấn luyện, Precision/Recall/PR/F1 và confusion matrix do run Colab lưu.", "models/phone_v3_colab/results.png; BoxP_curve.png; BoxR_curve.png; BoxPR_curve.png; BoxF1_curve.png; confusion_matrix.png; confusion_matrix_normalized.png", "Nộp khi Research Brief hoặc Poster dùng các hình này", "đầu ra validation của run Colab; phải ghi rõ split val và không suy ra Accuracy tổng thể.")
    add_evidence(doc, "MC10", "Sáu video độc lập và đánh giá luồng cảnh báo", "Sáu video một người, một camera; theo nhãn sơ bộ, 4/4 episode điện thoại được phát hiện; có 6 cảnh báo PHONE_DETECTED ngoài khoảng nhãn; tốc độ xử lý 9,65–10,95 FPS trên máy kiểm thử.", "video/01_binh_thuong.mp4.mp4 đến video/06_dien_thoai_kho.mp4.mp4; artifacts/video-intake/manifest-eval.json; artifacts/video-intake/evaluation-final.json; artifacts/video-intake/evaluation-summary.md", "Nên nộp sau khi nhóm xác nhận người review và quyền sử dụng video", "phạm vi chỉ một người, một nguồn video; nhãn hành vi chưa đầy đủ; không gọi 4/4 là độ chính xác 100%.")

    add_heading(doc, "VỊ TRÍ CHÈN HÌNH MINH HỌA")
    add_para(doc, "Các khung dưới đây là vị trí chờ ảnh. Khi hoàn thiện Research Brief, Poster hoặc BCTK, thay nguyên khung bằng ảnh tương ứng và giữ nguyên mã minh chứng, nguồn và chú thích. Không chèn ảnh khi chưa kiểm tra quyền sử dụng hoặc còn thông tin nhận diện không cần thiết.", first=0.18, after=4)
    add_placeholder(doc, "MC01-01", "artifacts/phone-v3-label-preview.jpg", "Một ảnh đại diện của tập validation với bounding box điện thoại; ảnh chỉ minh họa dữ liệu, không phải kết quả đo.")
    add_placeholder(doc, "MC04-01", "artifacts/research/error-analysis/review-01.png hoặc phiếu review đã được nhóm xác nhận", "Ví dụ trường hợp bỏ sót hoặc định vị chưa khớp; không dùng ảnh này để suy ra tỷ lệ lỗi của toàn bộ tập.")

    add_page_break(doc)
    add_heading(doc, "VỊ TRÍ CHÈN HÌNH (TIẾP)")
    add_placeholder(doc, "MC06-01", "artifacts/mediapipe-check/pose-hands-overlay.jpg", "Kết quả nạp MediaPipe Pose + Hands trên ảnh kiểm tra kỹ thuật; 33 landmark pose và hai bộ 21 landmark tay được tạo ra.")
    add_placeholder(doc, "MC07-01", "artifacts/phone-colab-check-1788700181192987400/snapshots/PHONE_DETECTED_1788700201485272900.jpg", "Snapshot được tạo khi pipeline phát event PHONE_DETECTED; kiểm thử fixture, không phải video phòng thi độc lập.")
    add_placeholder(doc, "MC11-01", "models/phone_v3_colab/results.png hoặc models/phone_v3_colab/BoxPR_curve.png", "Đường cong kết quả huấn luyện/đánh giá của checkpoint phone_v3_colab trên split validation.")
    add_placeholder(doc, "MC11-02", "models/phone_v3_colab/confusion_matrix.png", "Confusion matrix của mô hình YOLOv8 trên validation; giữ nguyên ô và quy ước trục khi đưa vào báo cáo.")
    add_placeholder(doc, "MC11-03 — tùy chọn", "models/phone_v3_colab/confusion_matrix_normalized.png", "Confusion matrix chuẩn hóa; chỉ giữ hình nếu Research Brief hoặc Poster cần trình bày tỷ lệ theo lớp.")

    add_page_break(doc)
    add_heading(doc, "MINH CHỨNG BỔ SUNG VÀ HỒ SƠ NHẬP FORM")
    add_label_para(doc, "MC09 — ", "Ứng viên dữ liệu âm tính/vật dễ nhầm. Nguồn: dataset/phone_negative_candidates/manifest.json; artifacts/research/negative-diagnosis/summary.json và thư mục review cùng phiên. Chỉ dùng sau khi nhóm review, xác nhận quyền dùng và lập nhãn; hiện chưa đưa vào train.", after=3, align=WD_ALIGN_PARAGRAPH.LEFT)
    add_label_para(doc, "MC10 — ", "Sáu video độc lập đã có trong thư mục video/. Nhãn sơ bộ: video 05 có một episode 9,25–25,50 giây; video 06 có ba episode 4,75–12,00, 24,75–40,50 và 44,50–46,60 giây. Kết quả pipeline: 4/4 episode được cảnh báo, 6 cảnh báo PHONE_DETECTED ngoài khoảng nhãn, tốc độ 9,65–10,95 FPS. Cần ghi người review, ngày review và quyền sử dụng video trước khi nộp.", after=4, align=WD_ALIGN_PARAGRAPH.LEFT)
    add_para(doc, "Nếu biểu mẫu chỉ cho phép ít tệp, ưu tiên MC01, MC02, MC03, MC06, MC07 và MC08; thêm MC05 hoặc MC11 khi nội dung hồ sơ thực sự dùng các kết quả đó. Không tải toàn bộ mã nguồn, toàn bộ ảnh thô hoặc toàn bộ checkpoint nếu biểu mẫu không yêu cầu.", first=0.18, after=4)
    add_para(doc, "Các hash SHA-256 chính để kiểm tra sau khi đóng gói:", first=0.18, after=2)
    hashes = [
        ("phone-v3-data-audit.json", "CC12705C853C506193B8D9004891C197999F26134D66A769BCBC1B399B99EAB5"),
        ("phone-v3-colab-import.json", "4C09E424DC85B0A27D11D6023A03B24CD97549416D58CD8878ED496ACC3DD784"),
        ("phone-colab-comparison.json", "9320E9F74687F628452F5B104187C0D74D4A59A6742C17C968AEEBB7B332B6C1"),
        ("detector-variants-validation-fixed.json", "0A246CDD40B573A9DCEBC755E4E8AE0F97759FB5798D396E9FFD54A3C4961230"),
        ("mediapipe-check/summary.json", "3C26331CF20988AFDBAA44ADCA86B8661FA285C1B4833A696E285971E2A847C4"),
        ("phone-colab-check-1788700181192987400/summary.json", "FA4B2652A21D8EF2919A5C51AF4D81BFC82CB4BE5D67622EB6380AFBA374EFF8"),
    ]
    for name, digest in hashes:
        add_code_line(doc, f"{name}: ", digest, after=0)

    add_heading(doc, "ĐIỂM CHƯA ĐƯỢC KHAI BÁO VÀ VIỆC CẦN BỔ SUNG")
    add_para(doc, "Chưa có minh chứng hợp lệ trong workspace cho các tuyên bố: độ chính xác 91,2%; F1 hành vi 85,3%; bộ dữ liệu 2.690 ảnh gốc hoặc 8.990 ảnh sau augmentation; 52 FPS GPU; tập test độc lập; nhận diện riêng earphone và document trong checkpoint Colab hiện tại; triển khai nghiệm thu trong phòng thi.", first=0.18, after=3)
    add_numbered(doc, 1, "Đường dẫn Google Form, hạn nộp và yêu cầu định dạng tệp do Khoa hoặc Phòng KHCN&HTQT cung cấp; mã dự Giải đã ghi là HUNRE.NH.2026.11.30.")
    add_numbered(doc, 2, "Xác nhận của nhóm/GVHD về tên đề tài, danh sách thành viên, tình trạng nghiệm thu, quyền sử dụng ảnh/dataset và việc được phép cung cấp checkpoint hoặc ảnh minh chứng.")
    add_numbered(doc, 3, "Xác nhận người review, ngày review, quyền sử dụng hình ảnh/video và nhãn thời gian của MC10; nếu hồ sơ khai đánh giá hành vi thì cần thêm nhãn cho từng hành vi và file evaluator tương ứng.")
    add_numbered(doc, 4, "Khai báo việc sử dụng AI trong quá trình rà soát/soạn thảo theo biểu mẫu liêm chính của Nhà trường nếu biểu mẫu yêu cầu; nội dung do trợ lý tạo không phải dữ liệu thực nghiệm.")
    add_para(doc, "Trước khi gửi: mở được từng tệp bằng tài khoản kiểm tra độc lập; dùng đúng tiền tố HUNRE.NH.2026.11.30; đồng bộ checkpoint, split, ngưỡng và số liệu giữa Research Brief, Poster và BCTK; kiểm tra quyền sử dụng ảnh/video; để GVHD/Khoa xác nhận các điểm còn thiếu.", first=0.18, after=0)

    doc.save(OUTPUT)
    print(OUTPUT)


if __name__ == "__main__":
    build()
