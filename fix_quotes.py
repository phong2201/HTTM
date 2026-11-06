with open('D:/HTTM/generate_pdf_report.py', 'r', encoding='utf-8') as f:
    t1 = f.read()

with open('D:/HTTM/generate_pdf_report_vi.py', 'r', encoding='utf-8') as f:
    t2 = f.read()

t1 = t1.replace("ASSIGN = '<font name='SegoeUISymbol'>", "ASSIGN = '<font name=\"SegoeUISymbol\">")
t1 = t1.replace("IN = '<font name='SegoeUISymbol'>", "IN = '<font name=\"SegoeUISymbol\">")
t1 = t1.replace("NOTIN = '<font name='SegoeUISymbol'>", "NOTIN = '<font name=\"SegoeUISymbol\">")
t1 = t1.replace("EMPTY = '<font name='SegoeUISymbol'>", "EMPTY = '<font name=\"SegoeUISymbol\">")
t1 = t1.replace("UNION = '<font name='SegoeUISymbol'>", "UNION = '<font name=\"SegoeUISymbol\">")
t1 = t1.replace("INTERSECT = '<font name='SegoeUISymbol'>", "INTERSECT = '<font name=\"SegoeUISymbol\">")
t1 = t1.replace("SETMINUS = '<font name='SegoeUISymbol'>", "SETMINUS = '<font name=\"SegoeUISymbol\">")
t1 = t1.replace("EXISTS = '<font name='SegoeUISymbol'>", "EXISTS = '<font name=\"SegoeUISymbol\">")
t1 = t1.replace("FORALL = '<font name='SegoeUISymbol'>", "FORALL = '<font name=\"SegoeUISymbol\">")
t1 = t1.replace("AND = '<font name='SegoeUISymbol'>", "AND = '<font name=\"SegoeUISymbol\">")
t1 = t1.replace("OR = '<font name='SegoeUISymbol'>", "OR = '<font name=\"SegoeUISymbol\">")
t1 = t1.replace("TIMES = '<font name='SegoeUISymbol'>", "TIMES = '<font name=\"SegoeUISymbol\">")
t1 = t1.replace("LE = '<font name='SegoeUISymbol'>", "LE = '<font name=\"SegoeUISymbol\">")
t1 = t1.replace("GE = '<font name='SegoeUISymbol'>", "GE = '<font name=\"SegoeUISymbol\">")
t1 = t1.replace("SUM = '<font name='SegoeUISymbol'>", "SUM = '<font name=\"SegoeUISymbol\">")
t1 = t1.replace("CONCAT = '<font name='SegoeUISymbol'>", "CONCAT = '<font name=\"SegoeUISymbol\">")
t1 = t1.replace("DOT = '<font name='SegoeUISymbol'>", "DOT = '<font name=\"SegoeUISymbol\">")

t2 = t2.replace("ASSIGN = '<font name='SegoeUISymbol'>", "ASSIGN = '<font name=\"SegoeUISymbol\">")
t2 = t2.replace("IN = '<font name='SegoeUISymbol'>", "IN = '<font name=\"SegoeUISymbol\">")
t2 = t2.replace("NOTIN = '<font name='SegoeUISymbol'>", "NOTIN = '<font name=\"SegoeUISymbol\">")
t2 = t2.replace("EMPTY = '<font name='SegoeUISymbol'>", "EMPTY = '<font name=\"SegoeUISymbol\">")
t2 = t2.replace("UNION = '<font name='SegoeUISymbol'>", "UNION = '<font name=\"SegoeUISymbol\">")
t2 = t2.replace("INTERSECT = '<font name='SegoeUISymbol'>", "INTERSECT = '<font name=\"SegoeUISymbol\">")
t2 = t2.replace("SETMINUS = '<font name='SegoeUISymbol'>", "SETMINUS = '<font name=\"SegoeUISymbol\">")
t2 = t2.replace("EXISTS = '<font name='SegoeUISymbol'>", "EXISTS = '<font name=\"SegoeUISymbol\">")
t2 = t2.replace("FORALL = '<font name='SegoeUISymbol'>", "FORALL = '<font name=\"SegoeUISymbol\">")
t2 = t2.replace("AND = '<font name='SegoeUISymbol'>", "AND = '<font name=\"SegoeUISymbol\">")
t2 = t2.replace("OR = '<font name='SegoeUISymbol'>", "OR = '<font name=\"SegoeUISymbol\">")
t2 = t2.replace("TIMES = '<font name='SegoeUISymbol'>", "TIMES = '<font name=\"SegoeUISymbol\">")
t2 = t2.replace("LE = '<font name='SegoeUISymbol'>", "LE = '<font name=\"SegoeUISymbol\">")
t2 = t2.replace("GE = '<font name='SegoeUISymbol'>", "GE = '<font name=\"SegoeUISymbol\">")
t2 = t2.replace("SUM = '<font name='SegoeUISymbol'>", "SUM = '<font name=\"SegoeUISymbol\">")
t2 = t2.replace("CONCAT = '<font name='SegoeUISymbol'>", "CONCAT = '<font name=\"SegoeUISymbol\">")
t2 = t2.replace("DOT = '<font name='SegoeUISymbol'>", "DOT = '<font name=\"SegoeUISymbol\">")

with open('D:/HTTM/generate_pdf_report.py', 'w', encoding='utf-8') as f:
    f.write(t1)

with open('D:/HTTM/generate_pdf_report_vi.py', 'w', encoding='utf-8') as f:
    f.write(t2)

print('Fixed font definitions!')
