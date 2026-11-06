with open('generate_pdf_report.py', 'r', encoding='utf-8') as f:
    text = f.read()

import re
old = re.search(r'    seq1_text = """[\s\S]*?Figure 3\.1: Sequence Diagram for UC-02 Real-time Recommendation Inference", styles\)', text)
if old:
    replacement = '''    story.append(Spacer(1, 4))
    story.append(create_image_flowable("excalidraw_04_session_rerank_sequence.png", max_w=6.0*inch, max_h=3.4*inch))
    story.append(create_caption("Figure 3.1: Sequence Interaction Diagram for UC-02 Real-Time Session Re-Ranking (Excalidraw Flow)", styles))'''
    text = text[:old.start()] + replacement + text[old.end():]
    with open('generate_pdf_report.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print("SUCCESS: Replaced seq1_text with Excalidraw flowable")
else:
    print("NOT FOUND")

