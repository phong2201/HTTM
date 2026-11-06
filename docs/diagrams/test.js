const { chromium } = require('playwright-core');

async function test() {
  const browser = await chromium.launch({
    executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    headless: true
  });
  const page = await browser.newPage();
  await page.setContent('<html><body style="background:#fafafa;padding:40px;"><h1 style="font-family:sans-serif;color:#1890ff;">Excalidraw Engine Ready</h1></body></html>');
  await page.screenshot({ path: 'test_engine.png' });
  await browser.close();
  console.log('SUCCESS_TEST_ENGINE');
}

test().catch(err => {
  console.error(err);
  process.exit(1);
});

