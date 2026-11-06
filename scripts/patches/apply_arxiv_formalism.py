def update_vietnamese_report():
    with open('D:/HTTM/generate_pdf_report_vi.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Font registration & math constants
    old_font_reg = '''pdfmetrics.registerFont(TTFont('Arial', r'C:\\Windows\\Fonts\\arial.ttf'))
pdfmetrics.registerFont(TTFont('Arial-Bold', r'C:\\Windows\\Fonts\\arialbd.ttf'))
pdfmetrics.registerFont(TTFont('Arial-Italic', r'C:\\Windows\\Fonts\\ariali.ttf'))'''

    new_font_reg = '''pdfmetrics.registerFont(TTFont('Arial', r'C:\\Windows\\Fonts\\arial.ttf'))
pdfmetrics.registerFont(TTFont('Arial-Bold', r'C:\\Windows\\Fonts\\arialbd.ttf'))
pdfmetrics.registerFont(TTFont('Arial-Italic', r'C:\\Windows\\Fonts\\ariali.ttf'))
pdfmetrics.registerFont(TTFont('SegoeUISymbol', r'C:\\Windows\\Fonts\\seguisym.ttf'))

# Ký hiệu Toán học chuẩn ấn phẩm arXiv / IEEE
ASSIGN = '<font name="SegoeUISymbol">\\u2190</font>'
IN = '<font name="SegoeUISymbol">\\u2208</font>'
NOTIN = '<font name="SegoeUISymbol">\\u2209</font>'
EMPTY = '<font name="SegoeUISymbol">\\u2205</font>'
UNION = '<font name="SegoeUISymbol">\\u222a</font>'
INTERSECT = '<font name="SegoeUISymbol">\\u2229</font>'
SETMINUS = '<font name="SegoeUISymbol">\\u2216</font>'
EXISTS = '<font name="SegoeUISymbol">\\u2203</font>'
FORALL = '<font name="SegoeUISymbol">\\u2200</font>'
AND = '<font name="SegoeUISymbol">\\u2227</font>'
OR = '<font name="SegoeUISymbol">\\u2228</font>'
TIMES = '<font name="SegoeUISymbol">\\u00d7</font>'
LE = '<font name="SegoeUISymbol">\\u2264</font>'
GE = '<font name="SegoeUISymbol">\\u2265</font>'
SUM = '<font name="SegoeUISymbol">\\u2211</font>'
LAMBDA = '&lambda;'
DELTA = '&Delta;'
CONCAT = '<font name="SegoeUISymbol">\\u2295</font>'
DOT = '<font name="SegoeUISymbol">\\u22c5</font>' '''

    if old_font_reg in content:
        content = content.replace(old_font_reg, new_font_reg, 1)

    # 2. Add build_arxiv_algorithm and build_arxiv_equation helpers
    helpers_vi = '''def create_caption(text, styles):
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
'''
    if "def create_caption(text, styles):\n    return Paragraph(f\"<b>{text}</b>\", styles['CaptionStyleVI'])" in content:
        content = content.replace("def create_caption(text, styles):\n    return Paragraph(f\"<b>{text}</b>\", styles['CaptionStyleVI'])", helpers_vi, 1)

    # 3. Replace Công thức 2.1 đến 2.4 trong VI
    old_eq_vi = '''    story.append(Paragraph("• <b>Độ đo Tạp chất Gini (Gini Impurity):</b> Tại mỗi nút nội bộ của cây quyết định, độ vẩn đục Gini của tập mẫu <i>S</i> kích thước <i>N</i> được tính toán:", bullet_style))
    story.append(Paragraph("<b>Công thức 2.1:</b> &nbsp;&nbsp; <i>I<sub>G</sub>(S) = 1 - &Sigma;<sub>c=0</sub><sup>1</sup> p<sub>c</sub><sup>2</sup> = 2 p<sub>0</sub> p<sub>1</sub></i>", eq_style))
    story.append(Paragraph("• <b>Độ Lợi Thông Tin (Gini Gain):</b> Khi phân chia tập <i>S</i> thành 2 tập con <i>S<sub>L</sub></i> và <i>S<sub>R</sub></i> theo ngưỡng &theta; của đặc trưng <i>j</i>:", bullet_style))
    story.append(Paragraph("<b>Công thức 2.2:</b> &nbsp;&nbsp; <i>&Delta;I<sub>G</sub>(S, j, &theta;) = I<sub>G</sub>(S) - [ (|S<sub>L</sub>|/|S|) I<sub>G</sub>(S<sub>L</sub>) + (|S<sub>R</sub>|/|S|) I<sub>G</sub>(S<sub>R</sub>) ]</i>", eq_style))
    story.append(Paragraph(
        "Cặp tối ưu <i>(j*, &theta;*)</i> được tìm kiếm thông qua việc tối đa hóa &Delta;I<sub>G</sub>. "
        "Để khắc phục nhược điểm phương sai lớn của cây quyết định đơn lẻ, Leo Breiman áp dụng hai cơ chế ngẫu nhiên hóa:",
        body_style
    ))
    story.append(Paragraph("• <b>Đóng gói mẫu (Bootstrap Aggregation - Bagging):</b> Với <i>B = 200</i> cây, mỗi cây <i>T<sub>b</sub></i> được huấn luyện trên tập dữ liệu D<sup>(b)</sup> rút trích có hoàn lại từ D. Xác suất một mẫu dữ liệu bị bỏ sót (Out-of-Bag - OOB) đạt xấp xỉ lý thuyết:", bullet_style))
    story.append(Paragraph("<b>Công thức 2.3:</b> &nbsp;&nbsp; <i>lim<sub>N &rarr; &infin;</sub> (1 - 1/N)<sup>N</sup> = 1/e &asymp; 0.368 (36.8% mẫu OOB dùng kiểm định chéo miễn phí)</i>", eq_style))
    story.append(Paragraph("• <b>Giảm phương sai nhờ chọn ngẫu nhiên đặc trưng:</b> Tại mỗi nút, chỉ có <i>m = &lfloor;&radic;14&rfloor; = 3</i> đặc trưng được chọn ngẫu nhiên để đánh giá. Phương sai của mô hình trung bình thỏa mãn:", bullet_style))
    story.append(Paragraph("<b>Công thức 2.4:</b> &nbsp;&nbsp; <i>Var((1/B) &Sigma;<sub>b=1</sub><sup>B</sup> T<sub>b</sub>(x)) = &rho; &sigma;<sup>2</sup> + ((1 - &rho;) / B) &sigma;<sup>2</sup></i>", eq_style))'''

    new_eq_vi = '''    story.append(Paragraph("• <b>Độ đo Tạp chất Gini (Gini Impurity):</b> Tại mỗi nút nội bộ của cây quyết định, độ vẩn đục Gini của tập mẫu <i>S</i> kích thước <i>N</i> được tính toán:", bullet_style))
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
    story.append(Paragraph("• <b>Giảm phương sai nhờ chọn ngẫu nhiên đặc trưng:</b> Tại mỗi nút, chỉ có <i>m = &lfloor;&radic;14&rfloor; = 3</i> đặc trưng được chọn ngẫu nhiên để đánh giá. Phương sai của mô hình trung bình thỏa mãn:", bullet_style))
    story.append(Spacer(1, 2))
    story.append(build_arxiv_equation("2.4", f"Var<font size=9.5>(</font>(1/<i>B</i>) {SUM}<sub><i>b</i>=1</sub><sup><i>B</i></sup> <i>T<sub>b</sub></i>(<b>x</b>)<font size=9.5>)</font> = &rho; &sigma;<sup>2</sup> + ((1 - &rho;) / <i>B</i>) &sigma;<sup>2</sup>"))
    story.append(Spacer(1, 4))'''

    if old_eq_vi in content:
        content = content.replace(old_eq_vi, new_eq_vi, 1)

    # 4. Replace Section 2.3 algorithm block by index slice
    idx1 = content.find('algo1_vi =')
    idx2 = content.find('story.append(PageBreak())', idx1)
    assert idx1 != -1 and idx2 != -1, "Algorithms block slice in VI not found"

    new_algos_vi = '''steps1_vi = [
        (1, f"<i>C<sub>u</sub></i> {ASSIGN} {EMPTY}"),
        (2, f"<i>C</i><sub>repurchase</sub> {ASSIGN} {{<i>i</i> {IN} <i>I</i> | {EXISTS} (<i>u</i>, <i>i</i>, <i>t</i>) {IN} <i>D</i> {AND} <i>t</i> {GE} <i>T</i><sub>cutoff</sub> - 28d}}"),
        (3, f"<i>C</i><sub>bestseller</sub> {ASSIGN} TopK({{<i>i</i> {IN} <i>I</i> | doanh_số(<i>i</i>, [<i>T</i><sub>cutoff</sub> - 7d, <i>T</i><sub>cutoff</sub>])}}, <i>K</i> = 12)"),
        (4, f"<i>C</i><sub>age</sub> {ASSIGN} TopK({{<i>i</i> {IN} <i>I</i> | doanh_số_theo_nhóm_tuổi(<i>i</i>, nhóm_tuổi(<i>u</i>))}}, <i>K</i> = 8)"),
        (5, f"<i>C</i><sub>copurchase</sub> {ASSIGN} {{<i>j</i> {IN} <i>I</i> | {EXISTS} <i>i</i> {IN} <i>C</i><sub>repurchase</sub> {AND} tần_suất_cùng_mua(<i>i</i>, <i>j</i>) {GE} 5}}"),
        (6, f"<i>C<sub>u</sub></i> {ASSIGN} GiớiHạn(<i>C</i><sub>repurchase</sub> {UNION} <i>C</i><sub>bestseller</sub> {UNION} <i>C</i><sub>age</sub> {UNION} <i>C</i><sub>copurchase</sub>, <i>C</i><sub>max</sub> = 100)"),
        (7, f"<i>Y</i><sub>thật</sub> {ASSIGN} {{<i>i</i> {IN} <i>I</i> | {EXISTS} (<i>u</i>, <i>i</i>, <i>t</i>) {IN} <i>D</i> {AND} <i>t</i> {IN} [<i>T</i><sub>cutoff</sub>, <i>T</i><sub>cutoff</sub> + 7d]}}"),
        (8, f"<b>MẫuDương</b> {ASSIGN} {{(<i>u</i>, <i>i</i>, 1) | <i>i</i> {IN} (<i>C<sub>u</sub></i> {INTERSECT} <i>Y</i><sub>thật</sub>)}} &nbsp;&nbsp;&nbsp;&nbsp;<font color=\\"#64748b\\"><i>// Giao dịch mua thực tế trong tuần đích</i></font>"),
        (9, f"<i>N</i><sub>ứng_viên</sub> {ASSIGN} <i>C<sub>u</sub></i> {SETMINUS} <i>Y</i><sub>thật</sub> &nbsp;&nbsp;&nbsp;&nbsp;<font color=\\"#64748b\\"><i>// Ứng viên thực sự không mua</i></font>"),
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
        (1, f"<b>a</b> {ASSIGN} <b>0</b><sub>|<i>V</i>|</sub> &nbsp;&nbsp;&nbsp;&nbsp;<font color=\\"#64748b\\"><i>// Khởi tạo vector trọng số neo ngành hàng từ vựng V</i></font>"),
        (2, f"<b>duyệt từng</b> sự kiện <i>e</i> = (<i>i<sub>e</sub></i>, &tau;<sub><i>e</i></sub>, <i>t<sub>e</sub></i>) {IN} <i>E<sub>u</sub></i> (mới nhất đến cũ nhất, tối đa 50) <b>thực hiện</b>:"),
        (3, f"&nbsp;&nbsp;&nbsp;&nbsp; {DELTA}<i>t</i> {ASSIGN} (<i>t</i><sub>hiện_tại</sub> - <i>t<sub>e</sub></i>) tính theo ngày"),
        (4, f"&nbsp;&nbsp;&nbsp;&nbsp; <i>w</i>(<i>e</i>) {ASSIGN} &omega;(&tau;<sub><i>e</i></sub>) {TIMES} 2<sup>-{DELTA}<i>t</i> / <i>t</i><sub>1/2</sub></sup> &nbsp;&nbsp;&nbsp;&nbsp;<font color=\\"#64748b\\"><i>// Phân rã bán rã hàm mũ t<sub>1/2</sub> = 3.0 ngày</i></font>"),
        (5, f"&nbsp;&nbsp;&nbsp;&nbsp; <b>a</b>[ngành_hàng(<i>i<sub>e</sub></i>)] {ASSIGN} <b>a</b>[ngành_hàng(<i>i<sub>e</sub></i>)] + <i>w</i>(<i>e</i>)"),
        (6, f"<b>kết thúc duyệt</b>"),
        (7, f"<i>B</i> {ASSIGN} {{<i>i<sub>e</sub></i> | &tau;<sub><i>e</i></sub> = ĐÃ_MUA {OR} (&tau;<sub><i>e</i></sub> = ĐÁNH_GIÁ {AND} điểm(<i>e</i>) {LE} 2)}} &nbsp;&nbsp;&nbsp;&nbsp;<font color=\\"#64748b\\"><i>// Tập loại trừ bắt buộc</i></font>"),
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
        (19, f"<b>trả về</b> <i>R<sub>u</sub></i> &nbsp;&nbsp;&nbsp;&nbsp;<font color=\\"#64748b\\"><i>// Danh sách Top-12 tái xếp hạng, tối ưu đa dạng danh mục</i></font>")
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
    '''

    content = content[:idx1] + new_algos_vi + content[idx2:]

    with open('D:/HTTM/generate_pdf_report_vi.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Successfully updated D:/HTTM/generate_pdf_report_vi.py with arXiv formalism!")

if __name__ == '__main__':
    update_vietnamese_report()
