const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright-core');

const DIAGRAMS_DIR = path.join(__dirname);
const ASSETS_DIR = path.join('D:', 'HTTM', 'docs', 'report_assets');
const roughJsCode = fs.readFileSync(path.join(DIAGRAMS_DIR, 'node_modules', 'roughjs', 'bundled', 'rough.js'), 'utf8');

function saveExcalidrawJson(filename, elements) {
  const doc = {
    type: "excalidraw",
    version: 2,
    source: "https://excalidraw.com",
    elements: elements,
    appState: {
      viewBackgroundColor: "#fdfbf7",
      gridSize: null
    },
    files: {}
  };
  const targetPath = path.join(DIAGRAMS_DIR, filename);
  fs.writeFileSync(targetPath, JSON.stringify(doc, null, 2), 'utf8');
  console.log(`[Excalidraw EN] Saved: ${targetPath}`);
}

function getDiagram1Elements() {
  return [];
}
function getDiagram2Elements() {
  return [];
}
function getDiagram3Elements() {
  return [];
}
function getDiagram4Elements() {
  return [];
}

function buildDiagramHtml(title, subtitle, drawFunctionBody, width = 1540, height = 1060) {
  return `<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>${title}</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&display=swap');
    body {
      margin: 0;
      padding: 30px;
      background: #fdfbf7;
      font-family: 'Nunito', 'Segoe UI', Arial, sans-serif;
      color: #1e293b;
    }
    .header-box {
      margin-bottom: 22px;
      border-bottom: 2px dashed #cbd5e1;
      padding-bottom: 14px;
      display: flex;
      justify-content: space-between;
      align-items: flex-end;
    }
    .main-title {
      font-size: 25px;
      font-weight: 900;
      color: #0f172a;
      margin: 0;
      letter-spacing: -0.3px;
    }
    .subtitle {
      font-size: 13.5px;
      color: #64748b;
      margin-top: 5px;
      font-weight: 600;
    }
    .badge {
      background: #e7f5ff;
      color: #1971c2;
      border: 1.5px solid #1971c2;
      border-radius: 20px;
      padding: 6px 16px;
      font-size: 12px;
      font-weight: 800;
      box-shadow: 0 2px 6px rgba(25, 113, 194, 0.12);
    }
    canvas {
      display: block;
      background: #ffffff;
      box-shadow: 0 6px 24px rgba(0,0,0,0.06);
      border-radius: 14px;
      border: 1px solid #e2e8f0;
    }
  </style>
</head>
<body>
  <div class="header-box">
    <div>
      <h1 class="main-title">${title}</h1>
      <div class="subtitle">${subtitle}</div>
    </div>
    <div class="badge">HUB Intelligent Systems • Excalidraw Publication Standard</div>
  </div>
  <canvas id="canvas" width="${width}" height="${height}"></canvas>

  <script>
    ${roughJsCode}
  </script>
  <script>
    (function() {
      const canvas = document.getElementById('canvas');
      const ctx = canvas.getContext('2d');
      const rc = rough.canvas(canvas);

      function drawModernCard(x, y, w, h, title, lines, strokeColor, options = {}) {
        rc.rectangle(x, y, w, h, {
          stroke: strokeColor,
          fill: '#ffffff',
          fillStyle: 'solid',
          roughness: options.roughness || 0.8,
          strokeWidth: options.strokeWidth || 1.8
        });

        ctx.fillStyle = strokeColor;
        ctx.beginPath();
        ctx.roundRect(x, y, w, 28, [6, 6, 0, 0]);
        ctx.fill();

        ctx.fillStyle = '#ffffff';
        ctx.font = 'bold 12.5px "Nunito", Arial, sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(title, x + w / 2, y + 19);

        if (lines && lines.length > 0) {
          ctx.font = 'normal 11px "Nunito", Arial, sans-serif';
          ctx.fillStyle = '#334155';
          ctx.textAlign = 'left';
          const startY = y + 48;
          const lineX = x + 16;
          lines.forEach((l, idx) => {
            ctx.fillText(l, lineX, startY + idx * 18);
          });
        }
      }

      function drawPillBadge(x, y, text1, text2, color = '#1971c2') {
        ctx.font = 'bold 11px "Nunito", Arial, sans-serif';
        const w1 = ctx.measureText(text1).width;
        ctx.font = 'normal 10px "Nunito", Arial, sans-serif';
        const w2 = text2 ? ctx.measureText(text2).width : 0;
        const boxW = Math.max(w1, w2) + 24;
        const boxH = text2 ? 34 : 22;

        ctx.fillStyle = '#ffffff';
        ctx.strokeStyle = color;
        ctx.lineWidth = 1.4;
        ctx.beginPath();
        ctx.roundRect(x - boxW / 2, y - boxH / 2, boxW, boxH, 6);
        ctx.fill();
        ctx.stroke();

        ctx.textAlign = 'center';
        if (text2) {
          ctx.fillStyle = color;
          ctx.font = 'bold 11px "Nunito", Arial, sans-serif';
          ctx.fillText(text1, x, y - 2);
          ctx.fillStyle = '#64748b';
          ctx.font = 'normal 10px "Nunito", Arial, sans-serif';
          ctx.fillText(text2, x, y + 11);
        } else {
          ctx.fillStyle = color;
          ctx.font = 'bold 11px "Nunito", Arial, sans-serif';
          ctx.fillText(text1, x, y + 4);
        }
      }

      function drawSleekArrow(x1, y1, x2, y2, color = '#2b8a3e', options = {}) {
        const angle = Math.atan2(y2 - y1, x2 - x1);
        const headLen = options.headLen || 12;
        const lineWidth = options.lineWidth || 2;

        ctx.save();
        ctx.strokeStyle = color;
        ctx.fillStyle = color;
        ctx.lineWidth = lineWidth;
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';

        ctx.beginPath();
        ctx.moveTo(x1, y1);
        ctx.lineTo(x2 - (headLen * 0.4) * Math.cos(angle), y2 - (headLen * 0.4) * Math.sin(angle));
        ctx.stroke();

        ctx.beginPath();
        ctx.moveTo(x2, y2);
        const spread = Math.PI / 6.5;
        ctx.lineTo(x2 - headLen * Math.cos(angle - spread), y2 - headLen * Math.sin(angle - spread));
        ctx.lineTo(x2 - (headLen * 0.72) * Math.cos(angle), y2 - (headLen * 0.72) * Math.sin(angle));
        ctx.lineTo(x2 - headLen * Math.cos(angle + spread), y2 - headLen * Math.sin(angle + spread));
        ctx.closePath();
        ctx.fill();
        ctx.restore();
      }

      const drawCleanArrow = drawSleekArrow;

      function drawBadgeArrow(x1, y1, x2, y2, text1, text2, color = '#1971c2', options = {}) {
        if (Math.abs(y1 - y2) < 2) {
          const isLeftToRight = x2 > x1;
          const midX = (x1 + x2) / 2;
          const midY = y1;

          ctx.font = 'bold 11px "Nunito", Arial, sans-serif';
          const w1 = ctx.measureText(text1).width;
          ctx.font = 'normal 10px "Nunito", Arial, sans-serif';
          const w2 = text2 ? ctx.measureText(text2).width : 0;
          const boxW = Math.max(w1, w2) + 22;

          const bLeft = midX - boxW / 2;
          const bRight = midX + boxW / 2;

          ctx.strokeStyle = color;
          ctx.lineWidth = 2;
          ctx.lineCap = 'round';

          if (isLeftToRight) {
            ctx.beginPath();
            ctx.moveTo(x1, midY);
            ctx.lineTo(bLeft, midY);
            ctx.stroke();

            drawPillBadge(midX, midY, text1, text2, color);
            drawSleekArrow(bRight, midY, x2, midY, color, options);
          } else {
            ctx.beginPath();
            ctx.moveTo(x1, midY);
            ctx.lineTo(bRight, midY);
            ctx.stroke();

            drawPillBadge(midX, midY, text1, text2, color);
            drawSleekArrow(bLeft, midY, x2, midY, color, options);
          }
        } else if (Math.abs(x1 - x2) < 2) {
          const isTopToBottom = y2 > y1;
          const midX = x1;
          const midY = (y1 + y2) / 2;

          ctx.font = 'bold 11px "Nunito", Arial, sans-serif';
          const w1 = ctx.measureText(text1).width;
          ctx.font = 'normal 10px "Nunito", Arial, sans-serif';
          const w2 = text2 ? ctx.measureText(text2).width : 0;
          const boxH = text2 ? 34 : 22;

          const bTop = midY - boxH / 2;
          const bBottom = midY + boxH / 2;

          ctx.strokeStyle = color;
          ctx.lineWidth = 2;
          ctx.lineCap = 'round';

          if (isTopToBottom) {
            ctx.beginPath();
            ctx.moveTo(midX, y1);
            ctx.lineTo(midX, bTop);
            ctx.stroke();

            drawPillBadge(midX, midY, text1, text2, color);
            drawSleekArrow(midX, bBottom, midX, y2, color, options);
          } else {
            ctx.beginPath();
            ctx.moveTo(midX, y1);
            ctx.lineTo(midX, bBottom);
            ctx.stroke();

            drawPillBadge(midX, midY, text1, text2, color);
            drawSleekArrow(midX, bTop, midX, y2, color, options);
          }
        } else {
          drawSleekArrow(x1, y1, x2, y2, color, options);
          drawPillBadge((x1 + x2) / 2, (y1 + y2) / 2, text1, text2, color);
        }
      }

      function drawSelfLoop(lifelineX, yTop, yBottom, text1, text2, color = '#2f9e44') {
        ctx.font = 'bold 11px "Nunito", Arial, sans-serif';
        const w1 = ctx.measureText(text1).width;
        ctx.font = 'normal 10px "Nunito", Arial, sans-serif';
        const w2 = text2 ? ctx.measureText(text2).width : 0;
        const boxW = Math.max(w1, w2) + 24;

        const leadIn = 25;
        const bLeft = lifelineX + leadIn;
        const bRight = bLeft + boxW;
        const bCenter = (bLeft + bRight) / 2;
        const loopRight = bRight + 20;
        const radius = 10;
        const headLen = 11;

        ctx.save();
        ctx.strokeStyle = color;
        ctx.lineWidth = 2;
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';

        // 1. Line from lifeline into left side of badge: --
        ctx.beginPath();
        ctx.moveTo(lifelineX, yTop);
        ctx.lineTo(bLeft, yTop);
        ctx.stroke();

        // 2. Draw Badge: [__]
        drawPillBadge(bCenter, yTop, text1, text2, color);

        // 3. Line from right side of badge, turning down: |--
        ctx.beginPath();
        ctx.moveTo(bRight, yTop);
        ctx.lineTo(loopRight - radius, yTop);
        ctx.arcTo(loopRight, yTop, loopRight, yTop + radius, radius);
        ctx.lineTo(loopRight, yBottom - radius);
        ctx.arcTo(loopRight, yBottom, loopRight - radius, yBottom, radius);
        ctx.lineTo(lifelineX + headLen * 0.4, yBottom);
        ctx.stroke();

        // 4. Arrow pointing left back to lifeline: <--
        ctx.beginPath();
        ctx.fillStyle = color;
        ctx.moveTo(lifelineX, yBottom);
        ctx.lineTo(lifelineX + headLen, yBottom - 5);
        ctx.lineTo(lifelineX + headLen * 0.72, yBottom);
        ctx.lineTo(lifelineX + headLen, yBottom + 5);
        ctx.closePath();
        ctx.fill();
        ctx.restore();
      }

      function drawActorEN(x, y, name1, name2, color = '#1971c2') {
        rc.circle(x, y - 25, 30, { stroke: color, strokeWidth: 2, roughness: 1.0, fill: '#ffffff', fillStyle: 'solid' });
        rc.line(x, y - 10, x, y + 25, { stroke: color, strokeWidth: 2, roughness: 1.0 });
        rc.line(x - 20, y + 5, x + 20, y + 5, { stroke: color, strokeWidth: 2, roughness: 1.0 });
        rc.line(x, y + 25, x - 15, y + 55, { stroke: color, strokeWidth: 2, roughness: 1.0 });
        rc.line(x, y + 25, x + 15, y + 55, { stroke: color, strokeWidth: 2, roughness: 1.0 });

        const tagW = 140;
        ctx.fillStyle = '#ffffff';
        ctx.strokeStyle = color;
        ctx.lineWidth = 1.2;
        ctx.beginPath();
        ctx.roundRect(x - tagW / 2, y + 68, tagW, 36, 6);
        ctx.fill();
        ctx.stroke();

        ctx.textAlign = 'center';
        ctx.fillStyle = color;
        ctx.font = 'bold 12px "Nunito", Arial, sans-serif';
        ctx.fillText(name1, x, y + 83);
        ctx.fillStyle = '#64748b';
        ctx.font = 'normal 10.5px "Nunito", Arial, sans-serif';
        ctx.fillText(name2, x, y + 97);
      }

      ${drawFunctionBody}
    })();
  </script>
</body>
</html>`;
}

