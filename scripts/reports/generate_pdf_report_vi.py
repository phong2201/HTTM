"""
=============================================================================
BÁO CÁO BÀI TẬP LỚN: HỆ THỐNG THÔNG MINH (INTELLIGENT SYSTEMS - CO5119/CO3041)
TRƯỜNG ĐẠI HỌC BÁCH KHOA - ĐHQG TP. HỒ CHÍ MINH • KHOA KH&KT MÁY TÍNH
ĐỀ TÀI: HỆ THỐNG GỢI Ý THỜI TRANG CÁ NHÂN HÓA ĐA TẦNG VỚI MÔ HÌNH RỪNG NGẪU NHIÊN
VÀ TÁI XẾP HẠNG PHIÊN THỜI GIAN THỰC (HUB)
Biên dịch tự động Two-Pass với font chữ tiếng Việt Unicode Arial chuẩn mực
=============================================================================
"""

import os
import sys

# Đảm bảo console Windows in tiếng Việt UTF-8 không lỗi
try:
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    if sys.stderr.encoding != 'utf-8':
        sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
    KeepTogether, HRFlowable, Preformatted, Flowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ---------------------------------------------------------------------------
# Đăng ký Font chữ Tiếng Việt Unicode Arial từ Windows
# ---------------------------------------------------------------------------
pdfmetrics.registerFont(TTFont('Arial', r'C:\Windows\Fonts\arial.ttf'))
pdfmetrics.registerFont(TTFont('Arial-Bold', r'C:\Windows\Fonts\arialbd.ttf'))
pdfmetrics.registerFont(TTFont('Arial-Italic', r'C:\Windows\Fonts\ariali.ttf'))
pdfmetrics.registerFont(TTFont('SegoeUISymbol', r'C:\Windows\Fonts\seguisym.ttf'))

# Ký hiệu Toán học chuẩn ấn phẩm arXiv / IEEE
ASSIGN = '<font name="SegoeUISymbol">\u2190</font>'
IN = '<font name="SegoeUISymbol">\u2208</font>'
NOTIN = '<font name="SegoeUISymbol">\u2209</font>'
EMPTY = '<font name="SegoeUISymbol">\u2205</font>'
UNION = '<font name="SegoeUISymbol">\u222a</font>'
INTERSECT = '<font name="SegoeUISymbol">\u2229</font>'
SETMINUS = '<font name="SegoeUISymbol">\u2216</font>'
EXISTS = '<font name="SegoeUISymbol">\u2203</font>'
FORALL = '<font name="SegoeUISymbol">\u2200</font>'
AND = '<font name="SegoeUISymbol">\u2227</font>'
OR = '<font name="SegoeUISymbol">\u2228</font>'
TIMES = '<font name="SegoeUISymbol">\u00d7</font>'
LE = '<font name="SegoeUISymbol">\u2264</font>'
GE = '<font name="SegoeUISymbol">\u2265</font>'
SUM = '<font name="SegoeUISymbol">\u2211</font>'
LAMBDA = '&lambda;'
DELTA = '&Delta;'
CONCAT = '<font name="SegoeUISymbol">\u2295</font>'
DOT = '<font name="SegoeUISymbol">\u22c5</font>' 

# ---------------------------------------------------------------------------
# Dynamic Two-Pass Page Tracking Architecture
# ---------------------------------------------------------------------------
PAGE_MAPPING = {}

class PageTracker(Flowable):
    def __init__(self, key):
        super().__init__()
        self.key = key
        self.width = 0
        self.height = 0

    def draw(self):
        current_page = self.canv._pageNumber
        if self.key not in PAGE_MAPPING or PAGE_MAPPING[self.key] != current_page:
            PAGE_MAPPING[self.key] = current_page

class NumberedCanvasVI(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        if self._pageNumber == 1:
            self.draw_cover_border()
            return

        self.saveState()
        self.setFont("Arial", 8)
        self.setFillColor(colors.HexColor('#64748b'))

        # Header running line
        self.setStrokeColor(colors.HexColor('#cbd5e1'))
        self.setLineWidth(0.5)
        self.line(38, 804, 557, 804)

        self.drawString(38, 809, "TRƯỜNG ĐH BÁCH KHOA - ĐHQG TP.HCM • KHOA KH&KT MÁY TÍNH")
        self.drawRightString(557, 809, "HỆ THỐNG THÔNG MINH HUB")

        # Footer running line
        self.setStrokeColor(colors.HexColor('#e2e8f0'))
        self.setLineWidth(0.5)
        self.line(38, 38, 557, 38)

        self.drawString(38, 26, "Báo Cáo Bài Tập Lớn - Nhóm Đào Duy Đạt, Phan Tiến Huy")
        page_str = f"Trang {self._pageNumber} / {page_count}"
        self.drawRightString(557, 26, page_str)

        self.restoreState()

    def draw_cover_border(self):
        self.saveState()
        self.setStrokeColor(colors.HexColor('#1e3a8a'))
        self.setLineWidth(3)
        self.rect(30, 30, 535, 782)

        self.setStrokeColor(colors.HexColor('#3b82f6'))
        self.setLineWidth(1)
        self.rect(34, 34, 527, 774)

        self.setFillColor(colors.HexColor('#1e3a8a'))
        for x, y in [(34, 34), (34, 808), (561, 34), (561, 808)]:
            self.rect(x - 3, y - 3, 6, 6, fill=1, stroke=0)

        self.restoreState()

# ---------------------------------------------------------------------------
# Helper nạp ảnh tự co dãn
# ---------------------------------------------------------------------------
ASSETS_DIR = Path(r"D:\HTTM\docs\report_assets")

def create_image_flowable(image_name, max_w=6.2*inch, max_h=3.6*inch):
    img_path = ASSETS_DIR / image_name
    if not img_path.exists():
        return Paragraph(f"<i>[Không tìm thấy ảnh: {image_name}]</i>", ParagraphStyle('MissingImg', fontName='Arial-Italic', fontSize=9, textColor=colors.red))
    
    from reportlab.platypus import Image as RLImg
    temp_img = RLImg(str(img_path))
    w = temp_img.imageWidth
    h = temp_img.imageHeight
    if w <= 0 or h <= 0:
        return Spacer(1, 10)
    
    scale = min(max_w / w, max_h / h)
    return RLImg(str(img_path), width=w * scale, height=h * scale)

def create_caption(text, styles):
    return Paragraph(f"<b>{text}</b>", styles['CaptionStyleVI'])

def build_arxiv_algorithm(algo_id, title, inputs, outputs, steps, font_family='Arial', width=490):
    algo_header_style = ParagraphStyle(
        f'ArxivAlgoHeader_VI_{algo_id}',
        fontName=f'{font_family}-Bold', fontSize=8.5, leading=11,
        textColor=colors.HexColor('#0f172a')
    )
    algo_io_style = ParagraphStyle(
        f'ArxivAlgoIO_VI_{algo_id}',
        fontName=font_family, fontSize=7.3, leading=10,
        textColor=colors.HexColor('#1e293b')
    )
    algo_num_style = ParagraphStyle(
        f'ArxivAlgoNum_VI_{algo_id}',
        fontName=font_family, fontSize=7.2, leading=9.6,
        alignment=2, textColor=colors.HexColor('#64748b')
    )
    algo_code_style = ParagraphStyle(
        f'ArxivAlgoCode_VI_{algo_id}',
        fontName=font_family, fontSize=7.2, leading=9.6,
        textColor=colors.HexColor('#0f172a')
    )
    
    rows = []
    rows.append([Paragraph(f"<b>Thuật toán {algo_id}:</b> {title}", algo_header_style), ""])
    rows.append([Paragraph(f"<b>Đầu vào:</b> {inputs}", algo_io_style), ""])
    rows.append([Paragraph(f"<b>Đầu ra:</b> {outputs}", algo_io_style), ""])
    
    for num, line in steps:
        rows.append([
            Paragraph(f"{num}:", algo_num_style),
            Paragraph(line, algo_code_style)
        ])
        
    t_style = [
        ('LINEABOVE', (0, 0), (-1, 0), 1.5, colors.HexColor('#0f172a')),
        ('SPAN', (0, 0), (1, 0)),
        ('SPAN', (0, 1), (1, 1)),
        ('SPAN', (0, 2), (1, 2)),
        ('LINEBELOW', (0, 0), (-1, 0), 0.75, colors.HexColor('#0f172a')),
        ('LINEBELOW', (0, 2), (-1, 2), 0.5, colors.HexColor('#94a3b8')),
        ('LINEBELOW', (0, -1), (-1, -1), 1.5, colors.HexColor('#0f172a')),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fafaf9')),
        ('TOPPADDING', (0, 0), (-1, 0), 3.5),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 3.5),
        ('TOPPADDING', (0, 1), (-1, 2), 2.0),
        ('BOTTOMPADDING', (0, 1), (-1, 2), 2.0),
        ('TOPPADDING', (0, 3), (-1, -1), 1.0),
        ('BOTTOMPADDING', (0, 3), (-1, -1), 1.0),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]
    
    table = Table(rows, colWidths=[22, width - 22])
    table.setStyle(TableStyle(t_style))
    return table

def build_arxiv_equation(eq_num, formula_html, font_family='Arial', accent_color='#0f766e', width=490):
    safe_id = str(eq_num).replace('.', '_')
    eq_math_style = ParagraphStyle(
        f'ArxivEqMath_VI_{safe_id}',
        fontName=font_family, fontSize=8.5, leading=12,
        alignment=1, textColor=colors.HexColor('#0f172a')
    )
    eq_num_style = ParagraphStyle(
        f'ArxivEqNum_VI_{safe_id}',
        fontName=f'{font_family}-Bold', fontSize=8.0, leading=12,
        alignment=2, textColor=colors.HexColor('#475569')
    )
    
    p_math = Paragraph(formula_html, eq_math_style)
    p_num = Paragraph(f"({eq_num})", eq_num_style)
    t = Table([[p_math, p_num]], colWidths=[width - 50, 50])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('LINELEFT', (0,0), (0,0), 2.5, colors.HexColor(accent_color)),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    return t


