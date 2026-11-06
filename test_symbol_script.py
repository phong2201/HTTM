from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
import pypdfium2 as pdfium

# Register Fonts
pdfmetrics.registerFont(TTFont('SegoeUISymbol', r'C:\Windows\Fonts\seguisym.ttf'))
pdfmetrics.registerFont(TTFont('Arial', r'C:\Windows\Fonts\arial.ttf'))
pdfmetrics.registerFont(TTFont('Arial-Bold', r'C:\Windows\Fonts\arialbd.ttf'))
pdfmetrics.registerFont(TTFont('Arial-Italic', r'C:\Windows\Fonts\ariali.ttf'))

# Math symbol shortcuts
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

styles = getSampleStyleSheet()

header_style = ParagraphStyle(
    'AlgoHeader', parent=styles['Normal'],
    fontName='Arial-Bold', fontSize=8.5, leading=11,
    textColor=colors.HexColor('#0f172a')
)
io_style = ParagraphStyle(
    'AlgoIO', parent=styles['Normal'],
    fontName='Arial', fontSize=7.2, leading=9.8,
    textColor=colors.HexColor('#1e293b')
)
num_style = ParagraphStyle(
    'AlgoNum', parent=styles['Normal'],
    fontName='Arial', fontSize=7.2, leading=9.6,
    alignment=2, textColor=colors.HexColor('#64748b')
)
code_style = ParagraphStyle(
    'AlgoCode', parent=styles['Normal'],
    fontName='Arial', fontSize=7.2, leading=9.6,
    textColor=colors.HexColor('#0f172a')
)