// -------------------------------------------------------------
// Canvas Script 1: Architecture (English, Sidebar Layout)
// -------------------------------------------------------------
const drawDiagram1CanvasEN = `
  const tiers = [
    {
      name: "TIER 1: PRESENTATION",
      sub: "Presentation Layer (React 18)",
      desc: "SPA • Tailwind CSS • Axios",
      y: 30, h: 180, bg: "#f0f7ff", stroke: "#1971c2"
    },
    {
      name: "TIER 2: API GATEWAY",
      sub: "API Routing (FastAPI Async)",
      desc: "22 Endpoints • JWT • CORS",
      y: 285, h: 180, bg: "#fff7ed", stroke: "#f76707"
    },
    {
      name: "TIER 3: ML ENGINE",
      sub: "Random Forest & Re-ranking",
      desc: "14 Features • B=200 Depth=12",
      y: 540, h: 195, bg: "#f0fdf4", stroke: "#2f9e44"
    },
    {
      name: "TIER 4: PERSISTENCE",
      sub: "Persistence & Kaggle Data",
      desc: "SQLite 3NF • 31.78M Rows",
      y: 810, h: 180, bg: "#faf5ff", stroke: "#7950f2"
    }
  ];

  tiers.forEach(t => {
    rc.rectangle(40, t.y, 230, t.h, {
      stroke: t.stroke, fill: t.bg, fillStyle: 'solid', roughness: 0.8, strokeWidth: 2
    });
    ctx.fillStyle = t.stroke;
    ctx.beginPath();
    ctx.roundRect(40, t.y, 230, 32, [6, 6, 0, 0]);
    ctx.fill();

    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 12.5px "Nunito", Arial, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(t.name, 155, t.y + 21);

    ctx.fillStyle = t.stroke;
    ctx.font = 'bold 12px "Nunito", Arial, sans-serif';
    ctx.fillText(t.sub, 155, t.y + 70);

    ctx.fillStyle = '#475569';
    ctx.font = 'normal 11px "Nunito", Arial, sans-serif';
    ctx.fillText(t.desc, 155, t.y + 98);

    rc.rectangle(285, t.y, 1205, t.h, {
      stroke: t.stroke, fill: '#ffffff', fillStyle: 'solid', roughness: 0.7, strokeWidth: 1.5, strokeLineDash: [6, 4]
    });
  });

  drawModernCard(305, 52, 380, 135, "Buyer Portal (Consumer Interface)", [
    "• Paginated catalog browsing & semantic product search",
    "• Top-12 personalized feed on homepage",
    "• Session click & detail view interaction tracking"
  ], "#1864ab");

  drawModernCard(715, 52, 400, 135, "Data Scientist Portal (Analytics Workspace)", [
    "• Interactive 10-chart EDA & distribution visualizer",
    "• MAP@12 benchmark metric dashboard & baseline radar",
    "• Sliced error matrix inspector & automated retraining trigger"
  ], "#1864ab");

  drawModernCard(1145, 52, 325, 135, "Store Administrator Portal (Operations)", [
    "• Catalog inventory management & CRUD operations",
    "• Real-time stock tracking & retail status controls",
    "• Commercial revenue KPIs & system audit logging"
  ], "#1864ab");

  drawModernCard(305, 307, 380, 135, "RESTful API Endpoints (22 Route Handlers)", [
    "• /api/recommendations/rerank (Real-time Session Feed)",
    "• /api/products, /api/auth, /api/cart, /api/orders",
    "• /api/ai/reports, /api/ai/trigger-training"
  ], "#d9480f");

  drawModernCard(715, 307, 400, 135, "Security & Validation Middleware", [
    "• JWT Bearer Token Authentication (OAuth2 compliant)",
    "• Input data integrity enforcement via Pydantic Schemas",
    "• CORS Cross-Origin protection & structured audit logging"
  ], "#d9480f");

  drawModernCard(1145, 307, 325, 135, "Asynchronous Background Dispatcher", [
    "• Non-blocking background worker for model retraining",
    "• Strict recommendation SLA guarantee: P95 < 50ms",
    "• High-throughput capability: > 200 requests/sec"
  ], "#d9480f");

  drawModernCard(305, 560, 380, 150, "Stage 1: Multi-Channel Candidate Retrieval", [
    "• National weekly bestseller heuristics (12 items)",
    "• Customer repurchase history heuristics",
    "• Department-aware item co-purchase graph",
    "• Candidate pool coverage: Recall@12 = 9.43%"
  ], "#2b8a3e");

  drawModernCard(715, 560, 400, 150, "14-Feature ML Engineering Pipeline", [
    "• Customer: Age, Club Member status, Activity score",
    "• Article: Price percentile, Department sales velocity",
    "• Interaction: Exponential time decay (lambda = 0.05)",
    "• Controlled negative sampling: 1 Purchase : 5 Non-purchase"
  ], "#2b8a3e");

  drawModernCard(1145, 560, 325, 150, "Random Forest Ranker & Session Engine", [
    "• Random Forest B=200 decision trees, Depth=12",
    "• Calibrated purchase probability predict_proba()",
    "• Session click half-life decay (t1/2 = 3.0 days)",
    "• Flood prevention category cap: MAX_PER_CODE = 1"
  ], "#2b8a3e");

  drawModernCard(305, 832, 380, 135, "Relational Database (SQLite)", [
    "• Tables: users, products, orders, feedbacks",
    "• Recommendations cache: user_recommendations",
    "• 3NF normalized schema ensuring transactional ACID"
  ], "#5f3dc4");

  drawModernCard(715, 832, 400, 135, "Model Artifacts & Feature Store", [
    "• model_rf_ranker.pkl (Serialized binary tree ensemble)",
    "• feature_metadata.json (Feature definitions & order)",
    "• StandardScaler & OneHotEncoder serialized state"
  ], "#5f3dc4");

  drawModernCard(1145, 832, 325, 135, "Kaggle H&M Benchmark Data", [
    "• 31.78M Transactions • 105K Articles • 1.37M Users",
    "• Rolling temporal train/val/test splits",
    "• 100% genuine Kaggle data (Zero simulated rows)"
  ], "#5f3dc4");

  drawBadgeArrow(495, 210, 495, 285, "Recommendation Query (HTTP/JSON)", "GET /predict/user_id", "#1864ab");
  drawBadgeArrow(915, 210, 915, 285, "Analytics & Retraining Ops", "GET /reports • POST /retrain", "#1864ab");
  drawBadgeArrow(1307, 210, 1307, 285, "Inventory Status & Health", "GET /admin/dashboard", "#1864ab");

  drawBadgeArrow(495, 465, 495, 540, "Retrieve Candidate Pool", "Multi-Heuristic Retrieval", "#d9480f");
  drawBadgeArrow(915, 465, 915, 540, "Assemble Feature Vector", "14-Dimensional Matrix", "#d9480f");
  drawBadgeArrow(1307, 465, 1307, 540, "Scoring & Re-ranking", "P95 Latency < 50ms", "#d9480f");

  drawBadgeArrow(495, 735, 495, 810, "Relational SQL Queries", "SQLAlchemy ORM", "#2b8a3e");
  drawBadgeArrow(915, 735, 915, 810, "Load Model Weights", "Joblib Deserializer", "#2b8a3e");
  drawBadgeArrow(1307, 735, 1307, 810, "Benchmark Data Ingestion", "Temporal Zero-Leak Split", "#2b8a3e");
`;

