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
  console.log(`[Excalidraw VI] Da cap nhat: ${targetPath}`);
}

// -------------------------------------------------------------
// SƠ ĐỒ 1: KIẾN TRÚC HỆ THỐNG 4 TẦNG (BẢN TIẾNG VIỆT ĐẸP MẮT)
// -------------------------------------------------------------
function getDiagram1ElementsVI() {
  const elements = [];
  let idCounter = 1;
  const nextId = () => `el_vi_${idCounter++}`;

  const tiers = [
    { title: "TẦNG 1: TRÌNH DIỄN GIAO DIỆN (REACT 18 SINGLE-PAGE APPLICATION)", y: 50, h: 180, bg: "#e7f5ff", stroke: "#1971c2" },
    { title: "TẦNG 2: CỔNG GIAO TIẾP & ĐIỀU PHỐI API (FASTAPI ASYNC GATEWAY)", y: 290, h: 180, bg: "#fff4e6", stroke: "#f76707" },
    { title: "TẦNG 3: ĐỘNG CƠ TRÍ TUỆ NHÂN TẠO & TÁI XẾP HẠNG MÔ HÌNH (RANDOM FOREST)", y: 530, h: 190, bg: "#ebfbee", stroke: "#2f9e44" },
    { title: "TẦNG 4: LƯU TRỮ & DỮ LIỆU CHUẨN BENCHMARK THỰC TẾ (SQLITE & KAGGLE H&M)", y: 780, h: 180, bg: "#f3f0ff", stroke: "#7950f2" }
  ];

  tiers.forEach(t => {
    elements.push({
      id: nextId(), type: "rectangle", x: 40, y: t.y, width: 1440, height: t.h,
      strokeColor: t.stroke, backgroundColor: t.bg, fillStyle: "solid", strokeWidth: 2, roughness: 0.9, roundness: { type: 3 }
    });
    elements.push({
      id: nextId(), type: "text", x: 65, y: t.y + 14, text: t.title, fontSize: 15, strokeColor: t.stroke
    });
  });

  return elements;
}

function getDiagram2ElementsVI() {
  return [];
}

function getDiagram3ElementsVI() {
  return [];
}

function getDiagram4ElementsVI() {
  return [];
}

