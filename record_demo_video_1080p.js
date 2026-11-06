const { chromium } = require('./front-end/node_modules/playwright');
const path = require('path');
const fs = require('fs');
const { execSync } = require('child_process');

async function injectCursorAndBanner(page) {
  await page.addInitScript(() => {
    window.addEventListener('DOMContentLoaded', () => {
      // 1. Tạo con trỏ chuột tùy biến (Custom Cursor)
      const cursor = document.createElement('div');
      cursor.id = 'demo-mouse-cursor';
      cursor.style.position = 'fixed';
      cursor.style.top = '0';
      cursor.style.left = '0';
      cursor.style.width = '22px';
      cursor.style.height = '22px';
      cursor.style.borderRadius = '50%';
      cursor.style.backgroundColor = 'rgba(232, 17, 45, 0.45)';
      cursor.style.border = '2.5px solid #ffffff';
      cursor.style.boxShadow = '0 0 12px rgba(232, 17, 45, 0.8), 0 2px 6px rgba(0,0,0,0.4)';
      cursor.style.pointerEvents = 'none';
      cursor.style.zIndex = '99999999';
      cursor.style.transform = 'translate(-50%, -50%)';
      cursor.style.transition = 'transform 0.08s ease, width 0.15s ease, height 0.15s ease, background-color 0.15s ease';
      document.body.appendChild(cursor);

      document.addEventListener('mousemove', (e) => {
        cursor.style.left = e.clientX + 'px';
        cursor.style.top = e.clientY + 'px';
      });

      document.addEventListener('mousedown', () => {
        cursor.style.width = '32px';
        cursor.style.height = '32px';
        cursor.style.backgroundColor = 'rgba(255, 75, 43, 0.75)';
      });

      document.addEventListener('mouseup', () => {
        cursor.style.width = '22px';
        cursor.style.height = '22px';
        cursor.style.backgroundColor = 'rgba(232, 17, 45, 0.45)';
      });
    });
  });
}

async function showBanner(page, title, subtitle, tag = 'DEMO LIVE') {
  await page.evaluate(({ title, subtitle, tag }) => {
    let el = document.getElementById('demo-step-banner');
    if (!el) {
      el = document.createElement('div');
      el.id = 'demo-step-banner';
      el.style.position = 'fixed';
      el.style.bottom = '32px';
      el.style.left = '50%';
      el.style.transform = 'translateX(-50%)';
      el.style.backgroundColor = 'rgba(15, 23, 42, 0.95)';
      el.style.backdropFilter = 'blur(12px)';
      el.style.color = '#ffffff';
      el.style.padding = '14px 32px';
      el.style.borderRadius = '16px';
      el.style.boxShadow = '0 25px 50px -12px rgba(0, 0, 0, 0.5), 0 0 20px rgba(56, 189, 248, 0.25)';
      el.style.fontFamily = 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
      el.style.zIndex = '9999999';
      el.style.display = 'flex';
      el.style.flexDirection = 'column';
      el.style.alignItems = 'center';
      el.style.gap = '5px';
      el.style.pointerEvents = 'none';
      el.style.border = '1.5px solid rgba(56, 189, 248, 0.4)';
      el.style.transition = 'all 0.35s cubic-bezier(0.16, 1, 0.3, 1)';
      el.style.minWidth = '420px';
      el.style.textAlign = 'center';
      document.body.appendChild(el);
    }
    el.innerHTML = `
      <div style="font-size: 16px; font-weight: 800; color: #38bdf8; display: flex; align-items: center; justify-content: center; gap: 10px; letter-spacing: -0.01em;">
        <span style="font-size: 11px; font-weight: 900; background: #e02424; color: #fff; padding: 2px 8px; border-radius: 9999px; text-transform: uppercase;">${tag}</span>
        <span>${title}</span>
      </div>
      <div style="font-size: 13.5px; color: #cbd5e1; font-weight: 400; line-height: 1.4;">${subtitle}</div>
    `;
  }, { title, subtitle, tag });
}

