with open('D:/HTTM/generate_pdf_report.py', 'r', encoding='utf-8') as f:
    text = f.read()

target = '''    story.append(algo1_flowable)
    story.append(create_caption("Algorithm 2.1: Multi-Channel Candidate Retrieval & Controlled Negative Sampling", styles))
    story.append(Spacer(1, 8))

    steps2 = ['''

replacement = '''    story.append(algo1_flowable)
    story.append(create_caption("Algorithm 2.1: Multi-Channel Candidate Retrieval & Controlled Negative Sampling", styles))
    story.append(PageBreak())

    steps2 = ['''

assert target in text, 'Target not found'
text = text.replace(target, replacement, 1)

with open('D:/HTTM/generate_pdf_report.py', 'w', encoding='utf-8') as f:
    f.write(text)

print('Successfully added PageBreak before Algorithm 2!')

