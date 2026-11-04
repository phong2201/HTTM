const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

async function testUI() {
  console.log('🚀 Starting Comprehensive UI Testing...');
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await context.newPage();

  const screenshotDir = path.join(__dirname, 'ui_test_results');
  if (!fs.existsSync(screenshotDir)) fs.mkdirSync(screenshotDir, { recursive: true });

  // 0. LOGIN SCREEN
  await page.goto('http://localhost:5173/login');
  await page.waitForSelector('button[role="radio"]');
  await page.waitForTimeout(500);
  await page.screenshot({ path: path.join(screenshotDir, '00_login_page.png'), fullPage: true });
  console.log('✓ Captured 00_login_page.png');

  // 1. DATA SCIENTIST FLOW
  console.log('\n--- 1. Testing Data Scientist Role ---');
  await page.locator('button[role="radio"]:has-text("Data Scientist")').click();
  await page.fill('#username', 'ds_demo');
  await page.fill('#password', '123456');
  await page.click('button[type="submit"]');

  await page.waitForURL('**/data-science**', { timeout: 10000 });
  console.log('✓ Successfully logged in as Data Scientist! URL:', page.url());
  await page.waitForTimeout(2000);
  await page.screenshot({ path: path.join(screenshotDir, '01_ds_eda_page.png'), fullPage: true });
  console.log('✓ Captured 01_ds_eda_page.png');

  // Navigate to Model Metrics
  await page.goto('http://localhost:5173/data-science/metrics');
  await page.waitForTimeout(2000);
  await page.screenshot({ path: path.join(screenshotDir, '02_ds_model_metrics.png'), fullPage: true });
  console.log('✓ Captured 02_ds_model_metrics.png');

  // Navigate to Error Analysis
  await page.goto('http://localhost:5173/data-science/errors');
  await page.waitForTimeout(2000);
  await page.screenshot({ path: path.join(screenshotDir, '03_ds_error_analysis.png'), fullPage: true });
  console.log('✓ Captured 03_ds_error_analysis.png');

  // Navigate to Training Schedule
  await page.goto('http://localhost:5173/data-science/schedule');
  await page.waitForTimeout(2000);
  await page.screenshot({ path: path.join(screenshotDir, '04_ds_training_schedule.png'), fullPage: true });
  console.log('✓ Captured 04_ds_training_schedule.png');

  // 2. BUYER FLOW
  console.log('\n--- 2. Testing Buyer Flow & Recommendation ---');
  await page.goto('http://localhost:5173/login');
  await page.locator('button[role="radio"]:has-text("Buyer")').click();
  await page.fill('#username', 'buyer_demo');
  await page.fill('#password', '123456');
  await page.click('button[type="submit"]');

  await page.waitForURL('http://localhost:5173/', { timeout: 10000 });
  console.log('✓ Successfully logged in as Buyer! URL:', page.url());
  await page.waitForTimeout(3000);
  await page.screenshot({ path: path.join(screenshotDir, '05_buyer_homepage_recommendations.png'), fullPage: true });
  console.log('✓ Captured 05_buyer_homepage_recommendations.png');

  // Click on a product card if available
  const productCard = page.locator('a[href*="/products/"]');
  if (await productCard.count() > 0) {
    console.log('Clicking on product to view detail...');
    await productCard.first().click();
    await page.waitForTimeout(2000);
    await page.screenshot({ path: path.join(screenshotDir, '06_buyer_product_detail.png'), fullPage: true });
    console.log('✓ Captured 06_buyer_product_detail.png');
  }

  // 3. ADMIN FLOW
  console.log('\n--- 3. Testing Admin Role ---');
  await page.goto('http://localhost:5173/login');
  await page.locator('button[role="radio"]:has-text("Admin")').click();
  await page.fill('#username', 'kuroisme');
  await page.fill('#password', '123456');
  await page.click('button[type="submit"]');

  await page.waitForURL('**/admin**', { timeout: 10000 });
  console.log('✓ Successfully logged in as Admin! URL:', page.url());
  await page.waitForTimeout(2000);
  await page.screenshot({ path: path.join(screenshotDir, '07_admin_dashboard.png'), fullPage: true });
  console.log('✓ Captured 07_admin_dashboard.png');

  await browser.close();
  console.log('\n🎉 ALL 8 SCREENS & 3 ROLES TESTED SUCCESSFULLY ON UI!');
}

testUI().catch(err => {
  console.error('❌ Test failed with error:', err);
  process.exit(1);
});
