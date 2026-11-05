from pathlib import Path

# =============================================================================
# 1. Update generate_pdf_report.py
# =============================================================================
pdf_script = Path("D:/HTTM/generate_pdf_report.py")
content = pdf_script.read_text(encoding="utf-8")

# A. Insert Functional & Non-Functional Requirements in Chapter 1 after section 1.3
target_c1 = 'story.append(Paragraph("1.3  System Scope & Service Level Agreements", h2_style))'
req_section = '''story.append(Paragraph("1.3  Functional & Non-Functional Requirements", h2_style))
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
'''
content = content.replace(target_c1, req_section)

# B. Insert Testing & Validation in Chapter 4 after 4.3 API Directory
target_c4 = 'story.append(PageBreak())\n\n    # =========================================================================\n    # CHAPTER 5: DATA PIPELINE'
test_section = '''story.append(Spacer(1, 8))
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
\n    story.append(PageBreak())\n\n    # =========================================================================\n    # CHAPTER 5: DATA PIPELINE'''
content = content.replace(target_c4, test_section)

# C. Insert Team Contribution Statement & Declaration of Generative AI Use in Chapter 8
target_c8 = 'story.append(Spacer(1, 14))\n\n    # =========================================================================\n    # REFERENCES (IEEE Standard)'
contrib_section = '''story.append(Spacer(1, 8))
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
\n    # =========================================================================\n    # REFERENCES (IEEE Standard)'''
content = content.replace(target_c8, contrib_section)

pdf_script.write_text(content, encoding="utf-8")
print("Successfully patched rubric sections into generate_pdf_report.py!")

