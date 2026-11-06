def polish_symbols():
    # 1. English
    with open('D:/HTTM/generate_pdf_report.py', 'r', encoding='utf-8') as f:
        text = f.read()
    
    text = text.replace('&real;<sup>d</sup>', '<font name="SegoeUISymbol">\\u211d</font><sup><i>d</i></sup>')
    text = text.replace('&lfloor;&radic;d&rfloor;', '<font name="SegoeUISymbol">\\u230a\\u221a<i>d</i>\\u230b</font>')
    
    with open('D:/HTTM/generate_pdf_report.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print('Polished symbols in generate_pdf_report.py')

    # 2. Vietnamese
    with open('D:/HTTM/generate_pdf_report_vi.py', 'r', encoding='utf-8') as f:
        text_vi = f.read()
        
    text_vi = text_vi.replace('&lfloor;&radic;14&rfloor; = 3', '<font name="SegoeUISymbol">\\u230a\\u221a14\\u230b</font> = 3')
    
    with open('D:/HTTM/generate_pdf_report_vi.py', 'w', encoding='utf-8') as f:
        f.write(text_vi)
    print('Polished symbols in generate_pdf_report_vi.py')

if __name__ == '__main__':
    polish_symbols()

