import re

with open('generate_pdf_report.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update fig_entries to include Figure 3.0
old_fig = '("Figure 2.1: Two-Stage Recommendation Architecture (Retrieval & Pointwise Ranker)", p_num(\'sec2_3\', 8)),'
new_fig = '''("Figure 2.1: End-to-End Machine Learning Pipeline & Two-Stage Recommendation Flow", p_num('sec2_3', 8)),
        ("Figure 3.0: Global System Use-Case Diagram & Actor Boundaries", p_num('sec3_1', 13)),'''
content = content.replace(old_fig, new_fig)

# 2. Replace ASCII arch_diagram in Section 2.3
target_sec2_3 = '''    arch_diagram = """
+-------------------------------------------------------------------------------------------------------+
|                                  TWO-STAGE RECOMMENDATION ARCHITECTURE                                 |
|                                                                                                       |
|  Full Catalog (105,542 Items) ------------------------+                                               |
|                                                       |                                               |
|  Active Customer u (Profile & History)                v                                               |
|         |                                 +-------------------------+                                 |
|         +-------------------------------->| STAGE 1: CANDIDATE GEN  | (High Recall Retrieval)         |
|                                           | Heuristics & Graphs     | Output: C = 100 candidates      |
|                                           +-------------------------+                                 |
|                                                       |                                               |
|                                                       v                                               |
|                                           +-------------------------+                                 |
|                                           | STAGE 2: FEATURE VECTOR | (14-Dimensional Extractor)      |
|                                           | User, Item & Dynamic Int| Pair: x_{u, i} for i in C       |
|                                           +-------------------------+                                 |
|                                                       |                                               |
|                                                       v                                               |
|                                           +-------------------------+                                 |
|                                           | RANDOM FOREST RANKER    | (Ensemble Scoring, B=200)       |
|                                           | Pointwise P(y=1 | x)    | Predicts p_hat(u, i)            |
|                                           +-------------------------+                                 |
|                                                       |                                               |
|                                                       v                                               |
|                                           +-------------------------+                                 |
|                                           | SESSION RE-RANKER       | (Real-time Decay & Diversity)   |
|                                           | Half-life Exponential   | Output: Top-12 Ranked List      |
|                                           +-------------------------+                                 |
+-------------------------------------------------------------------------------------------------------+
    """
    story.append(Preformatted(arch_diagram.strip(), code_style))
    story.append(create_caption("Figure 2.1: Two-Stage Recommendation Architecture (Retrieval & Pointwise Ranker)", styles))'''

replacement_sec2_3 = '''    story.append(Spacer(1, 4))
    story.append(create_image_flowable("excalidraw_03_ml_training_pipeline.png", max_w=6.2*inch, max_h=3.0*inch))
    story.append(create_caption("Figure 2.1: End-to-End Machine Learning Pipeline & Two-Stage Recommendation Flow (Excalidraw Visual Blueprint)", styles))
    story.append(Spacer(1, 6))'''

if target_sec2_3 in content:
    content = content.replace(target_sec2_3, replacement_sec2_3)
    print("Replaced Section 2.3 ASCII diagram with Excalidraw PNG")
else:
    print("Warning: Section 2.3 ASCII diagram target not found verbatim")

# 3. Add Figure 3.0 in Section 3.1
target_sec3_1 = '''    story.append(rbac_table)
    story.append(Spacer(1, 10))

    story.append(PageTracker('sec3_2'))'''

replacement_sec3_1 = '''    story.append(rbac_table)
    story.append(Spacer(1, 8))
    story.append(create_image_flowable("excalidraw_02_usecase_diagram.png", max_w=5.8*inch, max_h=3.5*inch))
    story.append(create_caption("Figure 3.0: Global System Use-Case Diagram & Actor Boundaries (Excalidraw Modeling)", styles))
    story.append(Spacer(1, 8))

    story.append(PageTracker('sec3_2'))'''

if target_sec3_1 in content:
    content = content.replace(target_sec3_1, replacement_sec3_1)
    print("Injected Figure 3.0 Use-Case Diagram into Section 3.1")
else:
    print("Warning: Section 3.1 target not found verbatim")

# 4. Replace Sequence Diagram in Section 3.3
target_seq1 = '''    seq1_text = """
Buyer               React Frontend (SPA)   FastAPI Recommender    Session Engine
  |                         |                      |                     |
  |-- Navigate to Home ---->|                      |                     |
  |                         |-- GET /predict ----->|                     |
  |                         |                      |-- Retrieve cand --->|
  |                         |                      |   Top-100 items     |
  |                         |                      |-- Query model ----->|
  |                         |                      |   RF predict_proba  |
  |                         |                      |<-- Scored pairs ----|
  |                         |                      |                     |
  |                         |                      |-- Apply session --->|
  |                         |                      |   Half-life decay   |
  |                         |                      |   Block purchased   |
  |                         |                      |   Enforce max_code  |
  |                         |                      |<-- Return Top-12 ---|
  |                         |                      |                     |
  |<-- HTTP 200 (Top-12) ---|                      |                     |
    """
    story.append(Preformatted(seq1_text.strip(), code_style))
    story.append(create_caption("Figure 3.1: Sequence Diagram for UC-02 Real-time Recommendation Inference", styles))'''

replacement_seq1 = '''    story.append(Spacer(1, 4))
    story.append(create_image_flowable("excalidraw_04_session_rerank_sequence.png", max_w=6.0*inch, max_h=3.4*inch))
    story.append(create_caption("Figure 3.1: Sequence Interaction Diagram for UC-02 Real-Time Session Re-Ranking (Excalidraw Flow)", styles))
    story.append(Spacer(1, 6))'''

if target_seq1 in content:
    content = content.replace(target_seq1, replacement_seq1)
    print("Replaced Sequence Diagram 1 with Excalidraw PNG")
else:
    print("Warning: Sequence Diagram 1 target not found verbatim")

# 5. Replace 4-Tier Architecture Diagram in Section 4.1
target_arch4 = '''    arch4_text = """
+-------------------------------------------------------------------------------------------------------+
| TIER 1: PRESENTATION LAYER (React 18 Single-Page Application)                                         |
| TypeScript, Vite, Tailwind CSS, Lucide React, Axios HTTP Service                                     |
| Role Spaces: /buyer (Storefront), /data-science (Observability), /admin (Operations Dashboard)       |
+-------------------------------------------------------------------------------------------------------+
                                                   |  RESTful JSON API over HTTPS
                                                   v
+-------------------------------------------------------------------------------------------------------+
| TIER 2: API GATEWAY & ROUTING LAYER (FastAPI Async Framework)                                        |
| Authentication & JWT Bearer Security (OAuth2), CORS Middleware, Pydantic Request Validation          |
| Routers: /auth, /products, /predict, /cart, /wishlist, /orders, /ai, /dashboard, /feedback             |
+-------------------------------------------------------------------------------------------------------+
                                                   |  Service Calls & Internal Dependency Injection
                                                   v
+-------------------------------------------------------------------------------------------------------+
| TIER 3: BUSINESS LOGIC & INFERENCE ENGINE (Python Core Services)                                      |
| • recommendation_service.py: Base prediction retrieval & caching                                      |
| • session_rerank.py: In-memory dynamic half-life decay re-ranking & diversity filter                 |
| • hm_pipeline_service.py: Background threading worker, Kaggle orchestration, scheduler daemon         |
| • sales_service.py: Commercial revenue aggregation, daily closure, monthly accounting                |
+-------------------------------------------------------------------------------------------------------+
                                                   |  SQLAlchemy ORM & Filesystem Persistence
                                                   v
+-------------------------------------------------------------------------------------------------------+
| TIER 4: PERSISTENCE & DATA STORAGE LAYER                                                              |
| • SQLite / PostgreSQL: Relational storage (Users, Products, Orders, Feedbacks, Recommendations)       |
| • File System Artifacts: Joblib Scaler (scaler.joblib), Random Forest model, runs.json, summary.json |
| • Static Image Server: Product catalog garment photography (/images/...)                             |
+-------------------------------------------------------------------------------------------------------+
    """
    story.append(Preformatted(arch4_text.strip(), code_style))
    story.append(create_caption("Figure 4.1: Enterprise 4-Tier Logical Architecture of the HUB System", styles))'''

replacement_arch4 = '''    story.append(Spacer(1, 4))
    story.append(create_image_flowable("excalidraw_01_architecture_4tier.png", max_w=6.2*inch, max_h=3.5*inch))
    story.append(create_caption("Figure 4.1: Enterprise 4-Tier Modular System Architecture (Excalidraw Visual Blueprint)", styles))
    story.append(Spacer(1, 6))'''

if target_arch4 in content:
    content = content.replace(target_arch4, replacement_arch4)
    print("Replaced 4-Tier Architecture Diagram with Excalidraw PNG")
else:
    print("Warning: 4-Tier Architecture Diagram target not found verbatim")

with open('generate_pdf_report.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("generate_pdf_report.py successfully updated with Excalidraw diagrams!")

