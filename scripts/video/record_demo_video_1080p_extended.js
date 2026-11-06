/**
 * KỊCH BẢN QUAY VIDEO DEMO FULL HD 1080P TOÀN DIỆN (EXTENDED FULL WALKTHROUGH ~7-10 PHÚT)
 * Đề tài: Hệ Thống Thông Minh Khuyến Nghị Sản Phẩm May Mặc HUB (Two-Stage Recommendation Pipeline)
 * Khoa Khoa Học & Kỹ Thuật Máy Tính - Trường ĐH Bách Khoa TP.HCM (ĐHQG-HCM)
 * 
 * Độ phân giải: 1920x1080 (Full HD, 30fps)
 * Trình diễn đầy đủ:
 *  1. THÊM MỚI (ADD): Đăng ký user mới, Thêm Wishlist, Thêm Đánh giá feedback, Thêm giỏ hàng,
 *     Thêm/Tạo đơn hàng mới (Checkout), Thêm cấu hình MLOps, Kích hoạt huấn luyện Train AI.
 *  2. XỬ LÝ (PROCESS): Tìm kiếm từ khóa thời gian thực, Lọc đa chiều (5 Index Groups, 11 Product Groups),
 *     Sắp xếp giá/bán chạy, Suy luận 2 giai đoạn (Random Forest 200 trees), Tái xếp hạng phiên (Algorithm 2),
 *     Cổng an toàn kiểm soát thoái hóa mô hình (Model Degradation Safety Gate).
 *  3. LỊCH SỬ CHẠY (RUN HISTORY & LOGS): Lịch sử đơn hàng cá nhân (/orders), Tiến trình & Run ID pipeline 6 bước (/data-science/schedule),
 *     Lịch sử toàn bộ đơn hàng hệ thống (/admin Orders), Dashboard doanh thu & nhật ký hoạt động (/dashboard).
 */

const path = require('path');
const fs = require('fs');
const { execSync } = require('child_process');
const projectRoot = path.resolve(__dirname, '../../');
const { chromium } = require(path.join(projectRoot, 'front-end/node_modules/playwright'));

async function injectCursorAndBanner(page) {
  await page.addInitScript(() => {
    window.addEventListener('DOMContentLoaded', () => {
      // 1. Con trỏ chuột ảo chuyên nghiệp phong cách ScreenStudio
      const cursor = document.createElement('div');
      cursor.id = 'demo-virtual-cursor';
      cursor.style.position = 'fixed';
      cursor.style.width = '24px';
      cursor.style.height = '24px';
      cursor.style.borderRadius = '50%';
      cursor.style.background = 'rgba(232, 17, 45, 0.82)';
      cursor.style.border = '2.5px solid #ffffff';
      cursor.style.boxShadow = '0 0 16px rgba(232, 17, 45, 0.95), 0 3px 8px rgba(0,0,0,0.45)';
      cursor.style.pointerEvents = 'none';
      cursor.style.zIndex = '999999';
      cursor.style.transform = 'translate(-50%, -50%)';
      cursor.style.top = '120px';
      cursor.style.left = '160px';
      document.body.appendChild(cursor);

      // Hiệu ứng sóng click lan tỏa (Click ripple ring)
      window.createClickRipple = (x, y) => {
        const ripple = document.createElement('div');
        ripple.style.position = 'fixed';
        ripple.style.left = `${x}px`;
        ripple.style.top = `${y}px`;
        ripple.style.width = '12px';
        ripple.style.height = '12px';
        ripple.style.borderRadius = '50%';
        ripple.style.border = '2.5px solid #E8112D';
        ripple.style.boxShadow = '0 0 12px #E8112D';
        ripple.style.transform = 'translate(-50%, -50%) scale(1)';
        ripple.style.pointerEvents = 'none';
        ripple.style.zIndex = '999998';
        ripple.style.transition = 'all 0.55s cubic-bezier(0.1, 0.8, 0.3, 1)';
        document.body.appendChild(ripple);
        requestAnimationFrame(() => {
          ripple.style.transform = 'translate(-50%, -50%) scale(5.8)';
          ripple.style.opacity = '0';
        });
        setTimeout(() => ripple.remove(), 600);
      };

      // 2. Banner thuyết minh cao cấp góc dưới màn hình
      const banner = document.createElement('div');
      banner.id = 'demo-scene-banner';
      banner.style.position = 'fixed';
      banner.style.bottom = '32px';
      banner.style.left = '50%';
      banner.style.transform = 'translateX(-50%)';
      banner.style.background = 'rgba(15, 23, 42, 0.94)';
      banner.style.backdropFilter = 'blur(20px)';
      banner.style.color = '#ffffff';
      banner.style.padding = '16px 32px';
      banner.style.borderRadius = '16px';
      banner.style.boxShadow = '0 20px 48px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(255, 255, 255, 0.15)';
      banner.style.zIndex = '999990';
      banner.style.display = 'flex';
      banner.style.flexDirection = 'column';
      banner.style.gap = '6px';
      banner.style.maxWidth = '980px';
      banner.style.width = 'max-content';
      banner.style.pointerEvents = 'none';
      banner.style.transition = 'all 0.35s cubic-bezier(0.16, 1, 0.3, 1)';
      banner.innerHTML = `
        <div style="display: flex; align-items: center; gap: 12px;">
          <span id="banner-tag" style="background: #E8112D; color: white; font-size: 11px; font-weight: 800; padding: 3px 10px; border-radius: 6px; letter-spacing: 0.6px; text-transform: uppercase;">DEMO</span>
          <span id="banner-title" style="font-weight: 800; font-size: 16px; letter-spacing: -0.2px; color: #f8fafc;">Khởi tạo hệ thống</span>
        </div>
        <div id="banner-desc" style="font-size: 13.5px; color: #cbd5e1; line-height: 1.5;">Đang tải ứng dụng thông minh HUB...</div>
      `;
      document.body.appendChild(banner);
    });
  });
}