// -------------------------------------------------------------
// HTML Canvas Renderer with Rough.js (No Overlap, 2-Line Badges)
// -------------------------------------------------------------
function buildDiagramHtmlVI(title, subtitle, drawFunctionBody, width = 1540, height = 1060) {
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
    <div class="badge">Hệ Thống Thông Minh HUB • Bản Vẽ Chuẩn Excalidraw Sát Nghĩa</div>
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

      function drawActorVI(x, y, name1, name2, color = '#1971c2') {
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
// SƠ ĐỒ 1: KIẾN TRÚC 4 TẦNG (THIẾT KẾ SIDEBAR TÁCH BIỆT - KHÔNG BAO GIỜ ĐÈ CHỮ)
// -------------------------------------------------------------
const drawDiagram1CanvasVI = `
  // Sidebar Tiers và Vùng Nội Dung Chính
  const tiers = [
    {
      name: "TẦNG 1: GIAO DIỆN",
      sub: "Presentation Layer (React 18)",
      desc: "SPA • Tailwind CSS • Axios",
      y: 30, h: 180, bg: "#f0f7ff", stroke: "#1971c2"
    },
    {
      name: "TẦNG 2: CỔNG API",
      sub: "API Gateway (FastAPI Async)",
      desc: "22 Endpoints • JWT • CORS",
      y: 285, h: 180, bg: "#fff7ed", stroke: "#f76707"
    },
    {
      name: "TẦNG 3: ML ENGINE",
      sub: "Random Forest & Re-ranking",
      desc: "14 Features • B=200 Depth=12",
      y: 540, h: 195, bg: "#f0fdf4", stroke: "#2f9e44"
    },
    {
      name: "TẦNG 4: LƯU TRỮ",
      sub: "Persistence & Kaggle Data",
      desc: "SQLite 3NF • 31.78M Rows",
      y: 810, h: 180, bg: "#faf5ff", stroke: "#7950f2"
    }
  ];

  tiers.forEach(t => {
    // Left Sidebar Tier Card (Nằm riêng biệt ở cột trái x=40..260)
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

    // Vùng bao bọc các card trong tầng (Main Lane)
    rc.rectangle(285, t.y, 1205, t.h, {
      stroke: t.stroke, fill: '#ffffff', fillStyle: 'solid', roughness: 0.7, strokeWidth: 1.5, strokeLineDash: [6, 4]
    });
  });

  // TẦNG 1 CARDS
  drawModernCard(305, 52, 380, 135, "Cổng Khách Mua Hàng (Buyer Portal)", [
    "• Duyệt danh mục phân trang & tìm kiếm thời trang",
    "• Bảng tin gợi ý Top-12 cá nhân hóa trên trang chủ",
    "• Theo dõi tương tác click xem chi tiết theo phiên"
  ], "#1864ab");

  drawModernCard(715, 52, 400, 135, "Cổng Data Scientist (Analytics Workspace)", [
    "• Bảng điều khiển 10 biểu đồ trực quan hóa dữ liệu EDA",
    "• Đánh giá độ đo MAP@12 và radar so sánh Baselines",
    "• Phân tích lát cắt ma trận lỗi & Kích hoạt tái huấn luyện"
  ], "#1864ab");

  drawModernCard(1145, 52, 325, 135, "Cổng Quản Trị Viên (Admin Operations)", [
    "• Quản trị CRUD danh mục & vòng đời sản phẩm",
    "• Kiểm soát lượng hàng tồn kho & trạng thái bán lẻ",
    "• Giám sát doanh thu thương mại & nhật ký hệ thống"
  ], "#1864ab");

  // TẦNG 2 CARDS
  drawModernCard(305, 307, 380, 135, "Danh Mục 22 RESTful API Endpoints", [
    "• /api/recommendations/rerank (Gợi ý theo phiên)",
    "• /api/products, /api/auth, /api/cart, /api/orders",
    "• /api/ai/reports, /api/ai/trigger-training"
  ], "#d9480f");

  drawModernCard(715, 307, 400, 135, "Middleware Bảo Mật & Xác Thực Phân Quyền", [
    "• Xác thực người dùng bằng JWT Bearer Token (OAuth2)",
    "• Kiểm định toàn vẹn dữ liệu đầu vào qua Pydantic Schema",
    "• Chính sách bảo vệ nguồn gốc chéo CORS & Ghi log"
  ], "#d9480f");

  drawModernCard(1145, 307, 325, 135, "Bộ Điều Phối Tác Vụ Bất Đồng Bộ", [
    "• Worker luồng chạy nền quản lý tiến trình huấn luyện",
    "• Cam kết SLA phản hồi gợi ý cực nhanh: P95 < 50ms",
    "• Năng lực phục vụ thông lượng cao: > 200 RPS"
  ], "#d9480f");

  // TẦNG 3 CARDS
  drawModernCard(305, 560, 380, 150, "Giai Đoạn 1: Rút Trích Ứng Viên Sơ Tuyển", [
    "• Heuristics Bestseller tuần toàn quốc (12 món)",
    "• Heuristics Mua lặp lại cá nhân (Repurchase)",
    "• Đồ thị đồng mua kết hợp danh mục (Co-purchase)",
    "• Tỷ lệ bao phủ khách hàng đạt Recall@12 = 9.43%"
  ], "#2b8a3e");

  drawModernCard(715, 560, 400, 150, "Pipeline Kỹ Nghệ 14 Đặc Trưng Máy Học", [
    "• Khách hàng: Độ tuổi, Tình trạng hội viên, Tích cực",
    "• Mặt hàng: Thứ hạng giá, Nhóm ngành, Tốc độ bán",
    "• Tương tác: Hàm phân rã thời gian (lambda = 0.05)",
    "• Lấy mẫu âm có kiểm soát tỷ lệ 1 Mua : 5 Không mua"
  ], "#2b8a3e");

  drawModernCard(1145, 560, 325, 150, "Bộ Xếp Hạng RF & Re-ranking Phiên", [
    "• Random Forest B=200 cây quyết định, Depth=12",
    "• Dự báo xác suất mua hàng qua predict_proba()",
    "• Phân rã chu kỳ bán rã t1/2 = 3.0 ngày theo click",
    "• Khống chế ngập lụt danh mục: MAX_PER_CODE = 1"
  ], "#2b8a3e");

  // TẦNG 4 CARDS
  drawModernCard(305, 832, 380, 135, "Cơ Sở Dữ Liệu Quan Hệ (SQLite)", [
    "• Bảng: users, products, orders, feedbacks",
    "• Bảng kết quả: user_recommendations",
    "• Lược đồ chuẩn hóa 3NF bảo đảm toàn vẹn dữ liệu"
  ], "#5f3dc4");

  drawModernCard(715, 832, 400, 135, "Hiện Vật Mô Hình & Lưu Trữ Đặc Trưng", [
    "• model_rf_ranker.pkl (Cây nhị phân tuần tự hóa)",
    "• feature_metadata.json (Siêu dữ liệu đặc trưng)",
    "• Bộ chuẩn hóa StandardScaler và Encoder lưu trữ"
  ], "#5f3dc4");

  drawModernCard(1145, 832, 325, 135, "Dữ Liệu Chuẩn Thực Tế Kaggle H&M", [
    "• 31.78M Giao dịch thực tế • 105K Mặt hàng",
    "• Cắt cửa sổ trượt thời gian (Temporal Rolling Split)",
    "• Cam kết 100% dữ liệu thật, không tạo số liệu giả"
  ], "#5f3dc4");

  // CÁC MŨI TÊN KẾT NỐI VÀ BADGE HOÀN TOÀN Ở KHOẢNG HỞ THOÁNG (CHUẨN --[_]-->)
  // Giữa Tầng 1 và Tầng 2 (Khoảng hở y=210..285, cao 75px)
  drawBadgeArrow(495, 210, 495, 285, "Yêu Cầu Gợi Ý (HTTP/JSON)", "GET /predict/user_id", "#1864ab");
  drawBadgeArrow(915, 210, 915, 285, "Thao Tác Quản Trị & EDA", "GET /reports • POST /retrain", "#1864ab");
  drawBadgeArrow(1307, 210, 1307, 285, "Kiểm Tra Trạng Thái & Kho", "GET /admin/dashboard", "#1864ab");

  // Giữa Tầng 2 và Tầng 3 (Khoảng hở y=465..540, cao 75px)
  drawBadgeArrow(495, 465, 495, 540, "Sinh Ứng Viên Sơ Tuyển", "Lọc Heuristic Đa Kênh", "#d9480f");
  drawBadgeArrow(915, 465, 915, 540, "Lắp Ráp Vector Đặc Trưng", "14 Features Matrix", "#d9480f");
  drawBadgeArrow(1307, 465, 1307, 540, "Chấm Điểm & Tái Xếp Hạng", "P95 Latency < 50ms", "#d9480f");

  // Giữa Tầng 3 và Tầng 4 (Khoảng hở y=735..810, cao 75px)
  drawBadgeArrow(495, 735, 495, 810, "Truy Vấn Dữ Liệu SQL", "SQLAlchemy ORM", "#2b8a3e");
  drawBadgeArrow(915, 735, 915, 810, "Nạp Mô Hình Đã Khớp", "Joblib Deserializer", "#2b8a3e");
  drawBadgeArrow(1307, 735, 1307, 810, "Nạp Tập Train/Val/Test", "Chống Rò Rỉ Tuyệt Đối", "#2b8a3e");
`;

// -------------------------------------------------------------
// SƠ ĐỒ 2: USE CASE (THOÁNG ĐÃNG, ĐƯỜNG KẾT NỐI KHÔNG CẮT CHÉO HỘP)
// -------------------------------------------------------------
const drawDiagram2CanvasVI = `
  rc.rectangle(260, 20, 960, 830, {
    stroke: '#64748b', fill: '#f8fafc', fillStyle: 'solid', strokeWidth: 2, roughness: 0.8
  });
  ctx.fillStyle = '#0f172a';
  ctx.font = 'bold 16px "Nunito", Arial, sans-serif';
  ctx.textAlign = 'left';
  ctx.fillText("PHẠM VI HỆ THỐNG: NỀN TẢNG GỢI Ý THỜI TRANG THÔNG MINH HUB", 290, 52);

  drawActorVI(120, 230, "Khách Mua Hàng", "(Buyer - Role 1)", "#1971c2");
  drawActorVI(120, 610, "Data Scientist", "(ML Engineer - Role 2)", "#2f9e44");
  drawActorVI(1360, 520, "Quản Trị Viên", "(Store Admin - Role 3)", "#e8590c");

  const ucs = [
    { title: "UC-01: Duyệt Danh Mục Sản Phẩm & Bộ Lọc", sub: "Tìm kiếm toàn văn • Lọc theo nhóm ngành • Xem thẻ trang phục", y: 75, stroke: "#1971c2", fill: "#e7f5ff" },
    { title: "UC-02: Xem Gợi Ý Cá Nhân Hóa (Top-12 RF)", sub: "Thu nhận danh sách gợi ý qua mô hình Random Forest Ranker", y: 168, stroke: "#1971c2", fill: "#e7f5ff" },
    { title: "UC-03: Tương Tác Phiên & Tái Xếp Hạng Tức Thì", sub: "Click/view kích hoạt tái xếp hạng luồng feed trong mili-giây", y: 261, stroke: "#1971c2", fill: "#e7f5ff" },
    { title: "UC-04: Xem Chi Tiết & Gợi Ý Phối Đồ Liên Quan", sub: "Heuristics đồng mua & các mặt hàng khách cùng quan tâm", y: 354, stroke: "#1971c2", fill: "#e7f5ff" },
    { title: "UC-05: Khám Phá EDA & Giám Sát Phân Phối Dữ Liệu", sub: "Theo dõi lượng giao dịch, độ tuổi, phân bố giá cả & trôi dạt", y: 457, stroke: "#2f9e44", fill: "#ebfbee" },
    { title: "UC-06: Đánh Giá Hiệu Năng Mô Hình & Lát Cắt Lỗi", sub: "Độ đo offline MAP@12, precision/recall, phân tích Active/Casual", y: 550, stroke: "#2f9e44", fill: "#ebfbee" },
    { title: "UC-07: Kích Hoạt Tái Huấn Luyện Mô Hình Tự Động", sub: "Cắt tập trượt thời gian, lấy mẫu âm, khớp 200 cây quyết định", y: 643, stroke: "#2f9e44", fill: "#ebfbee" },
    { title: "UC-08: Quản Trị Tồn Kho & Giám Sát Doanh Số", sub: "CRUD sản phẩm, trạng thái tồn kho, nhật ký giao dịch thương mại", y: 736, stroke: "#e8590c", fill: "#fff4e6" }
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

  // Mũi tên từ Khách Mua Hàng
  drawCleanArrow(190, 230, 440, 109, "#1971c2");
  drawCleanArrow(190, 230, 440, 202, "#1971c2");
  drawCleanArrow(190, 230, 440, 295, "#1971c2");
  drawCleanArrow(190, 230, 440, 388, "#1971c2");

  // Mũi tên từ Data Scientist
  drawCleanArrow(190, 610, 440, 491, "#2f9e44");
  drawCleanArrow(190, 610, 440, 584, "#2f9e44");
  drawCleanArrow(190, 610, 440, 677, "#2f9e44");

  // Mũi tên từ Quản Trị Viên (Kết nối thẳng gãy gọn vào UC-08 và UC-05, không cắt chéo lung tung)
  drawCleanArrow(1290, 520, 1030, 770, "#e8590c");
  drawCleanArrow(1290, 520, 1030, 491, "#e8590c");
`;

// -------------------------------------------------------------
// SƠ ĐỒ 3: ML TRAINING PIPELINE (KHOẢNG CÁCH THOÁNG ĐÃNG - CHUẨN --[_]-->)
// -------------------------------------------------------------
const drawDiagram3CanvasVI = `
  // HÀNG 1: TỪ BƯỚC 1 ĐẾN BƯỚC 4 (TRÁI QUA PHẢI)
  drawModernCard(40, 30, 255, 155, "[Bước 1] Dữ Liệu Thật Kaggle", [
    "• transactions_train.csv (31.78M)",
    "• articles.csv (105K mặt hàng)",
    "• customers.csv (1.37M hồ sơ)",
    "• Cam kết 100% dữ liệu thực tế"
  ], "#7950f2");

  drawBadgeArrow(295, 107, 442, 107, "Đã lọc", null, "#1971c2");

  drawModernCard(442, 30, 255, 155, "[Bước 2] Cửa Sổ Trượt 8 Tuần", [
    "• Lọc mốc thời gian t_dat < T (Cutoff)",
    "• Loại bỏ giao dịch rác / bất thường",
    "• Ổn định xu hướng mùa vụ thời trang",
    "• Thu hẹp không gian tính toán"
  ], "#1971c2");

  drawBadgeArrow(697, 107, 844, 107, "Cắt mốc", null, "#f76707");

  drawModernCard(844, 30, 255, 155, "[Bước 3] Chia Tập Chống Rò Rỉ", [
    "• Tập Train: 3 tuần (T-4 .. T-2)",
    "• Tập Validation: 1 tuần (T-1)",
    "• Tập Test: 1 tuần (T) [Mốc đóng]",
    "• Tuyệt đối không rò rỉ dữ liệu"
  ], "#f76707");

  drawBadgeArrow(1099, 107, 1246, 107, "Heuristics", null, "#2f9e44");

  drawModernCard(1246, 30, 255, 155, "[Bước 4] Rút Trích Ứng Viên", [
    "• Bestseller tuần quốc gia (BL1)",
    "• Mua lặp lại cá nhân (BL2)",
    "• Đồ thị đồng mua (Co-purchase)",
    "• Recall@12 đạt 9.43% độ bao phủ"
  ], "#2f9e44");

  // CHUYỂN TẦNG THẲNG ĐỨNG TỪ BƯỚC 4 XUỐNG BƯỚC 5 (CHUẨN --[_]--> THẲNG TRỤC)
  drawBadgeArrow(1373.5, 185, 1373.5, 310, "Lấy mẫu 1:5", "398.166 Dòng", "#2f9e44");

  // HÀNG 2: TỪ BƯỚC 5 ĐẾN BƯỚC 8 (PHẢI QUA TRÁI)
  drawModernCard(1246, 310, 255, 155, "[Bước 5] Lấy Mẫu Âm (1:5)", [
    "• 1 Mẫu Mua : 5 Mẫu Không Mua",
    "• Tổng mẫu huấn luyện: 398.166 dòng",
    "• Phân phối nhãn nhị phân cân bằng",
    "• Khắc phục độ thưa ma trận"
  ], "#2f9e44");

  drawBadgeArrow(1246, 387, 1099, 387, "Vector 14D", null, "#f76707");

  drawModernCard(844, 310, 255, 155, "[Bước 6] Kỹ Nghệ 14 Đặc Trưng", [
    "• Khách hàng: Tuổi, Club, Hoạt động",
    "• Mặt hàng: Giá, Phân khúc, Doanh số",
    "• Tương tác: Phân rã thời gian",
    "• Chuẩn hóa dữ liệu StandardScaler"
  ], "#f76707");

  drawBadgeArrow(844, 387, 697, 387, "Khớp cây", null, "#1971c2");

  drawModernCard(442, 310, 255, 155, "[Bước 7] Huấn Luyện Random Forest", [
    "• B=200 Cây quyết định, Depth=12",
    "• Đóng gói Bagging 63.2% mẫu dữ liệu",
    "• Chọn ngẫu nhiên căn bậc 2 đặc trưng",
    "• Trọng số cân bằng class_weight"
  ], "#1971c2");

  drawBadgeArrow(442, 387, 295, 387, "Đánh giá", null, "#7950f2");

  drawModernCard(40, 310, 255, 155, "[Bước 8] Đánh Giá & Triển Khai", [
    "• MAP@12 = 0.03014 (+356.6% vs BL1)",
    "• Chẩn đoán ma trận lỗi Active/Casual",
    "• Đóng gói tệp model_rf_ranker.pkl",
    "• Nạp trực tiếp vào API Gateway"
  ], "#7950f2");

  // Khung tổng kết định lượng
  rc.rectangle(40, 500, 1461, 88, {
    stroke: '#2b8a3e', fill: '#f0fdf4', fillStyle: 'solid', strokeWidth: 1.8, roughness: 0.8
  });
  ctx.fillStyle = '#166534';
  ctx.font = 'bold 14.5px "Nunito", Arial, sans-serif';
  ctx.textAlign = 'center';
  ctx.fillText("KẾT QUẢ THỰC NGHIỆM ĐỊNH LƯỢNG TRÊN TẬP KIỂM THỬ ĐỘC LẬP (HOLDOUT TEST SET)", 770, 529);

  ctx.font = 'normal 12px "Nunito", Arial, sans-serif';
  ctx.fillStyle = '#1e293b';
  ctx.fillText("• Baseline 1 (Bestseller Quốc Gia): MAP@12 = 0.00660   |   • Baseline 2 (Mua Lặp Lại Cá Nhân): MAP@12 = 0.02498", 770, 552);
  ctx.font = 'bold 12.5px "Nunito", Arial, sans-serif';
  ctx.fillStyle = '#15803d';
  ctx.fillText("• MÔ HÌNH RANDOM FOREST RANKER (HUB): MAP@12 = 0.03014 (VƯỢT TRỘI +356.6% SO VỚI BL1, +20.6% SO VỚI BL2)", 770, 573);
`;

// -------------------------------------------------------------
// SƠ ĐỒ 4: SEQUENCE DIAGRAM (RỘNG RÃI, CHUẨN --[_]--> KHÔNG TRÙNG LẶP)
// -------------------------------------------------------------
const drawDiagram4CanvasVI = `
  const cols = [
    { name: "Khách Mua Hàng", sub: "(Buyer Client)", x: 130, color: "#1971c2" },
    { name: "Giao Diện React 18", sub: "(Single Page App)", x: 420, color: "#1971c2" },
    { name: "Cổng API FastAPI", sub: "(Async Backend)", x: 720, color: "#f76707" },
    { name: "Mô Hình Random Forest", sub: "(Model Service)", x: 1020, color: "#2f9e44" },
    { name: "Động Cơ Tái Xếp Hạng", sub: "(Session Engine)", x: 1340, color: "#7950f2" }
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

  // Bước 1: Khách hàng click
  drawBadgeArrow(130, 120, 420, 120, "1. Click thẻ mặt hàng / Xem chi tiết", "Phát sinh tương tác trong phiên", "#1864ab");

  // Bước 2: React gửi request
  drawBadgeArrow(420, 195, 720, 195, "2. POST /api/recommendations/rerank", "{user_id, session_clicks, k=12}", "#d9480f");

  // Bước 3: Gateway truy vấn RF Service
  drawBadgeArrow(720, 270, 1020, 270, "3. Rút trích Ứng viên & 14 Vector", "Trích xuất đặc trưng từ Feature Store", "#2f9e44");

  // Bước 4: Tự xử lý RF Scoring (Chuẩn --[__] / <--| lồng ghép trực tiếp)
  drawSelfLoop(1020, 345, 395, "4. RF predict_proba()", "200 Cây Random Forest", "#2f9e44");

  // Bước 5: Truyền kết quả sang Session Engine
  drawBadgeArrow(1020, 460, 1340, 460, "5. Chuyển điểm cơ sở + Lịch sử", "Truyền chuỗi sự kiện click phiên", "#7950f2");

  // Bước 6: Tự xử lý Decay & Cap (Chuẩn --[__] / <--| lồng ghép trực tiếp)
  drawSelfLoop(1340, 535, 585, "6. Phân rã bán rã t1/2=3.0d", "Khống chế: MAX_PER_CODE=1", "#7950f2");

  // Bước 7: Trả về Top 12 (Đi từ Col 5 về Col 3, badge đặt ở giữa)
  drawBadgeArrow(1340, 650, 720, 650, "7. Trả về Top-12 đã Tái Xếp Hạng", "Đã lọc trùng lặp & tối ưu ngữ cảnh", "#2f9e44");

  // Bước 8: Trả JSON về React
  drawBadgeArrow(720, 725, 420, 725, "8. Phản hồi JSON danh sách Top-12", "Thời gian phản hồi P95 Latency < 45ms", "#d9480f");

  // Bước 9: React cập nhật giao diện
  drawBadgeArrow(420, 795, 130, 795, "9. Cập nhật mượt mà danh sách trên UI", "Khách hàng nhận gợi ý mới tức thì", "#1864ab");

  // Thanh cam kết SLA NFRs
  rc.rectangle(40, 850, 1600, 52, {
    stroke: '#1971c2', fill: '#f0f7ff', fillStyle: 'solid', strokeWidth: 1.6, roughness: 0.8
  });
  ctx.fillStyle = '#0f172a';
  ctx.font = 'bold 12px "Nunito", Arial, sans-serif';
  ctx.textAlign = 'center';
  ctx.fillText("CAM KẾT HIỆU NĂNG HỆ THỐNG: THỎA MÃN 100% CÁC YÊU CẦU PHI CHỨC NĂNG (NFRs)", 840, 872);
  ctx.font = 'normal 11px "Nunito", Arial, sans-serif';
  ctx.fillStyle = '#475569';
  ctx.fillText("Độ trễ trung bình: 32ms | Độ trễ P95: 45ms (< 50ms) | Thông lượng: > 200 RPS | Khách mới (Cold-start) tự động chuyển Bestseller", 840, 891);
`;

// -------------------------------------------------------------
// Main Runner
// -------------------------------------------------------------
async function run() {
  console.log("=== EXCALIDRAW VIETNAMESE COMPILER (SPACIOUS & SEPARATED - NO OVERLAP) ===");

  saveExcalidrawJson("01_system_architecture_4tier_vi.excalidraw", getDiagram1ElementsVI());
  saveExcalidrawJson("02_usecase_diagram_vi.excalidraw", getDiagram2ElementsVI());
  saveExcalidrawJson("03_ml_training_pipeline_vi.excalidraw", getDiagram3ElementsVI());
  saveExcalidrawJson("04_realtime_session_reranking_vi.excalidraw", getDiagram4ElementsVI());

  const browser = await chromium.launch({
    executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    headless: true
  });

  const diagramsToRender = [
    {
      title: "Hình 4.1: Kiến Trúc Phân Tầng Module 4 Lớp của Hệ Thống HUB",
      subtitle: "Chi tiết Tầng Trình diễn, Cổng API, Động cơ Trí tuệ Nhân tạo và Lưu trữ Dữ liệu Chuẩn (Thiết kế Sidebar)",
      script: drawDiagram1CanvasVI,
      outName: "excalidraw_01_architecture_4tier_vi.png",
      w: 1540, h: 1040
    },
    {
      title: "Hình 3.0: Sơ Đồ Trường Hợp Sử Dụng (Use-Case Diagram) Tổng Thể",
      subtitle: "Mối quan hệ Tác nhân (Buyer, Data Scientist, Admin) và Phạm vi Biên Hệ thống HUB",
      script: drawDiagram2CanvasVI,
      outName: "excalidraw_02_usecase_diagram_vi.png",
      w: 1540, h: 880
    },
    {
      title: "Hình 2.1: Quy Trình Luồng Dữ Liệu & Huấn Luyện Mô Hình Học Máy",
      subtitle: "Cắt tập trượt thời gian chống rò rỉ dữ liệu, Lấy mẫu âm 1:5, Kỹ nghệ 14 đặc trưng và Khớp Rừng Ngẫu Nhiên",
      script: drawDiagram3CanvasVI,
      outName: "excalidraw_03_ml_training_pipeline_vi.png",
      w: 1540, h: 630
    },
    {
      title: "Hình 3.1: Sơ Đồ Tuần Tự Tái Xếp Hạng Phiên Theo Thời Gian Thực",
      subtitle: "Ghi nhận phản hồi click của khách hàng, Phân rã bán rã hàm mũ và Khống chế đa dạng hóa danh mục",
      script: drawDiagram4CanvasVI,
      outName: "excalidraw_04_session_rerank_sequence_vi.png",
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

    const html = buildDiagramHtmlVI(d.title, d.subtitle, d.script, d.w, d.h);
    await page.setContent(html, { waitUntil: 'load' });
    await page.waitForTimeout(500);

    const canvasHandle = await page.$('#canvas');
    const outPath = path.join(ASSETS_DIR, d.outName);
    await canvasHandle.screenshot({ path: outPath });
    console.log(`[PNG VI Rendered] ${outPath}`);
    await page.close();
  }

  await browser.close();
  console.log("=== TOAN BO SO DO TIENG VIET MOI DA RENDER THANH CONG (TACH BACH THOANG DANG) ===");
}

run().catch(err => {
  console.error(err);
  process.exit(1);
});