// -------------------------------------------------------------
// Canvas Script 2: Use Cases (English)
// -------------------------------------------------------------
const drawDiagram2CanvasEN = `
  rc.rectangle(260, 20, 960, 830, {
    stroke: '#64748b', fill: '#f8fafc', fillStyle: 'solid', strokeWidth: 2, roughness: 0.8
  });
  ctx.fillStyle = '#0f172a';
  ctx.font = 'bold 16px "Nunito", Arial, sans-serif';
  ctx.textAlign = 'left';
  ctx.fillText("SYSTEM SCOPE: HUB INTELLIGENT PERSONALIZED FASHION PLATFORM", 290, 52);

  drawActorEN(120, 230, "Consumer Buyer", "(Primary Actor - Role 1)", "#1971c2");
  drawActorEN(120, 610, "Data Scientist", "(ML Engineer - Role 2)", "#2f9e44");
  drawActorEN(1360, 520, "Store Administrator", "(Operations - Role 3)", "#e8590c");

  const ucs = [
    { title: "UC-01: Browse Product Catalog & Filters", sub: "Full-text search • Department filters • Paginated product grid", y: 75, stroke: "#1971c2", fill: "#e7f5ff" },
    { title: "UC-02: View Personalized Recommendations (Top-12 RF)", sub: "Retrieve tailored 12 items via Random Forest ranker engine", y: 168, stroke: "#1971c2", fill: "#e7f5ff" },
    { title: "UC-03: Real-Time Session Feedback & Re-ranking", sub: "Click/view triggers sub-50ms session re-ranking on active feed", y: 261, stroke: "#1971c2", fill: "#e7f5ff" },
    { title: "UC-04: View Product Details & Related Cross-Sells", sub: "Co-purchase graph recommendations & complementary outfits", y: 354, stroke: "#1971c2", fill: "#e7f5ff" },
    { title: "UC-05: Inspect EDA & Data Drift Distributions", sub: "Track transaction volume, age brackets, price tiers & drift alerts", y: 457, stroke: "#2f9e44", fill: "#ebfbee" },
    { title: "UC-06: Evaluate Model Metrics & Sliced Errors", sub: "Offline MAP@12 benchmark, precision/recall, active vs casual slices", y: 550, stroke: "#2f9e44", fill: "#ebfbee" },
    { title: "UC-07: Trigger Automated Retraining Pipeline", sub: "Rolling temporal split, negative sampling, fit 200 decision trees", y: 643, stroke: "#2f9e44", fill: "#ebfbee" },
    { title: "UC-08: Manage Inventory & Monitor Global Sales", sub: "Catalog CRUD, inventory levels, order audit log, system metrics", y: 736, stroke: "#e8590c", fill: "#fff4e6" }
  ];

  ucs.forEach(u => {
    rc.rectangle(440, u.y, 590, 68, {
      stroke: u.stroke, fill: u.fill, fillStyle: 'solid', strokeWidth: 1.6, roughness: 0.8
    });

    ctx.fillStyle = u.stroke;
    ctx.font = 'bold 13.5px "Nunito", Arial, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(u.title, 735, u.y + 26);

    ctx.font = 'normal 11px "Nunito", Arial, sans-serif';
    ctx.fillStyle = '#475569';
    ctx.fillText(u.sub, 735, u.y + 48);
  });

  drawCleanArrow(190, 230, 440, 109, "#1971c2");
  drawCleanArrow(190, 230, 440, 202, "#1971c2");
  drawCleanArrow(190, 230, 440, 295, "#1971c2");
  drawCleanArrow(190, 230, 440, 388, "#1971c2");

  drawCleanArrow(190, 610, 440, 491, "#2f9e44");
  drawCleanArrow(190, 610, 440, 584, "#2f9e44");
  drawCleanArrow(190, 610, 440, 677, "#2f9e44");

  drawCleanArrow(1290, 520, 1030, 770, "#e8590c");
  drawCleanArrow(1290, 520, 1030, 491, "#e8590c");
`;