async function showBanner(page, title, desc, tag = 'DEMO') {
  await page.evaluate(({ title, desc, tag }) => {
    const bTitle = document.getElementById('banner-title');
    const bDesc = document.getElementById('banner-desc');
    const bTag = document.getElementById('banner-tag');
    if (bTitle) bTitle.textContent = title;
    if (bDesc) bDesc.textContent = desc;
    if (bTag) bTag.textContent = tag;
  }, { title, desc, tag });
}

async function moveCursorSmoothly(page, targetX, targetY, steps = 14) {
  await page.evaluate(async ({ toX, toY, steps }) => {
    const cur = document.getElementById('demo-virtual-cursor');
    if (!cur) return;
    const fromX = parseFloat(cur.style.left) || 120;
    const fromY = parseFloat(cur.style.top) || 120;
    for (let i = 1; i <= steps; i++) {
      const progress = i / steps;
      // easeInOutCubic
      const ease = progress < 0.5 ? 4 * progress * progress * progress : 1 - Math.pow(-2 * progress + 2, 3) / 2;
      cur.style.left = `${fromX + (toX - fromX) * ease}px`;
      cur.style.top = `${fromY + (toY - fromY) * ease}px`;
      await new Promise(r => setTimeout(r, 22));
    }
  }, { toX: targetX, toY: targetY, steps });
}

async function smoothMoveAndClick(page, locator) {
  try {
    const box = await locator.boundingBox();
    if (!box) {
      await locator.click({ force: true }).catch(() => {});
      return;
    }
    const targetX = box.x + box.width / 2;
    const targetY = box.y + box.height / 2;

    await moveCursorSmoothly(page, targetX, targetY, 14);
    await page.waitForTimeout(300);

    // Click animation
    await page.evaluate(({ x, y }) => {
      if (window.createClickRipple) window.createClickRipple(x, y);
      const cur = document.getElementById('demo-virtual-cursor');
      if (cur) cur.style.transform = 'translate(-50%, -50%) scale(0.75)';
    }, { x: targetX, y: targetY });

    await locator.click({ force: true }).catch(() => {});

    await page.waitForTimeout(220);
    await page.evaluate(() => {
      const cur = document.getElementById('demo-virtual-cursor');
      if (cur) cur.style.transform = 'translate(-50%, -50%) scale(1)';
    });
  } catch (err) {
    await locator.click({ force: true }).catch(() => {});
  }
}

async function smoothHover(page, locator) {
  try {
    const box = await locator.boundingBox();
    if (!box) return;
    const targetX = box.x + box.width / 2;
    const targetY = box.y + box.height / 2;
    await moveCursorSmoothly(page, targetX, targetY, 12);
    await page.waitForTimeout(600);
  } catch (err) {}
}

async function smoothScroll(page, deltaY, steps = 14) {
  const step = deltaY / steps;
  for (let i = 0; i < steps; i++) {
    await page.mouse.wheel(0, step);
    await page.waitForTimeout(55);
  }
}

