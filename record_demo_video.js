const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
const { execSync } = require('child_process');

async function showBanner(page, title, subtitle) {
  await page.evaluate(({ title, subtitle }) => {
    let el = document.getElementById('demo-step-banner');
    if (!el) {
      el = document.createElement('div');
      el.id = 'demo-step-banner';
      el.style.position = 'fixed';
      el.style.bottom = '28px';
      el.style.left = '50%';
      el.style.transform = 'translateX(-50%)';
      el.style.backgroundColor = 'rgba(15, 23, 42, 0.94)';
      el.style.backdropFilter = 'blur(10px)';
      el.style.color = '#ffffff';
      el.style.padding = '12px 28px';
      el.style.borderRadius = '14px';
      el.style.boxShadow = '0 20px 25px -5px rgba(0, 0, 0, 0.4), 0 10px 10px -5px rgba(0, 0, 0, 0.3)';
      el.style.fontFamily = 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
      el.style.zIndex = '9999999';
      el.style.display = 'flex';
      el.style.flexDirection = 'column';
      el.style.alignItems = 'center';
      el.style.gap = '4px';
      el.style.pointerEvents = 'none';
      el.style.border = '1px solid rgba(56, 189, 248, 0.3)';
      el.style.transition = 'all 0.3s cubic-bezier(0.16, 1, 0.3, 1)';
      document.body.appendChild(el);
    }
    el.innerHTML = `
      <div style="font-size: 15px; font-weight: 700; color: #38bdf8; display: flex; align-items: center; gap: 8px;">
        <span style="display:inline-block; width:10px; height:10px; border-radius:50%; background:#22c55e; box-shadow: 0 0 10px #22c55e;"></span>
        ${title}
      </div>
      <div style="font-size: 13px; color: #cbd5e1; font-weight: 400;">${subtitle}</div>
    `;
  }, { title, subtitle });
}

async function smoothMoveAndClick(page, locator) {
  await locator.scrollIntoViewIfNeeded();
  const box = await locator.boundingBox();
  if (box) {
    await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2, { steps: 20 });
    await page.waitForTimeout(100);
    await locator.click();
  } else {
    await locator.click();
  }
}