// -------------------------------------------------------------
// Canvas Script 3: ML Pipeline (English - Spacious --[_]--> Format)
// -------------------------------------------------------------
const drawDiagram3CanvasEN = `
  // ROW 1: STEP 1 TO STEP 4 (LEFT TO RIGHT)
  drawModernCard(40, 30, 255, 155, "[Step 1] Raw Kaggle Benchmark", [
    "• transactions_train.csv (31.78M)",
    "• articles.csv (105K catalog items)",
    "• customers.csv (1.37M user profiles)",
    "• 100% genuine Kaggle dataset"
  ], "#7950f2");

  drawBadgeArrow(295, 107, 442, 107, "Filtered", null, "#1971c2");

  drawModernCard(442, 30, 255, 155, "[Step 2] 8-Week Window & Filtering", [
    "• Temporal filter t_dat < Cutoff",
    "• Eliminate anomalous zero-activity rows",
    "• Stabilize seasonal fashion trends",
    "• Optimize computational memory footprint"
  ], "#1971c2");

  drawBadgeArrow(697, 107, 844, 107, "Temporal Cut", null, "#f76707");

  drawModernCard(844, 30, 255, 155, "[Step 3] Leak-Free Temporal Split", [
    "• Training Set: 3 weeks (T-4 .. T-2)",
    "• Validation Set: 1 week (T-1)",
    "• Holdout Test: 1 week (T) [Strict Cutoff]",
    "• Zero future leakage guaranteed"
  ], "#f76707");

  drawBadgeArrow(1099, 107, 1246, 107, "Heuristics", null, "#2f9e44");

  drawModernCard(1246, 30, 255, 155, "[Step 4] Candidate Retrieval", [
    "• National weekly bestseller (BL1)",
    "• Customer repurchase heuristic (BL2)",
    "• Co-purchase item correlation graph",
    "• Candidate coverage: Recall@12 = 9.43%"
  ], "#2f9e44");

  // VERTICAL TRANSITION FROM STEP 4 DOWN TO STEP 5 (--[_]--> ON CENTER AXIS)
  drawBadgeArrow(1373.5, 185, 1373.5, 310, "Sample 1:5", "398,166 Rows", "#2f9e44");

  // ROW 2: STEP 5 TO STEP 8 (RIGHT TO LEFT)
  drawModernCard(1246, 310, 255, 155, "[Step 5] Negative Sampling (1:5)", [
    "• 1 Positive Purchase : 5 Non-purchased",
    "• Total training rows: 398,166 samples",
    "• Balanced binary target distribution",
    "• Overcome extreme matrix sparsity"
  ], "#2f9e44");

  drawBadgeArrow(1246, 387, 1099, 387, "14D Vector", null, "#f76707");

  drawModernCard(844, 310, 255, 155, "[Step 6] 14 Handcrafted Features", [
    "• User: Age, Club Member, Activity score",
    "• Item: Price percentile, Department sales",
    "• Interaction: Exponential recency decay",
    "• StandardScaler normalized inputs"
  ], "#f76707");

  drawBadgeArrow(844, 387, 697, 387, "Ensemble", null, "#1971c2");

  drawModernCard(442, 310, 255, 155, "[Step 7] Random Forest Training", [
    "• B=200 Decision Trees, Max Depth=12",
    "• Bagging bootstrap 63.2% sample split",
    "• Random feature sub-sampling sqrt(p)",
    "• Balanced class weights for imbalance"
  ], "#1971c2");

  drawBadgeArrow(442, 387, 295, 387, "Evaluate", null, "#7950f2");

  drawModernCard(40, 310, 255, 155, "[Step 8] Evaluation & Serving", [
    "• MAP@12 = 0.03014 (+356.6% vs BL1)",
    "• Sliced error matrix: Active vs Casual",
    "• Serialized to model_rf_ranker.pkl",
    "• Deployed to FastAPI Inference Gateway"
  ], "#7950f2");

  // Bottom Summary Box
  rc.rectangle(40, 500, 1461, 88, {
    stroke: '#2b8a3e', fill: '#f0fdf4', fillStyle: 'solid', strokeWidth: 1.8, roughness: 0.8
  });
  ctx.fillStyle = '#166534';
  ctx.font = 'bold 14.5px "Nunito", Arial, sans-serif';
  ctx.textAlign = 'center';
  ctx.fillText("QUANTITATIVE BENCHMARK EVALUATION RESULTS ON INDEPENDENT HOLDOUT TEST SET", 770, 529);

  ctx.font = 'normal 12px "Nunito", Arial, sans-serif';
  ctx.fillStyle = '#1e293b';
  ctx.fillText("• Baseline 1 (National Bestseller): MAP@12 = 0.00660   |   • Baseline 2 (User Repurchase): MAP@12 = 0.02498", 770, 552);
  ctx.font = 'bold 12.5px "Nunito", Arial, sans-serif';
  ctx.fillStyle = '#15803d';
  ctx.fillText("• RANDOM FOREST RANKER MODEL (HUB): MAP@12 = 0.03014 (+356.6% OVER BL1, +20.6% OVER BL2)", 770, 573);
`;

