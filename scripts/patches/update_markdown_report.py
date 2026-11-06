from pathlib import Path

md_path = Path("D:/HTTM/REPORT_HCMUT_STANDARD.md")
content = md_path.read_text(encoding="utf-8")

# Let's check where Chapter 7 starts in markdown
c7_pos = content.find("# 7. Conclusion & Future Directions")

ui_chapter = """# 7. System Demonstration & Graphical User Interface

To deliver an enterprise-grade software solution, the HUB system features a rich, responsive Single-Page Application (SPA) crafted using React 18, TypeScript, Tailwind CSS v3, and Lucide icons. The interface is segregated into three dedicated workspaces tailored to the operational demands of each stakeholder persona.

## 7.1 Multi-Role Authentication Interface (LoginPage)

![Figure 7.1: Multi-Role Authentication Interface](docs/report_assets/00_login_page.png)

*Figure 7.1: Multi-Role Authentication Interface with Instant Demo Credentials*

- **URL:** `/auth/login`
- **Functionality:** Provides a unified authentication portal supporting instant role demo switches (Admin, Data Scientist, Buyer) with pre-filled credentials.
- **Security:** Upon credential submission, the backend authenticates the client via Bcrypt hashing and issues an HMAC-SHA256 signed JWT token containing `user_id` and `role_id` claims.

| UI Element | Component Specification & Implementation | Security & Operational Behavior |
|---|---|---|
| **Credential Fields** | Controlled React inputs with Formik/Zod validation | Requires minimum 6 characters; sanitizes input strings. |
| **Demo Switcher** | ButtonGroup pre-populating role test accounts | Switches between `buyer_test`, `ds_expert`, `kuroisme` (Admin). |
| **Session Vault** | `localStorage` token storage with Axios interceptor | Injects `Authorization: Bearer <token>` header on all subsequent calls. |

---

## 7.2 Buyer Storefront & Recommendation Discovery (HomePage)

![Figure 7.2: Buyer Personalized Homepage](docs/report_assets/05_buyer_homepage_recommendations.png)

*Figure 7.2: Buyer Personalized Homepage & AI Recommendation Showcase (HomePage)*

- **URL:** `/`
- **Functionality:** The primary visual anchor is the *“Gợi ý dành riêng cho bạn”* (Personalized Recommendations) showcase. The grid renders the Top-12 ranked fashion garments tailored to the logged-in customer's profile, accompanied by promotional hero banners and index department tabs.

| UI Element | Component Specification & Implementation | Algorithmic / Business Logic |
|---|---|---|
| **Recommendation Grid** | CSS Grid (4 columns desktop, responsive flex mobile) | Hydrated from `GET /predict/{user_id}`; renders Top-12 ranked cards. |
| **Garment Card** | `ProductCard` with lazy-loaded image, price, dept tag | Displays VND converted pricing, category badge, and hover interactions. |
| **Action Controls** | Interactive buttons: “Thêm vào giỏ” and Heart Wishlist | Dispatches `POST /cart` and logs telemetry signal for session reranking. |
| **Fallback Strip** | `BestSellersStrip` component for cold-start visitors | Automatically surfaces Top-12 national bestsellers when user history is empty. |

---

## 7.3 Product Detail View & Interaction Feedback (ProductDetailPage)

![Figure 7.3: Product Detail View](docs/report_assets/06_buyer_product_detail.png)

*Figure 7.3: Product Detail View & Real-time Interaction Tracking (ProductDetailPage)*

- **URL:** `/product/:id`
- **Functionality:** Upon route mounting, the client automatically dispatches a `VIEWED` telemetry interaction to the server. Buyers can inspect high-resolution photography, read detailed fabric compositions, select sizes, and submit 1–5 star feedback ratings.

| UI Element | Component Specification & Implementation | Operational Function |
|---|---|---|
| **Telemetry Hook** | `useEffect` mounting hook dispatching interaction API | Fires `POST /feedback` with `interaction_type='viewed'` (+1.0 weight). |
| **Size & Quantity** | `SelectDropdown` & `NumberInput` counter components | Enforces inventory stock validation bounds prior to cart dispatch. |
| **Rating Widget** | 5-Star interactive Lucide Star SVG rating bar | Submits `POST /feedback/{user_id}`; ratings &le; 2 stars trigger item block. |
| **Similar Items** | Horizontal scrolling strip of matching `product_code` items | Enables instant exploration of alternative colorways of the same design. |

---

## 7.4 Data Science Exploratory Analysis Dashboard (DataSciencePage)

![Figure 7.4: Data Science EDA Dashboard](docs/report_assets/01_ds_eda_page.png)

*Figure 7.4: Data Science Exploratory Analysis Dashboard (DataSciencePage)*

- **URL:** `/data-science`
- **Functionality:** Surfaces automated analytical reports compiled directly from the 31.78M Kaggle transaction logs, empowering machine learning engineers to detect macroeconomic shifts and retail seasonality prior to model retraining.

| Dashboard Panel | Underlying Analytical Chart / Artifact | Engineering Insight & Value |
|---|---|---|
| **Transaction Volume** | Daily time-series plot (`3_1_1_transactions_per_day.png`) | Detects promotional surges (Black Friday) and COVID-19 retail anomalies. |
| **Price Distribution** | Normalized price histogram (`3_1_2_price_distribution.png`) | Visualizes log-normal price density; confirms standard scaling parameters. |
| **Category Velocity** | Department sales growth bar chart (`3_1_5_index_group_sales.png`) | Identifies fastest-growing garment classes (e.g. Ladieswear vs Divided). |
| **Automated Insights** | Synthetic insight cards generated from `GET /ai/insights` | Summarizes category growth percentages and recommends feature adjustments. |

---

## 7.5 Model Metrics Validation & Benchmark Radar (ModelMetricsPage)

![Figure 7.5: Model Performance Validation](docs/report_assets/02_ds_model_metrics.png)

*Figure 7.5: Model Performance Validation & Baseline Benchmark Radar (ModelMetricsPage)*

- **URL:** `/data-science/metrics`
- **Functionality:** Top metric summary cards present official benchmark scores: MAP@12 (0.03014), Recall@12 (0.06274), and NDCG@12 (0.04430). A multi-axis radar chart visualizes the multi-metric superiority of the HUB Random Forest model against the Bestseller and Repurchase baselines.

| Evaluation Widget | Component Specification & Implementation | Evaluated Metric & Target |
|---|---|---|
| **Score Summary Cards** | `MetricCard` with improvement badge vs baseline | Validates +356% MAP gain over Bestsellers and +20.6% over Repurchase. |
| **Multi-Axis Radar** | Chart.js / SVG Radar canvas comparing 3 models | Spans MAP@12, Recall@12, Precision@12, NDCG@12, Candidate Recall. |
| **Temporal Split Card** | Card displaying active Train, Val, and Test dates | Confirms temporal integrity: Train (Aug 19–Sep 08), Val (Sep 09–Sep 15). |
| **Run History Table** | Paginated table of all historic training executions | Tracks `run_id`, subset mode, tree count, depth, and status (`written`). |

---

## 7.6 Sliced Error Diagnostics & Feature Importance (ErrorAnalysisPage)

![Figure 7.6: Sliced Error Diagnostics](docs/report_assets/03_ds_error_analysis.png)

*Figure 7.6: Sliced Error Diagnostics by Activity & Department (ErrorAnalysisPage)*

- **URL:** `/data-science/error-analysis`
- **Functionality:** Partitions test evaluations across customer activity tiers (Cold-Start, Low, Medium, VIP) and garment departments, alongside a horizontal Gini feature importance bar chart identifying primary ranking drivers.

| Diagnostic Module | Visual Breakdown & Tabular Structure | Diagnostic Purpose & Failure Mode |
|---|---|---|
| **Customer Slices** | 4-row table: Cold (0 tx), Low (1–2), Med (3–10), VIP (>10) | Pinpoints cold-start bottleneck (MAP=0.0071 vs VIP MAP=0.0589). |
| **Department Slices** | Breakdown across Garment Upper, Lower, Shoes, Access | Verifies balanced precision across major fast-fashion retail categories. |
| **Feature Importance** | Horizontal bar chart of top 10 features by Gini reduction | Validates `item_sales_1w` (24.8%) and repurchase flag (19.5%) dominance. |
| **Candidate Sources** | Pie / Stacked bar chart of Stage 1 channel recall | Confirms 9.43% aggregate recall across the 4 candidate heuristics. |

---

## 7.7 Automated Training Scheduler & Hyperparameter Tuning (TrainingSchedulePage)

![Figure 7.7: Automated Training Scheduler](docs/report_assets/04_ds_training_schedule.png)

*Figure 7.7: Automated Training Scheduler & Hyperparameter Tuning (TrainingSchedulePage)*

- **URL:** `/data-science/schedule`
- **Functionality:** Engineers can configure hyperparameters (trees, depth, sample fraction), toggle daily 02:00 AM automation, trigger on-demand execution, and monitor active training progress via a 6-step visual progress stepper.

| Control Widget | Component Specification & Implementation | Operational Function |
|---|---|---|
| **Config Form** | Inputs: `n_estimators`, `max_depth`, `runner` (`kaggle`/`local`) | Persists parameters to `runs/state.json` via `PUT /ai/training/config`. |
| **Schedule Toggle** | `ToggleSwitch` for daily 02:00 AM daemon execution | Enables background cron scheduler and startup catch-up backfilling. |
| **Trigger Button** | Primary action button spawning asynchronous worker thread | Dispatches `POST /ai/trigger-training`; acquires thread execution lock. |
| **6-Step Progress Stepper** | Dynamic stepper: Split &rarr; Cand &rarr; Feat &rarr; Fit &rarr; Eval &rarr; Write | Client polls `GET /ai/training/status` every 5s; displays real-time progress. |

---

## 7.8 Executive Commercial Dashboard & Operations (AdminDashboardPage)

![Figure 7.8: Executive Operations Dashboard](docs/report_assets/07_admin_dashboard.png)

*Figure 7.8: Executive Operations & Commercial Sales Monitoring (AdminDashboardPage)*

- **URL:** `/admin`
- **Functionality:** Aggregates commercial gross revenue metrics, monitors incoming orders, showcases top-performing products by revenue, and provides administrative controls for managing catalog products and customer identity links.

| Executive Widget | Component Specification & Implementation | Commercial / Operational Impact |
|---|---|---|
| **Revenue KPI Cards** | Summary statistics cards displaying GMV and orders | Hydrated from `GET /dashboard/metrics`; reflects real-time sales. |
| **Top Sold Products** | Table listing items ranked by units sold and revenue | Correlates high-ranking AI recommendations with commercial sales uplift. |
| **Order Lifecycle Tab** | Order management table with status dropdown transitions | Enables admins to advance orders from 'Pending' to 'Shipped' or 'Delivered'. |
| **Customer Linkages** | Account mapping viewer (`/ai/customer-links`) | Links web authentication accounts to Kaggle 64-hex customer identities. |

---

"""

new_content = content[:c7_pos] + ui_chapter + content[c7_pos:].replace("# 7. Conclusion & Future Directions", "# 8. Conclusion & Future Directions").replace("# 8. References", "# 9. References")
md_path.write_text(new_content, encoding="utf-8")
print("Successfully updated REPORT_HCMUT_STANDARD.md with Chapter 7 UI Walkthrough!")