async function recordDemo() {
  console.log('🎬 Bắt đầu quay Video Demo Hệ Thống Thông Minh HUB...');
  
  const tempVideoDir = path.join(__dirname, 'temp_video_record');
  if (fs.existsSync(tempVideoDir)) {
    fs.rmSync(tempVideoDir, { recursive: true, force: true });
  }
  fs.mkdirSync(tempVideoDir, { recursive: true });

  const browser = await chromium.launch({
    headless: true
  });

  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 },
    recordVideo: {
      dir: tempVideoDir,
      size: { width: 1440, height: 900 }
    }
  });

  const page = await context.newPage();

  try {
    // =========================================================================
    // SCENE 1: TRANG ĐĂNG NHẬP & PHÂN QUYỀN RBAC
    // =========================================================================
    console.log('[Scene 1] Mở trang Login');
    await page.goto('http://localhost:5173/login', { waitUntil: 'networkidle' });
    await showBanner(page, 'KHOA KH&KT MÁY TÍNH - ĐH BÁCH KHOA TP.HCM', 'Hệ Thống Thông Minh Gợi Ý Sản Phẩm HUB (Two-Stage Recommendation Engine)');
    await page.waitForTimeout(2500);

    await showBanner(page, 'PHÂN QUYỀN RBAC BA VAI TRÒ', 'Bảo mật JWT Bearer Token: Buyer (Khách mua), Data Scientist (Khoa học dữ liệu), Admin (Quản trị)');
    await page.waitForTimeout(2000);

    // =========================================================================
    // SCENE 2: LUỒNG BUYER (KHÁCH MUA HÀNG) & GỢI Ý CÁ NHÂN HÓA
    // =========================================================================
    console.log('[Scene 2] Đăng nhập Buyer');
    await showBanner(page, 'BƯỚC 1: ĐĂNG NHẬP VAI TRÒ BUYER', 'Tài khoản demo: buyer_demo | Truy cập danh mục sản phẩm & gợi ý cá nhân hóa');
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

    await showBanner(page, 'GỢI Ý CÁ NHÂN HÓA STAGE 1 (RETRIEVAL) & STAGE 2 (RANDOM FOREST)', 'Top-12 sản phẩm may mặc được lọc qua không gian 1.45×10¹¹ cặp và mô hình RF Ranker 200 cây');
    // Cuộn nhẹ để duyệt danh sách sản phẩm
    await page.mouse.wheel(0, 450);
    await page.waitForTimeout(2200);
    await page.mouse.wheel(0, 450);
    await page.waitForTimeout(2000);
    await page.mouse.wheel(0, -900);
    await page.waitForTimeout(1500);

    // =========================================================================
    // SCENE 3: TƯƠNG TÁC PHIÊN & RE-RANKING THỜI GIAN THỰC (ALGORITHM 2)
    // =========================================================================
    console.log('[Scene 3] Tương tác sản phẩm & Tái xếp hạng');
    await showBanner(page, 'BƯỚC 2: TƯƠNG TÁC PHIÊN & TÁI XẾP HẠNG THỜI GIAN THỰC', 'Click vào sản phẩm thời trang để kích hoạt hàm phân rã bán rã mũ t½ = 3.0 ngày (Thuật toán 2)');
    
    const firstProduct = page.locator('a[href*="/products/"]').first();
    if (await firstProduct.count() > 0) {
      await smoothMoveAndClick(page, firstProduct);
      await page.waitForTimeout(1500);
      await showBanner(page, 'CHI TIẾT MẶT HÀNG & THÊM VÀO GIỎ HÀNG', 'Ghi nhận sự kiện phiên (VIEWED / ADDED_TO_CART) cập nhật ngay vector trọng số neo danh mục a[c]');
      await page.waitForTimeout(2500);

      const addToCartBtn = page.locator('button:has-text("Thêm vào giỏ"), button:has-text("Add to cart"), button:has-text("Mua")').first();
      if (await addToCartBtn.count() > 0) {
        await smoothMoveAndClick(page, addToCartBtn);
        await page.waitForTimeout(1500);
      }
      
      // Quay về trang chủ xem danh sách đã được re-rank
      await page.goto('http://localhost:5173/', { waitUntil: 'networkidle' });
      await showBanner(page, 'KẾT QUẢ RE-RANKING TỨC THỜI', 'Các mặt hàng cùng ngành hàng được boost ưu tiên mà vẫn đảm bảo đa dạng hóa không trùng lặp');
      await page.waitForTimeout(2500);
    }

    // =========================================================================
    // SCENE 4: LUỒNG DATA SCIENTIST - DASHBOARD EDA & METRICS
    // =========================================================================
    console.log('[Scene 4] Đăng nhập Data Scientist');
    await page.goto('http://localhost:5173/login', { waitUntil: 'networkidle' });
    await showBanner(page, 'BƯỚC 3: ĐĂNG NHẬP VAI TRÒ DATA SCIENTIST', 'Tài khoản chuyên gia: ds_demo | Truy cập bảng điều khiển phân tích & huấn luyện ML');
    await smoothMoveAndClick(page, page.locator('button[role="radio"]:has-text("Data Scientist")'));
    await page.waitForTimeout(400);

    await page.fill('#username', 'ds_demo');
    await page.waitForTimeout(200);
    await page.fill('#password', '123456');
    await page.waitForTimeout(300);
    await smoothMoveAndClick(page, page.locator('button[type="submit"]'));

    await page.waitForURL('**/data-science**', { timeout: 12000 });
    console.log('✓ Đã vào trang Data Scientist');
    await page.waitForTimeout(1500);

    await showBanner(page, 'EXPLORATORY DATA ANALYSIS (EDA) DASHBOARD', 'Trực quan hóa 31.78M giao dịch Kaggle H&M, xu hướng doanh số, phân bố tuổi và rổ hàng');
    await page.mouse.wheel(0, 400);
    await page.waitForTimeout(2500);
    await page.mouse.wheel(0, 400);
    await page.waitForTimeout(2000);
    await page.mouse.wheel(0, -800);
    await page.waitForTimeout(1000);

    // Điều hướng sang Model Metrics
    console.log('[Scene 5] Model Metrics');
    await page.goto('http://localhost:5173/data-science/metrics', { waitUntil: 'networkidle' });
    await showBanner(page, 'ĐÁNH GIÁ ĐỊNH LƯỢNG MÔ HÌNH HỌC MÁY (RANDOM FOREST RANKER)', 'HUB đạt MAP@12 = 0.03014 (+356.6% so với Bestseller, +20.6% so với Repurchase)');
    await page.waitForTimeout(3000);
    await page.mouse.wheel(0, 450);
    await page.waitForTimeout(2500);
    await page.mouse.wheel(0, -450);
    await page.waitForTimeout(1000);

    // Điều hướng sang Error Analysis
    console.log('[Scene 6] Error Analysis');
    await page.goto('http://localhost:5173/data-science/errors', { waitUntil: 'networkidle' });
    await showBanner(page, 'MA TRẬN LỖI LÁT CẮT (SLICED ERROR ANALYSIS)', 'Phân tích phân hóa hành vi: Nhóm Active đạt MAP@12 = 0.04612, Nhóm Casual đạt MAP@12 = 0.01524');
    await page.waitForTimeout(3000);

    // Điều hướng sang Schedule & Safety Gate
    console.log('[Scene 7] Schedule & Safety Gate');
    await page.goto('http://localhost:5173/data-science/schedule', { waitUntil: 'networkidle' });
    await showBanner(page, 'LỊCH HUẤN LUYỆN LẠI & CỔNG THOÁI HÓA AN TOÀN (MODEL DEGRADATION GATE)', 'Tự động kiểm định hiệu năng mô hình mới; từ chối cập nhật nếu MAP@12 suy giảm dưới ngưỡng chuẩn');
    await page.waitForTimeout(3000);

    // =========================================================================
    // SCENE 8: LUỒNG ADMIN & KẾT LUẬN
    // =========================================================================
    console.log('[Scene 8] Admin Dashboard');
    await page.goto('http://localhost:5173/login', { waitUntil: 'networkidle' });
    await showBanner(page, 'BƯỚC 4: ĐĂNG NHẬP VAI TRÒ HỆ THỐNG ADMIN', 'Tài khoản quản trị viên: kuroisme | Giám sát vận hành và phân quyền RBAC');
    await smoothMoveAndClick(page, page.locator('button[role="radio"]:has-text("Admin")'));
    await page.waitForTimeout(400);

    await page.fill('#username', 'kuroisme');
    await page.waitForTimeout(200);
    await page.fill('#password', '123456');
    await page.waitForTimeout(300);
    await smoothMoveAndClick(page, page.locator('button[type="submit"]'));

    await page.waitForURL('**/admin**', { timeout: 12000 });
    console.log('✓ Đã vào trang Admin');
    await page.waitForTimeout(1500);

    await showBanner(page, 'BẢNG ĐIỀU KHIỂN QUẢN TRỊ VIÊN (ADMIN CONTROL CENTER)', 'Quản lý người dùng, phân quyền RBAC, kiểm toán giao dịch thời gian thực');
    await page.waitForTimeout(3000);

    await showBanner(page, 'TỔNG KẾT HỆ THỐNG THÔNG MINH HUB', 'Đề tài Bài Tập Lớn - Bộ môn Hệ Thống Thông Minh | Khoa KH&KT Máy Tính - ĐH Bách Khoa TP.HCM');
    await page.waitForTimeout(3500);

  } catch (error) {
    console.error('❌ Lỗi trong quá trình quay demo:', error);
  } finally {
    // Đóng trang và context để lưu video WebM
    await page.close();
    await context.close();
    await browser.close();
  }

  // Chuyển đổi file WebM sang MP4 bằng ffmpeg
  console.log('\n🎞️ Đang chuyển đổi định dạng video sang MP4 chuẩn Full HD...');
  const recordedFiles = fs.readdirSync(tempVideoDir).filter(f => f.endsWith('.webm'));
  if (recordedFiles.length === 0) {
    console.error('Không tìm thấy file WebM được tạo!');
    return;
  }

  const rawWebm = path.join(tempVideoDir, recordedFiles[0]);
  const outputMp4 = path.join(__dirname, 'DEMO_INTELLIGENT_SYSTEMS_HUB.mp4');
  const ffmpegExe = path.join(process.env.USERPROFILE, 'AppData/Local/ms-playwright/ffmpeg-1011/ffmpeg-win64.exe');

  try {
    const cmd = `"${ffmpegExe}" -y -i "${rawWebm}" -c:v libx264 -pix_fmt yuv420p -preset fast -crf 22 "${outputMp4}"`;
    console.log('Chạy lệnh chuyển đổi FFmpeg...');
    execSync(cmd, { stdio: 'inherit' });
    console.log(`\n🎉 XUẤT THÀNH CÔNG VIDEO DEMO MP4: ${outputMp4}`);

    // Copy sang thư mục brain artifacts
    const brainDir = 'C:\\Users\\Admin\\.gemini\\antigravity\\brain\\080f74fa-8893-4bd5-a16d-b4445c0ceaba';
    if (fs.existsSync(brainDir)) {
      const brainMp4 = path.join(brainDir, 'DEMO_INTELLIGENT_SYSTEMS_HUB.mp4');
      fs.copyFileSync(outputMp4, brainMp4);
      console.log(`✓ Đã sao chép video sang thư mục Brain: ${brainMp4}`);
    }
  } catch (err) {
    console.error('Lỗi khi convert FFmpeg, giữ nguyên WebM:', err);
  }
}

recordDemo();

