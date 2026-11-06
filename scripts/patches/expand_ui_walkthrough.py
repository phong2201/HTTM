from pathlib import Path

path = Path("D:/HTTM/generate_pdf_report.py")
content = path.read_text(encoding="utf-8")

# Find Chapter 7 start and Chapter 8 start
ch7_start = content.find("story.append(Paragraph(\"7  System Demonstration & Graphical User Interface\", h1_style))")
ch8_start = content.find("story.append(Paragraph(\"8  Conclusion & Future Roadmap\", h1_style))")

new_ch7 = """story.append(Paragraph("7  System Demonstration & Graphical User Interface", h1_style))
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
    """

content = content[:ch7_start] + new_ch7 + content[ch8_start:]
path.write_text(content, encoding="utf-8")
print("Successfully expanded Chapter 7 into dedicated full-page showcases!")