// -------------------------------------------------------------
// Canvas Script 4: Session Re-ranking Sequence (English - Spacious --[_]--> Format)
// -------------------------------------------------------------
const drawDiagram4CanvasEN = `
  const cols = [
    { name: "Consumer Buyer", sub: "(User Client)", x: 130, color: "#1971c2" },
    { name: "React 18 Frontend", sub: "(Single Page App)", x: 420, color: "#1971c2" },
    { name: "FastAPI Gateway", sub: "(Async Backend)", x: 720, color: "#f76707" },
    { name: "Random Forest Service", sub: "(ML Inference)", x: 1020, color: "#2f9e44" },
    { name: "Session Re-ranker", sub: "(Decay & Diversity)", x: 1340, color: "#7950f2" }
  ];

  cols.forEach(c => {
    rc.rectangle(c.x - 90, 25, 180, 52, {
      stroke: c.color, fill: '#ffffff', fillStyle: 'solid', strokeWidth: 1.8, roughness: 0.8
    });
    ctx.fillStyle = c.color;
    ctx.font = 'bold 12px "Nunito", Arial, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(c.name, c.x, 46);
    ctx.font = 'normal 10.5px "Nunito", Arial, sans-serif';
    ctx.fillStyle = '#64748b';
    ctx.fillText(c.sub, c.x, 63);

    ctx.save();
    ctx.strokeStyle = '#cbd5e1';
    ctx.lineWidth = 1.5;
    ctx.setLineDash([6, 4]);
    ctx.beginPath();
    ctx.moveTo(c.x, 77);
    ctx.lineTo(c.x, 825);
    ctx.stroke();
    ctx.restore();
  });

  drawBadgeArrow(130, 120, 420, 120, "1. Click Product Card / Detail View", "Captures In-Session Event", "#1864ab");
  drawBadgeArrow(420, 195, 720, 195, "2. POST /api/recommendations/rerank", "{user_id, session_clicks, k=12}", "#d9480f");
  drawBadgeArrow(720, 270, 1020, 270, "3. Candidate Retrieval & 14D Vectors", "Extract Features from Store", "#2f9e44");

  drawSelfLoop(1020, 345, 395, "4. RF predict_proba()", "200 Estimators Scoring", "#2f9e44");

  drawBadgeArrow(1020, 460, 1340, 460, "5. Forward Base Scores + Session", "Pass Intermediate Probabilities", "#7950f2");

  drawSelfLoop(1340, 535, 585, "6. Apply Session Decay & Cap", "w(t)=exp(-λΔt) • Diversified", "#7950f2");

  drawBadgeArrow(1340, 650, 720, 650, "7. Return Re-ranked Top-12 Items", "Deduplicated & Context-Aware", "#2f9e44");
  drawBadgeArrow(720, 725, 420, 725, "8. JSON Response Payload", "Strict SLA: Latency P95 < 45ms", "#d9480f");
  drawBadgeArrow(420, 795, 130, 795, "9. Dynamic UI Re-render", "Instant Client Feed Re-order", "#1864ab");

  rc.rectangle(40, 850, 1600, 52, {
    stroke: '#1971c2', fill: '#f0f7ff', fillStyle: 'solid', strokeWidth: 1.6, roughness: 0.8
  });
  ctx.fillStyle = '#0f172a';
  ctx.font = 'bold 12px "Nunito", Arial, sans-serif';
  ctx.textAlign = 'center';
  ctx.fillText("SYSTEM PERFORMANCE SLA: 100% COMPLIANCE WITH NON-FUNCTIONAL REQUIREMENTS (NFRs)", 840, 872);
  ctx.font = 'normal 11px "Nunito", Arial, sans-serif';
  ctx.fillStyle = '#475569';
  ctx.fillText("Average Latency: 32ms | P95 Latency: 45ms (< 50ms) | Throughput: > 200 RPS | Cold-Start Fallback: Automatic Weekly Bestseller", 840, 891);
`;

