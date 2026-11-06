import os
import sys
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, Preformatted, Flowable, Image as RLImage
)
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register TrueType Fonts for Publication-Grade Typography and Math Symbols
pdfmetrics.registerFont(TTFont('Arial', r'C:\Windows\Fonts\arial.ttf'))
pdfmetrics.registerFont(TTFont('Arial-Bold', r'C:\Windows\Fonts\arialbd.ttf'))
pdfmetrics.registerFont(TTFont('Arial-Italic', r'C:\Windows\Fonts\ariali.ttf'))
pdfmetrics.registerFont(TTFont('SegoeUISymbol', r'C:\Windows\Fonts\seguisym.ttf'))

# Publication Math Notation Constants (arXiv/LaTeX grade)
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
# Global Page Tracking for Two-Pass TOC Generation
# ---------------------------------------------------------------------------
PAGE_DICT = {}

class PageTracker(Flowable):
    def __init__(self, key):
        super().__init__()
        self.key = key
        self.width = 0
        self.height = 0

    def draw(self):
        PAGE_DICT[self.key] = self.canv._pageNumber


# ---------------------------------------------------------------------------
# NumberedCanvas for "Page X of Y" and Running Header/Footer
# ---------------------------------------------------------------------------
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, total_pages):
        # We do NOT draw running headers/footers on page 1 (Cover Page)
        if self._pageNumber == 1:
            self.draw_cover_border()
            return

        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor('#475569'))

        # Running Header
        header_text = "HO CHI MINH CITY UNIVERSITY OF TECHNOLOGY - CSE FACULTY | INTELLIGENT SYSTEMS"
        self.drawString(54, 800, header_text)
        self.setStrokeColor(colors.HexColor('#cbd5e1'))
        self.setLineWidth(0.6)
        self.line(54, 794, 541, 794)

        # Running Footer
        page_str = f"Page {self._pageNumber} of {total_pages}"
        self.setFont("Helvetica", 8)
        self.drawString(54, 38, "CO5119 / CO3041 - Large Assignment Report: HUB Recommendation System")
        self.drawRightString(541, 38, page_str)
        self.setStrokeColor(colors.HexColor('#cbd5e1'))
        self.setLineWidth(0.6)
        self.line(54, 48, 541, 48)

        self.restoreState()

    def draw_cover_border(self):
        """Draw formal double-line academic border with corner squares for Cover Page."""
        self.saveState()
        # Outer heavy border (Navy)
        self.setStrokeColor(colors.HexColor('#1e3a8a'))
        self.setLineWidth(3.0)
        self.rect(36, 36, 523, 770)

        # Inner thin border
        self.setStrokeColor(colors.HexColor('#1e3a8a'))
        self.setLineWidth(0.8)
        self.rect(42, 42, 511, 758)

        # Corner decorative squares
        self.setFillColor(colors.HexColor('#1e3a8a'))
        for x, y in [(38, 38), (38, 796), (549, 38), (549, 796)]:
            self.rect(x - 3, y - 3, 6, 6, fill=1, stroke=0)

        self.restoreState()


# ---------------------------------------------------------------------------
# Helper Functions for Image Embedding and Sizing
# ---------------------------------------------------------------------------
ASSETS_DIR = Path(r"D:\HTTM\docs\report_assets")

def create_image_flowable(image_name, max_w=6.2*inch, max_h=3.6*inch):
    img_path = ASSETS_DIR / image_name
    if not img_path.exists():
        return Paragraph(f"<i>[Image not found: {image_name}]</i>", ParagraphStyle('MissingImg', fontName='Helvetica-Oblique', fontSize=9, textColor=colors.red))
    
    from reportlab.platypus import Image as RLImg
    temp_img = RLImg(str(img_path))
    w = temp_img.imageWidth
    h = temp_img.imageHeight
    if w <= 0 or h <= 0:
        return Spacer(1, 10)
    
    scale = min(max_w / w, max_h / h)
    return RLImg(str(img_path), width=w * scale, height=h * scale)

def create_caption(text, styles):
    return Paragraph(f"<b>{text}</b>", styles['FigureCaption'])

def build_arxiv_algorithm(algo_id, title, inputs, outputs, steps, font_family='Arial', width=490):
    algo_header_style = ParagraphStyle(
        f'ArxivAlgoHeader_{algo_id}',
        fontName=f'{font_family}-Bold', fontSize=8.5, leading=11,
        textColor=colors.HexColor('#0f172a')
    )
    algo_io_style = ParagraphStyle(
        f'ArxivAlgoIO_{algo_id}',
        fontName=font_family, fontSize=7.3, leading=10,
        textColor=colors.HexColor('#1e293b')
    )
    algo_num_style = ParagraphStyle(
        f'ArxivAlgoNum_{algo_id}',
        fontName=font_family, fontSize=7.2, leading=9.6,
        alignment=2, textColor=colors.HexColor('#64748b')
    )
    algo_code_style = ParagraphStyle(
        f'ArxivAlgoCode_{algo_id}',
        fontName=font_family, fontSize=7.2, leading=9.6,
        textColor=colors.HexColor('#0f172a')
    )
    
    rows = []
    rows.append([Paragraph(f"<b>Algorithm {algo_id}:</b> {title}", algo_header_style), ""])
    rows.append([Paragraph(f"<b>Input:</b> {inputs}", algo_io_style), ""])
    rows.append([Paragraph(f"<b>Output:</b> {outputs}", algo_io_style), ""])
    
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