async function smoothMoveAndClick(page, locator) {
  await locator.scrollIntoViewIfNeeded();
  const box = await locator.boundingBox();
  if (box) {
    await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2, { steps: 22 });
    await page.waitForTimeout(150);
    await locator.click();
  } else {
    await locator.click();
  }
}

async function smoothHover(page, locator) {
  await locator.scrollIntoViewIfNeeded();
  const box = await locator.boundingBox();
  if (box) {
    await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2, { steps: 18 });
    await page.waitForTimeout(600);
  }
}

async function recordFullHDDemo() {
  console.log('🎬 [1080p] Bắt đầu quay Video Demo Hệ Thống Thông Minh HUB (1920x1080)...');
  
  const tempVideoDir = path.join(__dirname, 'temp_video_1080p');
  if (fs.existsSync(tempVideoDir)) {
    fs.rmSync(tempVideoDir, { recursive: true, force: true });
  }
  fs.mkdirSync(tempVideoDir, { recursive: true });

  const browser = await chromium.launch({
    headless: true
  });

  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    recordVideo: {
      dir: tempVideoDir,
      size: { width: 1920, height: 1080 }
    }
  });

  const page = await context.newPage();
  await injectCursorAndBanner(page);

  try {
    // =========================================================================
    // SCENE 1: TRANG ĐĂNG NHẬP & PHÂN QUYỀN RBAC (1080p)
    // =========================================================================
    console.log('[Scene 1] Đăng nhập & RBAC Selection');
    await page.goto('http://localhost:5173/login', { waitUntil: 'networkidle' });
    await showBanner(page, 'KHOA KH&KT MÁY TÍNH - ĐH BÁCH KHOA TP.HCM', 'Hệ Thống Thông Minh Khuyến Nghị Sản Phẩm HUB (Two-Stage Recommendation System)', 'HCMUT BTL');
    await page.waitForTimeout(3000);

    await showBanner(page, 'BẢO MẬT & PHÂN QUYỀN VAI TRÒ (RBAC)', '3 vai trò độc lập: Buyer (Khách mua), Data Scientist (Khoa học dữ liệu), Admin (Quản trị hệ thống)', 'RBAC JWT');
    await page.waitForTimeout(2500);

    // =========================================================================
    // SCENE 2: LUỒNG BUYER - TRANG CHỦ & CÁC MỤC SẢN PHẨM CHI TIẾT
    // =========================================================================
    console.log('[Scene 2] Buyer - Khám phá các mục sản phẩm Trang chủ');
    await showBanner(page, 'ĐĂNG NHẬP VAI TRÒ BUYER', 'Tài khoản demo: buyer_demo | Đăng nhập để trải nghiệm gợi ý cá nhân hóa và phiên mua sắm', 'BƯỚC 1');
    await smoothMoveAndClick(page, page.locator('button[role="radio"]:has-text("Buyer")'));
    await page.waitForTimeout(400);

    await page.fill('#username', 'buyer_demo');
    await page.waitForTimeout(200);
    await page.fill('#password', '123456');
    await page.waitForTimeout(300);
    await smoothMoveAndClick(page, page.locator('button[type="submit"]'));

    await page.waitForURL('http://localhost:5173/', { timeout: 12000 });
    console.log('✓ Đã vào trang chủ Buyer');
    await page.waitForTimeout(1500);

    // Banner AI Ranker Hero
    await showBanner(page, 'MỤC 1: BANNER TỔNG QUAN THUẬT TOÁN HỆ THỐNG', 'Pointwise Random Forest Ranker + Tái xếp hạng phiên | Dữ liệu Kaggle 31.8M giao dịch H&M', 'AI RANKER');
    await page.waitForTimeout(3000);

    // Mục: Gợi ý dành riêng cho bạn
    await showBanner(page, 'MỤC 2: SẢN PHẨM GỢI Ý DÀNH RIÊNG CHO BẠN (STAGE 1 & STAGE 2)', 'Gợi ý Top-12 cá nhân hóa được trích xuất từ 105k danh mục qua 200 Decision Trees', 'CÁ NHÂN HÓA');
    await page.mouse.wheel(0, 480);
    await page.waitForTimeout(2000);

    // Hover xem chi tiết các thẻ sản phẩm trong mục Gợi ý
    const recCards = page.locator('a[href*="/products/"]');
    if (await recCards.count() > 0) {
      await smoothHover(page, recCards.nth(0));
      await page.waitForTimeout(1200);
      if (await recCards.count() > 1) {
        await smoothHover(page, recCards.nth(1));
        await page.waitForTimeout(1200);
      }
    }

    // Mục: Bán chạy tuần & Khám phá danh mục
    await showBanner(page, 'MỤC 3: SẢN PHẨM BÁN CHẠY TUẦN (HEURISTIC BASELINE 1)', 'Chiến lược Baseline quốc gia: Sản phẩm có lượt bán cao nhất trong tuần trượt gần nhất', 'BESTSELLER');
    await page.mouse.wheel(0, 500);
    await page.waitForTimeout(2500);

    await showBanner(page, 'MỤC 4: KHÁM PHÁ TOÀN BỘ 5 DANH MỤC H&M', 'Ladieswear (Nữ), Menswear (Nam), Divided (Trẻ), Baby/Children, Sport', 'CATALOG');
    await page.mouse.wheel(0, 500);
    await page.waitForTimeout(2200);

    // Mục 5: Hàng mới về & Cam kết hệ thống
    await showBanner(page, 'MỤC 5: HÀNG MỚI VỀ & CAM KẾT VẬN HÀNH', 'Cập nhật sản phẩm liên tục, gợi ý tính toán lại lúc 02:00 hàng ngày', 'DỊCH VỤ');
    await page.mouse.wheel(0, 450);
    await page.waitForTimeout(2200);

    await page.mouse.wheel(0, -1900);
    await page.waitForTimeout(1200);

    // =========================================================================
    // SCENE 3: TRANG DANH MỤC SẢN PHẨM & TÌM KIẾM BỘ LỌC CHI TIẾT (/products)
    // =========================================================================
    console.log('[Scene 3] Khám phá Trang Danh Mục Sản Phẩm (/products)');
    await showBanner(page, 'TRANG TẤT CẢ SẢN PHẨM (CATALOG BROWSER)', 'Duyệt danh mục 105k mặt hàng H&M với bộ lọc đa tiêu chí và tính năng tìm kiếm tức thời', 'TÌM KIẾM & LỌC');
    
    const navProducts = page.locator('header nav a[href="/products"]');
    if (await navProducts.count() > 0) {
      await smoothMoveAndClick(page, navProducts);
    } else {
      await page.goto('http://localhost:5173/products', { waitUntil: 'networkidle' });
    }
    await page.waitForTimeout(2000);

    // Thao tác tìm kiếm
    await showBanner(page, 'TÌM KIẾM MẶT HÀNG THEO TỪ KHÓA', 'Tìm kiếm từ khóa "jacket" trong toàn bộ kho mặt hàng thời trang', 'SEARCH');
    const searchInput = page.locator('input[placeholder*="Tìm"], input[type="search"]').first();
    if (await searchInput.count() > 0) {
      await smoothMoveAndClick(page, searchInput);
      await searchInput.fill('jacket');
      await page.keyboard.press('Enter');
      await page.waitForTimeout(2200);
    }

    // Thao tác sắp xếp & lọc danh mục H&M toàn diện
    await showBanner(page, 'BỘ LỌC ĐA CHIỀU: NGÀNH HÀNG, MÀU SẮC & TIÊU CHÍ SẮP XẾP', '5 Danh mục H&M (Ladieswear, Menswear, Divided, Baby/Children, Sport) & 11 Nhóm hàng (Upper body, Shoes, Bags, Accessories...)', 'FILTERS');
    
    // Thử chọn danh mục Ladieswear
    const categorySelect = page.locator('select[aria-label="Danh mục"]').first();
    if (await categorySelect.count() > 0) {
      await smoothMoveAndClick(page, categorySelect);
      await categorySelect.selectOption({ label: 'Ladieswear' }).catch(() => {});
      await page.waitForTimeout(600);
    }

    // Thử chọn nhóm sản phẩm
    const groupSelect = page.locator('select[aria-label="Nhóm sản phẩm"]').first();
    if (await groupSelect.count() > 0) {
      await smoothMoveAndClick(page, groupSelect);
      await groupSelect.selectOption({ index: 1 }).catch(() => {});
      await page.waitForTimeout(600);
    }

    const filterBtn = page.locator('button[type="submit"]:has-text("Lọc")').first();
    if (await filterBtn.count() > 0) {
      await smoothMoveAndClick(page, filterBtn);
      await page.waitForTimeout(1500);
    }

    await page.mouse.wheel(0, 400);
    await page.waitForTimeout(2200);
    await page.mouse.wheel(0, -400);
    await page.waitForTimeout(1000);

    // =========================================================================
    // SCENE 4: CHI TIẾT SẢN PHẨM CHUYÊN SÂU (/products/:id)
    // =========================================================================
    console.log('[Scene 4] Xem chi tiết sản phẩm');
    await showBanner(page, 'XEM CHI TIẾT SẢN PHẨM (PRODUCT DETAIL PAGE)', 'Hiển thị ảnh chất lượng cao, mã sản phẩm, nhóm hàng, màu sắc, họa tiết và đánh giá', 'PRODUCT DETAIL');
    
    const productItem = page.locator('main a[href^="/products/"]').first();
    if (await productItem.count() > 0) {
      await smoothMoveAndClick(page, productItem);
      await page.waitForTimeout(2000);

      // Xem chi tiết các thuộc tính
      await showBanner(page, 'THÔNG SỐ MẶT HÀNG MAY MẶC CHÍNH XÁC', 'Bảng thông tin 14 đặc trưng: Garment Group, Product Type, Perceived Colour, Pattern', 'THUỘC TÍNH');
      await page.mouse.wheel(0, 300);
      await page.waitForTimeout(2200);

      // Tương tác Wishlist
      await showBanner(page, 'TƯƠNG TÁC NGƯỜI DÙNG: YÊU THÍCH (WISHLIST) & GIỎ HÀNG', 'Lưu lại sản phẩm yêu thích và thêm vào giỏ hàng (ghi nhận sự kiện phiên ADDED_TO_CART)', 'TƯƠNG TÁC');
      const heartBtn = page.locator('button:has(svg.lucide-heart), button:has-text("Wishlist")').first();
      if (await heartBtn.count() > 0) {
        await smoothMoveAndClick(page, heartBtn);
        await page.waitForTimeout(1500);
      }

      // Thêm vào giỏ hàng
      const addToCart = page.locator('button:has-text("Thêm vào giỏ"), button:has-text("Add to cart")').first();
      if (await addToCart.count() > 0) {
        await smoothMoveAndClick(page, addToCart);
        await page.waitForTimeout(2000);
      }
    }

    // =========================================================================
    // SCENE 5: CART DRAWER & KIỂM TRA ĐƠN HÀNG
    // =========================================================================
    console.log('[Scene 5] Cart Drawer');
    await showBanner(page, 'NGĂN KÉO GIỎ HÀNG THÔNG MINH (CART DRAWER)', 'Cập nhật tức thời số lượng mặt hàng, giá thành và tóm tắt thanh toán', 'CART DRAWER');
    await page.waitForTimeout(2500);

    // Đóng drawer an toàn bằng phím Escape
    await page.keyboard.press('Escape');
    await page.waitForTimeout(1200);

    // =========================================================================
    // SCENE 6: DEMO THUẬT TOÁN RE-RANKING PHIÊN THỜI GIAN THỰC (ALGORITHM 2)
    // =========================================================================
    console.log('[Scene 6] Kích hoạt Re-ranking phiên');
    await page.goto('http://localhost:5173/', { waitUntil: 'networkidle' });
    await showBanner(page, 'THUẬT TOÁN 2: TÁI XẾP HẠNG THEO PHIÊN THỜI GIAN THỰC', 'Hàm suy giảm bán rã w(e) = exp(-λΔt) tăng trọng số các mặt hàng tương đồng ngành hàng vừa xem', 'ALGORITHM 2');
    await page.mouse.wheel(0, 450);
    await page.waitForTimeout(3000);
    await page.mouse.wheel(0, -450);
    await page.waitForTimeout(1000);

    // =========================================================================
    // SCENE 6B: KHÁM PHÁ DANH SÁCH YÊU THÍCH (WISHLIST)
    // =========================================================================
    console.log('[Scene 6B] Trang Wishlist');
    await page.goto('http://localhost:5173/wishlist', { waitUntil: 'networkidle' });
    await showBanner(page, 'TRANG DANH SÁCH YÊU THÍCH (WISHLIST PAGE)', 'Quản lý toàn bộ mặt hàng đã lưu, đồng bộ tài khoản và thêm nhanh vào giỏ hàng', 'WISHLIST');
    await page.mouse.wheel(0, 300);
    await page.waitForTimeout(2500);
    await page.mouse.wheel(0, -300);
    await page.waitForTimeout(1000);

    // =========================================================================
    // SCENE 6C: TRANG THANH TOÁN (CHECKOUT)
    // =========================================================================
    console.log('[Scene 6C] Trang Checkout');
    await page.goto('http://localhost:5173/checkout', { waitUntil: 'networkidle' });
    await showBanner(page, 'TRANG THANH TOÁN ĐƠN HÀNG (CHECKOUT PROCESS)', 'Thông tin người nhận, lựa chọn 63 tỉnh thành & Phương thức thanh toán COD / Chuyển khoản', 'CHECKOUT');
    await page.mouse.wheel(0, 350);
    await page.waitForTimeout(2500);
    await page.mouse.wheel(0, -350);
    await page.waitForTimeout(1000);

    // =========================================================================
    // SCENE 6D: LỊCH SỬ ĐƠN HÀNG (ORDER HISTORY)
    // =========================================================================
    console.log('[Scene 6D] Trang Lịch Sử Đơn Hàng');
    await page.goto('http://localhost:5173/orders', { waitUntil: 'networkidle' });
    await showBanner(page, 'TRANG LỊCH SỬ ĐƠN HÀNG (ORDER HISTORY)', 'Tra cứu trạng thái vận chuyển, chi tiết từng kiện hàng và gửi đánh giá chất lượng', 'LỊCH SỬ ĐƠN HÀNG');
    await page.mouse.wheel(0, 300);
    await page.waitForTimeout(2500);
    await page.mouse.wheel(0, -300);
    await page.waitForTimeout(1000);

    // =========================================================================
    // SCENE 7: LUỒNG DATA SCIENTIST - EDA DASHBOARD
    // =========================================================================
    console.log('[Scene 7] Đăng nhập Data Scientist - EDA');
    await page.evaluate(() => { localStorage.clear(); sessionStorage.clear(); });
    await page.goto('http://localhost:5173/login', { waitUntil: 'networkidle' });
    await showBanner(page, 'CHUYỂN VAI TRÒ: CHUYÊN GIA DỮ LIỆU (DATA SCIENTIST)', 'Tài khoản chuyên gia: ds_demo | Truy cập toàn bộ Dashboard EDA & Đánh giá mô hình học máy', 'DATA SCIENTIST');
    await smoothMoveAndClick(page, page.locator('button[role="radio"]:has-text("Data Scientist")'));
    await page.waitForTimeout(400);

    await page.fill('#username', 'ds_demo');
    await page.waitForTimeout(200);
    await page.fill('#password', '123456');
    await page.waitForTimeout(300);
    await smoothMoveAndClick(page, page.locator('button[type="submit"]'));

    await page.waitForURL('**/data-science**', { timeout: 12000 });
    console.log('✓ Đã vào EDA Page');
    await page.waitForTimeout(1500);

    await showBanner(page, 'EXPLORATORY DATA ANALYSIS (EDA) DASHBOARD', 'Trực quan hóa phân phối 31.78M giao dịch H&M: Độ tuổi khách hàng, rổ hàng và phân bố theo mùa', 'EDA CHARTS');
    await page.mouse.wheel(0, 450);
    await page.waitForTimeout(2500);
    await page.mouse.wheel(0, 450);
    await page.waitForTimeout(2500);
    await page.mouse.wheel(0, -900);
    await page.waitForTimeout(1200);

    // =========================================================================
    // SCENE 8: DATA SCIENTIST - MODEL METRICS & RADAR CANVAS
    // =========================================================================
    console.log('[Scene 8] Model Metrics');
    await page.goto('http://localhost:5173/data-science/metrics', { waitUntil: 'networkidle' });
    await showBanner(page, 'KẾT QUẢ ĐỊNH LƯỢNG MÔ HÌNH HỌC MÁY (MODEL PERFORMANCE)', 'Random Forest Ranker: MAP@12 = 0.03014 (+356.6% so với Bestseller, +20.6% so với Repurchase)', 'BENCHMARK');
    await page.waitForTimeout(3000);
    await page.mouse.wheel(0, 500);
    await page.waitForTimeout(2800);
    await page.mouse.wheel(0, -500);
    await page.waitForTimeout(1000);

    // =========================================================================
    // SCENE 9: DATA SCIENTIST - ERROR ANALYSIS & SAFETY GATE
    // =========================================================================
    console.log('[Scene 9] Error Analysis & Safety Gate');
    await page.goto('http://localhost:5173/data-science/errors', { waitUntil: 'networkidle' });
    await showBanner(page, 'PHÂN TÍCH MA TRẬN LỖI LÁT CẮT (SLICED ERROR ANALYSIS)', 'Phân tách khách hàng Active (MAP@12 = 0.04612) vs Casual (MAP@12 = 0.01524) tránh ngộ nhận số liệu', 'SLICED ERROR');
    await page.waitForTimeout(3000);

    await page.goto('http://localhost:5173/data-science/schedule', { waitUntil: 'networkidle' });
    await showBanner(page, 'CỔNG THOÁI HÓA AN TOÀN (MODEL DEGRADATION SAFETY GATE)', 'Kiểm định hiệu năng trước khi đẩy model lên Production; tự động rollback nếu MAP@12 suy giảm', 'SAFETY GATE');
    await page.waitForTimeout(3000);

    // =========================================================================
    // SCENE 10: LUỒNG ADMIN & BẢNG ĐIỀU KHIỂN HỆ THỐNG
    // =========================================================================
    console.log('[Scene 10] Admin Dashboard');
    await page.evaluate(() => { localStorage.clear(); sessionStorage.clear(); });
    await page.goto('http://localhost:5173/login', { waitUntil: 'networkidle' });
    await showBanner(page, 'VAI TRÒ QUẢN TRỊ VIÊN HỆ THỐNG (SYSTEM ADMIN)', 'Tài khoản quản trị: kuroisme | Toàn quyền kiểm soát tài khoản người dùng và nhật ký hệ thống', 'ADMIN');
    await smoothMoveAndClick(page, page.locator('button[role="radio"]:has-text("Admin")'));
    await page.waitForTimeout(400);

    await page.fill('#username', 'kuroisme');
    await page.waitForTimeout(200);
    await page.fill('#password', '123456');
    await page.waitForTimeout(300);
    await smoothMoveAndClick(page, page.locator('button[type="submit"]'));

    await page.waitForURL('**/admin**', { timeout: 12000 });
    console.log('✓ Đã vào Admin Dashboard');
    await page.waitForTimeout(1500);

    await showBanner(page, 'ADMIN CONTROL CENTER: QUẢN LÝ TÀI KHOẢN & AUDIT LOGS', 'Xem danh sách tài khoản Buyer, Data Scientist, Admin và phân quyền RBAC thời gian thực', 'ADMIN RBAC');
    await page.mouse.wheel(0, 450);
    await page.waitForTimeout(2800);
    await page.mouse.wheel(0, -450);
    await page.waitForTimeout(1200);

    // =========================================================================
    // SCENE 11: OUTRO KẾT LUẬN
    // =========================================================================
    console.log('[Scene 11] Outro');
    await showBanner(page, 'HOÀN TẤT DEMO HỆ THỐNG THÔNG MINH HUB', 'Khoa Khoa Học & Kỹ Thuật Máy Tính - Trường ĐH Bách Khoa TP.HCM (ĐHQG-HCM)', 'KẾT THÚC');
    await page.waitForTimeout(3500);

  } catch (error) {
    console.error('❌ Lỗi trong quá trình quay demo 1080p:', error);
  } finally {
    await page.close();
    await context.close();
    await browser.close();
  }

  // Chuyển đổi sang MP4 1080p bằng FFmpeg
  console.log('\n🎞️ Đang kết xuất video sang MP4 chuẩn Full HD 1080p (1920x1080, 60fps)...');
  const recordedFiles = fs.readdirSync(tempVideoDir).filter(f => f.endsWith('.webm'));
  if (recordedFiles.length === 0) {
    console.error('Không tìm thấy file WebM được tạo!');
    return;
  }

  const rawWebm = path.join(tempVideoDir, recordedFiles[0]);
  const outputMp4 = path.join(__dirname, 'DEMO_INTELLIGENT_SYSTEMS_HUB_1080P.mp4');
  const ffmpegExe = 'C:\\Users\\Admin\\anaconda3\\envs\\hub\\Lib\\site-packages\\imageio_ffmpeg\\binaries\\ffmpeg-win-x86_64-v9.0.2.exe';

  try {
    // Convert sang MP4 chất lượng cao Full HD 1080p
    const cmd = `"${ffmpegExe}" -y -i "${rawWebm}" -vf "scale=1920:1080" -c:v libx264 -pix_fmt yuv420p -preset medium -crf 20 -r 30 "${outputMp4}"`;
    console.log('Đang thực thi mã hóa FFmpeg...');
    execSync(cmd, { stdio: 'inherit' });
    console.log(`\n🎉 XUẤT THÀNH CÔNG VIDEO DEMO 1080P: ${outputMp4}`);

    // Sao chép sang thư mục brain artifacts
    const brainDir = 'C:\\Users\\Admin\\.gemini\\antigravity\\brain\\080f74fa-8893-4bd5-a16d-b4445c0ceaba';
    if (fs.existsSync(brainDir)) {
      const brainMp4 = path.join(brainDir, 'DEMO_INTELLIGENT_SYSTEMS_HUB_1080P.mp4');
      fs.copyFileSync(outputMp4, brainMp4);
      console.log(`✓ Đã sao chép video 1080p sang thư mục Brain: ${brainMp4}`);
    }
  } catch (err) {
    console.error('Lỗi khi convert FFmpeg:', err);
  }
}

recordFullHDDemo();