async function run() {
  console.log("=== EXCALIDRAW ENGLISH COMPILER (SPACIOUS & SEPARATED - NO OVERLAP) ===");

  saveExcalidrawJson("01_system_architecture_4tier.excalidraw", getDiagram1Elements());
  saveExcalidrawJson("02_usecase_diagram.excalidraw", getDiagram2Elements());
  saveExcalidrawJson("03_ml_training_pipeline.excalidraw", getDiagram3Elements());
  saveExcalidrawJson("04_realtime_session_reranking.excalidraw", getDiagram4Elements());

  const browser = await chromium.launch({
    executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    headless: true
  });

  const diagramsToRender = [
    {
      title: "Figure 4.1: HUB System 4-Tier Modular Architecture",
      subtitle: "Detailed Presentation, API Gateway, Machine Learning Engine, and Benchmark Data Persistence (Sidebar Layout)",
      script: drawDiagram1CanvasEN,
      outName: "excalidraw_01_architecture_4tier.png",
      w: 1540, h: 1040
    },
    {
      title: "Figure 3.0: System Use-Case Diagram (HCMUT CO5119 / CO3041)",
      subtitle: "System Boundary with Buyer, Data Scientist (Core Requirement), and Store Admin Roles",
      script: drawDiagram2CanvasEN,
      outName: "excalidraw_02_usecase_diagram.png",
      w: 1540, h: 880
    },
    {
      title: "Figure 2.1: Machine Learning Training Pipeline & Benchmark Evaluation Workflow",
      subtitle: "8-Step Leak-Free Rolling Temporal Split, Heuristic Retrieval, 14 Features, 1:5 Negative Sampling & MAP@12",
      script: drawDiagram3CanvasEN,
      outName: "excalidraw_03_ml_training_pipeline.png",
      w: 1540, h: 630
    },
    {
      title: "Figure 3.1: Real-Time In-Session Re-Ranking Sequence Flow",
      subtitle: "Sub-50ms Latency Cycle: User Clicks -> API Gateway -> RF Scoring -> Exponential Session Decay -> UI Update",
      script: drawDiagram4CanvasEN,
      outName: "excalidraw_04_session_rerank_sequence.png",
      w: 1680, h: 930
    }
  ];

  for (const d of diagramsToRender) {
    const page = await browser.newPage({
      viewport: { width: 1800, height: 1220 },
      deviceScaleFactor: 2
    });
    page.on('console', msg => console.log('[BROWSER LOG]', msg.text()));
    page.on('pageerror', err => console.error('[BROWSER ERROR]', err.message));

    const html = buildDiagramHtml(d.title, d.subtitle, d.script, d.w, d.h);
    await page.setContent(html, { waitUntil: 'load' });
    await page.waitForTimeout(500);

    const canvasHandle = await page.$('#canvas');
    const outPath = path.join(ASSETS_DIR, d.outName);
    await canvasHandle.screenshot({ path: outPath });
    console.log(`[PNG EN Rendered] ${outPath}`);
    await page.close();
  }

  await browser.close();
  console.log("=== ALL ENGLISH DIAGRAMS SUCCESSFULLY RENDERED (SPACIOUS & SEPARATED) ===");
}

run().catch(err => {
  console.error(err);
  process.exit(1);
});