async function recordExtendedDemo() {
  console.log('🎬 [1080p Extended] Bắt đầu quay Video Demo Toàn Diện Hệ Thống HUB (1920x1080)...');

  const tempVideoDir = path.join(projectRoot, 'temp_video_1080p_extended');
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
    // PHẦN 1: GIỚI THIỆU & PHÂN QUYỀN VAI TRÒ (RBAC)
    // =========================================================================
    console.log('[Phần 1] Đăng nhập & RBAC Selection');
    await page.goto('http://localhost:5173/login', { waitUntil: 'networkidle' });
    await showBanner(
      page,
      'KHOA KHOA HỌC & KỸ THUẬT MÁY TÍNH - ĐH BÁCH KHOA TP.HCM (HCMUT)',
      'Hệ thống thông minh cá nhân hóa thời trang HUB: Kiến trúc Two-Stage Recommendation Pipeline',
      'BTL HCMUT'
    );
    await page.waitForTimeout(5500);

    await showBanner(
      page,
      'BẢO MẬT & PHÂN QUYỀN TRUY CẬP DỰA TRÊN VAI TRÒ (RBAC)',
      'Hệ thống phân tách 3 vai trò độc lập: Buyer (Khách mua), Data Scientist (Khoa học dữ liệu), Admin (Quản trị hệ thống)',
      'RBAC JWT'
    );
    await page.waitForTimeout(5000);

    // =========================================================================
    // PHẦN 2: THAO TÁC THÊM TÀI KHOẢN MỚI (REGISTER / ADD USER)
    // =========================================================================
    console.log('[Phần 2] Màn hình Đăng ký tài khoản');
    const registerLink = page.locator('a[href="/register"]').first();
    if (await registerLink.count() > 0) {
      await smoothMoveAndClick(page, registerLink);
    } else {
      await page.goto('http://localhost:5173/register', { waitUntil: 'networkidle' });
    }
    await page.waitForTimeout(2000);

    await showBanner(
      page,
      'THAO TÁC THÊM 1: ĐĂNG KÝ TÀI KHOẢN NGƯỜI DÙNG MỚI (ADD USER)',
      'Form đăng ký thông tin khách hàng mới: Tên tài khoản, Mật khẩu bảo mật, Họ và tên và Địa chỉ Email',
      'ADD USER'
    );
    await smoothScroll(page, 220);
    await page.waitForTimeout(4000);
    await smoothScroll(page, -220);
    await page.waitForTimeout(1500);

    // Quay lại trang đăng nhập
    await page.goto('http://localhost:5173/login', { waitUntil: 'networkidle' });
    await page.waitForTimeout(2000);

    // =========================================================================
    // PHẦN 3: LUỒNG BUYER - TRANG CHỦ & CÁC MỤC SẢN PHẨM CHI TIẾT
    // =========================================================================
    console.log('[Phần 3] Đăng nhập vai trò Buyer');
    await showBanner(
      page,
      'ĐĂNG NHẬP VAI TRÒ BUYER (KHÁCH MUA HÀNG)',
      'Tài khoản demo: buyer_demo | Đăng nhập bằng JWT Token để trải nghiệm không gian mua sắm cá nhân hóa',
      'ĐĂNG NHẬP'
    );
    await smoothMoveAndClick(page, page.locator('button[role="radio"]:has-text("Buyer")'));
    await page.waitForTimeout(600);

    await page.fill('#username', 'buyer_demo');
    await page.waitForTimeout(400);
    await page.fill('#password', '123456');
    await page.waitForTimeout(500);
    await smoothMoveAndClick(page, page.locator('button[type="submit"]'));

    await page.waitForURL('http://localhost:5173/', { timeout: 12000 });
    console.log('✓ Đã vào trang chủ Buyer');
    await page.waitForTimeout(3000);

    // Mục 1: AI Ranker Hero
    await showBanner(
      page,
      'MỤC 1: BANNER TỔNG QUAN THUẬT TOÁN HỆ THỐNG',
      'Pointwise Random Forest Ranker 200 Decision Trees + Tái xếp hạng phiên | MAP@12 = 0.0310 (+20.7% vs Heuristic)',
      'AI RANKER'
    );
    await page.waitForTimeout(5500);

    // Mục 2: Gợi ý cá nhân hóa
    await showBanner(
      page,
      'MỤC 2: SẢN PHẨM GỢI Ý DÀNH RIÊNG CHO BẠN (TWO-STAGE PIPELINE)',
      'Top-12 sản phẩm cá nhân hóa được dự đoán điểm số (score) và thứ hạng (rank) dựa trên lịch sử mua sắm',
      'CÁ NHÂN HÓA'
    );
    await smoothScroll(page, 520);
    await page.waitForTimeout(3500);

    const recCards = page.locator('main a[href*="/products/"]');
    if (await recCards.count() > 0) {
      await smoothHover(page, recCards.nth(0));
      await page.waitForTimeout(2000);
      if (await recCards.count() > 1) {
        await smoothHover(page, recCards.nth(1));
        await page.waitForTimeout(2000);
      }
    }

    // Mục 3: Bán chạy tuần
    await showBanner(
      page,
      'MỤC 3: SẢN PHẨM BÁN CHẠY NHẤT TUẦN (HEURISTIC BASELINE 1)',
      'Chiến lược Baseline quốc gia: Tổng hợp các sản phẩm có lượt mua cao nhất trong tuần trượt 7 ngày gần nhất',
      'BESTSELLER'
    );
    await smoothScroll(page, 540);
    await page.waitForTimeout(4500);

    // Mục 4: Toàn bộ 5 danh mục H&M
    await showBanner(
      page,
      'MỤC 4: KHÁM PHÁ TOÀN BỘ 5 DANH MỤC THỜI TRANG H&M',
      'Ladieswear (Nữ 40.2%), Menswear (Nam 19.8%), Divided (Trẻ 14.5%), Baby/Children (16.3%), Sport (9.2%)',
      '5 DANH MỤC'
    );
    await smoothScroll(page, 540);
    await page.waitForTimeout(4500);

    // Mục 5: Hàng mới về & Cam kết
    await showBanner(
      page,
      'MỤC 5: HÀNG MỚI VỀ & 4 CAM KẾT VẬN HÀNH DỊCH VỤ',
      'Sản phẩm mới cập nhật liên tục, gợi ý tính toán lại tự động lúc 02:00 sáng mỗi ngày',
      'CAM KẾT DỊCH VỤ'
    );
    await smoothScroll(page, 480);
    await page.waitForTimeout(4500);

    await smoothScroll(page, -2200);
    await page.waitForTimeout(2000);

    // =========================================================================
    // PHẦN 4: TÌM KIẾM, BỘ LỌC ĐA CHIỀU & PHÂN TRANG (/products)
    // =========================================================================
    console.log('[Phần 4] Duyệt Catalog sản phẩm & Bộ lọc');
    await showBanner(
      page,
      'TRANG TẤT CẢ SẢN PHẨM (CATALOG BROWSER - 105.100 MẶT HÀNG)',
      'Duyệt toàn bộ kho hàng H&M với bộ lọc đa tiêu chí, tìm kiếm từ khóa và sắp xếp thông minh',
      'CATALOG'
    );
    const navProducts = page.locator('header nav a[href="/products"]').first();
    if (await navProducts.count() > 0) {
      await smoothMoveAndClick(page, navProducts);
    } else {
      await page.goto('http://localhost:5173/products', { waitUntil: 'networkidle' });
    }
    await page.waitForTimeout(3000);

    // Xử lý Tìm kiếm từ khóa 1: jacket
    await showBanner(
      page,
      'XỬ LÝ TÌM KIẾM 1: TÌM KIẾM MẶT HÀNG "JACKET"',
      'Hệ thống lập tức truy vấn kho hàng thời trang lọc ra toàn bộ các dòng áo khoác',
      'SEARCH'
    );
    const searchInput = page.locator('input[placeholder*="Tìm"], input[type="search"]').first();
    if (await searchInput.count() > 0) {
      await smoothMoveAndClick(page, searchInput);
      await searchInput.fill('jacket');
      await page.keyboard.press('Enter');
      await page.waitForTimeout(3500);
      await searchInput.fill('');
    }

    // Xử lý Lọc theo 5 Danh mục H&M & 11 Nhóm hàng
    await showBanner(
      page,
      'XỬ LÝ BỘ LỌC 1: LỌC THEO DANH MỤC LADIESWEAR & NHÓM GARMENT UPPER BODY',
      'Lọc chính xác theo ngành hàng Nữ và Nhóm trang phục thân trên',
      'LỌC ĐA TIÊU CHÍ'
    );
    const catSelect = page.locator('select[aria-label="Danh mục"]').first();
    if (await catSelect.count() > 0) {
      await catSelect.selectOption({ label: 'Ladieswear' }).catch(() => {});
      await page.waitForTimeout(600);
    }
    const groupSelect = page.locator('select[aria-label="Nhóm sản phẩm"]').first();
    if (await groupSelect.count() > 0) {
      await groupSelect.selectOption({ index: 1 }).catch(() => {});
      await page.waitForTimeout(600);
    }
    const filterBtn = page.locator('button[type="submit"]:has-text("Lọc")').first();
    if (await filterBtn.count() > 0) {
      await smoothMoveAndClick(page, filterBtn);
      await page.waitForTimeout(3000);
    }
    await smoothScroll(page, 450);
    await page.waitForTimeout(3500);
    await smoothScroll(page, -450);
    await page.waitForTimeout(1500);

    // Xử lý Sắp xếp
    await showBanner(
      page,
      'XỬ LÝ SẮP XẾP: GIÁ TĂNG DẦN / BÁN CHẠY TUẦN',
      'Hệ thống tái lập trật tự sắp xếp giá trị sản phẩm tức thì phục vụ nhu cầu người mua',
      'SẮP XẾP'
    );
    const sortSelect = page.locator('select[aria-label="Sắp xếp"]').first();
    if (await sortSelect.count() > 0) {
      await sortSelect.selectOption({ label: 'Giá tăng' }).catch(() => {});
      await page.waitForTimeout(3000);
    }

    // =========================================================================
    // PHẦN 5: CHI TIẾT SẢN PHẨM & CÁC THAO TÁC THÊM (ADD WISHLIST / FEEDBACK / CART)
    // =========================================================================
    console.log('[Phần 5] Xem chi tiết sản phẩm');
    await showBanner(
      page,
      'XEM CHI TIẾT SẢN PHẨM (PRODUCT DETAIL PAGE)',
      'Hiển thị ảnh chất lượng cao, mã sản phẩm, nhóm hàng, màu sắc, họa tiết và đánh giá',
      'PRODUCT DETAIL'
    );

    const productItem = page.locator('main a[href^="/products/"]').first();
    if (await productItem.count() > 0) {
      await smoothMoveAndClick(page, productItem);
      await page.waitForTimeout(3500);

      // Xem chi tiết bảng 14 đặc trưng
      await showBanner(
        page,
        'BẢNG ĐẶC TẢ 14 ĐẶC TRƯNG THUỘC TÍNH SẢN PHẨM MAY MẶC',
        'Màu sắc, Loại sản phẩm, Nhóm hàng may mặc, Họa tiết, Ngành hàng và Mô tả chất liệu chi tiết',
        '14 THUỘC TÍNH'
      );
      await smoothScroll(page, 320);
      await page.waitForTimeout(4000);

      // Thao tác Thêm 1: Yêu thích (Wishlist)
      await showBanner(
        page,
        'THAO TÁC THÊM 2: LƯU VÀO DANH SÁCH YÊU THÍCH (ADD TO WISHLIST)',
        'Bấm biểu tượng trái tim để bookmark mặt hàng vào danh sách yêu thích cá nhân',
        'WISHLIST'
      );
      const heartBtn = page.locator('button:has(svg.lucide-heart), button:has-text("Yêu thích")').first();
      if (await heartBtn.count() > 0) {
        await smoothMoveAndClick(page, heartBtn);
        await page.waitForTimeout(2500);
      }

      // Thao tác Thêm 2: Đánh giá Feedback
      await showBanner(
        page,
        'THAO TÁC THÊM 3: GỬI ĐÁNH GIÁ VÀ XẾP HẠNG SAO (ADD FEEDBACK)',
        'Đánh giá chất lượng sản phẩm (1-5 sao) đóng góp dữ liệu phản hồi cho thuật toán',
        'FEEDBACK'
      );
      await smoothScroll(page, 380);
      await page.waitForTimeout(2500);
      const feedbackBtn = page.locator('button:has-text("Gửi đánh giá")').first();
      if (await feedbackBtn.count() > 0) {
        await smoothMoveAndClick(page, feedbackBtn);
        await page.waitForTimeout(2500);
      }
      await smoothScroll(page, -380);
      await page.waitForTimeout(1500);

      // Thao tác Thêm 3: Thêm vào giỏ hàng
      await showBanner(
        page,
        'THAO TÁC THÊM 4: THÊM VÀO GIỎ HÀNG (ADD TO CART)',
        'Ghi nhận sự kiện phiên ADDED_TO_CART kích hoạt tái xếp hạng tức thời',
        'ADD TO CART'
      );
      const addToCart = page.locator('button:has-text("Thêm vào giỏ")').first();
      if (await addToCart.count() > 0) {
        await smoothMoveAndClick(page, addToCart);
        await page.waitForTimeout(3000);
      }
    }

    // =========================================================================
    // PHẦN 6: XỬ LÝ NGĂN KÉO GIỎ HÀNG (CART DRAWER)
    // =========================================================================
    console.log('[Phần 6] Cart Drawer');
    await showBanner(
      page,
      'XỬ LÝ GIỎ HÀNG THÔNG MINH (CART DRAWER)',
      'Cập nhật tức thời số lượng mặt hàng, tự động tính tổng tiền thanh toán và chiết khấu',
      'CART DRAWER'
    );
    await page.waitForTimeout(4000);

    // Đóng drawer an toàn bằng phím Escape
    await page.keyboard.press('Escape');
    await page.waitForTimeout(1500);

    // =========================================================================
    // PHẦN 7: DANH SÁCH YÊU THÍCH (WISHLIST PAGE)
    // =========================================================================
    console.log('[Phần 7] Trang Wishlist');
    await page.goto('http://localhost:5173/wishlist', { waitUntil: 'networkidle' });
    await showBanner(
      page,
      'TRANG DANH SÁCH YÊU THÍCH (WISHLIST)',
      'Quản lý toàn bộ mặt hàng thời trang đã lưu, đồng bộ tài khoản và chuyển nhanh vào giỏ hàng',
      'WISHLIST'
    );
    await smoothScroll(page, 320);
    await page.waitForTimeout(4000);
    await smoothScroll(page, -320);
    await page.waitForTimeout(1500);

    // =========================================================================
    // PHẦN 8: XỬ LÝ THANH TOÁN & TẠO ĐƠN HÀNG MỚI (CHECKOUT - ADD ORDER)
    // =========================================================================
    console.log('[Phần 8] Trang Checkout & Tạo đơn hàng');
    await page.goto('http://localhost:5173/checkout', { waitUntil: 'networkidle' });
    await showBanner(
      page,
      'XỬ LÝ ĐẶT HÀNG MỚI: FORM THANH TOÁN (CHECKOUT)',
      'Điền thông tin địa chỉ giao hàng 63 tỉnh thành & Lựa chọn phương thức thanh toán COD / Chuyển khoản',
      'CHECKOUT'
    );
    await page.waitForTimeout(2500);

    // Điền thông tin giao hàng đầy đủ
    const nameInput = page.locator('input[name="name"], input#name').first();
    if (await nameInput.count() > 0) {
      await nameInput.fill('Nguyễn Văn A');
      await page.waitForTimeout(400);
    }
    const phoneInput = page.locator('input[name="phone"], input#phone').first();
    if (await phoneInput.count() > 0) {
      await phoneInput.fill('0901234567');
      await page.waitForTimeout(400);
    }
    const emailInput = page.locator('input[name="email"], input#email').first();
    if (await emailInput.count() > 0) {
      await emailInput.fill('nguyenvana@gmail.com');
      await page.waitForTimeout(400);
    }
    const addressInput = page.locator('input[name="address"], textarea[name="address"]').first();
    if (await addressInput.count() > 0) {
      await addressInput.fill('123 Đường Lê Lợi, Phường Bến Nghé');
      await page.waitForTimeout(400);
    }
    const citySelect = page.locator('select#city, select[name="city"]').first();
    if (await citySelect.count() > 0) {
      await citySelect.selectOption({ label: 'TP. Hồ Chí Minh' }).catch(() => {});
      await page.waitForTimeout(400);
    }
    const districtSelect = page.locator('select#district, select[name="district"]').first();
    if (await districtSelect.count() > 0) {
      await districtSelect.selectOption({ index: 1 }).catch(() => {});
      await page.waitForTimeout(400);
    }

    await smoothScroll(page, 380);
    await page.waitForTimeout(3000);

    // Bấm đặt hàng
    const submitOrderBtn = page.locator('button[type="submit"]:has-text("Đặt hàng"), button:has-text("Thanh toán")').first();
    if (await submitOrderBtn.count() > 0) {
      await showBanner(
        page,
        'THAO TÁC THÊM 5: XÁC NHẬN TẠO ĐƠN HÀNG MỚI (ADD ORDER)',
        'Hệ thống lưu trữ đơn hàng vào CSDL, ghi nhận log giao dịch và gửi thông báo thành công',
        'TẠO ĐƠN HÀNG'
      );
      await smoothMoveAndClick(page, submitOrderBtn);
      await page.waitForTimeout(3500);
    }

    // =========================================================================
    // PHẦN 9: LỊCH SỬ CHẠY / LỊCH SỬ ĐƠN HÀNG (/orders)
    // =========================================================================
    console.log('[Phần 9] Lịch sử đơn hàng');
    await page.goto('http://localhost:5173/orders', { waitUntil: 'networkidle' });
    await showBanner(
      page,
      'LỊCH SỬ CHẠY 1: LỊCH SỬ ĐƠN HÀNG ĐÃ ĐẶT (ORDER HISTORY)',
      'Tra cứu toàn bộ lịch sử giao dịch: Mã đơn, ngày giờ đặt, trạng thái (Đang xử lý, Hoàn tất) và hóa đơn',
      'LỊCH SỬ ĐƠN HÀNG'
    );
    await smoothScroll(page, 320);
    await page.waitForTimeout(4500);
    await smoothScroll(page, -320);
    await page.waitForTimeout(1500);

    // =========================================================================
    // PHẦN 10: XỬ LÝ TÁI XẾP HẠNG PHIÊN THỜI GIAN THỰC (ALGORITHM 2 RE-RANKING)
    // =========================================================================
    console.log('[Phần 10] Demo Re-ranking');
    await page.goto('http://localhost:5173/', { waitUntil: 'networkidle' });
    await showBanner(
      page,
      'THUẬT TOÁN 2: TÁI XẾP HẠNG THEO PHIÊN THỜI GIAN THỰC (SESSION RE-RANKING)',
      'Hàm suy giảm bán rã w(e) = exp(-λΔt) tăng tức thì trọng số các sản phẩm cùng ngành hàng vừa tương tác',
      'ALGORITHM 2'
    );
    await smoothScroll(page, 520);
    await page.waitForTimeout(4500);
    await smoothScroll(page, -520);
    await page.waitForTimeout(1500);

    // =========================================================================
    // PHẦN 11: DATA SCIENTIST - EDA DASHBOARD (9 BIỂU ĐỒ 31.78M GIAO DỊCH KAGGLE)
    // =========================================================================
    console.log('[Phần 11] Đăng nhập Data Scientist - EDA');
    await page.evaluate(() => { localStorage.clear(); sessionStorage.clear(); });
    await page.goto('http://localhost:5173/login', { waitUntil: 'networkidle' });
    await showBanner(
      page,
      'CHUYỂN VAI TRÒ: CHUYÊN GIA DỮ LIỆU (DATA SCIENTIST)',
      'Tài khoản chuyên gia: ds_demo | Toàn quyền truy cập Dashboard EDA & Đánh giá định lượng mô hình',
      'DATA SCIENTIST'
    );
    await smoothMoveAndClick(page, page.locator('button[role="radio"]:has-text("Data Scientist")'));
    await page.waitForTimeout(500);

    await page.fill('#username', 'ds_demo');
    await page.waitForTimeout(400);
    await page.fill('#password', '123456');
    await page.waitForTimeout(400);
    await smoothMoveAndClick(page, page.locator('button[type="submit"]'));

    await page.waitForURL('**/data-science**', { timeout: 12000 });
    console.log('✓ Đã vào EDA Page');
    await page.waitForTimeout(2500);

    await showBanner(
      page,
      'EXPLORATORY DATA ANALYSIS (EDA) DASHBOARD: 31.78M GIAO DỊCH H&M',
      'Trực quan hóa phân phối 9 đồ thị: Giao dịch theo ngày, Mức giá, Nhóm hàng, Độ tuổi và Phân bố mùa vụ',
      'EDA CHARTS'
    );
    await smoothScroll(page, 550);
    await page.waitForTimeout(4000);
    await smoothScroll(page, 550);
    await page.waitForTimeout(4000);
    await smoothScroll(page, 550);
    await page.waitForTimeout(4000);
    await smoothScroll(page, -1650);
    await page.waitForTimeout(2000);

    // =========================================================================
    // PHẦN 12: DATA SCIENTIST - MODEL METRICS & RADAR CHART (/data-science/model)
    // =========================================================================
    console.log('[Phần 12] Model Metrics');
    await page.goto('http://localhost:5173/data-science/model', { waitUntil: 'networkidle' });
    await showBanner(
      page,
      'ĐÁNH GIÁ ĐỊNH LƯỢNG MÔ HÌNH HỌC MÁY (MODEL PERFORMANCE BENCHMARK)',
      'Random Forest Ranker: MAP@12 = 0.03014 (+356.6% vs Bestseller BL1, +20.6% vs Repurchase BL2)',
      'BENCHMARK'
    );
    await page.waitForTimeout(4500);

    await showBanner(
      page,
      'BIỂU ĐỒ MẠNG NHỆN RADAR & TẦM QUAN TRỌNG ĐẶC TRƯNG (FEATURE IMPORTANCES)',
      'Đánh giá đồng thời đa tiêu chí MAP@12, NDCG@12, Recall@12 và độ phủ sản phẩm',
      'RADAR CHART'
    );
    await smoothScroll(page, 520);
    await page.waitForTimeout(4000);
    await smoothScroll(page, -520);
    await page.waitForTimeout(1500);

    // =========================================================================
    // PHẦN 13: DATA SCIENTIST - SLICED ERROR ANALYSIS (/data-science/errors)
    // =========================================================================
    console.log('[Phần 13] Sliced Error Analysis');
    await page.goto('http://localhost:5173/data-science/errors', { waitUntil: 'networkidle' });
    await showBanner(
      page,
      'PHÂN TÍCH MA TRẬN LỖI PHÂN TẦNG LÁT CẮT (SLICED ERROR ANALYSIS)',
      'Phân tách khách hàng Active (MAP@12 = 0.04612) vs Casual (MAP@12 = 0.01524) tránh ngộ nhận số liệu trung bình',
      'SLICED ERROR'
    );
    await smoothScroll(page, 450);
    await page.waitForTimeout(4500);
    await smoothScroll(page, -450);
    await page.waitForTimeout(1500);

    // =========================================================================
    // PHẦN 14: DATA SCIENTIST - MLOPS RETRAINING, LỊCH SỬ CHẠY & CỔNG AN TOÀN
    // =========================================================================
    console.log('[Phần 14] Training Schedule & MLOps');
    await page.goto('http://localhost:5173/data-science/schedule', { waitUntil: 'networkidle' });
    await showBanner(
      page,
      'LỊCH TRÌNH VẬN HÀNH MLOPS & CẤU HÌNH HUẤN LUYỆN LẠI (RETRAINING CONFIG)',
      'Lịch tự động Cron 02:00 sáng hàng ngày, cấu hình tham số Random Forest (n_estimators=200, max_depth=12)',
      'MLOPS CONFIG'
    );
    await page.waitForTimeout(4000);

    // Thao tác lưu cấu hình
    const saveCfgBtn = page.locator('button:has-text("Lưu cấu hình")').first();
    if (await saveCfgBtn.count() > 0) {
      await smoothMoveAndClick(page, saveCfgBtn);
      await page.waitForTimeout(2000);
    }

    // Thao tác Kích hoạt Huấn luyện AI
    await showBanner(
      page,
      'THAO TÁC XỬ LÝ 2: KÍCH HOẠT HUẤN LUYỆN LẠI MÔ HÌNH (TRIGGER TRAIN AI)',
      'Bấm nút "Train AI" gửi yêu cầu tái huấn luyện mô hình lên Kaggle / Local Engine',
      'TRAIN AI'
    );
    const trainAiBtn = page.locator('button:has-text("Train AI")').first();
    if (await trainAiBtn.count() > 0) {
      await smoothMoveAndClick(page, trainAiBtn);
      await page.waitForTimeout(3000);
    }

    // Hiển thị Tiến trình & Cổng an toàn
    await showBanner(
      page,
      'LỊCH SỬ CHẠY 2: TIẾN TRÌNH PIPELINE 6 BƯỚC & CỔNG THOÁI HÓA AN TOÀN',
      'Theo dõi trạng thái run_id, 6 bước huấn luyện và Cổng an toàn (Model Degradation Gate) ngăn suy giảm MAP@12',
      'SAFETY GATE'
    );
    await smoothScroll(page, 480);
    await page.waitForTimeout(5000);
    await smoothScroll(page, -480);
    await page.waitForTimeout(1500);

    // =========================================================================
    // PHẦN 15: ADMIN - DASHBOARD QUẢN TRỊ DOANH SỐ (/dashboard)
    // =========================================================================
    console.log('[Phần 15] Đăng nhập Admin - Dashboard');
    await page.evaluate(() => { localStorage.clear(); sessionStorage.clear(); });
    await page.goto('http://localhost:5173/login', { waitUntil: 'networkidle' });
    await showBanner(
      page,
      'CHUYỂN VAI TRÒ: QUẢN TRỊ VIÊN HỆ THỐNG (SYSTEM ADMIN)',
      'Tài khoản quản trị: kuroisme | Toàn quyền kiểm soát tài khoản, danh mục sản phẩm, đơn hàng và doanh số',
      'SYSTEM ADMIN'
    );
    await smoothMoveAndClick(page, page.locator('button[role="radio"]:has-text("Admin")'));
    await page.waitForTimeout(500);

    await page.fill('#username', 'kuroisme');
    await page.waitForTimeout(400);
    await page.fill('#password', '123456');
    await page.waitForTimeout(400);
    await smoothMoveAndClick(page, page.locator('button[type="submit"]'));

    await page.waitForURL('**/admin**', { timeout: 12000 });
    console.log('✓ Đã vào Admin Portal');
    await page.waitForTimeout(2000);

    // Vào Dashboard doanh số
    await page.goto('http://localhost:5173/dashboard', { waitUntil: 'networkidle' });
    await showBanner(
      page,
      'DASHBOARD QUẢN TRỊ DOANH THU & CHỈ SỐ VẬN HÀNH (/dashboard)',
      'Doanh thu Hôm nay, Tháng này, Năm nay; Biểu đồ doanh thu theo tháng và Top 5 sản phẩm bán chạy nhất',
      'DASHBOARD QUẢN TRỊ'
    );
    await smoothScroll(page, 480);
    await page.waitForTimeout(4000);
    await smoothScroll(page, 480);
    await page.waitForTimeout(3500);
    await smoothScroll(page, -960);
    await page.waitForTimeout(1500);

    // =========================================================================
    // PHẦN 16: ADMIN CRUD - QUẢN LÝ USER, SẢN PHẨM & XỬ LÝ ĐƠN HÀNG (/admin)
    // =========================================================================
    console.log('[Phần 16] Admin CRUD Control Center');
    await page.goto('http://localhost:5173/admin', { waitUntil: 'networkidle' });
    await showBanner(
      page,
      'ADMIN CONTROL CENTER - TAB 1: QUẢN LÝ NGƯỜI DÙNG (USERS TAB)',
      'Danh sách tài khoản toàn hệ thống, phân quyền vai trò (Buyer, Data Scientist, Admin) và kích hoạt tài khoản',
      'ADMIN USERS'
    );
    await smoothScroll(page, 380);
    await page.waitForTimeout(4000);
    await smoothScroll(page, -380);
    await page.waitForTimeout(1500);

    // Tab Products
    const prodTab = page.locator('button:has-text("Products")').first();
    if (await prodTab.count() > 0) {
      await smoothMoveAndClick(page, prodTab);
      await page.waitForTimeout(2000);
      await showBanner(
        page,
        'ADMIN CONTROL CENTER - TAB 2: QUẢN LÝ KHO SẢN PHẨM (PRODUCTS TAB)',
        'Kiểm tra danh mục hàng hóa, điều chỉnh giá bán, cập nhật số lượng tồn kho và trạng thái bày bán',
        'ADMIN PRODUCTS'
      );
      await smoothScroll(page, 380);
      await page.waitForTimeout(4000);
      await smoothScroll(page, -380);
      await page.waitForTimeout(1500);
    }

    // Tab Orders & Xử lý đơn hàng
    const orderTab = page.locator('button:has-text("Orders")').first();
    if (await orderTab.count() > 0) {
      await smoothMoveAndClick(page, orderTab);
      await page.waitForTimeout(2000);
      await showBanner(
        page,
        'ADMIN CONTROL CENTER - TAB 3: LỊCH SỬ & XỬ LÝ TOÀN BỘ ĐƠN HÀNG (ORDERS TAB)',
        'Xem danh sách mọi đơn hàng của khách, cập nhật trạng thái đơn hàng (Đang xử lý -> Hoàn tất / Đã hủy)',
        'XỬ LÝ ĐƠN HÀNG'
      );
      await smoothScroll(page, 380);
      await page.waitForTimeout(4500);
      await smoothScroll(page, -380);
      await page.waitForTimeout(1500);
    }

    // =========================================================================
    // PHẦN 17: OUTRO TỔNG KẾT TOÀN DIỆN
    // =========================================================================
    console.log('[Phần 17] Outro');
    await showBanner(
      page,
      'HOÀN TẤT DEMO ĐẦY ĐỦ HỆ THỐNG THÔNG MINH HUB',
      'Khoa Khoa Học & Kỹ Thuật Máy Tính - Trường ĐH Bách Khoa TP.HCM (ĐHQG-HCM) | Đề tài HK241',
      'TỔNG KẾT'
    );
    await page.waitForTimeout(5000);

  } catch (error) {
    console.error('❌ Lỗi trong quá trình quay demo 1080p extended:', error);
  } finally {
    await page.close();
    await context.close();
    await browser.close();
  }

  // Kết xuất video sang MP4 chuẩn Full HD 1080p bằng imageio-ffmpeg
  console.log('\n🎞️ Đang kết xuất video sang MP4 chuẩn Full HD 1080p (1920x1080, 30fps)...');
  const recordedFiles = fs.readdirSync(tempVideoDir).filter(f => f.endsWith('.webm'));
  if (recordedFiles.length === 0) {
    console.error('Không tìm thấy file WebM được tạo!');
    return;
  }

  const rawWebm = path.join(tempVideoDir, recordedFiles[0]);
  const outputMp4 = path.join(projectRoot, 'DEMO_INTELLIGENT_SYSTEMS_HUB_1080P.mp4');
  const ffmpegExe = 'C:\\Users\\Admin\\anaconda3\\envs\\hub\\Lib\\site-packages\\imageio_ffmpeg\\binaries\\ffmpeg-win-x86_64-v9.0.2.exe';

  try {
    const cmd = `"${ffmpegExe}" -y -i "${rawWebm}" -vf "scale=1920:1080" -c:v libx264 -pix_fmt yuv420p -preset medium -crf 20 -r 30 "${outputMp4}"`;
    console.log('Đang thực thi mã hóa FFmpeg...');
    execSync(cmd, { stdio: 'inherit' });
    console.log(`\n🎉 XUẤT THÀNH CÔNG VIDEO DEMO 1080P EXTENDED: ${outputMp4}`);

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

recordExtendedDemo();