def build_arxiv_algorithm(algo_id, title, inputs, outputs, steps, width=470):
    rows = []
    # Row 0: Header
    rows.append([Paragraph(f'<b>Algorithm {algo_id}:</b> {title}', header_style), ''])
    
    # Row 1: Inputs
    in_text = f'<b>Input:</b> {inputs}'
    rows.append([Paragraph(in_text, io_style), ''])
    
    # Row 2: Outputs
    out_text = f'<b>Output:</b> {outputs}'
    rows.append([Paragraph(out_text, io_style), ''])
    
    # Steps
    for num, line in steps:
        p_num = Paragraph(f'{num}:', num_style)
        p_code = Paragraph(line, code_style)
        rows.append([p_num, p_code])
        
    t_style = [
        # Top heavy rule
        ('LINEABOVE', (0, 0), (-1, 0), 1.5, colors.HexColor('#0f172a')),
        # Span header, input, output across both columns
        ('SPAN', (0, 0), (1, 0)),
        ('SPAN', (0, 1), (1, 1)),
        ('SPAN', (0, 2), (1, 2)),
        # Mid rule below header
        ('LINEBELOW', (0, 0), (-1, 0), 0.75, colors.HexColor('#0f172a')),
        # Divider below I/O
        ('LINEBELOW', (0, 2), (-1, 2), 0.5, colors.HexColor('#94a3b8')),
        # Bottom heavy rule
        ('LINEBELOW', (0, -1), (-1, -1), 1.5, colors.HexColor('#0f172a')),
        # Background subtle tint
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fafaf9')),
        # Margins & Paddings
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

steps1 = [
    (1, f'<i>C<sub>u</sub></i> {ASSIGN} {EMPTY}'),
    (2, f'<i>C</i><sub>repurchase</sub> {ASSIGN} {{<i>i</i> {IN} <i>I</i> | {EXISTS} (<i>u</i>, <i>i</i>, <i>t</i>) {IN} <i>D</i> {AND} <i>t</i> {GE} <i>T</i><sub>cutoff</sub> - 28d}}'),
    (3, f'<i>C</i><sub>bestseller</sub> {ASSIGN} TopK({{<i>i</i> {IN} <i>I</i> | sales_count(<i>i</i>, [<i>T</i><sub>cutoff</sub> - 7d, <i>T</i><sub>cutoff</sub>])}}, <i>K</i> = 12)'),
    (4, f'<i>C</i><sub>age</sub> {ASSIGN} TopK({{<i>i</i> {IN} <i>I</i> | sales_by_cohort(<i>i</i>, age_group(<i>u</i>))}}, <i>K</i> = 8)'),
    (5, f'<i>C</i><sub>copurchase</sub> {ASSIGN} {{<i>j</i> {IN} <i>I</i> | {EXISTS} <i>i</i> {IN} <i>C</i><sub>repurchase</sub> {AND} co_purchased(<i>i</i>, <i>j</i>) {GE} 5}}'),
    (6, f'<i>C<sub>u</sub></i> {ASSIGN} Truncate(<i>C</i><sub>repurchase</sub> {UNION} <i>C</i><sub>bestseller</sub> {UNION} <i>C</i><sub>age</sub> {UNION} <i>C</i><sub>copurchase</sub>, <i>C</i><sub>max</sub> = 100)'),
    (7, f'<i>Y</i><sub>true</sub> {ASSIGN} {{<i>i</i> {IN} <i>I</i> | {EXISTS} (<i>u</i>, <i>i</i>, <i>t</i>) {IN} <i>D</i> {AND} <i>t</i> {IN} [<i>T</i><sub>cutoff</sub>, <i>T</i><sub>cutoff</sub> + 7d]}}'),
    (8, f'<b>Positives</b> {ASSIGN} {{(<i>u</i>, <i>i</i>, 1) | <i>i</i> {IN} (<i>C<sub>u</sub></i> {INTERSECT} <i>Y</i><sub>true</sub>)}}'),
    (9, f'<i>N</i><sub>cand</sub> {ASSIGN} <i>C<sub>u</sub></i> {SETMINUS} <i>Y</i><sub>true</sub>'),
    (10, f'<i>k</i><sub>neg</sub> {ASSIGN} min(|<i>N</i><sub>cand</sub>|, {LAMBDA}<sub>neg</sub> {TIMES} |<b>Positives</b>|)'),
    (11, f'<b>Negatives</b> {ASSIGN} SampleWithoutReplacement(<i>N</i><sub>cand</sub>, <i>k</i><sub>neg</sub>)'),
    (12, f'<b>return</b> <i>T<sub>u</sub></i> {ASSIGN} <b>Positives</b> {UNION} {{(<i>u</i>, <i>j</i>, 0) | <i>j</i> {IN} <b>Negatives</b>}}')
]

algo1 = build_arxiv_algorithm(
    '1', 'Stage 1 Multi-Channel Candidate Retrieval & Controlled Negative Sampling',
    f'Customer <i>u</i> {IN} <i>U</i>, Transactions <i>D</i> (<i>t</i> &lt; <i>T</i><sub>cutoff</sub>), Catalog <i>I</i>, Cohorts <i>A</i>, Ratio {LAMBDA}<sub>neg</sub> = 5',
    f'Balanced training dataset <i>T<sub>u</sub></i> = {{(<i>u</i>, <i>i</i>, <i>y</i>)}} with label <i>y</i> {IN} {{0, 1}}',
    steps1
)

steps2 = [
    (1, f'<b>a</b> {ASSIGN} <b>0</b><sub>|<i>V</i>|</sub> &nbsp;&nbsp;&nbsp;&nbsp;<font color="#64748b"><i>// Initialize session anchor vector across category vocabulary V</i></font>'),
    (2, f'<b>for each</b> interaction event <i>e</i> = (<i>i<sub>e</sub></i>, &tau;<sub><i>e</i></sub>, <i>t<sub>e</sub></i>) {IN} <i>E<sub>u</sub></i> (ordered newest to oldest, max 50) <b>do</b>:'),
    (3, f'&nbsp;&nbsp;&nbsp;&nbsp; {DELTA}<i>t</i> {ASSIGN} (<i>t</i><sub>now</sub> - <i>t<sub>e</sub></i>) in days'),
    (4, f'&nbsp;&nbsp;&nbsp;&nbsp; <i>w</i>(<i>e</i>) {ASSIGN} &omega;(&tau;<sub><i>e</i></sub>) {TIMES} 2<sup>-{DELTA}<i>t</i> / <i>t</i><sub>1/2</sub></sup> &nbsp;&nbsp;&nbsp;&nbsp;<font color="#64748b"><i>// Half-life exponential decay t<sub>1/2</sub> = 3.0 days</i></font>'),
    (5, f'&nbsp;&nbsp;&nbsp;&nbsp; <b>a</b>[category(<i>i<sub>e</sub></i>)] {ASSIGN} <b>a</b>[category(<i>i<sub>e</sub></i>)] + <i>w</i>(<i>e</i>)'),
    (6, f'<b>end for</b>'),
    (7, f'<i>B</i> {ASSIGN} {{<i>i<sub>e</sub></i> | &tau;<sub><i>e</i></sub> = PURCHASED {OR} (&tau;<sub><i>e</i></sub> = FEEDBACK {AND} rating(<i>e</i>) {LE} 2)}} &nbsp;&nbsp;&nbsp;&nbsp;<font color="#64748b"><i>// Hard suppression set</i></font>'),
    (8, f'<i>C</i><sub>active</sub> {ASSIGN} {{(<i>i</i>, <i>p&#770;</i>(<i>u</i>, <i>i</i>)) {IN} <i>C<sub>u</sub></i> | <i>i</i> {NOTIN} <i>B</i>}}'),
    (9, f'<b>for each</b> candidate item (<i>i</i>, <i>p&#770;</i>) {IN} <i>C</i><sub>active</sub> <b>do</b>:'),
    (10, f'&nbsp;&nbsp;&nbsp;&nbsp; boost(<i>i</i>) {ASSIGN} {SUM}<sub><i>c</i> {IN} categories</sub> <b>a</b>[<i>c</i>] {DOT} Similarity(category(<i>i</i>), <i>c</i>)'),
    (11, f'&nbsp;&nbsp;&nbsp;&nbsp; <i>s</i><sub>final</sub>(<i>i</i>) {ASSIGN} <i>p&#770;</i> {TIMES} (1.0 + max(0.0, boost(<i>i</i>)))'),
    (12, f'<b>end for</b>'),
    (13, f'<i>S</i> {ASSIGN} SortDescending(<i>C</i><sub>active</sub>, key = <i>s</i><sub>final</sub>)'),
    (14, f'<i>R<sub>u</sub></i> {ASSIGN} [ ], &nbsp;&nbsp; <i>G</i><sub>seen</sub> {ASSIGN} {EMPTY}'),
    (15, f'<b>for each</b> (<i>i</i>, <i>s</i>) {IN} <i>S</i> <b>do</b>:'),
    (16, f'&nbsp;&nbsp;&nbsp;&nbsp; <b>if</b> product_code(<i>i</i>) {NOTIN} <i>G</i><sub>seen</sub> <b>then</b>:'),
    (17, f'&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <i>R<sub>u</sub></i> {ASSIGN} <i>R<sub>u</sub></i> {CONCAT} [<i>i</i>], &nbsp;&nbsp; <i>G</i><sub>seen</sub> {ASSIGN} <i>G</i><sub>seen</sub> {UNION} {{product_code(<i>i</i>)}}'),
    (18, f'&nbsp;&nbsp;&nbsp;&nbsp; <b>if</b> |<i>R<sub>u</sub></i>| = <i>K</i> <b>then</b> <b>break</b>'),
    (19, f'<b>return</b> <i>R<sub>u</sub></i> &nbsp;&nbsp;&nbsp;&nbsp;<font color="#64748b"><i>// Final re-ranked, diversified Top-12 recommendation sequence</i></font>')
]

algo2 = build_arxiv_algorithm(
    '2', 'Real-Time In-Session Dynamic Re-Ranking & Diversity Enforcement',
    f'Target user <i>u</i>, Model candidates {{(<i>i</i>, <i>p&#770;</i>(<i>u</i>, <i>i</i>))}}, Active session stream <i>E<sub>u</sub></i>, Length <i>K</i> = 12',
    f'Final context-adapted recommendation list <i>R<sub>u</sub></i> = [<i>i</i><sub>1</sub>, ..., <i>i<sub>K</sub></i>]',
    steps2
)

doc = SimpleDocTemplate('D:/HTTM/test_both_algos.pdf', pagesize=A4, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
doc.build([algo1, Spacer(1, 14), algo2])

pdf = pdfium.PdfDocument('D:/HTTM/test_both_algos.pdf')
img = pdf[0].render(scale=2).to_pil()
img.save('D:/HTTM/test_both_algos.png')
print('Both algorithms rendered to test_both_algos.png!')


# Test equation rendering
eq_math_style = ParagraphStyle(
    'EqMath', parent=styles['Normal'],
    fontName='Arial', fontSize=8.5, leading=12,
    alignment=1, textColor=colors.HexColor('#0f172a')
)
eq_num_style = ParagraphStyle(
    'EqNum', parent=styles['Normal'],
    fontName='Arial-Bold', fontSize=8.0, leading=12,
    alignment=2, textColor=colors.HexColor('#475569')
)

def build_arxiv_equation(eq_num, formula_html, width=470):
    p_math = Paragraph(formula_html, eq_math_style)
    p_num = Paragraph(f'({eq_num})', eq_num_style)
    t = Table([[p_math, p_num]], colWidths=[width - 50, 50])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('LINELEFT', (0,0), (0,0), 2.5, colors.HexColor('#2563eb')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    return t

eq27 = build_arxiv_equation(
    '2.7',
    f'<i>AP@12</i>(<i>u</i>) = (1 / min(|<i>Y<sub>u</sub></i>|, 12)) &nbsp;'
    f'{SUM}<sub><i>k</i>=1</sub><sup>12</sup> <i>P<sub>u</sub></i>(<i>k</i>) {TIMES} <i>rel<sub>u</sub></i>(<i>k</i>), &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'
    f'<i>MAP@12</i> = (1 / |<i>U</i>|) &nbsp;'
    f'{SUM}<sub><i>u</i>=1</sub><sup>|<i>U</i>|</sup> <i>AP@12</i>(<i>u</i>)'
)

doc2 = SimpleDocTemplate('D:/HTTM/test_eq.pdf', pagesize=A4, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
doc2.build([eq27])

pdf2 = pdfium.PdfDocument('D:/HTTM/test_eq.pdf')
img2 = pdf2[0].render(scale=2).to_pil()
img2.save('D:/HTTM/test_eq.png')
print('Rendered test_eq.png successfully!')