def build_arxiv_equation(eq_num, formula_html, font_family='Arial', accent_color='#2563eb', width=490):
    safe_id = str(eq_num).replace('.', '_')
    eq_math_style = ParagraphStyle(
        f'ArxivEqMath_{safe_id}',
        fontName=font_family, fontSize=8.5, leading=12,
        alignment=1, textColor=colors.HexColor('#0f172a')
    )
    eq_num_style = ParagraphStyle(
        f'ArxivEqNum_{safe_id}',
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
# Report Generator Function
# ---------------------------------------------------------------------------
def build_story(page_dict=None):
    if page_dict is None:
        page_dict = {}

    styles = getSampleStyleSheet()

    # Custom Typography Palette
    title_style = ParagraphStyle(
        'CoverTitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=18, leading=23,
        alignment=1, textColor=colors.HexColor('#0f172a'), spaceAfter=14
    )
    subtitle_style = ParagraphStyle(
        'CoverSubtitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=12, leading=16,
        alignment=1, textColor=colors.HexColor('#1e40af'), spaceAfter=20
    )
    meta_header_style = ParagraphStyle(
        'CoverMetaHeader', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=11, leading=15,
        alignment=1, textColor=colors.HexColor('#1e293b'), spaceAfter=6
    )
    h1_style = ParagraphStyle(
        'Heading1_Custom', parent=styles['Heading1'],
        fontName='Helvetica-Bold', fontSize=14, leading=18,
        textColor=colors.HexColor('#0f172a'), spaceBefore=14, spaceAfter=8, keepWithNext=True
    )
    h2_style = ParagraphStyle(
        'Heading2_Custom', parent=styles['Heading2'],
        fontName='Helvetica-Bold', fontSize=11.5, leading=15.5,
        textColor=colors.HexColor('#1e3a8a'), spaceBefore=10, spaceAfter=5, keepWithNext=True
    )
    h3_style = ParagraphStyle(
        'Heading3_Custom', parent=styles['Heading3'],
        fontName='Helvetica-Bold', fontSize=9.5, leading=13.5,
        textColor=colors.HexColor('#334155'), spaceBefore=8, spaceAfter=4, keepWithNext=True
    )
    body_style = ParagraphStyle(
        'Body_Custom', parent=styles['BodyText'],
        fontName='Helvetica', fontSize=9, leading=13,
        textColor=colors.HexColor('#1e293b'), spaceAfter=6, alignment=4 # Justify
    )
    bullet_style = ParagraphStyle(
        'Bullet_Custom', parent=body_style,
        leftIndent=14, firstLineIndent=-8, spaceAfter=4
    )
    code_style = ParagraphStyle(
        'Code_Custom', parent=styles['Normal'],
        fontName='Courier', fontSize=7.2, leading=9.2,
        textColor=colors.HexColor('#0f172a')
    )
    eq_style = ParagraphStyle(
        'Equation_Custom', parent=body_style,
        leftIndent=20, fontName='Helvetica-Bold', textColor=colors.HexColor('#1e3a8a'),
        spaceBefore=4, spaceAfter=6
    )
    fig_caption = ParagraphStyle(
        'FigureCaption', parent=styles['Normal'],
        fontName='Helvetica-Oblique', fontSize=8, leading=11,
        alignment=1, textColor=colors.HexColor('#475569'), spaceBefore=4, spaceAfter=10
    )
    table_cell = ParagraphStyle(
        'TableCell', parent=styles['Normal'],
        fontName='Helvetica', fontSize=7.8, leading=10.5,
        textColor=colors.HexColor('#1e293b')
    )
    table_cell_bold = ParagraphStyle(
        'TableCellBold', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=7.8, leading=10.5,
        textColor=colors.HexColor('#0f172a')
    )
    table_cell_header = ParagraphStyle(
        'TableHeader', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=8, leading=11,
        textColor=colors.white, alignment=1
    )

    styles.add(fig_caption)

    story = []

    # =========================================================================
    # 1. COVER PAGE (Trang Bìa Chuẩn Bách Khoa TP.HCM)
    # =========================================================================
    story.append(Spacer(1, 35))
    story.append(Paragraph("VIETNAM NATIONAL UNIVERSITY - HO CHI MINH CITY", meta_header_style))
    story.append(Paragraph("HO CHI MINH CITY UNIVERSITY OF TECHNOLOGY", meta_header_style))
    story.append(Paragraph("FACULTY OF COMPUTER SCIENCE AND ENGINEERING", ParagraphStyle('SubSub', parent=meta_header_style, fontSize=10, textColor=colors.HexColor('#475569'))))
    story.append(Spacer(1, 35))

    # Decorative BK Logo Box
    logo_data = [[
        Paragraph("<font size='26' color='#1e3a8a'><b>BK</b></font><br/><font size='9' color='#1e3a8a'><b>TP.HCM</b></font>", ParagraphStyle('LogoP', alignment=1))
    ]]
    logo_table = Table(logo_data, colWidths=[90], rowHeights=[65])
    logo_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor('#1e3a8a')),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
    ]))
    story.append(logo_table)
    story.append(Spacer(1, 40))

    story.append(Paragraph("LARGE ASSIGNMENT REPORT", subtitle_style))
    story.append(Paragraph("INTELLIGENT SYSTEMS (CO5119 / CO3041)", ParagraphStyle('CourseP', parent=subtitle_style, fontSize=13, textColor=colors.HexColor('#0f172a'))))
    story.append(Spacer(1, 10))

    story.append(Paragraph("HUB: A TWO-STAGE PERSONALIZED FASHION RECOMMENDATION SYSTEM USING RANDOM FOREST POINTWISE RANKING AND SESSION-AWARE RE-RANKING", title_style))
    story.append(Spacer(1, 30))

    # Metadata Box (Students & Instructor)
    meta_content = [
        [Paragraph("<b>Instructor:</b>", table_cell_bold), Paragraph("PhD. Quan Thanh Tho", table_cell)],
        [Paragraph("<b>Department:</b>", table_cell_bold), Paragraph("Computer Science and Engineering", table_cell)],
        [Paragraph("<b>Class:</b>", table_cell_bold), Paragraph("CO5119 / CO3041 - Semester 1 / 2026", table_cell)],
        [Paragraph("<b>Students:</b>", table_cell_bold), Paragraph("1. Dao Duy Dat &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- Student ID: <b>2352223</b><br/>2. Phan Tien Huy &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- Student ID: <b>2352402</b>", table_cell)],
    ]
    meta_table = Table(meta_content, colWidths=[100, 260])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f1f5f9')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(meta_table)

    story.append(Spacer(1, 65))
    story.append(Paragraph("<i>Ho Chi Minh City, November 2026</i>", ParagraphStyle('DateP', parent=styles['Normal'], alignment=1, fontSize=9.5, textColor=colors.HexColor('#64748b'))))

    story.append(PageBreak())

    # =========================================================================
    # 2. TABLE OF CONTENTS, LIST OF FIGURES & TABLES
    # =========================================================================
    story.append(PageTracker('toc_page'))
    story.append(Paragraph("Table of Contents", h1_style))
    story.append(Spacer(1, 6))

    def p_num(key, default_val):
        return str(page_dict.get(key, default_val))

    toc_entries = [
        ("1  Introduction & System Overview", p_num('ch1', 4), 0),
        ("   1.1 Fast-Fashion Recommendation Challenges", p_num('sec1_1', 4), 1),
        ("   1.2 Stakeholder Personas & Value Proposition", p_num('sec1_2', 4), 1),
        ("   1.3 System Scope & Service Level Agreements", p_num('sec1_3', 5), 1),
        ("2  Theoretical Foundations & Mathematical Formulation", p_num('ch2', 6), 0),
        ("   2.1 Decision Tree Formulation & Impurity Criteria", p_num('sec2_1', 6), 1),
        ("   2.2 Ensemble Dynamics: Breiman's Random Forest", p_num('sec2_2', 7), 1),
        ("   2.3 Two-Stage Recommendation Architecture", p_num('sec2_3', 8), 1),
        ("   2.4 Negative Sampling & Imbalance Rectification", p_num('sec2_4', 9), 1),
        ("   2.5 Formal Evaluation Metrics (MAP@12, NDCG@12)", p_num('sec2_5', 9), 1),
        ("3  Use-Case Modeling & Interaction Specification", p_num('ch3', 11), 0),
        ("   3.1 Actor Hierarchy & Role-Based Access Control", p_num('sec3_1', 11), 1),
        ("   3.2 Comprehensive Use Case Specifications (UC-01 to UC-08)", p_num('sec3_2', 12), 1),
        ("   3.3 Sequence Diagrams for Key Execution Flows", p_num('sec3_3', 15), 1),
        ("4  System Architecture & Database Design", p_num('ch4', 17), 0),
        ("   4.1 Enterprise 4-Tier Architecture Overview", p_num('sec4_1', 17), 1),
        ("   4.2 Relational Database Schema & Data Dictionary", p_num('sec4_2', 18), 1),
        ("   4.3 Comprehensive RESTful API Endpoint Directory", p_num('sec4_3', 20), 1),
        ("5  Data Pipeline, Preprocessing & Feature Engineering", p_num('ch5', 22), 0),
        ("   5.1 H&M Benchmark Characteristics & Raw Data Exploration", p_num('sec5_1', 22), 1),
        ("   5.2 Strict Temporal Rolling Split (Zero Data Leakage)", p_num('sec5_2', 24), 1),
        ("   5.3 Multi-Strategy Candidate Retrieval Algorithms", p_num('sec5_3', 25), 1),
        ("   5.4 14-Dimensional Feature Engineering Formulations", p_num('sec5_4', 26), 1),
        ("   5.5 Background Scheduler & Catch-up Backfill Engine", p_num('sec5_5', 27), 1),
        ("6  AI Training, Experimental Evaluation & Diagnostics", p_num('ch6', 28), 0),
        ("   6.1 Hyperparameter Specifications & Environment", p_num('sec6_1', 28), 1),
        ("   6.2 Experimental Results vs. Baselines (MAP@12, NDCG@12)", p_num('sec6_2', 29), 1),
        ("   6.3 Feature Importance Ranking & Interpretation", p_num('sec6_3', 30), 1),
        ("   6.4 Sliced Error Diagnostics Across User Segments", p_num('sec6_4', 31), 1),
        ("   6.5 Real-Time Session Re-ranking & Anti-Echo Chamber", p_num('sec6_5', 32), 1),
        ("7  System Demonstration & Graphical User Interface", p_num('ch7', 33), 0),
        ("   7.1 Buyer E-Commerce Experience Walkthrough", p_num('sec7_1', 33), 1),
        ("   7.2 Data Scientist Observability Workspace", p_num('sec7_2', 35), 1),
        ("   7.3 Administrator Control Panel Walkthrough", p_num('sec7_3', 37), 1),
        ("8  Conclusion & Future Roadmap", p_num('ch8', 38), 0),
        ("   8.1 Summary of System Contributions", p_num('sec8_1', 38), 1),
        ("   8.2 Technical Limitations & Enterprise Roadmap", p_num('sec8_2', 38), 1),
        ("References (IEEE Standard)", p_num('ref_sec', 39), 0),
    ]

    toc_rows = []
    for title, page, level in toc_entries:
        style_t = table_cell_bold if level == 0 else table_cell
        color_p = '#1e3a8a' if level == 0 else '#475569'
        toc_rows.append([
            Paragraph(f"<font color='{color_p}'>{title}</font>", style_t),
            Paragraph(f"<font color='{color_p}'><b>{page}</b></font>", ParagraphStyle('PNum', parent=style_t, alignment=2))
        ])

    toc_table = Table(toc_rows, colWidths=[420, 50])
    toc_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 1.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.5),
        ('LINEBELOW', (0,0), (-1,-1), 0.3, colors.HexColor('#f1f5f9')),
    ]))
    story.append(toc_table)

    story.append(Spacer(1, 14))
    story.append(Paragraph("List of Figures", h2_style))
    fig_entries = [
        ("Figure 2.1: End-to-End Machine Learning Pipeline & Two-Stage Recommendation Flow", p_num('sec2_3', 8)),
        ("Figure 3.0: Global System Use-Case Diagram & Actor Boundaries", p_num('sec3_1', 13)),
        ("Figure 3.1: Sequence Diagram for UC-02 Real-time Recommendation Inference", p_num('sec3_3', 15)),
        ("Figure 3.2: Sequence Diagram for UC-05 Background Model Retraining Pipeline", p_num('sec3_3', 16)),
        ("Figure 4.1: Enterprise 4-Tier Logical Architecture of the HUB System", p_num('sec4_1', 17)),
        ("Figure 4.2: Relational Database Entity-Relationship Diagram (ERD)", p_num('sec4_2', 19)),
        ("Figure 5.1: Daily Transaction Volume Across Entire H&M Historical Dataset", p_num('fig5_1', 22)),
        ("Figure 5.2: Normalized Product Price Distribution (Kernel Density Approximation)", p_num('fig5_2', 23)),
        ("Figure 5.3: Catalog Breakdown Across Top-15 Product Groups", p_num('fig5_3', 23)),
        ("Figure 5.4: Customer Age Demographic Histogram", p_num('fig5_4', 24)),
        ("Figure 5.5: Sales Volume by Department Index Group", p_num('fig5_5', 24)),
        ("Figure 5.6: Temporal Split Architecture and Feature Rolling Windows", p_num('sec5_2', 25)),
        ("Figure 6.1: Gini Impurity Feature Importance Ranking", p_num('sec6_3', 30)),
        ("Figure 7.1: Multi-Role Authentication Interface (LoginPage)", p_num('fig7_1', 33)),
        ("Figure 7.2: Buyer Personalized Homepage & Recommendation Showcase (HomePage)", p_num('fig7_2', 34)),
        ("Figure 7.3: Product Detail View & Real-time Interaction Tracking (ProductDetailPage)", p_num('fig7_3', 34)),
        ("Figure 7.4: Data Science Exploratory Analysis Dashboard (DataSciencePage)", p_num('fig7_4', 35)),
        ("Figure 7.5: Model Performance Validation & Baseline Benchmark Radar (ModelMetricsPage)", p_num('fig7_5', 36)),
        ("Figure 7.6: Sliced Error Diagnostics by Activity & Department (ErrorAnalysisPage)", p_num('fig7_6', 36)),
        ("Figure 7.7: Automated Training Scheduler & Hyperparameter Tuning (TrainingSchedulePage)", p_num('fig7_7', 37)),
        ("Figure 7.8: Executive Operations & Commercial Sales Monitoring (AdminDashboardPage)", p_num('fig7_8', 37)),
    ]
    fig_rows = [[Paragraph(f"<font color='#334155'>{f[0]}</font>", table_cell), Paragraph(f"<b>{f[1]}</b>", ParagraphStyle('PNumF', parent=table_cell, alignment=2))] for f in fig_entries]
    fig_table = Table(fig_rows, colWidths=[420, 50])
    fig_table.setStyle(TableStyle([
        ('TOPPADDING', (0,0), (-1,-1), 1.2), ('BOTTOMPADDING', (0,0), (-1,-1), 1.2),
        ('LINEBELOW', (0,0), (-1,-1), 0.3, colors.HexColor('#f8fafc'))
    ]))
    story.append(fig_table)

    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 1: INTRODUCTION & SYSTEM OVERVIEW
    # =========================================================================
    story.append(PageTracker('ch1'))
    story.append(Paragraph("1  Introduction & System Overview", h1_style))
    story.append(Spacer(1, 4))

    story.append(PageTracker('sec1_1'))
    story.append(Paragraph("1.1  Fast-Fashion Recommendation Challenges", h2_style))
    story.append(Paragraph(
        "Modern fast-fashion retail platforms operate under extreme operational conditions that challenge classical recommendation paradigms. "
        "Unlike digital media platforms (e.g., Netflix, Spotify) where item catalogs remain largely persistent and consumption is repeatable, "
        "fashion e-commerce platforms like H&M encounter three distinct computational and algorithmic barriers:",
        body_style
    ))
    story.append(Paragraph("• <b>Extreme Catalog Sparsity:</b> With over 105,542 active articles and 1,371,980 registered customers, the interaction matrix possesses an extreme sparsity exceeding 99.98%. Evaluating the raw Cartesian product results in approximately 1.45 &times; 10<sup>11</sup> candidate pairs, rendering exhaustive scoring computationally infeasible for real-time web applications.", bullet_style))
    story.append(Paragraph("• <b>Dynamic Catalog Churn and Seasonality:</b> Fast-fashion inventory turns over rapidly across weekly micro-seasons. Garments introduced in summer become obsolete in autumn. A customer's historical transactions from eight weeks prior reflect outdated thermal and aesthetic preferences, demanding aggressive time-decay weighting and rolling temporal feature windows.", bullet_style))
    story.append(Paragraph("• <b>Dual Latency vs. Accuracy Trade-Off:</b> A production recommender must deliver personalized items within strict sub-100ms budgets on web storefronts, while simultaneously incorporating in-session behavioral signals (views, cart additions, wishlist events) without waiting for offline model retraining.", bullet_style))

    story.append(PageTracker('sec1_2'))
    story.append(Paragraph("1.2  Stakeholder Personas & Value Proposition", h2_style))
    story.append(Paragraph(
        "To establish holistic software requirements, the HUB system defines three core stakeholder personas, each governing a dedicated architectural boundary:",
        body_style
    ))

    stakeholder_data = [
        [Paragraph("Stakeholder", table_cell_header), Paragraph("Primary Operational Responsibilities", table_cell_header), Paragraph("Delivered System Value", table_cell_header)],
        [
            Paragraph("<b>Buyer</b><br/>(End Customer)", table_cell),
            Paragraph("• Browses catalog products<br/>• Receives real-time personalized recommendations<br/>• Places commercial orders & submits 5-star ratings<br/>• Manages personal wishlist & shopping cart", table_cell),
            Paragraph("Drastically reduces catalog search fatigue; surfaces relevant garments matching historical affinity and current shopping intent within <50ms.", table_cell)
        ],
        [
            Paragraph("<b>Data Scientist</b><br/>(AI/ML Engineer)", table_cell),
            Paragraph("• Inspects raw & normalized EDA distributions<br/>• Triggers on-demand & scheduled retraining<br/>• Monitors MAP@12, Recall@12, and NDCG@12 vs baselines<br/>• Diagnoses slices by activity segments & product groups", table_cell),
            Paragraph("Full-lifecycle observability, automated experiment tracking, safety gates preventing deployment of sub-baseline models, and feature importance rankings.", table_cell)
        ],
        [
            Paragraph("<b>System Admin</b><br/>(Business Ops)", table_cell),
            Paragraph("• Monitors revenue metrics, gross merchandise value (GMV)<br/>• Updates commercial order statuses (Pending &rarr; Shipped)<br/>• Manages catalog inventory and customer linkages<br/>• Audits system health and background scheduler", table_cell),
            Paragraph("Centralized governance dashboard linking AI performance directly to commercial revenue, inventory turnover, and transaction throughput.", table_cell)
        ]
    ]
    st_table = Table(stakeholder_data, colWidths=[80, 210, 180])
    st_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a8a')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 5), ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6), ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(st_table)
    story.append(Spacer(1, 8))

    story.append(PageTracker('sec1_3'))
    story.append(Paragraph("1.3  Functional & Non-Functional Requirements", h2_style))
    story.append(Paragraph(
        "To satisfy software engineering standards, HUB explicitly specifies functional capabilities and non-functional quality attributes:",
        body_style
    ))

    fn_data = [
        [Paragraph("Category", table_cell_header), Paragraph("ID & Requirement Name", table_cell_header), Paragraph("Engineering Specification & Acceptance Boundary", table_cell_header)],
        [Paragraph("<b>Functional (FR)</b>", table_cell), Paragraph("FR-01: Multi-Role Auth", table_cell), Paragraph("Authenticate Buyer, Data Scientist, and Admin with signed JWT tokens.", table_cell)],
        [Paragraph("<b>Functional (FR)</b>", table_cell), Paragraph("FR-02: Real-time Recs", table_cell), Paragraph("Generate Top-12 personalized garments with in-session dynamic re-ranking.", table_cell)],
        [Paragraph("<b>Functional (FR)</b>", table_cell), Paragraph("FR-03: Interaction Logging", table_cell), Paragraph("Ingest views, cart adds, wishlists, and 1-5 star ratings for session vectors.", table_cell)],
        [Paragraph("<b>Functional (FR)</b>", table_cell), Paragraph("FR-04: ML Training Engine", table_cell), Paragraph("Trigger background training with 6-stage execution tracking and polling.", table_cell)],
        [Paragraph("<b>Functional (FR)</b>", table_cell), Paragraph("FR-05: Safety Guardrail", table_cell), Paragraph("Block deployment if model MAP@12 degrades below Bestseller baseline.", table_cell)],
        [Paragraph("<b>Functional (FR)</b>", table_cell), Paragraph("FR-06: Sliced Diagnostics", table_cell), Paragraph("Break down error metrics across customer tiers and product departments.", table_cell)],
        [Paragraph("<b>Non-Functional</b>", table_cell), Paragraph("NFR-01: Inference Latency", table_cell), Paragraph("95th percentile response time for <code>GET /predict</code> strictly under 80ms.", table_cell)],
        [Paragraph("<b>Non-Functional</b>", table_cell), Paragraph("NFR-02: Data Isolation", table_cell), Paragraph("Zero temporal data leakage; features computed strictly prior to cutoff.", table_cell)],
        [Paragraph("<b>Non-Functional</b>", table_cell), Paragraph("NFR-03: Test Coverage", table_cell), Paragraph("100% pass rate across 27 automated backend unit & integration tests.", table_cell)],
        [Paragraph("<b>Non-Functional</b>", table_cell), Paragraph("NFR-04: High Availability", table_cell), Paragraph("Scheduler catch-up backfill recovers missed runs upon server reboot.", table_cell)],
    ]
    t_fn = Table(fn_data, colWidths=[90, 130, 250])
    t_fn.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a8a')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 2.5), ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5), ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_fn)
    story.append(Spacer(1, 8))

    story.append(Paragraph(
        "The HUB project establishes explicit Service Level Agreements (SLAs) across latency, memory footprints, and predictive quality. "
        "Recommendation inference via <code>GET /predict/{user_id}</code> is constrained to an end-to-end response time under <b>80ms</b> (95th percentile). "
        "Offline model retraining is designed to execute asynchronously within <b>15 minutes</b> on Kaggle GPU/CPU kernels or local compute nodes. "
        "Crucially, the system introduces a mandatory <b>Safety Degradation Gate</b>: if a newly trained model achieves a validation MAP@12 inferior to "
        "the standard Bestseller baseline, deployment is halted and flagged for Data Scientist manual intervention.",
        body_style
    ))

    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 2: THEORETICAL FOUNDATIONS & MATHEMATICAL FORMULATION
    # =========================================================================
    story.append(PageTracker('ch2'))
    story.append(Paragraph("2  Theoretical Foundations & Mathematical Formulation", h1_style))
    story.append(Spacer(1, 4))

    story.append(PageTracker('sec2_1'))
    story.append(Paragraph("2.1  Decision Tree Formulation & Impurity Criteria", h2_style))
    story.append(Paragraph(
        "The core mathematical ranker employed in HUB is based on supervised binary classification decision trees recursively partitioned on feature space. "
        "Let a training node <i>m</i> contain subset &fnof;<sub>m</sub> with <i>N<sub>m</sub></i> interaction pairs <b>x</b><sub>i</sub> &isin; <font name='SegoeUISymbol'>\u211d</font><sup><i>d</i></sup> and labels <i>y<sub>i</sub> &isin; {0, 1}</i>. "
        "The empirical probability of positive purchase interaction at node <i>m</i> is defined as:",
        body_style
    ))
    story.append(Spacer(1, 2))
    story.append(build_arxiv_equation("2.1", f"<i>p<sub>mk</sub></i> = (1 / <i>N<sub>m</sub></i>) &nbsp;{SUM}<sub>(<b>x</b><sub><i>i</i></sub>, <i>y<sub>i</sub></i>) {IN} <i>D<sub>m</sub></i></sub> <b>1</b>(<i>y<sub>i</sub></i> = <i>k</i>), &nbsp;&nbsp;&nbsp;&nbsp; <i>k</i> {IN} {{0, 1}}"))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "To measure partition homogeneity, HUB employs the <b>Gini Impurity</b> criterion, which quantifies the probability of misclassifying a randomly chosen element:",
        body_style
    ))
    story.append(Spacer(1, 2))
    story.append(build_arxiv_equation("2.2", f"<i>I<sub>G</sub></i>(<i>m</i>) = 1 - {SUM}<sub><i>k</i> {IN} {{0, 1}}</sub> <i>p<sub>mk</sub></i><sup>2</sup> = 2 <i>p</i><sub><i>m</i>1</sub>(1 - <i>p</i><sub><i>m</i>1</sub>)"))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "For a candidate continuous or ordinal split candidate &theta; = (j, t) partitioning feature <i>j</i> at threshold <i>t</i> into left subset D<sub>m</sub><sup>L</sup>(&theta;) and right subset D<sub>m</sub><sup>R</sup>(&theta;), "
        "the optimal split &theta;<sup>*</sup> maximizes the <b>Information Gain</b> (or impurity reduction):",
        body_style
    ))
    story.append(Spacer(1, 2))
    story.append(build_arxiv_equation("2.3", f"{DELTA}<i>I<sub>G</sub></i>(<i>m</i>, &theta;) = <i>I<sub>G</sub></i>(<i>m</i>) - <font size=9.5>[</font> (<i>N<sub>m</sub><sup>L</sup></i> / <i>N<sub>m</sub></i>) <i>I<sub>G</sub></i>(<i>D<sub>m</sub><sup>L</sup></i>) + (<i>N<sub>m</sub><sup>R</sup></i> / <i>N<sub>m</sub></i>) <i>I<sub>G</sub></i>(<i>D<sub>m</sub><sup>R</sup></i>) <font size=9.5>]</font>"))
    story.append(Spacer(1, 4))

    story.append(PageTracker('sec2_2'))
    story.append(Paragraph("2.2  Ensemble Dynamics: Breiman's Random Forest", h2_style))
    story.append(Paragraph(
        "A single deep decision tree exhibits high variance and overfits transaction noise. Leo Breiman's Random Forest algorithm mitigates variance through two distinct randomization mechanisms: "
        "<b>Bootstrap Aggregation (Bagging)</b> and <b>Random Feature Subsampling</b>.",
        body_style
    ))
    story.append(Paragraph("• <b>Bootstrap Sampling Probability:</b> For an ensemble of <i>B = 200</i> trees, each tree <i>T<sub>b</sub></i> is trained on dataset D<sup>(b)</sup> constructed by sampling <i>N</i> instances from D uniformly with replacement. The theoretical probability of an instance being omitted from a tree is:", bullet_style))
    story.append(Spacer(1, 2))
    story.append(build_arxiv_equation("2.4", "lim<sub><i>N</i> &rarr; &infin;</sub> (1 - 1/<i>N</i>)<sup><i>N</i></sup> = 1/<i>e</i> &asymp; 0.368 &nbsp;&nbsp;&nbsp;&nbsp; (36.8% Out-of-Bag samples)"))
    story.append(Spacer(1, 4))
    story.append(Paragraph("• <b>Feature Subsampling & Variance Reduction:</b> At each internal node, only <i>m<sub>try</sub> = <font name='SegoeUISymbol'>\u230a\u221a<i>d</i>\u230b</font></i> features (out of <i>d = 14</i>) are evaluated. Let individual trees have variance &sigma;<sup>2</sup> and pairwise correlation &rho;. The variance of the ensemble mean prediction is:", bullet_style))
    story.append(Spacer(1, 2))
    story.append(build_arxiv_equation("2.5", f"Var<font size=9.5>(</font>(1/<i>B</i>) {SUM}<sub><i>b</i>=1</sub><sup><i>B</i></sup> <i>T<sub>b</sub></i>(<b>x</b>)<font size=9.5>)</font> = &rho; &sigma;<sup>2</sup> + ((1 - &rho;) / <i>B</i>) &sigma;<sup>2</sup>"))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "As <i>B &rarr; &infin;</i>, the second term vanishes, leaving <i>&rho; &sigma;<sup>2</sup></i>. Random feature subsampling forces trees to split on diverse signals, minimizing inter-tree correlation &rho; without inflating bias. "
        "The final predicted purchase probability for customer <i>u</i> and candidate article <i>i</i> is computed as the ensemble expectation:",
        body_style
    ))
    story.append(Spacer(1, 2))
    story.append(build_arxiv_equation("2.6", f"<i>p&#772;</i>(<i>u</i>, <i>i</i>) = (1 / <i>B</i>) {SUM}<sub><i>b</i>=1</sub><sup><i>B</i></sup> <i>P<sub>b</sub></i>(<i>y</i> = 1 | <b>x</b><sub><i>u,i</i></sub>)"))
    story.append(Spacer(1, 4))

    story.append(PageTracker('sec2_3'))
    story.append(Paragraph("2.3  Two-Stage Recommendation Architecture", h2_style))
    story.append(Paragraph(
        "To bypass the Cartesian explosion (1.45 &times; 10<sup>11</sup> pairs), HUB establishes a decoupled <b>Two-Stage Recommender Architecture</b>:",
        body_style
    ))

    story.append(Spacer(1, 4))
    story.append(create_image_flowable("excalidraw_03_ml_training_pipeline.png", max_w=6.2*inch, max_h=3.0*inch))
    story.append(create_caption("Figure 2.1: End-to-End Machine Learning Pipeline & Two-Stage Recommendation Flow (Excalidraw Visual Blueprint)", styles))
    story.append(Spacer(1, 6))

    story.append(Spacer(1, 8))
    story.append(Paragraph("2.3.1  Algorithmic Formalization of Two-Stage Pipeline", h3_style))
    story.append(Paragraph(
        "The end-to-end execution of the HUB recommendation engine is governed by two formal algorithms representing Stage 1 Retrieval and Stage 2 Real-Time Re-ranking:",
        body_style
    ))

    steps1 = [
        (1, f"<i>C<sub>u</sub></i> {ASSIGN} {EMPTY}"),
        (2, f"<i>C</i><sub>repurchase</sub> {ASSIGN} {{<i>i</i> {IN} <i>I</i> | {EXISTS} (<i>u</i>, <i>i</i>, <i>t</i>) {IN} <i>D</i> {AND} <i>t</i> {GE} <i>T</i><sub>cutoff</sub> - 28d}}"),
        (3, f"<i>C</i><sub>bestseller</sub> {ASSIGN} TopK({{<i>i</i> {IN} <i>I</i> | sales_count(<i>i</i>, [<i>T</i><sub>cutoff</sub> - 7d, <i>T</i><sub>cutoff</sub>])}}, <i>K</i> = 12)"),
        (4, f"<i>C</i><sub>age</sub> {ASSIGN} TopK({{<i>i</i> {IN} <i>I</i> | sales_by_cohort(<i>i</i>, age_group(<i>u</i>))}}, <i>K</i> = 8)"),
        (5, f"<i>C</i><sub>copurchase</sub> {ASSIGN} {{<i>j</i> {IN} <i>I</i> | {EXISTS} <i>i</i> {IN} <i>C</i><sub>repurchase</sub> {AND} co_purchased(<i>i</i>, <i>j</i>) {GE} 5}}"),
        (6, f"<i>C<sub>u</sub></i> {ASSIGN} Truncate(<i>C</i><sub>repurchase</sub> {UNION} <i>C</i><sub>bestseller</sub> {UNION} <i>C</i><sub>age</sub> {UNION} <i>C</i><sub>copurchase</sub>, <i>C</i><sub>max</sub> = 100)"),
        (7, f"<i>Y</i><sub>true</sub> {ASSIGN} {{<i>i</i> {IN} <i>I</i> | {EXISTS} (<i>u</i>, <i>i</i>, <i>t</i>) {IN} <i>D</i> {AND} <i>t</i> {IN} [<i>T</i><sub>cutoff</sub>, <i>T</i><sub>cutoff</sub> + 7d]}}"),
        (8, f"<b>Positives</b> {ASSIGN} {{(<i>u</i>, <i>i</i>, 1) | <i>i</i> {IN} (<i>C<sub>u</sub></i> {INTERSECT} <i>Y</i><sub>true</sub>)}} &nbsp;&nbsp;&nbsp;&nbsp;<font color=\"#64748b\"><i>// True purchase ground truth</i></font>"),
        (9, f"<i>N</i><sub>cand</sub> {ASSIGN} <i>C<sub>u</sub></i> {SETMINUS} <i>Y</i><sub>true</sub> &nbsp;&nbsp;&nbsp;&nbsp;<font color=\"#64748b\"><i>// Candidate negative item space</i></font>"),
        (10, f"<i>k</i><sub>neg</sub> {ASSIGN} min(|<i>N</i><sub>cand</sub>|, {LAMBDA}<sub>neg</sub> {TIMES} |<b>Positives</b>|)"),
        (11, f"<b>Negatives</b> {ASSIGN} SampleWithoutReplacement(<i>N</i><sub>cand</sub>, <i>k</i><sub>neg</sub>)"),
        (12, f"<b>return</b> <i>T<sub>u</sub></i> {ASSIGN} <b>Positives</b> {UNION} {{(<i>u</i>, <i>j</i>, 0) | <i>j</i> {IN} <b>Negatives</b>}}")
    ]
    algo1_flowable = build_arxiv_algorithm(
        "1", "Stage 1 Multi-Channel Candidate Retrieval & Controlled Negative Sampling",
        f"Customer <i>u</i> {IN} <i>U</i>, Transactions <i>D</i> (<i>t</i> &lt; <i>T</i><sub>cutoff</sub>), Catalog <i>I</i>, Cohorts <i>A</i>, Ratio {LAMBDA}<sub>neg</sub> = 5",
        f"Balanced training set <i>T<sub>u</sub></i> = {{(<i>u</i>, <i>i</i>, <i>y</i>)}} with binary label <i>y</i> {IN} {{0, 1}}",
        steps1
    )
    story.append(algo1_flowable)
    story.append(create_caption("Algorithm 2.1: Multi-Channel Candidate Retrieval & Controlled Negative Sampling", styles))
    story.append(PageBreak())

    steps2 = [
        (1, f"<b>a</b> {ASSIGN} <b>0</b><sub>|<i>V</i>|</sub> &nbsp;&nbsp;&nbsp;&nbsp;<font color=\"#64748b\"><i>// Initialize session anchor category weight vector</i></font>"),
        (2, f"<b>for each</b> event <i>e</i> = (<i>i<sub>e</sub></i>, &tau;<sub><i>e</i></sub>, <i>t<sub>e</sub></i>) {IN} <i>E<sub>u</sub></i> (ordered newest to oldest, max 50) <b>do</b>:"),
        (3, f"&nbsp;&nbsp;&nbsp;&nbsp; {DELTA}<i>t</i> {ASSIGN} (<i>t</i><sub>now</sub> - <i>t<sub>e</sub></i>) in days"),
        (4, f"&nbsp;&nbsp;&nbsp;&nbsp; <i>w</i>(<i>e</i>) {ASSIGN} &omega;(&tau;<sub><i>e</i></sub>) {TIMES} 2<sup>-{DELTA}<i>t</i> / <i>t</i><sub>1/2</sub></sup> &nbsp;&nbsp;&nbsp;&nbsp;<font color=\"#64748b\"><i>// Exponential decay with half-life t<sub>1/2</sub> = 3.0 days</i></font>"),
        (5, f"&nbsp;&nbsp;&nbsp;&nbsp; <b>a</b>[category(<i>i<sub>e</sub></i>)] {ASSIGN} <b>a</b>[category(<i>i<sub>e</sub></i>)] + <i>w</i>(<i>e</i>)"),
        (6, f"<b>end for</b>"),
        (7, f"<i>B</i> {ASSIGN} {{<i>i<sub>e</sub></i> | &tau;<sub><i>e</i></sub> = PURCHASED {OR} (&tau;<sub><i>e</i></sub> = FEEDBACK {AND} rating(<i>e</i>) {LE} 2)}} &nbsp;&nbsp;&nbsp;&nbsp;<font color=\"#64748b\"><i>// Hard suppression</i></font>"),
        (8, f"<i>C</i><sub>active</sub> {ASSIGN} {{(<i>i</i>, <i>p&#770;</i>(<i>u</i>, <i>i</i>)) {IN} <i>C<sub>u</sub></i> | <i>i</i> {NOTIN} <i>B</i>}}"),
        (9, f"<b>for each</b> candidate (<i>i</i>, <i>p&#770;</i>) {IN} <i>C</i><sub>active</sub> <b>do</b>:"),
        (10, f"&nbsp;&nbsp;&nbsp;&nbsp; boost(<i>i</i>) {ASSIGN} {SUM}<sub><i>c</i> {IN} categories</sub> <b>a</b>[<i>c</i>] {DOT} Similarity(category(<i>i</i>), <i>c</i>)"),
        (11, f"&nbsp;&nbsp;&nbsp;&nbsp; <i>s</i><sub>final</sub>(<i>i</i>) {ASSIGN} <i>p&#770;</i> {TIMES} (1.0 + max(0.0, boost(<i>i</i>)))"),
        (12, f"<b>end for</b>"),
        (13, f"<i>S</i> {ASSIGN} SortDescending(<i>C</i><sub>active</sub>, key = <i>s</i><sub>final</sub>)"),
        (14, f"<i>R<sub>u</sub></i> {ASSIGN} [ ], &nbsp;&nbsp; <i>G</i><sub>seen</sub> {ASSIGN} {EMPTY}"),
        (15, f"<b>for each</b> (<i>i</i>, <i>s</i>) {IN} <i>S</i> <b>do</b>:"),
        (16, f"&nbsp;&nbsp;&nbsp;&nbsp; <b>if</b> product_code(<i>i</i>) {NOTIN} <i>G</i><sub>seen</sub> <b>then</b>:"),
        (17, f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <i>R<sub>u</sub></i> {ASSIGN} <i>R<sub>u</sub></i> {CONCAT} [<i>i</i>], &nbsp;&nbsp; <i>G</i><sub>seen</sub> {ASSIGN} <i>G</i><sub>seen</sub> {UNION} {{product_code(<i>i</i>)}}"),
        (18, f"&nbsp;&nbsp;&nbsp;&nbsp; <b>if</b> |<i>R<sub>u</sub></i>| = <i>K</i> <b>then</b> <b>break</b>"),
        (19, f"<b>return</b> <i>R<sub>u</sub></i> &nbsp;&nbsp;&nbsp;&nbsp;<font color=\"#64748b\"><i>// Final re-ranked diversified Top-12 recommendation sequence</i></font>")
    ]
    algo2_flowable = build_arxiv_algorithm(
        "2", "Real-Time In-Session Dynamic Re-Ranking with Half-Life Exponential Decay",
        f"User <i>u</i>, Pre-scored Candidates {{(<i>i</i>, <i>p&#770;</i>(<i>u</i>, <i>i</i>))}}, Active Session Stream <i>E<sub>u</sub></i>, Target <i>K</i> = 12",
        f"Final context-aware recommendation sequence <i>R<sub>u</sub></i> = [<i>i</i><sub>1</sub>, ..., <i>i<sub>K</sub></i>]",
        steps2
    )
    story.append(algo2_flowable)
    story.append(create_caption("Algorithm 2.2: Real-Time In-Session Dynamic Re-Ranking & Diversity Enforcement", styles))
    story.append(Spacer(1, 8))


    story.append(PageTracker('sec2_4'))
    story.append(Paragraph("2.4  Negative Sampling & Imbalance Rectification", h2_style))
    story.append(Paragraph(
        "Within candidate sets, true purchases represent fewer than 1% of candidate pairs. Training a classifier on raw candidate sets causes severe positive class suppression. "
        "HUB implements a <b>Controlled Negative Subsampling Ratio</b> of <i>&lambda;<sub>neg</sub> = 5</i> negative samples for every positive purchase transaction. "
        "Negative instances are drawn strictly from candidate items generated for customer <i>u</i> that were not purchased during the target week. "
        "This compresses training instances to approximately 398,166 balanced rows, accelerating model convergence while maintaining ranking calibration.",
        body_style
    ))

    story.append(PageTracker('sec2_5'))
    story.append(Paragraph("2.5  Formal Evaluation Metrics (MAP@12, NDCG@12)", h2_style))
    story.append(Paragraph(
        "To rigorously quantify recommendation ranking accuracy against Kaggle benchmark standards, the system tracks five standardized information retrieval metrics:",
        body_style
    ))
    story.append(Paragraph("• <b>Mean Average Precision at 12 (MAP@12):</b> Computes rank-weighted precision across top-12 recommendations normalized by the minimum of ground-truth purchases and 12:", bullet_style))
    story.append(Spacer(1, 2))
    story.append(build_arxiv_equation("2.7", f"<i>AP@12</i>(<i>u</i>) = (1 / min(|<i>Y<sub>u</sub></i>|, 12)) &nbsp;{SUM}<sub><i>k</i>=1</sub><sup>12</sup> <i>P<sub>u</sub></i>(<i>k</i>) {TIMES} <i>rel<sub>u</sub></i>(<i>k</i>), &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <i>MAP@12</i> = (1 / |<i>U</i>|) &nbsp;{SUM}<sub><i>u</i>=1</sub><sup>|<i>U</i>|</sup> <i>AP@12</i>(<i>u</i>)"))
    story.append(Spacer(1, 4))
    story.append(Paragraph("• <b>Normalized Discounted Cumulative Gain at 12 (NDCG@12):</b> Penalizes relevant items appearing lower in the recommended list using logarithmic positional discounting:", bullet_style))
    story.append(Spacer(1, 2))
    story.append(build_arxiv_equation("2.8", f"<i>DCG@12</i>(<i>u</i>) = {SUM}<sub><i>k</i>=1</sub><sup>12</sup> (2<sup><i>rel<sub>u</sub></i>(<i>k</i>)</sup> - 1) / log<sub>2</sub>(<i>k</i> + 1), &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <i>NDCG@12</i>(<i>u</i>) = <i>DCG@12</i>(<i>u</i>) / <i>IDCG@12</i>(<i>u</i>)"))
    story.append(Spacer(1, 4))
    story.append(Paragraph("• <b>Candidate Retrieval Recall (Stage 1 Recall):</b> Quantifies the percentage of true future purchases captured within the top-100 candidate pool: <i>Recall<sub>cand</sub> = |C<sub>u</sub> &cap; Y<sub>u</sub>| / |Y<sub>u</sub>|</i>.", bullet_style))

    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 3: USE-CASE MODELING & INTERACTION SPECIFICATION
    # =========================================================================
    story.append(PageTracker('ch3'))
    story.append(Paragraph("3  Use-Case Modeling & Interaction Specification", h1_style))
    story.append(Spacer(1, 4))

    story.append(PageTracker('sec3_1'))
    story.append(Paragraph("3.1  Actor Hierarchy & Role-Based Access Control", h2_style))
    story.append(Paragraph(
        "HUB organizes permissions into an enterprise Role-Based Access Control (RBAC) hierarchy. System privileges are encapsulated in database roles: "
        "<code>ROLE_BUYER (1)</code>, <code>ROLE_DATA_SCIENTIST (2)</code>, and <code>ROLE_ADMIN (3)</code>. All endpoints enforce token-based claims verification.",
        body_style
    ))

    rbac_data = [
        [Paragraph("System Capability / Endpoint Group", table_cell_header), Paragraph("Buyer", table_cell_header), Paragraph("Data Scientist", table_cell_header), Paragraph("Administrator", table_cell_header)],
        [Paragraph("Catalog Browsing & Search (<code>/products</code>)", table_cell), Paragraph("READ", table_cell), Paragraph("READ", table_cell), Paragraph("FULL CONTROL", table_cell)],
        [Paragraph("Personalized Predictions (<code>/predict/{id}</code>)", table_cell), Paragraph("OWN USER", table_cell), Paragraph("ALL USERS", table_cell), Paragraph("ALL USERS", table_cell)],
        [Paragraph("Cart, Wishlist & Orders (<code>/cart, /orders</code>)", table_cell), Paragraph("OWN USER", table_cell), Paragraph("DENIED", table_cell), Paragraph("FULL AUDIT", table_cell)],
        [Paragraph("EDA Reports & Insights (<code>/ai/reports, /ai/insights</code>)", table_cell), Paragraph("DENIED", table_cell), Paragraph("READ", table_cell), Paragraph("READ", table_cell)],
        [Paragraph("Trigger ML Pipeline & Tuning (<code>/ai/trigger-training</code>)", table_cell), Paragraph("DENIED", table_cell), Paragraph("EXECUTE", table_cell), Paragraph("EXECUTE", table_cell)],
        [Paragraph("Model Degradation Resolution (<code>/ai/training/resolve</code>)", table_cell), Paragraph("DENIED", table_cell), Paragraph("EXECUTE", table_cell), Paragraph("EXECUTE", table_cell)],
        [Paragraph("User Role Modification (<code>/auth/{user}/role</code>)", table_cell), Paragraph("DENIED", table_cell), Paragraph("DENIED", table_cell), Paragraph("ADMIN ONLY", table_cell)],
    ]
    rbac_table = Table(rbac_data, colWidths=[180, 80, 100, 110])
    rbac_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a8a')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('ALIGN', (1,1), (-1,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 4), ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(rbac_table)
    story.append(Spacer(1, 8))
    story.append(create_image_flowable("excalidraw_02_usecase_diagram.png", max_w=5.8*inch, max_h=3.5*inch))
    story.append(create_caption("Figure 3.0: Global System Use-Case Diagram & Actor Boundaries (Excalidraw Modeling)", styles))
    story.append(Spacer(1, 8))

    story.append(PageTracker('sec3_2'))
    story.append(Paragraph("3.2  Comprehensive Use Case Specifications (UC-01 to UC-08)", h2_style))

    def make_uc_table(uc_id, name, actor, pre_c, post_c, main_flow, alt_flow):
        content = [
            [Paragraph(f"<b>Use Case ID:</b> {uc_id}", table_cell_bold), Paragraph(f"<b>Use Case Name:</b> {name}", table_cell_bold)],
            [Paragraph(f"<b>Primary Actor:</b> {actor}", table_cell), Paragraph(f"<b>Pre-condition:</b> {pre_c}", table_cell)],
            [Paragraph(f"<b>Post-condition:</b> {post_c}", table_cell), ""],
            [Paragraph(f"<b>Main Event Flow:</b><br/>{main_flow}", table_cell), ""],
            [Paragraph(f"<b>Alternative & Exception Flow:</b><br/>{alt_flow}", table_cell), ""],
        ]
        t = Table(content, colWidths=[150, 320])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#94a3b8')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('TOPPADDING', (0,0), (-1,-1), 4), ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('SPAN', (0,2), (1,2)), ('SPAN', (0,3), (1,3)), ('SPAN', (0,4), (1,4)),
        ]))
        return t

    story.append(Paragraph("<b>Table 3.1: Specification for UC-01 & UC-02</b>", h3_style))
    story.append(make_uc_table(
        "UC-01", "User Authentication & Role Routing", "Buyer / Data Scientist / Admin",
        "User possesses registered credentials or initiates registration.",
        "JWT token stored in client localStorage; client routed to designated role dashboard.",
        "1. User navigates to <code>/auth/login</code>.<br/>2. Submits username and password via form.<br/>3. Backend verifies password hash via passlib Bcrypt.<br/>4. Generates signed JWT bearer token containing user_id and role_id.<br/>5. Frontend redirects Buyer &rarr; <code>/</code>, Data Scientist &rarr; <code>/data-science</code>, Admin &rarr; <code>/admin</code>.",
        "3a. Invalid credentials: Return HTTP 401 Unauthorized; display error toast alert.<br/>1b. New user: Submits registration form at <code>/auth/register</code>; account provisioned."
    ))
    story.append(Spacer(1, 8))

    story.append(make_uc_table(
        "UC-02", "Personalized Recommendation Discovery", "Buyer",
        "User authenticated with Buyer role; active ModelVersion loaded.",
        "Personalized Top-12 garment cards rendered with dynamic session adaptations.",
        "1. Buyer navigates to homepage <code>/</code>.<br/>2. Frontend issues request to <code>GET /predict/{user_id}?k=12</code>.<br/>3. Recommendation service retrieves pre-scored Random Forest candidates from <code>user_recommendations</code>.<br/>4. Session Re-ranker fetches in-memory recent interactions (views, cart) and recalculates scores.<br/>5. Returns ordered array of 12 items with image URLs and metadata.",
        "3a. Cold Start Customer (no historical model predictions): Backend queries <code>GET /products/best-sellers</code>; returns top-12 national weekly bestsellers."
    ))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>Table 3.2: Specification for UC-03 & UC-04</b>", h3_style))
    story.append(make_uc_table(
        "UC-03", "Order Submission & Multi-Product Feedback", "Buyer",
        "Items added to shopping cart; valid user session.",
        "Commercial order persisted; interaction feedback logged; customer session vector updated.",
        "1. Buyer inspects cart and clicks 'Checkout'.<br/>2. Frontend sends <code>POST /orders</code> with items and delivery note.<br/>3. System creates Order record in 'pending' status.<br/>4. Buyer completes payment and submits 1-5 star feedback via <code>POST /feedback/{user_id}</code>.<br/>5. Session reranking vector updates; purchased item IDs added to exclusion list.",
        "2a. Inventory depleted: System rejects checkout with HTTP 400 'Insufficient stock'."
    ))
    story.append(Spacer(1, 8))

    story.append(make_uc_table(
        "UC-04", "Exploratory Data Analysis (EDA) Inspection", "Data Scientist",
        "User authenticated with Data Scientist role.",
        "Interactive distribution plots rendered across raw and normalized transaction windows.",
        "1. Data Scientist navigates to <code>/data-science</code>.<br/>2. Frontend fetches report artifacts via <code>GET /ai/reports/eda</code> and insights via <code>GET /ai/insights</code>.<br/>3. System renders daily transaction plots, price distribution histograms, and customer age curves.<br/>4. Displays automated synthetic textual insights highlighting top growing product categories.",
        "2a. Artifacts missing: System returns empty array; prompts user to execute pipeline."
    ))

    story.append(PageBreak())

    story.append(Paragraph("<b>Table 3.3: Specification for UC-05 & UC-06</b>", h3_style))
    story.append(make_uc_table(
        "UC-05", "Trigger Training Pipeline & Parameter Tuning", "Data Scientist",
        "Data Scientist role verified; data files accessible.",
        "Asynchronous worker spawned; execution tracked across 6 standardized milestones.",
        "1. Data Scientist opens <code>/data-science/schedule</code>.<br/>2. Modifies configuration: <code>n_estimators=200</code>, <code>max_depth=12</code>, <code>runner=kaggle</code>.<br/>3. Clicks 'Huấn luyện ngay' (Trigger Training).<br/>4. Frontend sends <code>PUT /ai/training/config</code> followed by <code>POST /ai/trigger-training</code>.<br/>5. Backend acquires threading lock and launches background thread <code>hm-{run_id}</code>.<br/>6. Client polls <code>GET /ai/training/status</code> every 5s, updating visual progress bar.",
        "5a. Lock contention (training already in progress): Server responds with HTTP 409 Conflict."
    ))
    story.append(Spacer(1, 8))

    story.append(make_uc_table(
        "UC-06", "Model Metrics Validation vs. Baselines", "Data Scientist",
        "At least one training run completed successfully.",
        "Comparative metrics and radar charts visualised against baseline algorithms.",
        "1. Data Scientist opens <code>/data-science/metrics</code>.<br/>2. Frontend queries <code>GET /ai/metrics/latest</code>.<br/>3. System renders comparative table displaying MAP@12, Recall@12, Precision@12, and NDCG@12.<br/>4. Highlights improvement deltas (+356% vs Bestseller Baseline; +20.6% vs Repurchase Baseline).<br/>5. Renders interactive multi-axis radar chart showing relative model dominance.",
        "2a. No runs completed: Displays placeholder toast and guides user to Schedule page."
    ))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>Table 3.4: Specification for UC-07 & UC-08</b>", h3_style))
    story.append(make_uc_table(
        "UC-07", "Sliced Error Diagnostics & Feature Importance", "Data Scientist",
        "Model training completed with diagnostics artifacts generated.",
        "Detailed error breakdown rendered by customer activity segments and garment groups.",
        "1. Data Scientist opens <code>/data-science/error-analysis</code>.<br/>2. Frontend queries <code>GET /ai/error-analysis</code>.<br/>3. Renders customer segment breakdown: Cold-Start (0 tx), Low Activity (1-2 tx), Medium (3-10 tx), VIP (>10 tx).<br/>4. Renders product group precision/recall breakdown (Garment Upper, Lower, Shoes, Accessories).<br/>5. Displays Gini feature importance bar chart identifying primary ranking drivers.",
        "3a. Corrupted diagnostics file: System falls back to raw summary metrics."
    ))
    story.append(Spacer(1, 8))

    story.append(make_uc_table(
        "UC-08", "Model Degradation Safety Gate & Resolution", "Data Scientist",
        "Newly finished model run produced MAP@12 inferior to Bestseller baseline.",
        "System enters pending exception state; deployment safely halted until user decision.",
        "1. Pipeline worker finishes Step 5; detects <code>val_map12 < baseline_map12</code>.<br/>2. Worker flags state as <code>worse_than_baseline</code>; halts automatic recommendation table overwrite.<br/>3. Data Scientist inspects notification dialog on web UI.<br/>4. Selects resolution action: 'Keep Old Model' (<code>keep</code>) or 'Force Overwrite' (<code>overwrite</code>).<br/>5. Frontend submits <code>POST /ai/training/resolve</code> with chosen decision.<br/>6. System clears pending state and confirms active model version.",
        "4a. User rejects deployment: System purges pending run artifacts, leaving active model untouched."
    ))

    story.append(PageBreak())

    story.append(PageTracker('sec3_3'))
    story.append(Paragraph("3.3  Sequence Diagrams for Key Execution Flows", h2_style))
    story.append(Paragraph(
        "The following sequence diagrams illustrate the temporal message exchanges between the React client, FastAPI application layer, and backend execution workers.",
        body_style
    ))

    story.append(Spacer(1, 4))
    story.append(create_image_flowable("excalidraw_04_session_rerank_sequence.png", max_w=6.0*inch, max_h=3.4*inch))
    story.append(create_caption("Figure 3.1: Sequence Interaction Diagram for UC-02 Real-Time Session Re-Ranking (Excalidraw Flow)", styles))
    story.append(Spacer(1, 10))

    seq2_text = """
Data Scientist         FastAPI Router         Worker Thread          Kaggle Kernel
      |                      |                      |                      |
      |-- PUT config ------->|                      |                      |
      |-- POST trigger ----->|                      |                      |
      |                      |-- Acquire lock       |                      |
      |                      |-- Spawn worker ----->|                      |
      |<- 202 Accepted ------|                      |                      |
      |                      |                      |-- Push kernel ------>|
      |                      |                      |   hub_pipeline.py    |
      |-- GET status (poll)->|                      |<-- Status: Step 1-5 -|
      |<- Progress: 33% -----|                      |                      |
      |-- GET status (poll)->|                      |<-- Output files -----|
      |                      |                      |    summary.json      |
      |                      |                      |    recs.csv          |
      |                      |                      |-- Baseline check     |
      |                      |                      |-- Write DB Table --->|
      |-- GET status ------->|                      |   user_recommendations
      |<- Status: 'done' ----|                      |                      |
    """
    story.append(Preformatted(seq2_text.strip(), code_style))
    story.append(create_caption("Figure 3.2: Sequence Diagram for UC-05 Background Model Retraining Pipeline", styles))

    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 4: SYSTEM ARCHITECTURE & DATABASE DESIGN
    # =========================================================================
    story.append(PageTracker('ch4'))
    story.append(Paragraph("4  System Architecture & Database Design", h1_style))
    story.append(Spacer(1, 4))

    story.append(PageTracker('sec4_1'))
    story.append(Paragraph("4.1  Enterprise 4-Tier Architecture Overview", h2_style))
    story.append(Paragraph(
        "HUB implements a resilient 4-tier enterprise decoupled architecture designed for high availability, modularity, and rapid inference:",
        body_style
    ))

    story.append(Spacer(1, 4))
    story.append(create_image_flowable("excalidraw_01_architecture_4tier.png", max_w=6.2*inch, max_h=3.5*inch))
    story.append(create_caption("Figure 4.1: Enterprise 4-Tier Modular System Architecture (Excalidraw Visual Blueprint)", styles))
    story.append(Spacer(1, 6))

    story.append(PageTracker('sec4_2'))
    story.append(Paragraph("4.2  Relational Database Schema & Data Dictionary", h2_style))
    story.append(Paragraph(
        "The relational database schema comprises 10 primary tables ensuring Third Normal Form (3NF) compliance across e-commerce transactions and machine learning predictions:",
        body_style
    ))

    erd_text = """
+-------------------+       +-------------------+       +-------------------+
|       users       |       |      orders       |       |    order_items    |
+-------------------+       +-------------------+       +-------------------+
| id (PK, UUID)     |<----->| id (PK, UUID)     |<----->| id (PK, INT)      |
| username (STR)    |       | user_id (FK)      |       | order_id (FK)     |
| email (STR)       |       | total_amount (FLT)|       | product_id (FK)   |
| password_hash(STR)|       | status (INT)      |       | quantity (INT)    |
| role_id (INT)     |       | created_at (DATE) |       | unit_price (FLT)  |
+-------------------+       +-------------------+       +-------------------+
        ^                           ^
        |                           |
+-------------------+       +-------------------+       +-------------------+
|user_customer_link |       |     feedbacks     |       |    cart_items     |
+-------------------+       +-------------------+       +-------------------+
| user_id (PK, FK)  |       | id (PK, UUID)     |       | id (PK, INT)      |
| customer_id (HEX) |       | user_id (FK)      |       | user_id (FK)      |
| created_at (DATE) |       | product_id (FK)   |       | product_id (FK)   |
+-------------------+       | rank (1-5 STARS)  |       | quantity (INT)    |
                            +-------------------+       +-------------------+
        ^
        |
+-------------------+       +-------------------+       +-------------------+
|user_recommendation|       |  model_versions   |       |     products      |
+-------------------+       +-------------------+       +-------------------+
| id (PK, INT)      |       | id (PK, INT)      |       | id (PK, UUID)     |
| user_id (FK)      |<----->| version_name (STR)|       | article_id (STR)  |
| product_id (FK)   |       | run_id (STR)      |       | prod_name (STR)   |
| score (FLOAT)     |       | map12 (FLOAT)     |       | product_group(STR)|
| rank (1-50)       |       | is_active (BOOL)  |       | price (FLOAT)     |
| version_id (FK)   |       +-------------------+       | image_url (STR)   |
+-------------------+                                   +-------------------+
    """
    story.append(Preformatted(erd_text.strip(), code_style))
    story.append(create_caption("Figure 4.2: Relational Database Entity-Relationship Diagram (ERD)", styles))

    story.append(Spacer(1, 10))
    story.append(Paragraph("4.2.1  Relational Database Data Dictionary", h3_style))
    story.append(Paragraph(
        "To ensure strict database integrity and schema governance across microservices, the following data dictionary defines the primary entity attributes, data types, constraints, and operational purposes:",
        body_style
    ))

    dd_data = [
        [Paragraph("Table Name", table_cell_header), Paragraph("Column Name", table_cell_header), Paragraph("Data Type", table_cell_header), Paragraph("Constraints", table_cell_header), Paragraph("Business Function & Description", table_cell_header)],
        [Paragraph("<code>users</code>", table_cell), Paragraph("<code>id</code>", table_cell), Paragraph("UUID", table_cell), Paragraph("PRIMARY KEY", table_cell), Paragraph("Unique internal user identifier", table_cell)],
        [Paragraph("<code>users</code>", table_cell), Paragraph("<code>username</code>", table_cell), Paragraph("VARCHAR(64)", table_cell), Paragraph("UNIQUE, NOT NULL", table_cell), Paragraph("Login username handle", table_cell)],
        [Paragraph("<code>users</code>", table_cell), Paragraph("<code>role_id</code>", table_cell), Paragraph("INTEGER", table_cell), Paragraph("NOT NULL, DEFAULT 1", table_cell), Paragraph("Role: 1=Buyer, 2=Data Scientist, 3=Admin", table_cell)],
        [Paragraph("<code>users</code>", table_cell), Paragraph("<code>password_hash</code>", table_cell), Paragraph("VARCHAR(255)", table_cell), Paragraph("NOT NULL", table_cell), Paragraph("Bcrypt hashed credential string", table_cell)],
        [Paragraph("<code>products</code>", table_cell), Paragraph("<code>id</code>", table_cell), Paragraph("UUID", table_cell), Paragraph("PRIMARY KEY", table_cell), Paragraph("Unique product primary key", table_cell)],
        [Paragraph("<code>products</code>", table_cell), Paragraph("<code>article_id</code>", table_cell), Paragraph("CHAR(10)", table_cell), Paragraph("INDEX, UNIQUE", table_cell), Paragraph("10-digit zero-padded H&M article code", table_cell)],
        [Paragraph("<code>products</code>", table_cell), Paragraph("<code>product_code</code>", table_cell), Paragraph("CHAR(7)", table_cell), Paragraph("INDEX", table_cell), Paragraph("Garment style code (links color variants)", table_cell)],
        [Paragraph("<code>products</code>", table_cell), Paragraph("<code>price</code>", table_cell), Paragraph("FLOAT", table_cell), Paragraph("NOT NULL", table_cell), Paragraph("VND estimated retail price", table_cell)],
        [Paragraph("<code>orders</code>", table_cell), Paragraph("<code>id</code>", table_cell), Paragraph("UUID", table_cell), Paragraph("PRIMARY KEY", table_cell), Paragraph("Unique transaction order identifier", table_cell)],
        [Paragraph("<code>orders</code>", table_cell), Paragraph("<code>user_id</code>", table_cell), Paragraph("UUID", table_cell), Paragraph("FOREIGN KEY (users)", table_cell), Paragraph("Purchasing buyer identifier", table_cell)],
        [Paragraph("<code>orders</code>", table_cell), Paragraph("<code>status</code>", table_cell), Paragraph("INTEGER", table_cell), Paragraph("NOT NULL, DEFAULT 1", table_cell), Paragraph("Status: 1=Pending, 2=Confirmed, 3=Shipped", table_cell)],
        [Paragraph("<code>orders</code>", table_cell), Paragraph("<code>total_amount</code>", table_cell), Paragraph("FLOAT", table_cell), Paragraph("NOT NULL", table_cell), Paragraph("Gross transaction order value (VND)", table_cell)],
        [Paragraph("<code>feedbacks</code>", table_cell), Paragraph("<code>id</code>", table_cell), Paragraph("UUID", table_cell), Paragraph("PRIMARY KEY", table_cell), Paragraph("Unique feedback record key", table_cell)],
        [Paragraph("<code>feedbacks</code>", table_cell), Paragraph("<code>user_id</code>", table_cell), Paragraph("UUID", table_cell), Paragraph("FOREIGN KEY (users)", table_cell), Paragraph("Evaluating user identifier", table_cell)],
        [Paragraph("<code>feedbacks</code>", table_cell), Paragraph("<code>product_id</code>", table_cell), Paragraph("UUID", table_cell), Paragraph("FOREIGN KEY (products)", table_cell), Paragraph("Evaluated garment identifier", table_cell)],
        [Paragraph("<code>feedbacks</code>", table_cell), Paragraph("<code>rank</code>", table_cell), Paragraph("INTEGER", table_cell), Paragraph("CHECK (rank BETWEEN 1 AND 5)", table_cell), Paragraph("Explicit 1 to 5 star customer satisfaction rating", table_cell)],
        [Paragraph("<code>user_rec</code>", table_cell), Paragraph("<code>user_id</code>", table_cell), Paragraph("UUID", table_cell), Paragraph("FOREIGN KEY (users)", table_cell), Paragraph("Target customer for personalized recommendations", table_cell)],
        [Paragraph("<code>user_rec</code>", table_cell), Paragraph("<code>product_id</code>", table_cell), Paragraph("UUID", table_cell), Paragraph("FOREIGN KEY (products)", table_cell), Paragraph("Recommended garment article", table_cell)],
        [Paragraph("<code>user_rec</code>", table_cell), Paragraph("<code>score</code>", table_cell), Paragraph("FLOAT", table_cell), Paragraph("NOT NULL", table_cell), Paragraph("Random Forest posterior probability p_hat(u, i)", table_cell)],
        [Paragraph("<code>user_rec</code>", table_cell), Paragraph("<code>rank</code>", table_cell), Paragraph("INTEGER", table_cell), Paragraph("NOT NULL (1 to 50)", table_cell), Paragraph("Model preference ranking ordinal", table_cell)],
        [Paragraph("<code>user_rec</code>", table_cell), Paragraph("<code>version_id</code>", table_cell), Paragraph("INTEGER", table_cell), Paragraph("FOREIGN KEY (model_versions)", table_cell), Paragraph("Link to active training run ModelVersion", table_cell)],
        [Paragraph("<code>links</code>", table_cell), Paragraph("<code>user_id</code>", table_cell), Paragraph("UUID", table_cell), Paragraph("PRIMARY KEY, FK(users)", table_cell), Paragraph("Authenticated web user UUID", table_cell)],
        [Paragraph("<code>links</code>", table_cell), Paragraph("<code>customer_id</code>", table_cell), Paragraph("CHAR(64)", table_cell), Paragraph("INDEX, NOT NULL", table_cell), Paragraph("H&M 64-character hexadecimal customer hash", table_cell)],
    ]
    dd_table = Table(dd_data, colWidths=[65, 80, 75, 110, 140])
    dd_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a8a')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 2.5), ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 4), ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(dd_table)
    story.append(Spacer(1, 10))


    story.append(PageBreak())

    story.append(PageTracker('sec4_3'))
    story.append(Paragraph("4.3  Comprehensive RESTful API Endpoint Directory", h2_style))
    story.append(Paragraph(
        "The following table provides the exhaustive specification for all 22 production REST endpoints exposed by the FastAPI application:",
        body_style
    ))

    api_data = [
        [Paragraph("Method & Route", table_cell_header), Paragraph("Summary / Function", table_cell_header), Paragraph("Auth Scope", table_cell_header), Paragraph("Success / Status", table_cell_header)],
        [Paragraph("<code>POST /auth/login</code>", table_cell), Paragraph("OAuth2 Password flow; returns JWT bearer token", table_cell), Paragraph("Public", table_cell), Paragraph("200 OK (Token)", table_cell)],
        [Paragraph("<code>POST /auth/register</code>", table_cell), Paragraph("Register new Buyer account with hashed password", table_cell), Paragraph("Public", table_cell), Paragraph("201 Created", table_cell)],
        [Paragraph("<code>GET /users/me</code>", table_cell), Paragraph("Fetch authenticated user profile and active role", table_cell), Paragraph("Bearer Token", table_cell), Paragraph("200 OK (User)", table_cell)],
        [Paragraph("<code>PATCH /auth/{user}/role</code>", table_cell), Paragraph("Elevate or modify user permission role", table_cell), Paragraph("Admin Only", table_cell), Paragraph("200 OK", table_cell)],
        [Paragraph("<code>GET /products/</code>", table_cell), Paragraph("Paginated catalog retrieval with filtering", table_cell), Paragraph("Public / Any", table_cell), Paragraph("200 OK (List)", table_cell)],
        [Paragraph("<code>GET /products/{id}</code>", table_cell), Paragraph("Fetch single product specifications and image", table_cell), Paragraph("Public / Any", table_cell), Paragraph("200 OK", table_cell)],
        [Paragraph("<code>GET /products/best-sellers</code>", table_cell), Paragraph("Retrieve Top-N weekly national bestsellers", table_cell), Paragraph("Public / Any", table_cell), Paragraph("200 OK (List)", table_cell)],
        [Paragraph("<code>GET /predict/{user_id}</code>", table_cell), Paragraph("Generate personalized Top-K recommendations", table_cell), Paragraph("Buyer / Admin", table_cell), Paragraph("200 OK (Scored)", table_cell)],
        [Paragraph("<code>POST /cart</code>", table_cell), Paragraph("Add product to personal shopping cart", table_cell), Paragraph("Buyer", table_cell), Paragraph("201 Created", table_cell)],
        [Paragraph("<code>GET /cart</code>", table_cell), Paragraph("List items currently in shopping cart", table_cell), Paragraph("Buyer", table_cell), Paragraph("200 OK", table_cell)],
        [Paragraph("<code>POST /orders</code>", table_cell), Paragraph("Submit order from cart items", table_cell), Paragraph("Buyer", table_cell), Paragraph("201 Created", table_cell)],
        [Paragraph("<code>POST /feedback/{user_id}</code>", table_cell), Paragraph("Submit 1-5 star product evaluation", table_cell), Paragraph("Buyer", table_cell), Paragraph("201 Created", table_cell)],
        [Paragraph("<code>POST /ai/trigger-training</code>", table_cell), Paragraph("Trigger asynchronous model retraining", table_cell), Paragraph("Data Scientist", table_cell), Paragraph("202 Accepted", table_cell)],
        [Paragraph("<code>GET /ai/training/status</code>", table_cell), Paragraph("Poll current pipeline execution progress (0-6)", table_cell), Paragraph("Data Scientist", table_cell), Paragraph("200 OK (Status)", table_cell)],
        [Paragraph("<code>PUT /ai/training/config</code>", table_cell), Paragraph("Save hyperparameter and schedule configuration", table_cell), Paragraph("Data Scientist", table_cell), Paragraph("200 OK", table_cell)],
        [Paragraph("<code>POST /ai/training/resolve</code>", table_cell), Paragraph("Resolve degradation exception (overwrite/keep)", table_cell), Paragraph("Data Scientist", table_cell), Paragraph("200 OK", table_cell)],
        [Paragraph("<code>GET /ai/metrics/latest</code>", table_cell), Paragraph("Fetch latest validation metrics vs baselines", table_cell), Paragraph("Data Scientist", table_cell), Paragraph("200 OK", table_cell)],
        [Paragraph("<code>GET /ai/error-analysis</code>", table_cell), Paragraph("Retrieve sliced diagnostics and feature importances", table_cell), Paragraph("Data Scientist", table_cell), Paragraph("200 OK", table_cell)],
        [Paragraph("<code>GET /ai/insights</code>", table_cell), Paragraph("Fetch automated synthetic trend & optimization text", table_cell), Paragraph("Data Scientist", table_cell), Paragraph("200 OK", table_cell)],
        [Paragraph("<code>GET /ai/reports/eda</code>", table_cell), Paragraph("List available original and normalized EDA charts", table_cell), Paragraph("Data Scientist", table_cell), Paragraph("200 OK", table_cell)],
        [Paragraph("<code>GET /dashboard/metrics</code>", table_cell), Paragraph("Retrieve operational system metrics and top sales", table_cell), Paragraph("Admin Only", table_cell), Paragraph("200 OK", table_cell)],
        [Paragraph("<code>GET /dashboard/sales</code>", table_cell), Paragraph("Fetch commercial sales summaries and closures", table_cell), Paragraph("Admin Only", table_cell), Paragraph("200 OK", table_cell)],
    ]
    api_table = Table(api_data, colWidths=[120, 160, 90, 100])
    api_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a8a')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5), ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(api_table)

    story.append(Spacer(1, 8))
    story.append(Paragraph("4.4  Testing, Input Validation & Quality Assurance", h2_style))
    story.append(Paragraph(
        "To guarantee robust operational stability and prevent regression, HUB incorporates an automated test suite implemented in <code>pytest</code> "
        "covering API endpoints, Pydantic input schemas, and pipeline services:",
        body_style
    ))

    test_data = [
        [Paragraph("Test Module", table_cell_header), Paragraph("Target Component", table_cell_header), Paragraph("Evaluated Test Scenarios", table_cell_header), Paragraph("Result", table_cell_header)],
        [Paragraph("<code>test_api.py</code>", table_cell), Paragraph("FastAPI Routers & Endpoints", table_cell), Paragraph("Auth token issuance, catalog filtering, cart CRUD, order placement, feedback ranking.", table_cell), Paragraph("17 Passed", table_cell)],
        [Paragraph("<code>test_pipeline.py</code>", table_cell), Paragraph("HM Pipeline & Services", table_cell), Paragraph("Config persistence, state machine, worker lock contention, scheduler catch-up.", table_cell), Paragraph("10 Passed", table_cell)],
        [Paragraph("<b>Total Suite</b>", table_cell_bold), Paragraph("<b>Full Application Stack</b>", table_cell_bold), Paragraph("<b>End-to-end integration, error boundary handling, and schema validation.</b>", table_cell_bold), Paragraph("<b>27 / 27 Passed (100%)</b>", table_cell_bold)],
    ]
    t_test = Table(test_data, colWidths=[90, 120, 190, 70])
    t_test.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a8a')),
        ('BACKGROUND', (0,3), (-1,3), colors.HexColor('#f0fdf4')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('ALIGN', (3,1), (3,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5), ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_test)
    story.append(Spacer(1, 8))

    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 5: DATA PIPELINE, PREPROCESSING & FEATURE ENGINEERING
    # =========================================================================
    story.append(PageTracker('ch5'))
    story.append(Paragraph("5  Data Pipeline, Preprocessing & Feature Engineering", h1_style))
    story.append(Spacer(1, 4))

    story.append(PageTracker('sec5_1'))
    story.append(Paragraph("5.1  H&M Benchmark Characteristics & Raw Data Exploration", h2_style))
    story.append(Paragraph(
        "HUB is trained and evaluated strictly on 100% genuine transaction records from the official Kaggle H&M Personalized Fashion Recommendations benchmark. "
        "The corpus contains <b>31,788,324 purchase logs</b>, <b>105,542 unique articles</b>, and <b>1,371,980 customer accounts</b> spanning from September 2018 to September 2020. "
        "Exploratory Data Analysis reveals critical real-world phenomena:",
        body_style
    ))

    # Embed EDA 3_1_1 and 3_1_2
    story.append(PageTracker('fig5_1'))
    story.append(create_image_flowable("3_1_1_transactions_per_day.png", max_w=5.8*inch, max_h=2.2*inch))
    story.append(create_caption("Figure 5.1: Daily Transaction Volume Across Entire H&M Historical Dataset", styles))

    story.append(Paragraph(
        "Figure 5.1 displays daily transaction volumes across the two-year span. Distinct seasonal spikes correspond to Black Friday promotional surges (late November) "
        "and summer clearance campaigns, alongside a pronounced drop during the initial COVID-19 European retail restrictions in March–April 2020.",
        body_style
    ))

    # Dual EDA images side by side: 3_1_2 Price & 3_1_4 Age
    story.append(PageTracker('fig5_2'))
    img_price = create_image_flowable("3_1_2_price_distribution.png", max_w=2.8*inch, max_h=1.8*inch)
    img_age = create_image_flowable("3_1_4_customer_age.png", max_w=2.8*inch, max_h=1.8*inch)
    eda_dual = Table([[img_price, img_age]], colWidths=[240, 240])
    eda_dual.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
    story.append(eda_dual)
    story.append(create_caption("Figure 5.2: Normalized Price Distribution (Left) & Customer Age Demographic Distribution (Right)", styles))

    story.append(PageTracker('fig5_4'))
    story.append(Paragraph(
        "The price distribution (Figure 5.2, Left) exhibits a heavily right-skewed log-normal characteristic, with over 75% of garments priced between 0.015 and 0.045 (normalized scale). "
        "The customer age demographic (Figure 5.2, Right) displays a bimodal distribution with dominant peaks at age 26 (young professionals / students) and age 51 (mature family buyers). "
        "Approximately 1.2% of customer profiles omit age metadata, which the pipeline imputes with the median age of 32.",
        body_style
    ))

    # Dual EDA images: 3_1_3 Product Groups & 3_1_5 Index Group
    story.append(PageTracker('fig5_3'))
    img_groups = create_image_flowable("3_1_3_product_group_counts.png", max_w=2.8*inch, max_h=1.9*inch)
    img_index = create_image_flowable("3_1_5_index_group_sales.png", max_w=2.8*inch, max_h=1.9*inch)
    eda_dual2 = Table([[img_groups, img_index]], colWidths=[240, 240])
    eda_dual2.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
    story.append(eda_dual2)
    story.append(create_caption("Figure 5.3: Catalog Size Across Product Groups (Left) & Sales by Index Department (Right)", styles))

    story.append(Spacer(1, 10))
    story.append(Paragraph("5.1.1  Normalized Distribution & Candidate Recall Diagnostics", h3_style))
    story.append(Paragraph(
        "To evaluate sampling stability and label equilibrium prior to model fitting, the pipeline generates five diagnostic distribution plots from the normalized training split:",
        body_style
    ))

    # Dual plots: 3_3_2 Purchases per customer & 3_3_3 Longtail article popularity
    img_purchases = create_image_flowable("3_3_2_purchases_per_customer.png", max_w=2.8*inch, max_h=1.8*inch)
    img_longtail = create_image_flowable("3_3_3_article_popularity_longtail.png", max_w=2.8*inch, max_h=1.8*inch)
    norm_dual1 = Table([[img_purchases, img_longtail]], colWidths=[240, 240])
    norm_dual1.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
    story.append(norm_dual1)
    story.append(create_caption("Figure 5.4: Normalized Purchases per Customer (Left) & Longtail Article Popularity Decay (Right)", styles))

    story.append(Paragraph(
        "As illustrated in Figure 5.4 (Right), garment sales follow an extreme power-law distribution where the top 1% of articles generate over 28% of all transaction volume. "
        "The customer transaction density (Figure 5.4, Left) shows that over 65% of active customers make fewer than 3 purchases within the 8-week feature window, "
        "underscoring the absolute necessity of collaborative and popularity fallback heuristics.",
        body_style
    ))

    # Dual plots: 3_3_4 Candidate sources & 3_3_5 Label balance
    img_cand_src = create_image_flowable("3_3_4_candidate_sources.png", max_w=2.8*inch, max_h=1.8*inch)
    img_balance = create_image_flowable("3_3_5_label_balance.png", max_w=2.8*inch, max_h=1.8*inch)
    norm_dual2 = Table([[img_cand_src, img_balance]], colWidths=[240, 240])
    norm_dual2.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
    story.append(norm_dual2)
    story.append(create_caption("Figure 5.5: Stage 1 Candidate Source Recall Distribution (Left) & 1:5 Label Balance (Right)", styles))

    story.append(Paragraph(
        "Figure 5.5 (Left) confirms the synergistic contributions of candidate retrieval channels: Repurchase heuristics capture 4.8% standalone recall, "
        "weekly bestsellers add 3.2%, and age-cohort/co-purchase associations capture an additional 1.4%, achieving an aggregate Candidate Recall of <b>9.43%</b>. "
        "Figure 5.5 (Right) verifies the post-sampling label distribution: positive purchase events constitute exactly 16.7% (1:5 ratio) of the 398,166 training instances.",
        body_style
    ))
    story.append(Spacer(1, 8))


    story.append(PageBreak())

    story.append(PageTracker('sec5_2'))
    story.append(Paragraph("5.2  Strict Temporal Rolling Split (Zero Data Leakage)", h2_style))
    story.append(Paragraph(
        "A catastrophic vulnerability in e-commerce recommender benchmarking is <i>future-to-past data leakage</i>, which occurs when future customer purchases leak into historical feature aggregates. "
        "HUB enforces a mathematically rigorous <b>Strict Temporal Rolling Split</b>:",
        body_style
    ))

    split_diag = """
+-------------------------------------------------------------------------------------------------------+
|                                    TEMPORAL ROLLING SPLIT TIMELINE                                    |
|                                                                                                       |
|  [ Feature Window: 8 Weeks ]--------->| [ Training Target Week: 3 Weeks ]                             |
|  2020-06-24             2020-08-18    | 2020-08-19                2020-09-08                          |
|                                       | (TRAINING LABELS)                                             |
|                                       |                                                               |
|  [ Feature Window: 8 Weeks ]------------------------->| [ Validation Target: 1 Wk ]                   |
|  2020-07-15             2020-09-08                    | 2020-09-09           2020-09-15               |
|                                                       | (VALIDATION LABELS)                           |
|                                                       |                                               |
|  [ Feature Window: 8 Weeks ]------------------------------------------>| [ Test Target: 1 Wk ]        |
|  2020-07-22             2020-09-15                                     | 2020-09-16     2020-09-22    |
|                                                                        | (HOLDOUT TEST LABELS)        |
+-------------------------------------------------------------------------------------------------------+
    """
    story.append(Preformatted(split_diag.strip(), code_style))
    story.append(create_caption("Figure 5.6: Temporal Split Architecture and Feature Rolling Windows", styles))

    story.append(Paragraph(
        "For any target evaluation week starting at cutoff timestamp <i>T<sub>cutoff</sub></i>, feature extraction strictly filters transactions satisfying <i>t_dat < T<sub>cutoff</sub></i>. "
        "User purchase velocity, item bestseller rankings, and interaction recency scores are computed solely from past interactions, guaranteeing zero leakage into the future.",
        body_style
    ))

    story.append(PageTracker('sec5_3'))
    story.append(Paragraph("5.3  Multi-Strategy Candidate Retrieval Algorithms", h2_style))
    story.append(Paragraph(
        "Stage 1 generates up to <i>C = 100</i> candidate articles per customer using four complementary heuristic and graph retrieval channels:",
        body_style
    ))
    story.append(Paragraph("1. <b>Customer Repurchase Channel:</b> Retrieves all articles purchased by customer <i>u</i> within the preceding 4 weeks. Repeat purchases account for ~35% of fast-fashion shopping frequency.", bullet_style))
    story.append(Paragraph("2. <b>Weekly Nationwide Bestsellers:</b> Identifies top-12 most purchased articles nationwide in the most recent 7 days, capturing macro trend velocity.", bullet_style))
    story.append(Paragraph("3. <b>Age-Bucket Bestsellers:</b> Customers are partitioned into 5 age tiers (&lt;20, 20–29, 30–39, 40–49, &ge;50). The top-8 bestsellers within the customer's age cohort are injected.", bullet_style))
    story.append(Paragraph("4. <b>Co-Purchase Graph Associations:</b> For each item purchased by <i>u</i> in the last 14 days, the system retrieves items frequently purchased together in the same basket (co-purchase support count &ge; 5).", bullet_style))

    story.append(PageTracker('sec5_4'))
    story.append(Paragraph("5.4  14-Dimensional Feature Engineering Formulations", h2_style))
    story.append(Paragraph(
        "Each customer-candidate pair (u, i) is converted into a 14-dimensional dense feature vector:",
        body_style
    ))

    features_table_data = [
        [Paragraph("Idx", table_cell_header), Paragraph("Feature Name", table_cell_header), Paragraph("Mathematical Definition / Source", table_cell_header), Paragraph("Intuition & Signal", table_cell_header)],
        [Paragraph("1", table_cell), Paragraph("<code>user_total_purchases</code>", table_cell), Paragraph("<i>|{tx &isin; D | user(tx) = u}|</i>", table_cell), Paragraph("User historical purchase frequency & engagement level", table_cell)],
        [Paragraph("2", table_cell), Paragraph("<code>user_unique_articles</code>", table_cell), Paragraph("<i>|Unique(article &isin; D<sub>u</sub>)|</i>", table_cell), Paragraph("Diversity and exploration tendency of customer", table_cell)],
        [Paragraph("3", table_cell), Paragraph("<code>user_mean_price</code>", table_cell), Paragraph("<i>(1 / N<sub>u</sub>) &Sigma; price(tx)</i>", table_cell), Paragraph("Average spending power / willingness-to-pay", table_cell)],
        [Paragraph("4", table_cell), Paragraph("<code>item_sales_1w</code>", table_cell), Paragraph("<i>|{tx | item = i, t &isin; [T-7, T]}|</i>", table_cell), Paragraph("Immediate short-term weekly sales momentum", table_cell)],
        [Paragraph("5", table_cell), Paragraph("<code>item_sales_2w</code>", table_cell), Paragraph("<i>|{tx | item = i, t &isin; [T-14, T]}|</i>", table_cell), Paragraph("Medium-term bi-weekly trend stability", table_cell)],
        [Paragraph("6", table_cell), Paragraph("<code>item_sales_4w</code>", table_cell), Paragraph("<i>|{tx | item = i, t &isin; [T-28, T]}|</i>", table_cell), Paragraph("Long-term monthly sales baseline", table_cell)],
        [Paragraph("7", table_cell), Paragraph("<code>item_price</code>", table_cell), Paragraph("<i>price(i)</i> normalized to [0, 1]", table_cell), Paragraph("Garment price point", table_cell)],
        [Paragraph("8", table_cell), Paragraph("<code>price_ratio</code>", table_cell), Paragraph("<i>item_price / (user_mean_price + &epsilon;)</i>", table_cell), Paragraph("Affordability relative to user customary spending", table_cell)],
        [Paragraph("9", table_cell), Paragraph("<code>user_bought_item_before</code>", table_cell), Paragraph("<i>&Iopf;(i &isin; D<sub>u</sub>) &isin; {0, 1}</i>", table_cell), Paragraph("Direct repeat purchase propensity signal", table_cell)],
        [Paragraph("10", table_cell), Paragraph("<code>days_since_last_purchase</code>", table_cell), Paragraph("<i>(T<sub>cutoff</sub> - max(t_dat<sub>u</sub>)) / 86400</i>", table_cell), Paragraph("Customer recency decay signal", table_cell)],
        [Paragraph("11", table_cell), Paragraph("<code>sales_channel_ratio</code>", table_cell), Paragraph("<i>Sales<sub>online</sub> / (Sales<sub>total</sub> + &epsilon;)</i>", table_cell), Paragraph("Garment online vs in-store distribution preference", table_cell)],
        [Paragraph("12", table_cell), Paragraph("<code>dept_popularity</code>", table_cell), Paragraph("<i>Sales<sub>dept(i)</sub> / &Sigma; Sales</i>", table_cell), Paragraph("Macro popularity of garment department", table_cell)],
        [Paragraph("13", table_cell), Paragraph("<code>user_dept_affinity</code>", table_cell), Paragraph("<i>|D<sub>u</sub> &cap; dept(i)| / |D<sub>u</sub>|</i>", table_cell), Paragraph("Customer preference for this specific category", table_cell)],
        [Paragraph("14", table_cell), Paragraph("<code>recency_decay_score</code>", table_cell), Paragraph("<i>exp(-&lambda; &Delta; t<sub>u,i</sub>)</i>", table_cell), Paragraph("Exponential temporal decay for prior item interaction", table_cell)],
    ]
    f_table = Table(features_table_data, colWidths=[20, 130, 150, 170])
    f_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a8a')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 4), ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(f_table)

    story.append(PageBreak())

    story.append(PageTracker('sec5_5'))
    story.append(Paragraph("5.5  Background Scheduler & Catch-up Backfill Engine", h2_style))
    story.append(Paragraph(
        "Production recommendation systems require periodic retraining without human developer intervention. "
        "HUB incorporates a lightweight asynchronous daemon scheduler thread within <code>hm_pipeline_service.py</code> that executes every 30 seconds:",
        body_style
    ))
    story.append(Paragraph("• <b>Scheduled 02:00 AM Cron Execution:</b> When the host server clock crosses 02:00 AM local time, if <code>schedule_enabled = True</code> and <code>last_scheduled_date != today</code>, the scheduler automatically triggers a background pipeline run.", bullet_style))
    story.append(Paragraph("• <b>Startup Catch-Up Backfill Mechanism:</b> In development or on-premise environments, host machines are frequently shut down overnight. Upon server startup during the day, the daemon immediately evaluates whether today's scheduled run was missed. If overdue, it executes a catch-up retraining job immediately, ensuring recommendation tables remain fresh without manual intervention.", bullet_style))

    story.append(Spacer(1, 10))

    # =========================================================================
    # CHAPTER 6: AI TRAINING, EXPERIMENTAL EVALUATION & DIAGNOSTICS
    # =========================================================================
    story.append(PageTracker('ch6'))
    story.append(Paragraph("6  AI Training, Experimental Evaluation & Diagnostics", h1_style))
    story.append(Spacer(1, 4))

    story.append(PageTracker('sec6_1'))
    story.append(Paragraph("6.1  Hyperparameter Specifications & Environment", h2_style))
    story.append(Paragraph(
        "The primary ranking model was trained using Scikit-Learn's optimized multi-threaded Random Forest implementation. "
        "Hyperparameters were selected via validation cross-entropy and MAP@12 convergence on held-out validation sets:",
        body_style
    ))

    hyper_data = [
        [Paragraph("Hyperparameter", table_cell_header), Paragraph("Configured Value", table_cell_header), Paragraph("Theoretical & Practical Rationale", table_cell_header)],
        [Paragraph("Number of Trees (<code>n_estimators</code>)", table_cell), Paragraph("<b>200</b>", table_cell), Paragraph("Sufficient ensemble size to stabilize variance; gains beyond 200 trees plateau (<0.01% MAP).", table_cell)],
        [Paragraph("Maximum Tree Depth (<code>max_depth</code>)", table_cell), Paragraph("<b>12</b>", table_cell), Paragraph("Constrains tree complexity to prevent memorization of noise while capturing 3rd-order feature interactions.", table_cell)],
        [Paragraph("Min Samples per Leaf (<code>min_samples_leaf</code>)", table_cell), Paragraph("<b>5</b>", table_cell), Paragraph("Regularization barrier ensuring leaf purchase probability estimates are based on at least 5 instances.", table_cell)],
        [Paragraph("Feature Subsample (<code>max_features</code>)", table_cell), Paragraph("<b>'sqrt' (&asymp; 3)</b>", table_cell), Paragraph("Breiman's theoretical optimum &lfloor;&radic;14&rfloor; = 3 features evaluated per node split.", table_cell)],
        [Paragraph("Negative-to-Positive Ratio", table_cell), Paragraph("<b>5.0</b>", table_cell), Paragraph("Compresses training instances to 398,166 rows, balancing class gradient without severe bias.", table_cell)],
        [Paragraph("Candidate Cutoff (<i>C</i>)", table_cell), Paragraph("<b>100</b>", table_cell), Paragraph("Balances Candidate Recall (9.43%) against memory footprint and scoring latency.", table_cell)],
        [Paragraph("Random Seed", table_cell), Paragraph("<b>42</b>", table_cell), Paragraph("Guarantees deterministic reproducibility across Kaggle and local execution runs.", table_cell)],
    ]
    h_table = Table(hyper_data, colWidths=[140, 90, 240])
    h_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a8a')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 3.5), ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 6), ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(h_table)
    story.append(Spacer(1, 10))

    story.append(PageTracker('sec6_2'))
    story.append(Paragraph("6.2  Experimental Results vs. Baselines (MAP@12, NDCG@12)", h2_style))
    story.append(Paragraph(
        "To establish rigorous academic benchmark validity, the HUB Random Forest model is evaluated alongside two industry-standard baseline systems: "
        "<b>BL1: Weekly Bestsellers</b> (unpersonalized top-12 nationwide popularity) and <b>BL2: Repurchase Recency</b> (user's most recently purchased items padded with bestsellers). "
        "Evaluations were performed across 72,019 active validation customers and holdout test sets:",
        body_style
    ))

    benchmark_data = [
        [Paragraph("Algorithm / Model Architecture", table_cell_header), Paragraph("MAP@12", table_cell_header), Paragraph("Recall@12", table_cell_header), Paragraph("Precision@12", table_cell_header), Paragraph("NDCG@12", table_cell_header), Paragraph("Improvement", table_cell_header)],
        [Paragraph("<b>Baseline 1:</b> Weekly Bestsellers (BL1)", table_cell), Paragraph("0.00660", table_cell), Paragraph("0.02091", table_cell), Paragraph("0.00493", table_cell), Paragraph("0.01260", table_cell), Paragraph("Baseline (0%)", table_cell)],
        [Paragraph("<b>Baseline 2:</b> Repurchase Recency (BL2)", table_cell), Paragraph("0.02498", table_cell), Paragraph("0.04906", table_cell), Paragraph("0.00977", table_cell), Paragraph("0.03592", table_cell), Paragraph("+278.4% vs BL1", table_cell)],
        [Paragraph("<b>HUB:</b> Two-Stage Random Forest (Validation)", table_cell_bold), Paragraph("<b>0.03014</b>", table_cell_bold), Paragraph("<b>0.06274</b>", table_cell_bold), Paragraph("<b>0.01246</b>", table_cell_bold), Paragraph("<b>0.04430</b>", table_cell_bold), Paragraph("<b>+356.6% vs BL1<br/>+20.6% vs BL2</b>", table_cell_bold)],
        [Paragraph("<b>HUB:</b> Two-Stage Random Forest (Test Set)", table_cell_bold), Paragraph("<b>0.03104</b>", table_cell_bold), Paragraph("<b>0.06656</b>", table_cell_bold), Paragraph("<b>0.01313</b>", table_cell_bold), Paragraph("<b>0.04594</b>", table_cell_bold), Paragraph("<b>Consistent Gain</b>", table_cell_bold)],
    ]
    b_table = Table(benchmark_data, colWidths=[150, 60, 60, 65, 65, 70])
    b_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a8a')),
        ('BACKGROUND', (0,3), (-1,3), colors.HexColor('#f0fdf4')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('ALIGN', (1,1), (-1,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 4), ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(b_table)

    story.append(PageBreak())

    story.append(PageTracker('sec6_3'))
    story.append(Paragraph("6.3  Feature Importance Ranking & Interpretation", h2_style))
    story.append(Paragraph(
        "Feature importances derived via total Gini impurity reduction reveal the primary behavioral signals driving garment purchase decisions:",
        body_style
    ))

    importance_data = [
        [Paragraph("Rank", table_cell_header), Paragraph("Feature Name", table_cell_header), Paragraph("Gini Importance", table_cell_header), Paragraph("Cumulative", table_cell_header), Paragraph("Primary Behavioral Impact", table_cell_header)],
        [Paragraph("1", table_cell), Paragraph("<code>item_sales_1w</code>", table_cell), Paragraph("0.2482 (24.8%)", table_cell), Paragraph("24.8%", table_cell), Paragraph("Immediate short-term fashion trend momentum", table_cell)],
        [Paragraph("2", table_cell), Paragraph("<code>user_bought_item_before</code>", table_cell), Paragraph("0.1945 (19.5%)", table_cell), Paragraph("44.3%", table_cell), Paragraph("Brand/style loyalty & repurchase affinity", table_cell)],
        [Paragraph("3", table_cell), Paragraph("<code>user_dept_affinity</code>", table_cell), Paragraph("0.1420 (14.2%)", table_cell), Paragraph("58.5%", table_cell), Paragraph("Customer historical category loyalty (e.g., Womenswear)", table_cell)],
        [Paragraph("4", table_cell), Paragraph("<code>price_ratio</code>", table_cell), Paragraph("0.1115 (11.2%)", table_cell), Paragraph("69.7%", table_cell), Paragraph("Price alignment with user historical spending habit", table_cell)],
        [Paragraph("5", table_cell), Paragraph("<code>item_sales_2w</code>", table_cell), Paragraph("0.0894 (8.9%)", table_cell), Paragraph("78.6%", table_cell), Paragraph("Mid-term trend velocity validation", table_cell)],
        [Paragraph("6", table_cell), Paragraph("<code>recency_decay_score</code>", table_cell), Paragraph("0.0712 (7.1%)", table_cell), Paragraph("85.7%", table_cell), Paragraph("Temporal proximity of prior customer interaction", table_cell)],
        [Paragraph("7", table_cell), Paragraph("<code>days_since_last_purchase</code>", table_cell), Paragraph("0.0490 (4.9%)", table_cell), Paragraph("90.6%", table_cell), Paragraph("Customer active status vs churn dormancy", table_cell)],
        [Paragraph("8-14", table_cell), Paragraph("Remaining 7 Features", table_cell), Paragraph("0.0942 (9.4%)", table_cell), Paragraph("100.0%", table_cell), Paragraph("Catalog baseline, online ratio, customer diversity", table_cell)],
    ]
    imp_table = Table(importance_data, colWidths=[30, 130, 90, 65, 155])
    imp_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a8a')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('ALIGN', (0,1), (0,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(imp_table)
    story.append(Spacer(1, 8))

    story.append(PageTracker('sec6_4'))
    story.append(Paragraph("6.4  Sliced Error Diagnostics Across User Segments", h2_style))
    story.append(Paragraph(
        "To ensure algorithmic fairness and evaluate performance across disparate customer cohorts, the test corpus was sliced across historical interaction volume:",
        body_style
    ))

    sliced_data = [
        [Paragraph("Customer Cohort Slice", table_cell_header), Paragraph("Active Users", table_cell_header), Paragraph("MAP@12", table_cell_header), Paragraph("Recall@12", table_cell_header), Paragraph("Failure Mode Analysis & Remediation Strategy", table_cell_header)],
        [
            Paragraph("<b>Cold-Start</b><br/>(0 prior tx in window)", table_cell),
            Paragraph("18,420 (25.6%)", table_cell),
            Paragraph("0.0071", table_cell),
            Paragraph("0.0215", table_cell),
            Paragraph("Model lacks historical affinity vector; falls back to age bestsellers. Remediated via real-time session reranking upon first click.", table_cell)
        ],
        [
            Paragraph("<b>Low Activity</b><br/>(1–2 prior tx)", table_cell),
            Paragraph("24,150 (33.5%)", table_cell),
            Paragraph("0.0234", table_cell),
            Paragraph("0.0482", table_cell),
            Paragraph("Repurchase channel captures repeat items; candidate pool slightly constrained.", table_cell)
        ],
        [
            Paragraph("<b>Medium Activity</b><br/>(3–10 prior tx)", table_cell),
            Paragraph("22,810 (31.7%)", table_cell),
            Paragraph("0.0412", table_cell),
            Paragraph("0.0894", table_cell),
            Paragraph("Optimal operating regime: rich department affinity and price ratio calibration yield peak performance.", table_cell)
        ],
        [
            Paragraph("<b>VIP Power Users</b><br/>(>10 prior tx)", table_cell),
            Paragraph("6,639 (9.2%)", table_cell),
            Paragraph("0.0589", table_cell),
            Paragraph("0.1345", table_cell),
            Paragraph("High repurchase density and frequent co-purchase associations maximize candidate recall.", table_cell)
        ]
    ]
    sl_table = Table(sliced_data, colWidths=[90, 75, 55, 55, 195])
    sl_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a8a')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 4), ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(sl_table)

    story.append(PageBreak())

    story.append(PageTracker('sec6_5'))
    story.append(Paragraph("6.5  Real-Time Session Re-ranking & Anti-Echo Chamber", h2_style))
    story.append(Paragraph(
        "A static daily recommendation list fails to reflect active user intent. When a buyer visits the store and views winter jackets, the homepage must adapt dynamically without waiting for nightly batch retraining. "
        "HUB implements a real-time <b>Session Re-ranking Engine</b> in <code>services/session_rerank.py</code> operating at inference time:",
        body_style
    ))
    story.append(Paragraph("• <b>Exponential Time-Decay Signal:</b> Recent in-session events decay according to a half-life of <i>t<sub>1/2</sub> = 3.0</i> days: <i>w(t) = w<sub>0</sub> &times; 0.5<sup>&Delta; t / 3.0</sup></i>.", bullet_style))
    story.append(Paragraph("• <b>Interaction Event Weights:</b> <code>VIEWED (+1.0)</code>, <code>ADDED_TO_CART (+2.5)</code>, <code>ADDED_TO_WISHLIST (+3.0)</code>, <code>REMOVED_FROM_CART (-1.0)</code>, <code>REMOVED_FROM_WISHLIST (-2.0)</code>.", bullet_style))
    story.append(Paragraph("• <b>Anti-Echo Chamber & Diversity Filter:</b> Recommending 12 identical garments differing only in color creates a poor user experience. The engine enforces <code>MAX_PER_CODE = 1</code>: only a single color variant of any <code>product_code</code> may appear in the final Top-12 list. Items already purchased or rated &le; 2 stars are strictly purged.", bullet_style))

    story.append(Spacer(1, 10))

    # =========================================================================
    # CHAPTER 7: SYSTEM DEMONSTRATION & GRAPHICAL USER INTERFACE
    # =========================================================================
    story.append(PageTracker('ch7'))
    story.append(Paragraph("7  System Demonstration & Graphical User Interface", h1_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "To provide an enterprise-grade software solution, the HUB system features a rich, responsive Single-Page Application (SPA) "
        "crafted using React 18, TypeScript, Tailwind CSS v3, and Lucide icons. "
        "The interface is segregated into three dedicated workspaces tailored to the operational demands of each stakeholder persona. "
        "The following sub-sections walk through each primary user surface, detailing component architecture, interaction states, and telemetry hooks.",
        body_style
    ))
    story.append(Spacer(1, 6))

    # -------------------------------------------------------------------------
    # 7.1 Multi-Role Authentication Interface
    # -------------------------------------------------------------------------
    story.append(PageTracker('sec7_1'))
    story.append(Paragraph("7.1  Multi-Role Authentication Interface (LoginPage)", h2_style))
    story.append(PageTracker('fig7_1'))
    story.append(create_image_flowable("00_login_page.png", max_w=5.4*inch, max_h=2.5*inch))
    story.append(create_caption("Figure 7.1: Multi-Role Authentication Interface with Instant Demo Credentials", styles))
    story.append(Paragraph(
        "Figure 7.1 presents the unified authentication portal (<code>/auth/login</code>). "
        "To facilitate rapid institutional review and grading, the interface includes one-click demo credentials for Buyer, Data Scientist, and Administrator accounts. "
        "Upon credential submission, the backend authenticates the client via Bcrypt hashing and issues an HMAC-SHA256 signed JWT token containing <code>user_id</code> and <code>role_id</code> claims.",
        body_style
    ))

    login_specs = [
        [Paragraph("UI Element", table_cell_header), Paragraph("Component Specification & Implementation", table_cell_header), Paragraph("Security & Operational Behavior", table_cell_header)],
        [Paragraph("Credential Fields", table_cell), Paragraph("Controlled React inputs with Formik/Zod validation", table_cell), Paragraph("Requires minimum 6 characters; sanitizes input strings.", table_cell)],
        [Paragraph("Demo Switcher", table_cell), Paragraph("ButtonGroup pre-populating role test accounts", table_cell), Paragraph("Switches between 'buyer_test', 'ds_expert', 'kuroisme' (Admin).", table_cell)],
        [Paragraph("Session Vault", table_cell), Paragraph("localStorage token storage with Axios interceptor", table_cell), Paragraph("Injects Authorization: Bearer token header on all subsequent calls.", table_cell)],
    ]
    t_login = Table(login_specs, colWidths=[100, 180, 190])
    t_login.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a8a')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_login)

    story.append(PageBreak())

    # -------------------------------------------------------------------------
    # 7.2 Buyer Storefront & Recommendation Discovery
    # -------------------------------------------------------------------------
    story.append(PageTracker('sec7_2'))
    story.append(Paragraph("7.2  Buyer Personalized Storefront (HomePage)", h2_style))
    story.append(PageTracker('fig7_2'))
    story.append(create_image_flowable("05_buyer_homepage_recommendations.png", max_w=5.4*inch, max_h=3.2*inch))
    story.append(create_caption("Figure 7.2: Buyer Personalized Homepage & AI Recommendation Grid (HomePage)", styles))
    story.append(Paragraph(
        "Figure 7.2 showcases the buyer storefront homepage (<code>/</code>). "
        "The primary visual anchor is the 'Gợi ý dành riêng cho bạn' (Personalized Recommendations) showcase. "
        "The grid renders the Top-12 ranked fashion garments tailored to the logged-in customer's profile, accompanied by promotional hero banners and index department tabs.",
        body_style
    ))

    home_specs = [
        [Paragraph("UI Element", table_cell_header), Paragraph("Component Specification & Implementation", table_cell_header), Paragraph("Algorithmic / Business Logic", table_cell_header)],
        [Paragraph("Recommendation Grid", table_cell), Paragraph("CSS Grid (4 columns desktop, responsive flex mobile)", table_cell), Paragraph("Hydrated from <code>GET /predict/{user_id}</code>; renders Top-12 ranked cards.", table_cell)],
        [Paragraph("Garment Card", table_cell), Paragraph("ProductCard with lazy-loaded image, price, dept tag", table_cell), Paragraph("Displays VND converted pricing, category badge, and hover interactions.", table_cell)],
        [Paragraph("Action Controls", table_cell), Paragraph("Interactive buttons: 'Thêm vào giỏ' and Heart Wishlist", table_cell), Paragraph("Dispatches <code>POST /cart</code> and logs telemetry signal for session reranking.", table_cell)],
        [Paragraph("Fallback Strip", table_cell), Paragraph("BestSellersStrip component for cold-start visitors", table_cell), Paragraph("Automatically surfaces Top-12 national bestsellers when user history is empty.", table_cell)],
    ]
    t_home = Table(home_specs, colWidths=[100, 180, 190])
    t_home.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a8a')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_home)

    story.append(PageBreak())

    # -------------------------------------------------------------------------
    # 7.3 Product Detail & Interaction Feedback
    # -------------------------------------------------------------------------
    story.append(PageTracker('sec7_3'))
    story.append(Paragraph("7.3  Product Detail View & Feedback Rating (ProductDetailPage)", h2_style))
    story.append(PageTracker('fig7_3'))
    story.append(create_image_flowable("06_buyer_product_detail.png", max_w=5.4*inch, max_h=2.6*inch))
    story.append(create_caption("Figure 7.3: Product Detail View & Real-time Interaction Tracking (ProductDetailPage)", styles))
    story.append(Paragraph(
        "Figure 7.3 illustrates the comprehensive garment inspection screen (<code>/product/:id</code>). "
        "Upon route mounting, the client automatically dispatches a <code>VIEWED</code> telemetry interaction to the server. "
        "Buyers can inspect high-resolution photography, read detailed fabric compositions, select sizes, and submit 1-5 star feedback ratings.",
        body_style
    ))

    detail_specs = [
        [Paragraph("UI Element", table_cell_header), Paragraph("Component Specification & Implementation", table_cell_header), Paragraph("Operational Function", table_cell_header)],
        [Paragraph("Telemetry Hook", table_cell), Paragraph("useEffect mounting hook dispatching interaction API", table_cell), Paragraph("Fires <code>POST /feedback</code> with interaction_type='viewed' (+1.0 weight).", table_cell)],
        [Paragraph("Size & Quantity", table_cell), Paragraph("SelectDropdown & NumberInput counter components", table_cell), Paragraph("Enforces inventory stock validation bounds prior to cart dispatch.", table_cell)],
        [Paragraph("Rating Widget", table_cell), Paragraph("5-Star interactive Lucide Star SVG rating bar", table_cell), Paragraph("Submits <code>POST /feedback/{user_id}</code>; ratings <= 2 stars trigger item block.", table_cell)],
        [Paragraph("Similar Items", table_cell), Paragraph("Horizontal scrolling strip of matching product_code items", table_cell), Paragraph("Enables instant exploration of alternative colorways of the same design.", table_cell)],
    ]
    t_detail = Table(detail_specs, colWidths=[100, 180, 190])
    t_detail.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a8a')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_detail)

    story.append(PageBreak())

    # -------------------------------------------------------------------------
    # 7.4 Data Science Exploratory Analysis Dashboard
    # -------------------------------------------------------------------------
    story.append(PageTracker('sec7_4'))
    story.append(Paragraph("7.4  Data Science Exploratory Analysis Dashboard (DataSciencePage)", h2_style))
    story.append(PageTracker('fig7_4'))
    story.append(create_image_flowable("01_ds_eda_page.png", max_w=5.4*inch, max_h=3.2*inch))
    story.append(create_caption("Figure 7.4: Data Science Exploratory Analysis Dashboard (DataSciencePage)", styles))
    story.append(Paragraph(
        "Figure 7.4 presents the Data Science EDA exploration interface (<code>/data-science</code>). "
        "The screen surfaces automated analytical reports compiled directly from the 31.78M Kaggle transaction logs, "
        "empowering machine learning engineers to detect macroeconomic shifts and retail seasonality prior to model retraining.",
        body_style
    ))

    eda_specs = [
        [Paragraph("Dashboard Panel", table_cell_header), Paragraph("Underlying Analytical Chart / Artifact", table_cell_header), Paragraph("Engineering Insight & Value", table_cell_header)],
        [Paragraph("Transaction Volume", table_cell), Paragraph("Daily time-series plot (<code>3_1_1_transactions_per_day.png</code>)", table_cell), Paragraph("Detects promotional surges (Black Friday) and COVID-19 retail anomalies.", table_cell)],
        [Paragraph("Price Distribution", table_cell), Paragraph("Normalized price histogram (<code>3_1_2_price_distribution.png</code>)", table_cell), Paragraph("Visualizes log-normal price density; confirms standard scaling parameters.", table_cell)],
        [Paragraph("Category Velocity", table_cell), Paragraph("Department sales growth bar chart (<code>3_1_5_index_group_sales.png</code>)", table_cell), Paragraph("Identifies fastest-growing garment classes (e.g. Ladieswear vs Divided).", table_cell)],
        [Paragraph("Automated Insights", table_cell), Paragraph("Synthetic insight cards generated from <code>GET /ai/insights</code>", table_cell), Paragraph("Summarizes category growth percentages and recommends feature adjustments.", table_cell)],
    ]
    t_eda = Table(eda_specs, colWidths=[105, 185, 180])
    t_eda.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a8a')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_eda)

    story.append(PageBreak())

    # -------------------------------------------------------------------------
    # 7.5 Model Performance Validation & Radar Benchmarking
    # -------------------------------------------------------------------------
    story.append(PageTracker('sec7_5'))
    story.append(Paragraph("7.5  Model Metrics Validation & Benchmark Radar (ModelMetricsPage)", h2_style))
    story.append(PageTracker('fig7_5'))
    story.append(create_image_flowable("02_ds_model_metrics.png", max_w=5.4*inch, max_h=2.7*inch))
    story.append(create_caption("Figure 7.5: Model Performance Validation & Baseline Benchmark Radar (ModelMetricsPage)", styles))
    story.append(Paragraph(
        "Figure 7.5 illustrates the model evaluation workspace (<code>/data-science/metrics</code>). "
        "Top metric summary cards present official benchmark scores: MAP@12 (0.03014), Recall@12 (0.06274), and NDCG@12 (0.04430). "
        "A multi-axis radar chart visualizes the multi-metric superiority of the HUB Random Forest model against the Bestseller and Repurchase baselines.",
        body_style
    ))

    metric_specs = [
        [Paragraph("Evaluation Widget", table_cell_header), Paragraph("Component Specification & Implementation", table_cell_header), Paragraph("Evaluated Metric & Target", table_cell_header)],
        [Paragraph("Score Summary Cards", table_cell), Paragraph("MetricCard with improvement badge vs baseline", table_cell), Paragraph("Validates +356% MAP gain over Bestsellers and +20.6% over Repurchase.", table_cell)],
        [Paragraph("Multi-Axis Radar", table_cell), Paragraph("Chart.js / SVG Radar canvas comparing 3 models", table_cell), Paragraph("Spans MAP@12, Recall@12, Precision@12, NDCG@12, Candidate Recall.", table_cell)],
        [Paragraph("Temporal Split Card", table_cell), Paragraph("Card displaying active Train, Val, and Test dates", table_cell), Paragraph("Confirms temporal integrity: Train (Aug 19-Sep 08), Val (Sep 09-Sep 15).", table_cell)],
        [Paragraph("Run History Table", table_cell), Paragraph("Paginated table of all historic training executions", table_cell), Paragraph("Tracks run_id, subset mode, tree count, depth, and status ('written').", table_cell)],
    ]
    t_metric = Table(metric_specs, colWidths=[105, 185, 180])
    t_metric.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a8a')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_metric)

    story.append(PageBreak())

    # -------------------------------------------------------------------------
    # 7.6 Sliced Error Diagnostics
    # -------------------------------------------------------------------------
    story.append(PageTracker('sec7_6'))
    story.append(Paragraph("7.6  Sliced Error Diagnostics & Feature Importance (ErrorAnalysisPage)", h2_style))
    story.append(PageTracker('fig7_6'))
    story.append(create_image_flowable("03_ds_error_analysis.png", max_w=5.4*inch, max_h=2.7*inch))
    story.append(create_caption("Figure 7.6: Sliced Error Diagnostics by Activity & Department (ErrorAnalysisPage)", styles))
    story.append(Paragraph(
        "Figure 7.6 showcases the diagnostic deep-dive interface (<code>/data-science/error-analysis</code>). "
        "The interface partitions test evaluations across customer activity tiers (Cold-Start, Low, Medium, VIP) "
        "and garment departments, alongside a horizontal Gini feature importance bar chart identifying primary ranking drivers.",
        body_style
    ))

    error_specs = [
        [Paragraph("Diagnostic Module", table_cell_header), Paragraph("Visual Breakdown & Tabular Structure", table_cell_header), Paragraph("Diagnostic Purpose & Failure Mode", table_cell_header)],
        [Paragraph("Customer Slices", table_cell), Paragraph("4-row table: Cold (0 tx), Low (1-2), Med (3-10), VIP (>10)", table_cell), Paragraph("Pinpoints cold-start bottleneck (MAP=0.0071 vs VIP MAP=0.0589).", table_cell)],
        [Paragraph("Department Slices", table_cell), Paragraph("Breakdown across Garment Upper, Lower, Shoes, Access", table_cell), Paragraph("Verifies balanced precision across major fast-fashion retail categories.", table_cell)],
        [Paragraph("Feature Importance", table_cell), Paragraph("Horizontal bar chart of top 10 features by Gini reduction", table_cell), Paragraph("Validates item_sales_1w (24.8%) and repurchase flag (19.5%) dominance.", table_cell)],
        [Paragraph("Candidate Sources", table_cell), Paragraph("Pie / Stacked bar chart of Stage 1 channel recall", table_cell), Paragraph("Confirms 9.43% aggregate recall across the 4 candidate heuristics.", table_cell)],
    ]
    t_error = Table(error_specs, colWidths=[105, 185, 180])
    t_error.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a8a')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_error)

    story.append(PageBreak())

    # -------------------------------------------------------------------------
    # 7.7 Training Schedule & Pipeline Automation
    # -------------------------------------------------------------------------
    story.append(PageTracker('sec7_7'))
    story.append(Paragraph("7.7  Automated Training Scheduler & Hyperparameter Tuning (TrainingSchedulePage)", h2_style))
    story.append(PageTracker('fig7_7'))
    story.append(create_image_flowable("04_ds_training_schedule.png", max_w=5.4*inch, max_h=2.8*inch))
    story.append(create_caption("Figure 7.7: Automated Training Scheduler & Hyperparameter Tuning (TrainingSchedulePage)", styles))
    story.append(Paragraph(
        "Figure 7.7 presents the training orchestration dashboard (<code>/data-science/schedule</code>). "
        "Data scientists can configure hyperparameters (trees, depth, sample fraction), toggle daily 02:00 AM automation, "
        "trigger on-demand execution, and monitor active training progress via a 6-step visual progress stepper.",
        body_style
    ))

    sched_specs = [
        [Paragraph("Control Widget", table_cell_header), Paragraph("Component Specification & Implementation", table_cell_header), Paragraph("Operational Function", table_cell_header)],
        [Paragraph("Config Form", table_cell), Paragraph("Inputs: n_estimators, max_depth, runner ('kaggle'/'local')", table_cell), Paragraph("Persists parameters to runs/state.json via <code>PUT /ai/training/config</code>.", table_cell)],
        [Paragraph("Schedule Toggle", table_cell), Paragraph("ToggleSwitch for daily 02:00 AM daemon execution", table_cell), Paragraph("Enables background cron scheduler and startup catch-up backfilling.", table_cell)],
        [Paragraph("Trigger Button", table_cell), Paragraph("Primary action button spawning asynchronous worker thread", table_cell), Paragraph("Dispatches <code>POST /ai/trigger-training</code>; acquires thread execution lock.", table_cell)],
        [Paragraph("6-Step Progress Stepper", table_cell), Paragraph("Dynamic stepper: Split &rarr; Cand &rarr; Feat &rarr; Fit &rarr; Eval &rarr; Write", table_cell), Paragraph("Client polls <code>GET /ai/training/status</code> every 5s; displays real-time progress.", table_cell)],
    ]
    t_sched = Table(sched_specs, colWidths=[105, 185, 180])
    t_sched.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a8a')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_sched)

    story.append(PageBreak())

    # -------------------------------------------------------------------------
    # 7.8 Administrator Commercial Dashboard
    # -------------------------------------------------------------------------
    story.append(PageTracker('sec7_8'))
    story.append(Paragraph("7.8  Executive Commercial Dashboard & Operations (AdminDashboardPage)", h2_style))
    story.append(PageTracker('fig7_8'))
    story.append(create_image_flowable("07_admin_dashboard.png", max_w=5.4*inch, max_h=2.8*inch))
    story.append(create_caption("Figure 7.8: Executive Operations & Commercial Sales Monitoring (AdminDashboardPage)", styles))
    story.append(Paragraph(
        "Figure 7.8 depicts the executive administrative dashboard (<code>/admin</code>). "
        "The control center aggregates commercial gross revenue metrics, monitors incoming orders, showcases top-performing products by revenue, "
        "and provides administrative controls for managing catalog products and customer identity links.",
        body_style
    ))

    admin_specs = [
        [Paragraph("Executive Widget", table_cell_header), Paragraph("Component Specification & Implementation", table_cell_header), Paragraph("Commercial / Operational Impact", table_cell_header)],
        [Paragraph("Revenue KPI Cards", table_cell), Paragraph("Summary statistics cards displaying GMV and orders", table_cell), Paragraph("Hydrated from <code>GET /dashboard/metrics</code>; reflects real-time sales.", table_cell)],
        [Paragraph("Top Sold Products", table_cell), Paragraph("Table listing items ranked by units sold and revenue", table_cell), Paragraph("Correlates high-ranking AI recommendations with commercial sales uplift.", table_cell)],
        [Paragraph("Order Lifecycle Tab", table_cell), Paragraph("Order management table with status dropdown transitions", table_cell), Paragraph("Enables admins to advance orders from 'Pending' to 'Shipped' or 'Delivered'.", table_cell)],
        [Paragraph("Customer Linkages", table_cell), Paragraph("Account mapping viewer (<code>/ai/customer-links</code>)", table_cell), Paragraph("Links web authentication accounts to Kaggle 64-hex customer identities.", table_cell)],
    ]
    t_admin = Table(admin_specs, colWidths=[105, 185, 180])
    t_admin.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a8a')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_admin)

    story.append(PageBreak())
    story.append(Paragraph("8  Conclusion & Future Roadmap", h1_style))
    story.append(Spacer(1, 4))

    story.append(PageTracker('sec8_1'))
    story.append(Paragraph("8.1  Summary of System Contributions", h2_style))
    story.append(Paragraph(
        "The HUB Intelligent Recommendation System delivers an end-to-end production solution for fast-fashion e-commerce. Key technical contributions include:",
        body_style
    ))
    story.append(Paragraph("• <b>Rigorously Proven Ranking Accuracy:</b> Achieved a validation MAP@12 of <b>0.03014</b>, outperforming standard Bestseller baselines by <b>+356.6% (4.5&times;)</b> and Repurchase baselines by <b>+20.6%</b> on 100% genuine H&M benchmark data.", bullet_style))
    story.append(Paragraph("• <b>Zero Data Leakage Guarantee:</b> Formulated a strict temporal rolling window split ensuring all behavioral features strictly precede target evaluation timestamps.", bullet_style))
    story.append(Paragraph("• <b>Real-time Session Adaptivity:</b> Deployed an inference-time session re-ranking engine with exponential half-life decay (t<sub>1/2</sub> = 3 days) and anti-echo chamber diversity filters, delivering recommendations in <50ms.", bullet_style))
    story.append(Paragraph("• <b>Automated Enterprise Operations:</b> Implemented a background scheduler with automated startup catch-up backfilling and safety degradation gates preventing bad model deployment.", bullet_style))

    story.append(PageTracker('sec8_2'))
    story.append(Paragraph("8.2  Technical Limitations & Enterprise Roadmap", h2_style))
    story.append(Paragraph(
        "Despite robust performance, two inherent architectural limitations remain to be addressed in future enterprise iterations:",
        body_style
    ))
    story.append(Paragraph("• <b>Stage 1 Candidate Retrieval Ceiling:</b> The heuristic candidate generation phase captures 9.43% of eventual purchases, placing an upper theoretical ceiling on Stage 2 recall.", bullet_style))
    story.append(Paragraph("• <b>Pointwise Binary Approximation:</b> Pointwise binary classification optimizes independent instance margins rather than directly maximizing listwise discounted cumulative gain.", bullet_style))
    story.append(Paragraph(
        "To surpass these boundaries, the project defines a structured 3-phase technical roadmap:",
        body_style
    ))
    story.append(Paragraph("1. <b>Two-Tower Deep Neural Embeddings (Phase 1):</b> Replace heuristic candidate generation with dual-encoder User and Item neural networks. Projecting customers and garments into a shared 64-dimensional vector space enables Maximum Inner Product Search (MIPS) via ScaNN or FAISS, expanding candidate recall from 9.4% to >25%.", bullet_style))
    story.append(Paragraph("2. <b>Listwise LambdaMART Objective (Phase 2):</b> Transition Stage 2 from Random Forest pointwise classification to LightGBM LambdaMART ranker with pairwise gradients optimizing NDCG@12 directly.", bullet_style))
    story.append(Paragraph("3. <b>Streaming Online Feature Stores (Phase 3):</b> Deploy Redis and Kafka to track live purchase counters and item velocity in sub-second windows.", bullet_style))

    story.append(Spacer(1, 8))
    story.append(Paragraph("8.3  Team Contribution Statement", h2_style))
    story.append(Paragraph(
        "In accordance with HCMUT academic project guidelines, team members contributed equally (50% / 50%) across all development and research stages:",
        body_style
    ))

    contrib_data = [
        [Paragraph("Student Name & ID", table_cell_header), Paragraph("Assigned Technical Modules & Responsibilities", table_cell_header), Paragraph("Contribution", table_cell_header)],
        [
            Paragraph("<b>Dao Duy Dat</b><br/>ID: 2352223", table_cell),
            Paragraph("• AI Pipeline: Candidate Generation heuristics, Negative Sampling, Random Forest fitting.<br/>• Backend: FastAPI routing, recommendation service, session re-ranking engine.<br/>• Evaluation: MAP@12, NDCG@12 metric validation, Kaggle benchmark integration.", table_cell),
            Paragraph("<b>50%</b>", table_cell)
        ],
        [
            Paragraph("<b>Phan Tien Huy</b><br/>ID: 2352402", table_cell),
            Paragraph("• Frontend: React 18 SPA architecture, Tailwind CSS UI components, Vite tooling.<br/>• Observability: Data Science EDA dashboard, model metrics radar charts, error slices.<br/>• DevOps & QA: Pytest test suite (27 tests), database schema design, ReportLab PDF generator.", table_cell),
            Paragraph("<b>50%</b>", table_cell)
        ],
    ]
    t_contrib = Table(contrib_data, colWidths=[110, 300, 60])
    t_contrib.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a8a')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('ALIGN', (2,1), (2,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 4), ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5), ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_contrib)
    story.append(Spacer(1, 8))

    story.append(Paragraph("8.4  Declaration of Generative AI Use", h2_style))
    story.append(Paragraph(
        "<b>Institutional Transparency Statement:</b> During the development of the HUB system and the compilation of this academic report, "
        "the team utilized Generative AI tools (Antigravity by Google DeepMind and OpenAI Codex) as an agentic pair-programming assistant, "
        "peer reviewer, and automated ReportLab PDF layout generator. "
        "Specifically: AI was employed for boilerplate code scaffolding, writing unit tests, and cross-checking mathematical formulas against the codebase. "
        "All core algorithms, machine learning model architectures, training executions on Kaggle H&M data, database schemas, "
        "and critical software decisions were designed, verified, and audited by the student authors.",
        body_style
    ))
    story.append(Spacer(1, 10))

    # =========================================================================
    # REFERENCES (IEEE Standard)
    # =========================================================================
    story.append(PageTracker('ref_sec'))
    story.append(Paragraph("References", h1_style))
    references = [
        "[1] L. Breiman, \"Random Forests,\" <i>Machine Learning</i>, vol. 45, no. 1, pp. 5–32, Oct. 2001.",
        "[2] J. R. Quinlan, \"Induction of Decision Trees,\" <i>Machine Learning</i>, vol. 1, no. 1, pp. 81–106, Mar. 1986.",
        "[3] H&M Group, \"H&M Personalized Fashion Recommendations: Kaggle Competition Dataset,\" Kaggle Inc., 2022. [Online]. Available: https://www.kaggle.com/competitions/h-and-m-personalized-fashion-recommendations",
        "[4] F. Pedregosa <i>et al.</i>, \"Scikit-learn: Machine Learning in Python,\" <i>Journal of Machine Learning Research</i>, vol. 12, pp. 2825–2830, Nov. 2011.",
        "[5] P. Covington, J. Adams, and E. Sargin, \"Deep Neural Networks for YouTube Recommendations,\" in <i>Proceedings of the 10th ACM Conference on Recommender Systems (RecSys '16)</i>, Boston, MA, USA, 2016, pp. 191–198.",
        "[6] H. Steck, \"Calibrated Recommendations,\" in <i>Proceedings of the 12th ACM Conference on Recommender Systems (RecSys '18)</i>, Vancouver, BC, Canada, 2018, pp. 154–162.",
        "[7] C. Burges <i>et al.</i>, \"Learning to Rank using Gradient Descent,\" in <i>Proceedings of the 22nd International Conference on Machine Learning (ICML '05)</i>, Bonn, Germany, 2005, pp. 89–96.",
        "[8] G. Ke <i>et al.</i>, \"LightGBM: A Highly Efficient Gradient Boosting Decision Tree,\" in <i>Advances in Neural Information Processing Systems (NeurIPS '17)</i>, Long Beach, CA, USA, 2017, pp. 3146–3154."
    ]
    for ref in references:
        story.append(Paragraph(ref, ParagraphStyle('RefEntry', parent=body_style, leftIndent=18, firstLineIndent=-18, spaceAfter=5)))

    return story


# ---------------------------------------------------------------------------
# Two-Pass PDF Build Runner
# ---------------------------------------------------------------------------
def build_pdf_report(output_path='D:\\HTTM\\REPORT_INTELLIGENT_SYSTEMS_HUB.pdf'):
    global PAGE_DICT

    print("=== PASS 1: Dry-run compilation to record exact flowable page numbers ===")
    PAGE_DICT.clear()
    doc_dry = SimpleDocTemplate(
        output_path, pagesize=A4,
        leftMargin=54, rightMargin=54, topMargin=54, bottomMargin=54
    )
    story_pass1 = build_story(page_dict={})
    doc_dry.build(story_pass1, canvasmaker=NumberedCanvas)
    recorded_pages = dict(PAGE_DICT)
    print(f"Recorded page mapping: {recorded_pages}")

    print("=== PASS 2: Final publication compilation with synchronized Table of Contents ===")
    doc_final = SimpleDocTemplate(
        output_path, pagesize=A4,
        leftMargin=54, rightMargin=54, topMargin=54, bottomMargin=54
    )
    story_pass2 = build_story(page_dict=recorded_pages)
    doc_final.build(story_pass2, canvasmaker=NumberedCanvas)
    print(f"Successfully generated publication-grade academic report PDF at: {output_path}")

if __name__ == '__main__':
    target = sys.argv[1] if len(sys.argv) > 1 else r'D:\HTTM\REPORT_INTELLIGENT_SYSTEMS_HUB.pdf'
    build_pdf_report(target)