# ---------------------------------------------------------------------------
# Xây dựng Story (Two-Pass Builder)
# ---------------------------------------------------------------------------
def build_report_story():
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'CoverTitleVI', fontName='Arial-Bold', fontSize=18, leading=24,
        alignment=1, textColor=colors.HexColor('#1e3a8a')
    )
    subtitle_style = ParagraphStyle(
        'CoverSubTitleVI', fontName='Arial', fontSize=11, leading=16,
        alignment=1, textColor=colors.HexColor('#334155')
    )
    h1_style = ParagraphStyle(
        'Heading1VI', fontName='Arial-Bold', fontSize=15, leading=19,
        textColor=colors.HexColor('#1e3a8a'), keepWithNext=True, spaceBefore=12, spaceAfter=6
    )
    h2_style = ParagraphStyle(
        'Heading2VI', fontName='Arial-Bold', fontSize=12, leading=16,
        textColor=colors.HexColor('#1e40af'), keepWithNext=True, spaceBefore=9, spaceAfter=4
    )
    h3_style = ParagraphStyle(
        'Heading3VI', fontName='Arial-Bold', fontSize=10, leading=14,
        textColor=colors.HexColor('#0f172a'), keepWithNext=True, spaceBefore=7, spaceAfter=3
    )
    body_style = ParagraphStyle(
        'BodyTextVI', fontName='Arial', fontSize=9.5, leading=14,
        textColor=colors.HexColor('#1e293b'), alignment=4, spaceBefore=2, spaceAfter=4
    )
    bullet_style = ParagraphStyle(
        'BulletTextVI', fontName='Arial', fontSize=9, leading=13.5,
        textColor=colors.HexColor('#1e293b'), spaceBefore=2, spaceAfter=2, leftIndent=12
    )
    table_cell = ParagraphStyle('CellVI', fontName='Arial', fontSize=8, leading=11, textColor=colors.HexColor('#1e293b'))
    table_cell_bold = ParagraphStyle('CellBoldVI', fontName='Arial-Bold', fontSize=8, leading=11, textColor=colors.HexColor('#0f172a'))
    table_cell_header = ParagraphStyle('CellHeaderVI', fontName='Arial-Bold', fontSize=8.5, leading=12, textColor=colors.white, alignment=1)
    caption_style = ParagraphStyle('CaptionStyleVI', fontName='Arial-Bold', fontSize=8.5, leading=12, textColor=colors.HexColor('#475569'), alignment=1, spaceBefore=3, spaceAfter=8)
    styles.add(caption_style)
    eq_style = ParagraphStyle('EqVI', fontName='Arial-Italic', fontSize=9, leading=13, textColor=colors.HexColor('#1e3a8a'), leftIndent=18, spaceBefore=3, spaceAfter=3)
    code_style = ParagraphStyle('CodeVI', fontName='Courier', fontSize=7.2, leading=9.2, textColor=colors.HexColor('#0f172a'), spaceBefore=2, spaceAfter=2)

    story = []

    # =========================================================================
    # TRANG BÌA (COVER PAGE)
    # =========================================================================
    story.append(Spacer(1, 15))
    story.append(Paragraph("ĐẠI HỌC QUỐC GIA THÀNH PHỐ HỒ CHÍ MINH", ParagraphStyle('UnivVI', fontName='Arial-Bold', fontSize=12, leading=16, alignment=1, textColor=colors.HexColor('#1e3a8a'))))
    story.append(Paragraph("TRƯỜNG ĐẠI HỌC BÁCH KHOA", ParagraphStyle('Univ2VI', fontName='Arial-Bold', fontSize=13, leading=17, alignment=1, textColor=colors.HexColor('#1e3a8a'))))
    story.append(Paragraph("KHOA KHOA HỌC & KỸ THUẬT MÁY TÍNH", ParagraphStyle('FacultyVI', fontName='Arial-Bold', fontSize=11, leading=15, alignment=1, textColor=colors.HexColor('#2563eb'))))

    story.append(Spacer(1, 25))
    story.append(HRFlowable(width="60%", thickness=1.5, color=colors.HexColor('#1e3a8a'), spaceBefore=5, spaceAfter=15))

    story.append(Paragraph("BÁO CÁO BÀI TẬP LỚN MÔN HỌC", ParagraphStyle('DocTypeVI', fontName='Arial-Bold', fontSize=13, leading=17, alignment=1, textColor=colors.HexColor('#b91c1c'))))
    story.append(Paragraph("HỆ THỐNG THÔNG MINH (INTELLIGENT SYSTEMS - CO5119 / CO3041)", ParagraphStyle('CourseVI', fontName='Arial-Bold', fontSize=11.5, leading=16, alignment=1, textColor=colors.HexColor('#0f172a'))))

    story.append(Spacer(1, 20))
    story.append(Paragraph("HỆ THỐNG GỢI Ý THỜI TRANG CÁ NHÂN HÓA ĐA TẦNG VỚI MÔ HÌNH RỪNG NGẪU NHIÊN VÀ TÁI XẾP HẠNG PHIÊN THỜI GIAN THỰC (HUB)", title_style))
    story.append(Spacer(1, 8))
    story.append(Paragraph("A Two-Stage Personalized Fashion Recommendation System with Random Forest Pointwise Ranker & Real-Time In-Session Re-ranking", subtitle_style))

    story.append(Spacer(1, 35))

    # Bảng thông tin nhóm thực hiện & GVHD
    meta_info = [
        [Paragraph("<b>Giảng viên hướng dẫn:</b>", table_cell_bold), Paragraph("TS. Quán Thành Thơ", table_cell)],
        [Paragraph("<b>Khoa phụ trách:</b>", table_cell_bold), Paragraph("Khoa Khoa học & Kỹ thuật Máy tính (CSE - HCMUT)", table_cell)],
        [Paragraph("<b>Học kỳ áp dụng:</b>", table_cell_bold), Paragraph("Học kỳ 1 Năm học 2024 - 2025 (HK241)", table_cell)],
        [Paragraph("<b>Sinh viên thực hiện 1:</b>", table_cell_bold), Paragraph("<b>Đào Duy Đạt</b> (Trưởng nhóm - Đóng góp: 50%)<br/><i>Phụ trách: Kiến trúc Hệ thống, Thuật toán Random Forest, Tích hợp Full-stack</i>", table_cell)],
        [Paragraph("<b>Sinh viên thực hiện 2:</b>", table_cell_bold), Paragraph("<b>Phan Tiến Huy</b> (Thành viên - Đóng góp: 50%)<br/><i>Phụ trách: Tiền xử lý Dữ liệu Kaggle, Bộ kiểm thử QA & Trực quan hóa</i>", table_cell)],
        [Paragraph("<b>Bộ dữ liệu thực tế:</b>", table_cell_bold), Paragraph("Kaggle H&M Personalized Fashion Recommendations (31.78M Giao dịch thật)", table_cell)],
        [Paragraph("<b>Thời gian hoàn thành:</b>", table_cell_bold), Paragraph("Tháng 11 Năm 2024", table_cell)],
    ]
    meta_table = Table(meta_info, colWidths=[150, 310])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(meta_table)

    story.append(Spacer(1, 40))
    story.append(Paragraph("TP. HỒ CHÍ MINH, THÁNG 11/2024", ParagraphStyle('LocVI', fontName='Arial-Bold', fontSize=10, leading=14, alignment=1, textColor=colors.HexColor('#64748b'))))

    story.append(PageBreak())

    # =========================================================================
    # TRANG MỤC LỤC & DANH MỤC HÌNH VẼ / BẢNG BIỂU
    # =========================================================================
    story.append(PageTracker('toc_page'))
    story.append(Paragraph("MỤC LỤC BÁO CÁO HỌC THUẬT", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cbd5e1'), spaceBefore=2, spaceAfter=8))

    def p_num(key, default_val):
        return str(PAGE_MAPPING.get(key, default_val))

    toc_entries = [
        ("1  Đặt Vấn Đề, Phạm Vi & Đặc Tả Yêu Cầu Hệ Thống", p_num('ch1', 4), 0),
        ("   1.1 Bối Cảnh Thực Tế & Thách Thức Ngành Bán Lẻ Thời Trang", p_num('sec1_1', 4), 1),
        ("   1.2 Nhận Diện Các Tác Nhân Hệ Thống (Stakeholders & Actors)", p_num('sec1_2', 4), 1),
        ("   1.3 Bảng Đặc Tả Yêu Cầu Chức Năng (FRs) & Phi Chức Năng (NFRs)", p_num('sec1_3', 5), 1),
        ("2  Cơ Sở Lý Thuyết & Mô Hình Thuật Toán Cốt Lõi", p_num('ch2', 6), 0),
        ("   2.1 Thuật Toán Rừng Ngẫu Nhiên (Random Forest Ranker & Bagging)", p_num('sec2_1', 6), 1),
        ("   2.2 Kiến Trúc Hai Giai Đoạn (Two-Stage Recommendation Pipeline)", p_num('sec2_3', 7), 1),
        ("   2.3 Thuật Toán Rút Trích Ứng Viên & Tái Xếp Hạng Phiên Bán Rã", p_num('sec2_4', 8), 1),
        ("3  Mô Hình Hóa Trường Hợp Sử Dụng (Use-Case) & Đặc Tả Tương Tác", p_num('ch3', 9), 0),
        ("   3.1 Sơ Đồ Use-Case Tổng Thể & Ranh Giới Quyền Hạn (RBAC)", p_num('sec3_1', 9), 1),
        ("   3.2 Bảng Đặc Tả Chi Tiết 8 Use-Case (UC-01 đến UC-08)", p_num('sec3_2', 10), 1),
        ("   3.3 Sơ Đồ Tuần Tự (Sequence Diagrams) Tương Tác Thời Gian Thực", p_num('sec3_3', 14), 1),
        ("4  Kiến Trúc Hệ Thống & Thiết Kế Cơ Sở Dữ Liệu", p_num('ch4', 15), 0),
        ("   4.1 Kiến Trúc 4 Tầng Module (Enterprise 4-Tier Architecture)", p_num('sec4_1', 15), 1),
        ("   4.2 Từ Điển Dữ Liệu Quan Hệ 23 Thuộc Tính & Lược Đồ CSDL 3NF", p_num('sec4_2', 16), 1),
        ("   4.3 Danh Mục 22 RESTful API & Bộ Kiểm Thử Tự Động (27 Tests QA)", p_num('sec4_3', 17), 1),
        ("5  Phân Tích Khám Phá Dữ Liệu (EDA) & Chống Rò Rỉ Dữ Liệu", p_num('ch5', 19), 0),
        ("   5.1 Bộ Dữ Liệu Thực Tế H&M Kaggle (31.78M Giao Dịch Thật)", p_num('sec5_1', 19), 1),
        ("   5.2 Bộ 10 Biểu Đồ Phân Tích Kinh Doanh & Chẩn Đoán Machine Learning", p_num('fig5_1', 19), 1),
        ("   5.3 Cơ Chế Chia Tập Cửa Sổ Trượt Thời Gian Chống Rò Rỉ (No Leakage)", p_num('sec5_2', 21), 1),
        ("   5.4 Rút Trích Ứng Viên Sơ Tuyển & Kỹ Nghệ 14 Đặc Trưng Học Máy", p_num('sec5_3', 21), 1),
        ("6  Huấn Luyện Mô Hình, Đánh Giá Thực Nghiệm & Phân Tích Lát Cắt Lỗi", p_num('ch6', 23), 0),
        ("   6.1 Thiết Lập Huấn Luyện & Tối Ưu Siêu Tham Số Cây Quyết Định", p_num('sec6_1', 23), 1),
        ("   6.2 Độ Đo MAP@12 Chuẩn Kaggle & Kết Quả Vượt Trội So Với Baselines", p_num('sec6_2', 24), 1),
        ("   6.3 Phân Tích Lát Cắt Lỗi (Active vs Inactive & Nhóm Ngành Hàng)", p_num('sec6_3', 25), 1),
        ("   6.4 Cơ Chế Tái Xếp Hạng Bán Rã & Khống Chế Ngập Lụt Danh Mục", p_num('sec6_4', 26), 1),
        ("7  Minh Họa Giao Diện Người Dùng & Triển Khai Hệ Thống Thực Tế", p_num('ch7', 27), 0),
        ("   7.1 Không Gian Khách Hàng (Buyer Portal & Trang Chi Tiết Sản Phẩm)", p_num('sec7_1', 27), 1),
        ("   7.2 Không Gian Data Scientist (Bảng Điều Khiển EDA, Metrics & Retrain)", p_num('sec7_2', 29), 1),
        ("   7.3 Không Gian Quản Trị Viên (Admin Operations Dashboard)", p_num('sec7_3', 33), 1),
        ("8  Kết Luận, Đóng Góp Nhóm & Tuyên Bố Trí Tuệ Nhân Tạo", p_num('ch8', 34), 0),
        ("   8.1 Tổng Kết Đóng Góp & Giá Trị Thực Tiễn Của Hệ Thống", p_num('sec8_1', 34), 1),
        ("   8.2 Bảng Phân Công Công Việc & Tỷ Lệ Đóng Góp Nhóm (50% - 50%)", p_num('sec8_2', 34), 1),
        ("   8.3 Tuyên Bố Liêm Chính Học Thuật & Sử Dụng GenAI Minh Bạch", p_num('sec8_3', 35), 1),
        ("   8.4 Chuẩn Bị Bộ Câu Hỏi - Trả Lời Phản Biện Bảo Vệ Đồ Án", p_num('sec8_4', 35), 1),
        ("Tài Liệu Tham Khảo (Chuẩn IEEE)", p_num('ref_sec', 36), 0),
    ]

    toc_rows = []
    for title, page, level in toc_entries:
        style_t = table_cell_bold if level == 0 else table_cell
        color_p = '#1e3a8a' if level == 0 else '#475569'
        toc_rows.append([
            Paragraph(f"<font color='{color_p}'>{title}</font>", style_t),
            Paragraph(f"<font color='{color_p}'><b>{page}</b></font>", ParagraphStyle('PNumVI', parent=style_t, alignment=2))
        ])

    toc_table = Table(toc_rows, colWidths=[420, 50])
    toc_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 1.3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.3),
        ('LINEBELOW', (0,0), (-1,-1), 0.3, colors.HexColor('#f1f5f9')),
    ]))
    story.append(toc_table)

    story.append(Spacer(1, 10))
    story.append(Paragraph("DANH MỤC HÌNH VẼ CHÍNH", h2_style))
    fig_entries = [
        ("Hình 2.1: Quy Trình Luồng Dữ Liệu & Huấn Luyện Mô Hình Học Máy (Excalidraw)", p_num('sec2_3', 7)),
        ("Hình 3.0: Sơ Đồ Trường Hợp Sử Dụng (Use-Case) Tổng Thể Hệ Thống (Excalidraw)", p_num('sec3_1', 9)),
        ("Hình 3.1: Sơ Đồ Tuần Tự Tái Xếp Hạng Phiên Theo Thời Gian Thực (Excalidraw)", p_num('sec3_3', 14)),
        ("Hình 4.1: Kiến Trúc Phân Tầng Module 4 Lớp của Hệ Thống HUB (Excalidraw)", p_num('sec4_1', 15)),
        ("Hình 5.1: Doanh Số Giao Dịch Hàng Ngày Trên Dữ Liệu Lịch Sử Kaggle H&M", p_num('fig5_1', 19)),
        ("Hình 5.2: Phân Bố Giá Sản Phẩm Chuẩn Hóa & Độ Tuổi Khách Hàng", p_num('fig5_2', 19)),
        ("Hình 5.3: Cơ Cấu Phân Khúc 15 Nhóm Ngành Hàng May Mặc H&M", p_num('fig5_3', 20)),
        ("Hình 5.4: Phân Bố Số Lần Mua Sắm & Đường Cong Đuôi Dài Long-tail", p_num('fig5_4', 20)),
        ("Hình 7.1: Giao Diện Đăng Nhập Đa Vai Trò (LoginPage)", p_num('fig7_1', 27)),
        ("Hình 7.2: Trang Chủ Gợi Ý Cá Nhân Hóa Dành Cho Khách Hàng (HomePage)", p_num('fig7_2', 28)),
        ("Hình 7.3: Trang Chi Tiết Sản Phẩm & Gợi Ý Phối Đồ Liên Quan (ProductDetailPage)", p_num('fig7_3', 28)),
        ("Hình 7.4: Bảng Điều Khiển Khám Phá Dữ Liệu EDA (DataSciencePage)", p_num('fig7_4', 29)),
        ("Hình 7.5: Bảng Đánh Giá Độ Đo Mô Hình & So Sánh Baselines (ModelMetricsPage)", p_num('fig7_5', 30)),
        ("Hình 7.6: Ma Trận Phân Tích Lát Cắt Lỗi Đa Chiều (ErrorAnalysisPage)", p_num('fig7_6', 31)),
        ("Hình 7.7: Bảng Quản Trị Tái Huấn Luyện & Chỉnh Siêu Tham Số (TrainingSchedulePage)", p_num('fig7_7', 32)),
        ("Hình 7.8: Bảng Điều Khiển Quản Trị Cửa Hàng & Doanh Thu (AdminDashboardPage)", p_num('fig7_8', 33)),
    ]
    fig_rows = [[Paragraph(f"<font color='#334155'>{f[0]}</font>", table_cell), Paragraph(f"<b>{f[1]}</b>", ParagraphStyle('PNumFVI', parent=table_cell, alignment=2))] for f in fig_entries]
    fig_table = Table(fig_rows, colWidths=[420, 50])
    fig_table.setStyle(TableStyle([
        ('TOPPADDING', (0,0), (-1,-1), 1.2), ('BOTTOMPADDING', (0,0), (-1,-1), 1.2),
        ('LINEBELOW', (0,0), (-1,-1), 0.3, colors.HexColor('#f8fafc'))
    ]))
    story.append(fig_table)

    story.append(PageBreak())

    # =========================================================================
    # CHƯƠNG 1: ĐẶT VẤN ĐỀ, PHẠM VI & ĐẶC TẢ YÊU CẦU
    # =========================================================================
    story.append(PageTracker('ch1'))
    story.append(Paragraph("1  Đặt Vấn Đề, Phạm Vi & Đặc Tả Yêu Cầu Hệ Thống", h1_style))
    story.append(Spacer(1, 4))

    story.append(PageTracker('sec1_1'))
    story.append(Paragraph("1.1  Bối Cảnh Thực Tế & Thách Thức Ngành Bán Lẻ Thời Trang", h2_style))
    story.append(Paragraph(
        "Thương mại điện tử thời trang nhanh (Fast Fashion E-Commerce) có quy mô danh mục khổng lồ (>105.000 mặt hàng) nhưng chu kỳ sống của sản phẩm lại rất ngắn (chỉ kéo dài vài tuần). "
        "Người tiêu dùng thường xuyên rơi vào trạng thái 'quá tải lựa chọn' (Choice Overload), dẫn đến sụt giảm tỷ lệ chuyển đổi đơn hàng. "
        "Thách thức kỹ thuật lớn nhất nằm ở tính thưa thớt của ma trận giao dịch (Sparsity > 99.98%), hiện tượng trôi dạt thị hiếu theo mùa vụ (Seasonal Trend Drift), và yêu cầu độ trễ suy luận thời gian thực cực thấp (< 50ms) để giữ chân khách hàng trên website.",
        body_style
    ))
    story.append(Paragraph(
        "Mục tiêu của đề tài <b>HUB</b> là xây dựng một nền tảng thương mại điện tử hoàn chỉnh, tích hợp hệ thống khuyến nghị hai giai đoạn (Two-Stage Recommendation System) với thuật toán cốt lõi là <b>Rừng ngẫu nhiên (Random Forest)</b> "
        "và cơ chế <b>Tái xếp hạng theo phiên (Session Re-ranking)</b>. Hệ thống giải quyết trọn vẹn yêu cầu bài toán từ khâu phân tích dữ liệu thực tế Kaggle, huấn luyện mô hình chống rò rỉ dữ liệu, đến xây dựng API backend và giao diện người dùng tương tác.",
        body_style
    ))

    story.append(PageTracker('sec1_2'))
    story.append(Paragraph("1.2  Nhận Diện Các Tác Nhân Hệ Thống (Stakeholders & Actors)", h2_style))
    story.append(Paragraph(
        "Tuân thủ nghiêm ngặt chuẩn mực công nghệ phần mềm và đề bài môn học, HUB định danh 3 vai trò tác nhân độc lập:",
        body_style
    ))
    story.append(Paragraph("• <b>Khách Mua Hàng (Buyer - Role 1):</b> Tác nhân tiêu dùng trực tiếp. Tương tác với giao diện để duyệt danh mục, nhận danh sách 12 sản phẩm gợi ý cá nhân hóa trên trang chủ, click xem sản phẩm để hệ thống tự động tái xếp hạng feed tức thì, thêm hàng vào giỏ và hoàn tất thanh toán.", bullet_style))
    story.append(Paragraph("• <b>Nhà Khoa Học Dữ Liệu (Data Scientist - Role 2):</b> Tác nhân trọng tâm của đề tài. Được trang bị không gian làm việc chuyên sâu gồm: Bảng điều khiển phân tích khám phá dữ liệu (EDA) và giám sát trôi dạt phân phối (Data Drift), màn hình đánh giá độ đo MAP@12 và độ chính xác phân loại so với các Baselines, công cụ chẩn đoán ma trận lỗi trên từng phân khúc khách hàng, và giao diện cấu hình siêu tham số kích hoạt luồng tái huấn luyện mô hình tự động.", bullet_style))
    story.append(Paragraph("• <b>Quản Trị Viên Cửa Hàng (Store Manager / Admin - Role 3):</b> Quản lý vòng đời sản phẩm (CRUD), điều phối lượng hàng tồn kho, giám sát doanh số thương mại và theo dõi nhật ký kiểm toán hệ thống.", bullet_style))

    story.append(PageTracker('sec1_3'))
    story.append(Paragraph("1.3  Bảng Đặc Tả Yêu Cầu Chức Năng (FRs) & Phi Chức Năng (NFRs)", h2_style))

    fr_data = [
        [Paragraph("Mã Yêu Cầu", table_cell_header), Paragraph("Tên Chức Năng", table_cell_header), Paragraph("Tác Nhân", table_cell_header), Paragraph("Mô Tả Nghiệp Vụ Thực Hiện", table_cell_header)],
        [Paragraph("<b>FR-01</b>", table_cell), Paragraph("Quản lý danh mục & Tìm kiếm", table_cell_bold), Paragraph("Buyer, Admin", table_cell), Paragraph("Lọc sản phẩm theo nhóm ngành, loại trang phục, màu sắc và tìm kiếm toàn văn.", table_cell)],
        [Paragraph("<b>FR-02</b>", table_cell), Paragraph("Gợi ý cá nhân hóa hai giai đoạn", table_cell_bold), Paragraph("Buyer", table_cell), Paragraph("Xuất ra Top-12 sản phẩm được Random Forest Ranker chấm điểm cao nhất cho từng cá nhân.", table_cell)],
        [Paragraph("<b>FR-03</b>", table_cell), Paragraph("Tái xếp hạng phiên thời gian thực", table_cell_bold), Paragraph("Buyer", table_cell), Paragraph("Tự động phạt/thưởng điểm và tái sắp xếp Top-12 khi phát sinh sự kiện click trong phiên.", table_cell)],
        [Paragraph("<b>FR-04</b>", table_cell), Paragraph("Trực quan hóa phân phối EDA", table_cell_bold), Paragraph("Data Scientist", table_cell), Paragraph("Hiển thị 10 biểu đồ trực quan về lượng giao dịch, giá bán, độ tuổi và tần suất mua hàng.", table_cell)],
        [Paragraph("<b>FR-05</b>", table_cell), Paragraph("Đánh giá mô hình & Lát cắt lỗi", table_cell_bold), Paragraph("Data Scientist", table_cell), Paragraph("Đo lường chỉ số MAP@12, vẽ biểu đồ so sánh Baselines và phân rã lỗi trên khách tích cực / vãng lai.", table_cell)],
        [Paragraph("<b>FR-06</b>", table_cell), Paragraph("Quản trị tái huấn luyện mô hình", table_cell_bold), Paragraph("Data Scientist", table_cell), Paragraph("Tùy chỉnh số cây, độ sâu và kích hoạt tiến trình ngầm huấn luyện lại mô hình.", table_cell)],
    ]
    fr_table = Table(fr_data, colWidths=[55, 120, 75, 220])
    fr_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a8a')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 3.5), ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
    ]))
    story.append(fr_table)
    story.append(create_caption("Bảng 1.1: Đặc tả Danh mục Yêu cầu Chức năng (Functional Requirements)", styles))

    story.append(Spacer(1, 6))

    nfr_data = [
        [Paragraph("Mã Yêu Cầu", table_cell_header), Paragraph("Chỉ Tiêu Đánh Giá", table_cell_header), Paragraph("Chỉ Số Đo Lường Định Lượng", table_cell_header), Paragraph("Giải Pháp Kiến Trúc Hiện Thực", table_cell_header)],
        [Paragraph("<b>NFR-01</b>", table_cell), Paragraph("Độ trễ suy luận (Latency)", table_cell_bold), Paragraph("P95 Response Time < 50ms", table_cell), Paragraph("Tính trước điểm ứng viên, lưu cache bộ nhớ trong, tối ưu vector hóa Re-ranking.", table_cell)],
        [Paragraph("<b>NFR-02</b>", table_cell), Paragraph("Thông lượng phục vụ (Throughput)", table_cell_bold), Paragraph("> 200 Requests/sec (RPS)", table_cell), Paragraph("FastAPI bất đồng bộ (asyncio), kết nối ORM tối ưu, kiến trúc non-blocking I/O.", table_cell)],
        [Paragraph("<b>NFR-03</b>", table_cell), Paragraph("Toàn vẹn dữ liệu (Integrity)", table_cell_bold), Paragraph("Tuyệt đối không rò rỉ dữ liệu", table_cell), Paragraph("Chia tập trượt thời gian t_dat < t_split, không lấy thông tin tương lai tạo đặc trưng.", table_cell)],
        [Paragraph("<b>NFR-04</b>", table_cell), Paragraph("Bảo mật phân quyền (Security)", table_cell_bold), Paragraph("JWT Bearer Auth & Role Guards", table_cell), Paragraph("Mã hóa mật khẩu Bcrypt, phân quyền chặt chẽ giữa Buyer và Data Scientist.", table_cell)],
    ]
    nfr_table = Table(nfr_data, colWidths=[55, 120, 110, 185])
    nfr_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f766e')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 3.5), ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
    ]))
    story.append(nfr_table)
    story.append(create_caption("Bảng 1.2: Đặc tả Danh mục Yêu cầu Phi Chức năng (Non-Functional Requirements)", styles))

    story.append(PageBreak())

    # =========================================================================
    # CHƯƠNG 2: CƠ SỞ LÝ THUYẾT & MÔ HÌNH THUẬT TOÁN
    # =========================================================================
    story.append(PageTracker('ch2'))
    story.append(Paragraph("2  Cơ Sở Lý Thuyết & Mô Hình Thuật Toán Cốt Lõi", h1_style))
    story.append(Spacer(1, 4))

    story.append(PageTracker('sec2_1'))
    story.append(Paragraph("2.1  Thuật Toán Rừng Ngẫu Nhiên (Random Forest Ranker & Bagging)", h2_style))
    story.append(Paragraph(
        "Thuật toán chính được quy định trong đề tài là <b>Rừng ngẫu nhiên (Random Forest)</b>. "
        "Mô hình được áp dụng cho bài toán Pointwise Learning-to-Rank nhằm dự báo xác suất một khách hàng <i>u</i> sẽ mua mặt hàng may mặc <i>i</i>: <i>P(y = 1 | x<sub>u,i</sub>)</i>.",
        body_style
    ))
    story.append(Paragraph("• <b>Độ đo Tạp chất Gini (Gini Impurity):</b> Tại mỗi nút nội bộ của cây quyết định, độ vẩn đục Gini của tập mẫu <i>S</i> kích thước <i>N</i> được tính toán:", bullet_style))
    story.append(Spacer(1, 2))
    story.append(build_arxiv_equation("2.1", f"<i>I<sub>G</sub></i>(<i>S</i>) = 1 - {SUM}<sub><i>c</i>=0</sub><sup>1</sup> <i>p<sub>c</sub></i><sup>2</sup> = 2 <i>p</i><sub>0</sub> <i>p</i><sub>1</sub>"))
    story.append(Spacer(1, 4))
    story.append(Paragraph("• <b>Độ Lợi Thông Tin (Gini Gain):</b> Khi phân chia tập <i>S</i> thành 2 tập con <i>S<sub>L</sub></i> và <i>S<sub>R</sub></i> theo ngưỡng &theta; của đặc trưng <i>j</i>:", bullet_style))
    story.append(Spacer(1, 2))
    story.append(build_arxiv_equation("2.2", f"{DELTA}<i>I<sub>G</sub></i>(<i>S</i>, <i>j</i>, &theta;) = <i>I<sub>G</sub></i>(<i>S</i>) - <font size=9.5>[</font> (|<i>S<sub>L</sub></i>|/|<i>S</i>|) <i>I<sub>G</sub></i>(<i>S<sub>L</sub></i>) + (|<i>S<sub>R</sub></i>|/|<i>S</i>|) <i>I<sub>G</sub></i>(<i>S<sub>R</sub></i>) <font size=9.5>]</font>"))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "Cặp tối ưu <i>(j*, &theta;*)</i> được tìm kiếm thông qua việc tối đa hóa &Delta;I<sub>G</sub>. "
        "Để khắc phục nhược điểm phương sai lớn của cây quyết định đơn lẻ, Leo Breiman áp dụng hai cơ chế ngẫu nhiên hóa:",
        body_style
    ))
    story.append(Paragraph("• <b>Đóng gói mẫu (Bootstrap Aggregation - Bagging):</b> Với <i>B = 200</i> cây, mỗi cây <i>T<sub>b</sub></i> được huấn luyện trên tập dữ liệu D<sup>(b)</sup> rút trích có hoàn lại từ D. Xác suất một mẫu dữ liệu bị bỏ sót (Out-of-Bag - OOB) đạt xấp xỉ lý thuyết:", bullet_style))
    story.append(Spacer(1, 2))
    story.append(build_arxiv_equation("2.3", "lim<sub><i>N</i> &rarr; &infin;</sub> (1 - 1/<i>N</i>)<sup><i>N</i></sup> = 1/<i>e</i> &asymp; 0.368 &nbsp;&nbsp;&nbsp;&nbsp; (36.8% mẫu OOB dùng kiểm định chéo miễn phí)"))
    story.append(Spacer(1, 4))
    story.append(Paragraph("• <b>Giảm phương sai nhờ chọn ngẫu nhiên đặc trưng:</b> Tại mỗi nút, chỉ có <i>m = <font name='SegoeUISymbol'>\u230a\u221a14\u230b</font> = 3</i> đặc trưng được chọn ngẫu nhiên để đánh giá. Phương sai của mô hình trung bình thỏa mãn:", bullet_style))
    story.append(Spacer(1, 2))
    story.append(build_arxiv_equation("2.4", f"Var<font size=9.5>(</font>(1/<i>B</i>) {SUM}<sub><i>b</i>=1</sub><sup><i>B</i></sup> <i>T<sub>b</sub></i>(<b>x</b>)<font size=9.5>)</font> = &rho; &sigma;<sup>2</sup> + ((1 - &rho;) / <i>B</i>) &sigma;<sup>2</sup>"))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "Khi <i>B &rarr; &infin;</i>, số hạng thứ hai triệt tiêu về 0. Việc ngẫu nhiên hóa đặc trưng làm giảm mạnh hệ số tương quan giữa các cây &rho;, qua đó giảm phương sai toàn cục mà không làm tăng độ chệch (Bias).",
        body_style
    ))

    story.append(PageTracker('sec2_3'))
    story.append(Paragraph("2.2  Kiến Trúc Hai Giai Đoạn (Two-Stage Recommendation Pipeline)", h2_style))
    story.append(Paragraph(
        "Để vượt qua thách thức không gian tích Descartes (1.45 &times; 10<sup>11</sup> cặp sản phẩm - khách hàng), HUB áp dụng kiến trúc khuyến nghị 2 giai đoạn chuẩn công nghiệp:",
        body_style
    ))

    # Nhúng Sơ đồ Excalidraw Tiếng Việt
    story.append(Spacer(1, 4))
    story.append(create_image_flowable("excalidraw_03_ml_training_pipeline_vi.png", max_w=6.2*inch, max_h=3.0*inch))
    story.append(create_caption("Hình 2.1: Quy Trình Luồng Dữ Liệu & Huấn Luyện Mô Hình Học Máy (Bản Tiếng Việt Excalidraw)", styles))
    story.append(Spacer(1, 6))

    story.append(PageTracker('sec2_4'))
    story.append(Paragraph("2.3  Thuật Toán Rút Trích Ứng Viên & Tái Xếp Hạng Phiên Bán Rã", h2_style))

    steps1_vi = [
        (1, f"<i>C<sub>u</sub></i> {ASSIGN} {EMPTY}"),
        (2, f"<i>C</i><sub>repurchase</sub> {ASSIGN} {{<i>i</i> {IN} <i>I</i> | {EXISTS} (<i>u</i>, <i>i</i>, <i>t</i>) {IN} <i>D</i> {AND} <i>t</i> {GE} <i>T</i><sub>cutoff</sub> - 28d}}"),
        (3, f"<i>C</i><sub>bestseller</sub> {ASSIGN} TopK({{<i>i</i> {IN} <i>I</i> | doanh_số(<i>i</i>, [<i>T</i><sub>cutoff</sub> - 7d, <i>T</i><sub>cutoff</sub>])}}, <i>K</i> = 12)"),
        (4, f"<i>C</i><sub>age</sub> {ASSIGN} TopK({{<i>i</i> {IN} <i>I</i> | doanh_số_theo_nhóm_tuổi(<i>i</i>, nhóm_tuổi(<i>u</i>))}}, <i>K</i> = 8)"),
        (5, f"<i>C</i><sub>copurchase</sub> {ASSIGN} {{<i>j</i> {IN} <i>I</i> | {EXISTS} <i>i</i> {IN} <i>C</i><sub>repurchase</sub> {AND} tần_suất_cùng_mua(<i>i</i>, <i>j</i>) {GE} 5}}"),
        (6, f"<i>C<sub>u</sub></i> {ASSIGN} GiớiHạn(<i>C</i><sub>repurchase</sub> {UNION} <i>C</i><sub>bestseller</sub> {UNION} <i>C</i><sub>age</sub> {UNION} <i>C</i><sub>copurchase</sub>, <i>C</i><sub>max</sub> = 100)"),
        (7, f"<i>Y</i><sub>thật</sub> {ASSIGN} {{<i>i</i> {IN} <i>I</i> | {EXISTS} (<i>u</i>, <i>i</i>, <i>t</i>) {IN} <i>D</i> {AND} <i>t</i> {IN} [<i>T</i><sub>cutoff</sub>, <i>T</i><sub>cutoff</sub> + 7d]}}"),
        (8, f"<b>MẫuDương</b> {ASSIGN} {{(<i>u</i>, <i>i</i>, 1) | <i>i</i> {IN} (<i>C<sub>u</sub></i> {INTERSECT} <i>Y</i><sub>thật</sub>)}} &nbsp;&nbsp;&nbsp;&nbsp;<font color=\"#64748b\"><i>// Giao dịch mua thực tế trong tuần đích</i></font>"),
        (9, f"<i>N</i><sub>ứng_viên</sub> {ASSIGN} <i>C<sub>u</sub></i> {SETMINUS} <i>Y</i><sub>thật</sub> &nbsp;&nbsp;&nbsp;&nbsp;<font color=\"#64748b\"><i>// Ứng viên thực sự không mua</i></font>"),
        (10, f"<i>k</i><sub>âm</sub> {ASSIGN} min(|<i>N</i><sub>ứng_viên</sub>|, {LAMBDA}<sub>neg</sub> {TIMES} |<b>MẫuDương</b>|)"),
        (11, f"<b>MẫuÂm</b> {ASSIGN} LấyMẫuKhôngHoànLại(<i>N</i><sub>ứng_viên</sub>, <i>k</i><sub>âm</sub>)"),
        (12, f"<b>trả về</b> <i>T<sub>u</sub></i> {ASSIGN} <b>MẫuDương</b> {UNION} {{(<i>u</i>, <i>j</i>, 0) | <i>j</i> {IN} <b>MẫuÂm</b>}}")
    ]
    algo1_vi_flowable = build_arxiv_algorithm(
        "1", "Rút Trích Ứng Viên Đa Kênh & Lấy Mẫu Âm Có Kiểm Soát (Stage 1)",
        f"Khách hàng <i>u</i> {IN} <i>U</i>, Lịch sử <i>D</i> (<i>t</i> &lt; <i>T</i><sub>cutoff</sub>), Danh mục <i>I</i>, Nhóm tuổi <i>A</i>, Tỷ lệ {LAMBDA}<sub>neg</sub> = 5",
        f"Tập mẫu huấn luyện cân bằng <i>T<sub>u</sub></i> = {{(<i>u</i>, <i>i</i>, <i>y</i>)}} với nhãn <i>y</i> {IN} {{0, 1}}",
        steps1_vi
    )
    story.append(algo1_vi_flowable)
    story.append(create_caption("Thuật toán 2.1: Rút Trích Ứng Viên Sơ Tuyển & Lấy Mẫu Âm Cân Bằng Nhãn", styles))
    story.append(Spacer(1, 8))

    steps2_vi = [
        (1, f"<b>a</b> {ASSIGN} <b>0</b><sub>|<i>V</i>|</sub> &nbsp;&nbsp;&nbsp;&nbsp;<font color=\"#64748b\"><i>// Khởi tạo vector trọng số neo ngành hàng từ vựng V</i></font>"),
        (2, f"<b>duyệt từng</b> sự kiện <i>e</i> = (<i>i<sub>e</sub></i>, &tau;<sub><i>e</i></sub>, <i>t<sub>e</sub></i>) {IN} <i>E<sub>u</sub></i> (mới nhất đến cũ nhất, tối đa 50) <b>thực hiện</b>:"),
        (3, f"&nbsp;&nbsp;&nbsp;&nbsp; {DELTA}<i>t</i> {ASSIGN} (<i>t</i><sub>hiện_tại</sub> - <i>t<sub>e</sub></i>) tính theo ngày"),
        (4, f"&nbsp;&nbsp;&nbsp;&nbsp; <i>w</i>(<i>e</i>) {ASSIGN} &omega;(&tau;<sub><i>e</i></sub>) {TIMES} 2<sup>-{DELTA}<i>t</i> / <i>t</i><sub>1/2</sub></sup> &nbsp;&nbsp;&nbsp;&nbsp;<font color=\"#64748b\"><i>// Phân rã bán rã hàm mũ t<sub>1/2</sub> = 3.0 ngày</i></font>"),
        (5, f"&nbsp;&nbsp;&nbsp;&nbsp; <b>a</b>[ngành_hàng(<i>i<sub>e</sub></i>)] {ASSIGN} <b>a</b>[ngành_hàng(<i>i<sub>e</sub></i>)] + <i>w</i>(<i>e</i>)"),
        (6, f"<b>kết thúc duyệt</b>"),
        (7, f"<i>B</i> {ASSIGN} {{<i>i<sub>e</sub></i> | &tau;<sub><i>e</i></sub> = ĐÃ_MUA {OR} (&tau;<sub><i>e</i></sub> = ĐÁNH_GIÁ {AND} điểm(<i>e</i>) {LE} 2)}} &nbsp;&nbsp;&nbsp;&nbsp;<font color=\"#64748b\"><i>// Tập loại trừ bắt buộc</i></font>"),
        (8, f"<i>C</i><sub>khả_dĩ</sub> {ASSIGN} {{(<i>i</i>, <i>p&#770;</i>(<i>u</i>, <i>i</i>)) {IN} <i>C<sub>u</sub></i> | <i>i</i> {NOTIN} <i>B</i>}}"),
        (9, f"<b>duyệt từng</b> ứng viên (<i>i</i>, <i>p&#770;</i>) {IN} <i>C</i><sub>khả_dĩ</sub> <b>thực hiện</b>:"),
        (10, f"&nbsp;&nbsp;&nbsp;&nbsp; boost(<i>i</i>) {ASSIGN} {SUM}<sub><i>c</i> {IN} danh_mục</sub> <b>a</b>[<i>c</i>] {DOT} ĐộTươngĐồng(ngành_hàng(<i>i</i>), <i>c</i>)"),
        (11, f"&nbsp;&nbsp;&nbsp;&nbsp; <i>s</i><sub>cuối</sub>(<i>i</i>) {ASSIGN} <i>p&#770;</i> {TIMES} (1.0 + max(0.0, boost(<i>i</i>)))"),
        (12, f"<b>kết thúc duyệt</b>"),
        (13, f"<i>S</i> {ASSIGN} SắpXếpGiảmDần(<i>C</i><sub>khả_dĩ</sub>, khóa = <i>s</i><sub>cuối</sub>)"),
        (14, f"<i>R<sub>u</sub></i> {ASSIGN} [ ], &nbsp;&nbsp; <i>G</i><sub>đã_chọn</sub> {ASSIGN} {EMPTY}"),
        (15, f"<b>duyệt từng</b> (<i>i</i>, <i>s</i>) {IN} <i>S</i> <b>thực hiện</b>:"),
        (16, f"&nbsp;&nbsp;&nbsp;&nbsp; <b>nếu</b> mã_nhóm(<i>i</i>) {NOTIN} <i>G</i><sub>đã_chọn</sub> <b>thì</b>:"),
        (17, f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <i>R<sub>u</sub></i> {ASSIGN} <i>R<sub>u</sub></i> {CONCAT} [<i>i</i>], &nbsp;&nbsp; <i>G</i><sub>đã_chọn</sub> {ASSIGN} <i>G</i><sub>đã_chọn</sub> {UNION} {{mã_nhóm(<i>i</i>)}}"),
        (18, f"&nbsp;&nbsp;&nbsp;&nbsp; <b>nếu</b> |<i>R<sub>u</sub></i>| = <i>K</i> <b>thì</b> <b>ngắt vòng lặp</b>"),
        (19, f"<b>trả về</b> <i>R<sub>u</sub></i> &nbsp;&nbsp;&nbsp;&nbsp;<font color=\"#64748b\"><i>// Danh sách Top-12 tái xếp hạng, tối ưu đa dạng danh mục</i></font>")
    ]
    algo2_vi_flowable = build_arxiv_algorithm(
        "2", "Tái Xếp Hạng Theo Phiên Thời Gian Thực Với Phân Rã Bán Rã Hàm Mũ (Stage 2)",
        f"Khách hàng <i>u</i>, Ứng viên {{(<i>i</i>, <i>p&#770;</i>(<i>u</i>, <i>i</i>))}}, Chuỗi phiên <i>E<sub>u</sub></i>, <i>K</i> = 12",
        f"Danh sách Top-12 tái xếp hạng <i>R<sub>u</sub></i> = [<i>i</i><sub>1</sub>, ..., <i>i<sub>K</sub></i>]",
        steps2_vi
    )
    story.append(algo2_vi_flowable)
    story.append(create_caption("Thuật toán 2.2: Tái Xếp Hạng Phiên Thời Gian Thực với Phân Rã Bán Rã", styles))
    story.append(Spacer(1, 8))
    story.append(PageBreak())

    # =========================================================================
    # CHƯƠNG 3: MÔ HÌNH HÓA USE-CASE & ĐẶC TẢ TƯƠNG TÁC
    # =========================================================================
    story.append(PageTracker('ch3'))
    story.append(Paragraph("3  Mô Hình Hóa Trường Hợp Sử Dụng (Use-Case) & Đặc Tả Tương Tác", h1_style))
    story.append(Spacer(1, 4))

    story.append(PageTracker('sec3_1'))
    story.append(Paragraph("3.1  Sơ Đồ Use-Case Tổng Thể & Ranh Giới Quyền Hạn (RBAC)", h2_style))
    story.append(Paragraph(
        "HUB tổ chức phân quyền bảo mật theo mô hình RBAC với 3 vai trò: <code>ROLE_BUYER (1)</code>, <code>ROLE_DATA_SCIENTIST (2)</code>, và <code>ROLE_ADMIN (3)</code>. "
        "Mọi truy xuất API đều được xác thực thông qua mã thông báo JWT Bearer Token.",
        body_style
    ))

    # Bảng RBAC Tiếng Việt
    rbac_data_vi = [
        [Paragraph("Nhóm Quyền Hạn / API Endpoint", table_cell_header), Paragraph("Buyer", table_cell_header), Paragraph("Data Scientist", table_cell_header), Paragraph("Admin", table_cell_header)],
        [Paragraph("Duyệt & Tìm kiếm Sản phẩm (<code>/products</code>)", table_cell), Paragraph("ĐỌC (READ)", table_cell), Paragraph("ĐỌC (READ)", table_cell), Paragraph("TOÀN QUYỀN", table_cell)],
        [Paragraph("Xem Gợi ý Cá nhân hóa (<code>/predict/{id}</code>)", table_cell), Paragraph("CHÍNH CHỦ", table_cell), Paragraph("TẤT CẢ USER", table_cell), Paragraph("TẤT CẢ USER", table_cell)],
        [Paragraph("Giỏ hàng & Đơn hàng (<code>/cart, /orders</code>)", table_cell), Paragraph("CHÍNH CHỦ", table_cell), Paragraph("TỪ CHỐI", table_cell), Paragraph("KIỂM TOÁN", table_cell)],
        [Paragraph("Xem Báo cáo EDA & Trôi dạt (<code>/ai/reports</code>)", table_cell), Paragraph("TỪ CHỐI", table_cell), Paragraph("ĐỌC (READ)", table_cell), Paragraph("ĐỌC (READ)", table_cell)],
        [Paragraph("Kích hoạt Tái huấn luyện (<code>/ai/trigger-training</code>)", table_cell), Paragraph("TỪ CHỐI", table_cell), Paragraph("THỰC THI", table_cell), Paragraph("THỰC THI", table_cell)],
        [Paragraph("Phân quyền Người dùng (<code>/auth/{user}/role</code>)", table_cell), Paragraph("TỪ CHỐI", table_cell), Paragraph("TỪ CHỐI", table_cell), Paragraph("CHỈ ADMIN", table_cell)],
    ]
    rbac_table_vi = Table(rbac_data_vi, colWidths=[180, 80, 100, 110])
    rbac_table_vi.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a8a')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('ALIGN', (1,1), (-1,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 3.5), ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
    ]))
    story.append(rbac_table_vi)
    story.append(create_caption("Bảng 3.1: Ma trận Phân quyền Truy cập Theo Vai trò (Role-Based Access Control)", styles))

    story.append(Spacer(1, 6))

    # Nhúng Sơ đồ Use-Case Excalidraw Tiếng Việt
    story.append(create_image_flowable("excalidraw_02_usecase_diagram_vi.png", max_w=5.8*inch, max_h=3.5*inch))
    story.append(create_caption("Hình 3.0: Sơ Đồ Trường Hợp Sử Dụng (Use-Case Diagram) Tổng Thể Hệ Thống", styles))
    story.append(Spacer(1, 6))

    story.append(PageTracker('sec3_2'))
    story.append(Paragraph("3.2  Bảng Đặc Tả Chi Tiết 8 Use-Case (UC-01 đến UC-08)", h2_style))

    def make_uc_table_vi(uc_id, name, actor, pre_c, post_c, main_flow, alt_flow):
        content = [
            [Paragraph(f"<b>Mã Use-Case:</b> {uc_id}", table_cell_bold), Paragraph(f"<b>Tên Use-Case:</b> {name}", table_cell_bold)],
            [Paragraph(f"<b>Tác nhân chính:</b> {actor}", table_cell), Paragraph(f"<b>Tiền điều kiện:</b> {pre_c}", table_cell)],
            [Paragraph(f"<b>Hậu điều kiện:</b> {post_c}", table_cell), ""],
            [Paragraph(f"<b>Luồng sự kiện chính:</b><br/>{main_flow}", table_cell), ""],
            [Paragraph(f"<b>Luồng ngoại lệ / rẽ nhánh:</b><br/>{alt_flow}", table_cell), ""],
        ]
        t = Table(content, colWidths=[150, 320])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#94a3b8')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('TOPPADDING', (0,0), (-1,-1), 3.5), ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
            ('SPAN', (0,2), (1,2)), ('SPAN', (0,3), (1,3)), ('SPAN', (0,4), (1,4)),
        ]))
        return t

    story.append(Paragraph("<b>Bảng 3.2: Đặc tả Chi tiết UC-01 & UC-02</b>", h3_style))
    story.append(make_uc_table_vi(
        "UC-01", "Xác thực Người dùng & Phân quyền Điều hướng", "Buyer / Data Scientist / Admin",
        "Người dùng mở giao diện hệ thống; sở hữu tài khoản hoặc đăng ký mới.",
        "Cấp phát JWT Bearer Token lưu vào localStorage; định tuyến đến không gian vai trò.",
        "1. Người dùng nhập tên tài khoản và mật khẩu tại form đăng nhập.<br/>2. Backend kiểm tra mã băm Bcrypt.<br/>3. Sinh Token JWT chứa mã user_id và role_id.<br/>4. Frontend điều hướng: Buyer &rarr; <code>/</code>, Data Scientist &rarr; <code>/data-science</code>, Admin &rarr; <code>/admin</code>.",
        "2a. Sai mật khẩu: Trả về HTTP 401 Unauthorized; hiển thị cảnh báo lỗi.<br/>1b. Tài khoản mới: Người dùng đăng ký tại <code>/auth/register</code>; khởi tạo tài khoản mới."
    ))
    story.append(Spacer(1, 6))

    story.append(make_uc_table_vi(
        "UC-02", "Xem Gợi Ý Thời Trang Cá Nhân Hóa", "Buyer (Khách mua hàng)",
        "Đã đăng nhập vai trò Buyer; dịch vụ gợi ý đang hoạt động.",
        "Hiển thị 12 thẻ mặt hàng trang phục cá nhân hóa tối ưu nhất trên trang chủ.",
        "1. Khách hàng truy cập trang chủ <code>/</code>.<br/>2. Giao diện gửi request <code>GET /predict/{user_id}?k=12</code>.<br/>3. Service nạp các ứng viên đã chấm điểm từ bảng <code>user_recommendations</code>.<br/>4. Bộ Session Re-ranker tính toán tương tác phiên làm việc và sắp xếp lại Top-12.<br/>5. Trả về mảng 12 sản phẩm kèm ảnh và thông số.",
        "3a. Khách hàng mới (Cold Start): Backend tự động truy vấn <code>GET /products/best-sellers</code> trả về 12 sản phẩm bán chạy nhất toàn quốc."
    ))

    story.append(PageBreak())

    story.append(Paragraph("<b>Bảng 3.3: Đặc tả Chi tiết UC-05 & UC-07 (Dành Cho Data Scientist)</b>", h3_style))
    story.append(make_uc_table_vi(
        "UC-05", "Khám Phá Dữ Liệu & Giám Sát Phân Phối (EDA)", "Data Scientist",
        "Đăng nhập với vai trò Data Scientist hợp lệ.",
        "Hiển thị bảng điều khiển 10 biểu đồ trực quan hóa dữ liệu thực tế.",
        "1. Data Scientist mở trang <code>/data-science</code>.<br/>2. Frontend gọi <code>GET /ai/reports/eda</code> và <code>GET /ai/insights</code>.<br/>3. Hệ thống render biểu đồ giao dịch theo ngày, phân phối giá và cơ cấu độ tuổi.<br/>4. Hiển thị phân tích tự động về các nhóm ngành hàng tăng trưởng mạnh.",
        "2a. Thiếu hiện vật dữ liệu: Hệ thống thông báo rỗng và hướng dẫn kích hoạt tiền xử lý."
    ))
    story.append(Spacer(1, 6))

    story.append(make_uc_table_vi(
        "UC-07", "Kích Hoạt Tái Huấn Luyện & Tối Ưu Siêu Tham Số", "Data Scientist",
        "Quyền Data Scientist được xác nhận; tệp dữ liệu huấn luyện sẵn sàng.",
        "Khởi tạo worker luồng ngầm thực thi; cập nhật tệp mô hình mới.",
        "1. Data Scientist truy cập <code>/data-science/schedule</code>.<br/>2. Cấu hình số cây <code>n_estimators=200</code>, độ sâu <code>max_depth=12</code>.<br/>3. Nhấn nút 'Huấn luyện ngay' (Trigger Training).<br/>4. Frontend gửi <code>PUT /ai/training/config</code> và <code>POST /ai/trigger-training</code>.<br/>5. Backend chiếm khóa threading lock, sinh worker ngầm <code>hm-{run_id}</code>.<br/>6. Giao diện tự động thăm dò <code>GET /ai/training/status</code> mỗi 5s để cập nhật tiến trình.",
        "5a. Trùng lặp tiến trình (đang có đợt huấn luyện khác): Server trả về HTTP 409 Conflict."
    ))

    story.append(Spacer(1, 8))
    story.append(PageTracker('sec3_3'))
    story.append(Paragraph("3.3  Sơ Đồ Tuần Tự (Sequence Diagrams) Tương Tác Thời Gian Thực", h2_style))
    story.append(Paragraph(
        "Quá trình tương tác nhận gợi ý và tái xếp hạng tức thì theo phiên của khách hàng diễn ra dưới 50ms:",
        body_style
    ))

    # Nhúng Sơ đồ Sequence Excalidraw Tiếng Việt
    story.append(Spacer(1, 4))
    story.append(create_image_flowable("excalidraw_04_session_rerank_sequence_vi.png", max_w=6.0*inch, max_h=3.4*inch))
    story.append(create_caption("Hình 3.1: Sơ Đồ Tuần Tự Tái Xếp Hạng Phiên Theo Thời Gian Thực (Bản Tiếng Việt Excalidraw)", styles))
    story.append(Spacer(1, 6))

    story.append(PageBreak())

    # =========================================================================
    # CHƯƠNG 4: KIẾN TRÚC HỆ THỐNG & CƠ SỞ DỮ LIỆU
    # =========================================================================
    story.append(PageTracker('ch4'))
    story.append(Paragraph("4  Kiến Trúc Hệ Thống & Thiết Kế Cơ Sở Dữ Liệu", h1_style))
    story.append(Spacer(1, 4))

    story.append(PageTracker('sec4_1'))
    story.append(Paragraph("4.1  Kiến Trúc 4 Tầng Module (Enterprise 4-Tier Architecture)", h2_style))
    story.append(Paragraph(
        "Hệ thống HUB được cấu trúc theo 4 tầng module phân tách rành mạch:",
        body_style
    ))

    # Nhúng Sơ đồ Architecture Excalidraw Tiếng Việt
    story.append(Spacer(1, 4))
    story.append(create_image_flowable("excalidraw_01_architecture_4tier_vi.png", max_w=6.2*inch, max_h=3.5*inch))
    story.append(create_caption("Hình 4.1: Kiến Trúc Phân Tầng Module 4 Lớp của Hệ Thống HUB (Bản Tiếng Việt Excalidraw)", styles))
    story.append(Spacer(1, 6))

    story.append(PageTracker('sec4_2'))
    story.append(Paragraph("4.2  Từ Điển Dữ Liệu Quan Hệ 23 Thuộc Tính & Lược Đồ CSDL 3NF", h2_style))

    dict_data_vi = [
        [Paragraph("Tên Bảng", table_cell_header), Paragraph("Tên Thuộc Tính", table_cell_header), Paragraph("Kiểu Dữ Liệu", table_cell_header), Paragraph("Ràng Buộc", table_cell_header), Paragraph("Ý Nghĩa Nghiệp Vụ Chuyên Môn", table_cell_header)],
        [Paragraph("<code>users</code>", table_cell), Paragraph("<code>id</code>", table_cell_bold), Paragraph("VARCHAR(36)", table_cell), Paragraph("PK, UUID", table_cell), Paragraph("Mã định danh duy nhất của người dùng.", table_cell)],
        [Paragraph("<code>users</code>", table_cell), Paragraph("<code>username</code>", table_cell_bold), Paragraph("VARCHAR(50)", table_cell), Paragraph("UNIQUE, NOT NULL", table_cell), Paragraph("Tên tài khoản dùng để đăng nhập hệ thống.", table_cell)],
        [Paragraph("<code>users</code>", table_cell), Paragraph("<code>role_id</code>", table_cell_bold), Paragraph("INTEGER", table_cell), Paragraph("NOT NULL", table_cell), Paragraph("Vai trò: 1 (Buyer), 2 (Data Scientist), 3 (Admin).", table_cell)],
        [Paragraph("<code>products</code>", table_cell), Paragraph("<code>article_id</code>", table_cell_bold), Paragraph("VARCHAR(10)", table_cell), Paragraph("PK, H&M ID", table_cell), Paragraph("Mã sản phẩm 10 chữ số chuẩn Kaggle H&M.", table_cell)],
        [Paragraph("<code>products</code>", table_cell), Paragraph("<code>prod_name</code>", table_cell_bold), Paragraph("VARCHAR(255)", table_cell), Paragraph("NOT NULL", table_cell), Paragraph("Tên thương mại chi tiết của trang phục.", table_cell)],
        [Paragraph("<code>products</code>", table_cell), Paragraph("<code>product_type_name</code>", table_cell_bold), Paragraph("VARCHAR(100)", table_cell), Paragraph("INDEXED", table_cell), Paragraph("Loại trang phục (Trousers, Dress, Sweater...).", table_cell)],
        [Paragraph("<code>products</code>", table_cell), Paragraph("<code>price</code>", table_cell_bold), Paragraph("FLOAT", table_cell), Paragraph("NOT NULL", table_cell), Paragraph("Giá bán chuẩn hóa theo đơn vị benchmark.", table_cell)],
        [Paragraph("<code>orders</code>", table_cell), Paragraph("<code>id</code>", table_cell_bold), Paragraph("VARCHAR(36)", table_cell), Paragraph("PK, UUID", table_cell), Paragraph("Mã định danh duy nhất của đơn đặt hàng.", table_cell)],
        [Paragraph("<code>orders</code>", table_cell), Paragraph("<code>user_id</code>", table_cell_bold), Paragraph("VARCHAR(36)", table_cell), Paragraph("FK &rarr; users.id", table_cell), Paragraph("Khách hàng thực hiện đơn hàng mua sắm.", table_cell)],
        [Paragraph("<code>orders</code>", table_cell), Paragraph("<code>order_date</code>", table_cell_bold), Paragraph("DATETIME", table_cell), Paragraph("NOT NULL", table_cell), Paragraph("Thời điểm giao dịch thanh toán thành công.", table_cell)],
        [Paragraph("<code>user_recommendations</code>", table_cell), Paragraph("<code>user_id</code>", table_cell_bold), Paragraph("VARCHAR(36)", table_cell), Paragraph("FK, COMPOSITE PK", table_cell), Paragraph("Mã khách hàng nhận danh sách đề xuất.", table_cell)],
        [Paragraph("<code>user_recommendations</code>", table_cell), Paragraph("<code>article_id</code>", table_cell_bold), Paragraph("VARCHAR(10)", table_cell), Paragraph("FK, COMPOSITE PK", table_cell), Paragraph("Mã sản phẩm được mô hình đề xuất.", table_cell)],
        [Paragraph("<code>user_recommendations</code>", table_cell), Paragraph("<code>score</code>", table_cell_bold), Paragraph("FLOAT", table_cell), Paragraph("NOT NULL", table_cell), Paragraph("Xác suất mua dự báo P(y=1 | x) bởi Random Forest.", table_cell)],
        [Paragraph("<code>user_recommendations</code>", table_cell), Paragraph("<code>rank</code>", table_cell_bold), Paragraph("INTEGER", table_cell), Paragraph("1 .. 12", table_cell), Paragraph("Thứ hạng ưu tiên trong danh sách Top-12.", table_cell)],
    ]
    dict_table_vi = Table(dict_data_vi, colWidths=[90, 85, 75, 80, 140])
    dict_table_vi.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a8a')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 2.5), ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(dict_table_vi)
    story.append(create_caption("Bảng 4.1: Từ Điển Dữ Liệu Quan Hệ 23 Thuộc Tính Chuẩn 3NF", styles))

    story.append(PageTracker('sec4_3'))
    story.append(Paragraph("4.3  Danh Mục 22 RESTful API & Bộ Kiểm Thử Tự Động (27 Tests QA)", h2_style))
    story.append(Paragraph(
        "Hệ thống cung cấp 22 API endpoints đạt chuẩn OpenAPI và được kiểm định toàn diện bởi bộ kiểm thử tự động <code>pytest</code> gồm 27 ca kiểm thử (17 test API và 10 test ML Pipeline). "
        "Toàn bộ 27/27 test đều vượt qua 100% trong 6.01 giây, chứng minh hệ thống vận hành ổn định và không phát sinh lỗi biên.",
        body_style
    ))

    story.append(PageBreak())

    # =========================================================================
    # CHƯƠNG 5: PHÂN TÍCH KHÁM PHÁ DỮ LIỆU & CHỐNG RÒ RỈ
    # =========================================================================
    story.append(PageTracker('ch5'))
    story.append(Paragraph("5  Phân Tích Khám Phá Dữ Liệu (EDA) & Chống Rò Rỉ Dữ Liệu", h1_style))
    story.append(Spacer(1, 4))

    story.append(PageTracker('sec5_1'))
    story.append(Paragraph("5.1  Bộ Dữ Liệu Thực Tế H&M Kaggle (31.78M Giao Dịch Thật)", h2_style))
    story.append(Paragraph(
        "Hệ thống khai thác bộ dữ liệu chuẩn quốc tế <b>H&M Personalized Fashion Recommendations</b> (Kaggle Competition Benchmark) gồm 31.788.324 giao dịch thực tế, 105.542 mặt hàng và 1.371.980 hồ sơ khách hàng. "
        "<b>Cam kết học thuật: Tuyệt đối không sử dụng dữ liệu giả lập (Zero Simulated Data)</b>.",
        body_style
    ))

    story.append(PageTracker('fig5_1'))
    story.append(Paragraph("5.2  Bộ 10 Biểu Đồ Phân Tích Kinh Doanh & Chẩn Đoán Machine Learning", h2_style))

    # Biểu đồ EDA 1: Doanh số theo thời gian
    story.append(create_image_flowable("3_1_1_transactions_per_day.png", max_w=5.8*inch, max_h=2.2*inch))
    story.append(create_caption("Hình 5.1: Doanh Số Giao Dịch Hàng Ngày Trên Dữ Liệu Lịch Sử Kaggle H&M (Nhận Diện Xu Hướng Mùa Vụ)", styles))
    story.append(Spacer(1, 6))

    # Cặp biểu đồ EDA 2 & 3: Giá bán & Độ tuổi
    img_price = create_image_flowable("3_1_2_price_distribution.png", max_w=2.8*inch, max_h=1.8*inch)
    img_age = create_image_flowable("3_1_4_customer_age.png", max_w=2.8*inch, max_h=1.8*inch)
    grid_eda1 = Table([
        [img_price, img_age],
        [Paragraph("<b>Hình 5.2a: Phân Bố Giá Bán Chuẩn Hóa</b>", caption_style), Paragraph("<b>Hình 5.2b: Cơ Cấu Độ Tuổi Khách Hàng</b>", caption_style)]
    ], colWidths=[235, 235])
    grid_eda1.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER')]))
    story.append(grid_eda1)
    story.append(Spacer(1, 6))

    # Cặp biểu đồ EDA 4 & 5: Nhóm ngành hàng & Doanh số chỉ mục
    img_groups = create_image_flowable("3_1_3_product_group_counts.png", max_w=2.8*inch, max_h=1.8*inch)
    img_index = create_image_flowable("3_1_5_index_group_sales.png", max_w=2.8*inch, max_h=1.8*inch)
    grid_eda2 = Table([
        [img_groups, img_index],
        [Paragraph("<b>Hình 5.3a: Tần Suất 15 Nhóm Ngành Hàng</b>", caption_style), Paragraph("<b>Hình 5.3b: Doanh Số Theo Nhóm Chỉ Mục</b>", caption_style)]
    ], colWidths=[235, 235])
    grid_eda2.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER')]))
    story.append(grid_eda2)

    story.append(PageBreak())

    # Cặp biểu đồ Chẩn đoán ML 6 & 7: Số lần mua & Phân phối đuôi dài
    story.append(Paragraph("<b>Các Biểu Đồ Chẩn Đoán Machine Learning & Lấy Mẫu:</b>", h3_style))
    img_purchases = create_image_flowable("3_3_2_purchases_per_customer.png", max_w=2.8*inch, max_h=1.8*inch)
    img_longtail = create_image_flowable("3_3_3_article_popularity_longtail.png", max_w=2.8*inch, max_h=1.8*inch)
    grid_diag1 = Table([
        [img_purchases, img_longtail],
        [Paragraph("<b>Hình 5.4a: Phân Bố Lượt Mua/Khách Hàng</b>", caption_style), Paragraph("<b>Hình 5.4b: Đường Cong Đuôi Dài Long-Tail</b>", caption_style)]
    ], colWidths=[235, 235])
    grid_diag1.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER')]))
    story.append(grid_diag1)
    story.append(Spacer(1, 6))

    # Cặp biểu đồ Chẩn đoán ML 8 & 9: Nguồn ứng viên & Cân bằng nhãn 1:5
    img_cand_src = create_image_flowable("3_3_4_candidate_sources.png", max_w=2.8*inch, max_h=1.8*inch)
    img_balance = create_image_flowable("3_3_5_label_balance.png", max_w=2.8*inch, max_h=1.8*inch)
    grid_diag2 = Table([
        [img_cand_src, img_balance],
        [Paragraph("<b>Hình 5.5a: Tỷ Trọng Đóng Góp Nguồn Ứng Viên</b>", caption_style), Paragraph("<b>Hình 5.5b: Tỷ Lệ Cân Bằng Nhãn Âm Dương (1:5)</b>", caption_style)]
    ], colWidths=[235, 235])
    grid_diag2.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER')]))
    story.append(grid_diag2)
    story.append(Spacer(1, 6))

    story.append(PageTracker('sec5_2'))
    story.append(Paragraph("5.3  Cơ Chế Chia Tập Cửa Sổ Trượt Thời Gian Chống Rò Rỉ (No Leakage)", h2_style))
    story.append(Paragraph(
        "HUB áp dụng nguyên tắc phân chia cửa sổ trượt thời gian tuyệt đối (Temporal Rolling Split): "
        "Tập Huấn Luyện (Train) 3 tuần, Tập Đánh Giá (Validation) 1 tuần, và Tập Kiểm Thử (Test) 1 tuần. "
        "Mọi đặc trưng của khách hàng và sản phẩm chỉ được tính toán trên mốc quá khứ <i>t_dat < t_split</i>, tuyệt đối không lấy bất kỳ thông tin nào trong tuần tương lai để tạo đặc trưng, loại trừ hoàn toàn nguy cơ rò rỉ dữ liệu (Data Leakage).",
        body_style
    ))

    story.append(PageTracker('sec5_3'))
    story.append(Paragraph("5.4  Rút Trích Ứng Viên Sơ Tuyển & Kỹ Nghệ 14 Đặc Trưng Học Máy", h2_style))
    story.append(Paragraph(
        "Giai đoạn 1 kết hợp 3 kênh Heuristic: Bestseller toàn quốc (12 món), Lịch sử mua lặp lại (Repurchase), và Đồ thị đồng mua (Co-purchase) đạt độ bao phủ Recall@12 = 9.43%. "
        "Sau đó, tập dữ liệu được bổ sung mẫu âm theo tỷ lệ 1:5 tạo nên tập mẫu huấn luyện 398.166 dòng sạch. "
        "Mỗi cặp khách hàng - sản phẩm được trích xuất 14 đặc trưng kỹ nghệ phản ánh độ tuổi, tình trạng hội viên, giá bán, tốc độ bán và hệ số phân rã thời gian tương tác (&lambda; = 0.05).",
        body_style
    ))

    story.append(PageBreak())

    # =========================================================================
    # CHƯƠNG 6: HUẤN LUYỆN, ĐÁNH GIÁ THỰC NGHIỆM & PHÂN TÍCH LỖI
    # =========================================================================
    story.append(PageTracker('ch6'))
    story.append(Paragraph("6  Huấn Luyện Mô Hình, Đánh Giá Thực Nghiệm & Phân Tích Lát Cắt Lỗi", h1_style))
    story.append(Spacer(1, 4))

    story.append(PageTracker('sec6_1'))
    story.append(Paragraph("6.1  Thiết Lập Huấn Luyện & Tối Ưu Siêu Tham Số Cây Quyết Định", h2_style))
    story.append(Paragraph(
        "Mô hình Random Forest được cấu hình tối ưu: <i>B = 200</i> cây quyết định, <code>max_depth = 12</code> nhằm khống chế quá khớp, <code>min_samples_split = 20</code> và <code>class_weight = 'balanced'</code>.",
        body_style
    ))

    story.append(PageTracker('sec6_2'))
    story.append(Paragraph("6.2  Độ Đo MAP@12 Chuẩn Kaggle & Kết Quả Vượt Trội So Với Baselines", h2_style))
    story.append(Paragraph(
        "Chỉ số đánh giá chính thức là <b>Mean Average Precision at 12 (MAP@12)</b> theo chuẩn cuộc thi Kaggle H&M:",
        body_style
    ))
    story.append(Paragraph("<b>Công thức 6.1:</b> &nbsp;&nbsp; <i>AP@12(u) = (1 / min(|Y<sub>u</sub>|, 12)) &Sigma;<sub>k=1</sub><sup>12</sup> P<sub>u</sub>(k) &times; rel<sub>u</sub>(k), &nbsp;&nbsp;&nbsp; MAP@12 = (1 / |U|) &Sigma;<sub>u=1</sub><sup>|U|</sup> AP@12(u)</i>", eq_style))

    eval_data_vi = [
        [Paragraph("Mô Hình / Phương Pháp Đánh Giá", table_cell_header), Paragraph("MAP@12", table_cell_header), Paragraph("Precision@12", table_cell_header), Paragraph("Recall@12", table_cell_header), Paragraph("Tỷ Lệ Tăng Trưởng Vượt Trội", table_cell_header)],
        [Paragraph("<b>Baseline 1: Bestseller Toàn Quốc (Global BL1)</b>", table_cell), Paragraph("0.00660", table_cell), Paragraph("0.0124", table_cell), Paragraph("0.0210", table_cell), Paragraph("Mốc đối chuẩn cơ sở", table_cell)],
        [Paragraph("<b>Baseline 2: Mua Lặp Lại Cá Nhân (Repurchase BL2)</b>", table_cell), Paragraph("0.02498", table_cell), Paragraph("0.0385", table_cell), Paragraph("0.0612", table_cell), Paragraph("+278.5% so với BL1", table_cell)],
        [Paragraph("<b>HUB: Random Forest Ranker (Mô hình Đề tài)</b>", table_cell_bold), Paragraph("<b>0.03014</b>", table_cell_bold), Paragraph("<b>0.0461</b>", table_cell_bold), Paragraph("<b>0.0943</b>", table_cell_bold), Paragraph("<b>+356.6% so với BL1<br/>+20.6% so với BL2</b>", table_cell_bold)],
    ]
    eval_table_vi = Table(eval_data_vi, colWidths=[150, 65, 75, 65, 115])
    eval_table_vi.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a8a')),
        ('BACKGROUND', (0,3), (-1,3), colors.HexColor('#f0fdf4')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('ALIGN', (1,1), (-1,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 4), ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(eval_table_vi)
    story.append(create_caption("Bảng 6.1: Kết Quả Thực Nghiệm So Sánh Hiệu Năng MAP@12 Giữa HUB và Các Baselines", styles))

    story.append(PageTracker('sec6_3'))
    story.append(Paragraph("6.3  Phân Tích Lát Cắt Lỗi (Active vs Inactive & Nhóm Ngành Hàng)", h2_style))
    story.append(Paragraph(
        "Phân tích lát cắt lỗi cho thấy sự phân hóa rõ nét: Nhóm khách hàng tích cực (&ge; 5 giao dịch quá khứ) đạt <b>MAP@12 = 0.04820</b>, "
        "trong khi nhóm khách vãng lai (Cold Start) đạt <b>MAP@12 = 0.00810</b>. Hệ thống xử lý xuất sắc nhóm khách vãng lai bằng cơ chế fallback sang sản phẩm thịnh hành theo độ tuổi, không làm gián đoạn trải nghiệm.",
        body_style
    ))

    story.append(PageTracker('sec6_4'))
    story.append(Paragraph("6.4  Cơ Chế Tái Xếp Hạng Bán Rã & Khống Chế Ngập Lụt Danh Mục", h2_style))
    story.append(Paragraph(
        "Nhằm tránh hiện tượng 'bong bóng bộ lọc' (Filter Bubble) và gợi ý toàn các sản phẩm trùng lặp, HUB tích hợp cơ chế phân rã bán rã thời gian với chu kỳ bán rã <i>t<sub>1/2</sub> = 3.0</i> ngày. "
        "Đồng thời, hệ thống áp đặt quy tắc khống chế nghiêm ngặt: <b>MAX_PER_CODE = 1</b>, đảm bảo trong danh sách Top-12 không bao giờ xuất hiện hai sản phẩm có cùng phân loại trang phục.",
        body_style
    ))

    story.append(PageBreak())

    # =========================================================================
    # CHƯƠNG 7: MINH HỌA GIAO DIỆN NGƯỜI DÙNG & TRIỂN KHAI THỰC TẾ
    # =========================================================================
    story.append(PageTracker('ch7'))
    story.append(Paragraph("7  Minh Họa Giao Diện Người Dùng & Triển Khai Hệ Thống Thực Tế", h1_style))
    story.append(Spacer(1, 4))

    story.append(PageTracker('sec7_1'))
    story.append(Paragraph("7.1  Không Gian Khách Hàng (Buyer Portal & Trang Chi Tiết Sản Phẩm)", h2_style))

    story.append(PageTracker('fig7_1'))
    story.append(create_image_flowable("00_login_page.png", max_w=5.4*inch, max_h=2.4*inch))
    story.append(create_caption("Hình 7.1: Giao Diện Đăng Nhập Đa Vai Trò Phân Quyền Bảo Mật (LoginPage)", styles))
    story.append(Spacer(1, 6))

    story.append(PageTracker('fig7_2'))
    story.append(create_image_flowable("05_buyer_homepage_recommendations.png", max_w=5.4*inch, max_h=2.8*inch))
    story.append(create_caption("Hình 7.2: Trang Chủ Gợi Ý Cá Nhân Hóa Dành Cho Khách Hàng (HomePage - Top 12 Recommendations)", styles))

    story.append(PageBreak())

    story.append(PageTracker('fig7_3'))
    story.append(create_image_flowable("06_buyer_product_detail.png", max_w=5.4*inch, max_h=2.6*inch))
    story.append(create_caption("Hình 7.3: Trang Chi Tiết Sản Phẩm & Gợi Ý Phối Đồ Liên Quan (ProductDetailPage - Cross-Selling)", styles))
    story.append(Spacer(1, 6))

    story.append(PageTracker('sec7_2'))
    story.append(Paragraph("7.2  Không Gian Data Scientist (Bảng Điều Khiển EDA, Metrics & Retrain)", h2_style))

    story.append(PageTracker('fig7_4'))
    story.append(create_image_flowable("01_ds_eda_page.png", max_w=5.4*inch, max_h=3.0*inch))
    story.append(create_caption("Hình 7.4: Bảng Điều Khiển Khám Phá Dữ Liệu & Giám Sát Phân Phối Dành Cho Data Scientist (DataSciencePage)", styles))

    story.append(PageBreak())

    story.append(PageTracker('fig7_5'))
    story.append(create_image_flowable("02_ds_model_metrics.png", max_w=5.4*inch, max_h=2.7*inch))
    story.append(create_caption("Hình 7.5: Bảng Đánh Giá Độ Đo Hiệu Năng Mô Hình & So Sánh Baselines (ModelMetricsPage)", styles))
    story.append(Spacer(1, 6))

    story.append(PageTracker('fig7_6'))
    story.append(create_image_flowable("03_ds_error_analysis.png", max_w=5.4*inch, max_h=2.7*inch))
    story.append(create_caption("Hình 7.6: Ma Trận Phân Tích Lát Cắt Lỗi Theo Hoạt Động & Ngành Hàng (ErrorAnalysisPage)", styles))

    story.append(PageBreak())

    story.append(PageTracker('fig7_7'))
    story.append(create_image_flowable("04_ds_training_schedule.png", max_w=5.4*inch, max_h=2.8*inch))
    story.append(create_caption("Hình 7.7: Bảng Quản Trị Lịch Trình Tái Huấn Luyện & Tối Ưu Siêu Tham Số (TrainingSchedulePage)", styles))
    story.append(Spacer(1, 6))

    story.append(PageTracker('sec7_3'))
    story.append(Paragraph("7.3  Không Gian Quản Trị Viên (Admin Operations Dashboard)", h2_style))

    story.append(PageTracker('fig7_8'))
    story.append(create_image_flowable("07_admin_dashboard.png", max_w=5.4*inch, max_h=2.8*inch))
    story.append(create_caption("Hình 7.8: Bảng Điều Khiển Vận Hành Cửa Hàng & Doanh Thu Thương Mại (AdminDashboardPage)", styles))

    story.append(PageBreak())

    # =========================================================================
    # CHƯƠNG 8: KẾT LUẬN, ĐÓNG GÓP & TUYÊN BỐ GENAI
    # =========================================================================
    story.append(PageTracker('ch8'))
    story.append(Paragraph("8  Kết Luận, Đóng Góp Nhóm & Tuyên Bố Trí Tuệ Nhân Tạo", h1_style))
    story.append(Spacer(1, 4))

    story.append(PageTracker('sec8_1'))
    story.append(Paragraph("8.1  Tổng Kết Đóng Góp & Giá Trị Thực Tiễn Của Hệ Thống", h2_style))
    story.append(Paragraph(
        "Đề tài đã hoàn thành xuất sắc các mục tiêu đề ra: Xây dựng thành công hệ thống gợi ý thời trang cá nhân hóa HUB vận hành thực tế (không chỉ dừng lại ở Jupyter Notebook), "
        "đạt hiệu năng vượt trội với chỉ số <b>MAP@12 = 0.03014</b> (+356.6% so với Bestseller toàn quốc), cam kết độ trễ suy luận đầu cuối P95 < 50ms và bảo đảm tính trung thực học thuật 100%.",
        body_style
    ))

    story.append(PageTracker('sec8_2'))
    story.append(Paragraph("8.2  Bảng Phân Công Công Việc & Tỷ Lệ Đóng Góp Nhóm (50% - 50%)", h2_style))

    contrib_data_vi = [
        [Paragraph("Thành Viên", table_cell_header), Paragraph("Vai Trò", table_cell_header), Paragraph("Chi Tiết Các Nhiệm Vụ Phụ Trách Cụ Thể", table_cell_header), Paragraph("Tỷ Lệ Đóng Góp", table_cell_header)],
        [
            Paragraph("<b>Đào Duy Đạt</b>", table_cell_bold),
            Paragraph("Trưởng nhóm", table_cell),
            Paragraph(
                "• Thiết kế kiến trúc 4 tầng hệ thống & lược đồ CSDL quan hệ 3NF.<br/>"
                "• Cài đặt thuật toán Random Forest Ranker, Bagging và Session Re-ranking.<br/>"
                "• Hiện thực hóa 22 RESTful API trên FastAPI và Frontend React 18.<br/>"
                "• Viết kịch bản ReportLab biên dịch báo cáo học thuật PDF hai ngôn ngữ.",
                table_cell
            ),
            Paragraph("<b>50%</b>", table_cell_bold)
        ],
        [
            Paragraph("<b>Phan Tiến Huy</b>", table_cell_bold),
            Paragraph("Thành viên", table_cell),
            Paragraph(
                "• Tải, làm sạch và xử lý tập dữ liệu Kaggle H&M 31.78M giao dịch thực tế.<br/>"
                "• Xây dựng quy trình chia tập trượt thời gian chống rò rỉ dữ liệu.<br/>"
                "• Hiện thực bộ kiểm thử tự động 27/27 test với <code>pytest</code>.<br/>"
                "• Thiết kế hệ thống 10 biểu đồ EDA và 4 sơ đồ kiến trúc chuẩn Excalidraw.",
                table_cell
            ),
            Paragraph("<b>50%</b>", table_cell_bold)
        ],
    ]
    contrib_table_vi = Table(contrib_data_vi, colWidths=[90, 75, 235, 70])
    contrib_table_vi.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a8a')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('ALIGN', (3,1), (3,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 4), ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(contrib_table_vi)
    story.append(create_caption("Bảng 8.1: Bảng Phân Công Nhiệm Vụ & Cam Kết Tỷ Lệ Đóng Góp Thành Viên", styles))

    story.append(PageTracker('sec8_3'))
    story.append(Paragraph("8.3  Tuyên Bố Liêm Chính Học Thuật & Sử Dụng GenAI Minh Bạch", h2_style))
    story.append(Paragraph(
        "Nhóm thực hiện cam kết tuân thủ quy định liêm chính học thuật của Trường Đại học Bách Khoa - ĐHQG TP.HCM: "
        "Các công cụ AI (Antigravity Assistant và Codex) chỉ được sử dụng với vai trò trợ lý hỗ trợ rà soát cú pháp mã nguồn, sinh khung boilerplate cho bộ kiểm thử pytest, "
        "và canh chỉnh tọa độ bố cục ReportLab PDF. "
        "Toàn bộ thiết kế kiến trúc hệ thống, lựa chọn thuật toán Rừng ngẫu nhiên, chứng minh toán học giảm phương sai, và giải pháp chống rò rỉ dữ liệu đều do nhóm sinh viên trực tiếp tự chủ thực hiện 100%.",
        body_style
    ))

    story.append(PageTracker('sec8_4'))
    story.append(Paragraph("8.4  Chuẩn Bị Bộ Câu Hỏi - Trả Lời Phản Biện Bảo Vệ Đồ Án", h2_style))
    story.append(Paragraph("• <b>Câu hỏi 1: Tại sao chọn Random Forest thay vì GBDT (XGBoost/LightGBM) hay Deep Learning?</b><br/><i>Trả lời:</i> Random Forest áp dụng Bagging cho phép huấn luyện song song cực nhanh, xử lý tốt ma trận thưa mà không bị overfit, và đặc biệt là độ trễ suy luận (Inference Latency) ở cấp độ mili-giây (< 5ms cho 100 ứng viên), đáp ứng hoàn hảo yêu cầu phi chức năng NFR-01 của web thời gian thực.", bullet_style))
    story.append(Paragraph("• <b>Câu hỏi 2: Làm sao đảm bảo không bị rò rỉ dữ liệu (Data Leakage)?</b><br/><i>Trả lời:</i> Nhóm thiết lập mốc thời gian tuyệt đối <i>t_dat < t_split</i>. Mọi đặc trưng tần suất mua, độ nhạy giá hay sở thích đều chỉ tính trên cửa sổ trượt 8 tuần trước ngày chia tập, tuyệt đối không dùng thông tin trong tuần kiểm thử để tạo đặc trưng.", bullet_style))
    story.append(Paragraph("• <b>Câu hỏi 3: Cơ chế Re-ranking hoạt động như thế nào khi click trong phiên?</b><br/><i>Trả lời:</i> Hệ thống lưu vết click trong session và áp dụng hàm phân rã bán rã <i>w(t) = exp(-ln2 * dt / 3.0)</i> để tăng điểm cho các món cùng loại, đồng thời áp đặt <i>MAX_PER_CODE = 1</i> để tránh việc gợi ý toàn các sản phẩm trùng lặp.", bullet_style))

    story.append(Spacer(1, 10))
    story.append(PageTracker('ref_sec'))
    story.append(Paragraph("Tài Liệu Tham Khảo (Chuẩn IEEE)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cbd5e1'), spaceBefore=2, spaceAfter=6))
    refs = [
        "[1] L. Breiman, \"Random Forests,\" <i>Machine Learning</i>, vol. 45, no. 1, pp. 5–32, 2001.",
        "[2] H&M Group, \"H&M Personalized Fashion Recommendations Dataset,\" Kaggle Competition Benchmark, 2022.",
        "[3] F. Ricci, L. Rokach, and B. Shapira, <i>Recommender Systems Handbook</i>, 3rd ed., Springer, 2022.",
        "[4] P. Covington, J. Adams, and E. Sargin, \"Deep Neural Networks for YouTube Recommendations,\" in <i>Proc. 10th ACM Conf. Recommender Systems (RecSys)</i>, 2016, pp. 191–198.",
        "[5] S. Rendle, C. Freudenthaler, Z. Gantner, and L. Schmidt-Thieme, \"BPR: Bayesian Personalized Ranking from Implicit Feedback,\" in <i>Proc. 25th Conf. Uncertainty in Artificial Intelligence (UAI)</i>, 2009.",
    ]
    for r in refs:
        story.append(Paragraph(r, bullet_style))

    return story

# ---------------------------------------------------------------------------
# Hàm thực thi chính (Main Compilation)
# ---------------------------------------------------------------------------
def generate_pdf_vietnamese():
    pdf_path = r"D:\HTTM\REPORT_INTELLIGENT_SYSTEMS_HUB_VI.pdf"
    
    # PASS 1: Đo lường số trang chính xác của từng Flowable
    print("=== PASS 1 (VI): Ghi nhan so trang thuc te ===")
    PAGE_MAPPING.clear()
    doc_dry = SimpleDocTemplate(
        "dry_run_vi.pdf", pagesize=A4,
        leftMargin=38, rightMargin=38, topMargin=38, bottomMargin=38
    )
    story_pass1 = build_report_story()
    doc_dry.build(story_pass1, canvasmaker=NumberedCanvasVI)
    print(f"Bang phan trang: {PAGE_MAPPING}")
    if os.path.exists("dry_run_vi.pdf"):
        try: os.remove("dry_run_vi.pdf")
        except: pass

    # PASS 2: Biên dịch ấn bản chính thức với Mục Lục đồng bộ 100%
    print("=== PASS 2 (VI): Bien dich an ban tieng Viet chinh thuc ===")
    doc_final = SimpleDocTemplate(
        pdf_path, pagesize=A4,
        leftMargin=38, rightMargin=38, topMargin=38, bottomMargin=38
    )
    story_pass2 = build_report_story()
    doc_final.build(story_pass2, canvasmaker=NumberedCanvasVI)
    print(f"Bien dich thanh cong Bao cao Tieng Viet tai: {pdf_path}")

if __name__ == "__main__":
    generate_pdf_vietnamese()
