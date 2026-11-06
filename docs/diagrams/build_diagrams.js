const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright-core');

const DIAGRAMS_DIR = path.join(__dirname);
const ASSETS_DIR = path.join('D:', 'HTTM', 'docs', 'report_assets');

// Helper to build Excalidraw element JSON
function createExcalidrawBox(id, x, y, width, height, text, strokeColor, bgColor, subtext = '') {
  return [
    {
      id: `box_${id}`,
      type: "rectangle",
      x, y, width, height,
      angle: 0,
      strokeColor: strokeColor || "#1e1e1e",
      backgroundColor: bgColor || "#ffffff",
      fillStyle: "solid",
      strokeWidth: 2,
      strokeStyle: "solid",
      roughness: 1,
      opacity: 100,
      roundness: { type: 3 },
      seed: Math.floor(Math.random() * 100000)
    },
    {
      id: `text_${id}`,
      type: "text",
      x: x + 10,
      y: y + (subtext ? height / 4 : height / 2 - 10),
      width: width - 20,
      height: height / 2,
      angle: 0,
      strokeColor: "#1e1e1e",
      backgroundColor: "transparent",
      fillStyle: "solid",
      strokeWidth: 1,
      strokeStyle: "solid",
      roughness: 1,
      opacity: 100,
      text: subtext ? `${text}\n${subtext}` : text,
      fontSize: 16,
      fontFamily: 1,
      textAlign: "center",
      verticalAlign: "middle",
      containerId: `box_${id}`,
      originalText: subtext ? `${text}\n${subtext}` : text
    }
  ];
}

function createExcalidrawArrow(id, startX, startY, endX, endY, label = '') {
  return [
    {
      id: `arrow_${id}`,
      type: "arrow",
      x: startX,
      y: startY,
      width: endX - startX,
      height: endY - startY,
      angle: 0,
      strokeColor: "#2b8a3e",
      backgroundColor: "transparent",
      fillStyle: "solid",
      strokeWidth: 2,
      strokeStyle: "solid",
      roughness: 1,
      opacity: 100,
      points: [[0, 0], [endX - startX, endY - startY]],
      roundness: { type: 2 },
      seed: Math.floor(Math.random() * 100000)
    }
  ];
}

function saveExcalidrawFile(filename, elements) {
  const excalidrawDoc = {
    type: "excalidraw",
    version: 2,
    source: "https://excalidraw.com",
    elements: elements,
    appState: {
      viewBackgroundColor: "#ffffff",
      gridSize: null
    },
    files: {}
  };
  const filePath = path.join(DIAGRAMS_DIR, filename);
  fs.writeFileSync(filePath, JSON.stringify(excalidrawDoc, null, 2), 'utf8');
  console.log(`Saved Excalidraw JSON: ${filePath}`);
}

async function renderHtmlToPng(htmlContent, outputPngPath, width = 1400, height = 900) {
  const browser = await chromium.launch({
    executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    headless: true
  });
  const page = await browser.newPage({
    viewport: { width, height },
    deviceScaleFactor: 2 // High DPI for crystal clear PDF printing
  });
  await page.setContent(htmlContent, { waitUntil: 'networkidle' });
  await page.waitForTimeout(500); // ensure fonts/canvas render
  await page.screenshot({ path: outputPngPath, fullPage: false });
  await browser.close();
  console.log(`Rendered PNG Diagram: ${outputPngPath}`);
}

console.log("Excalidraw Builder Module loaded successfully.");
module.exports = {
  createExcalidrawBox,
  createExcalidrawArrow,
  saveExcalidrawFile,
  renderHtmlToPng,
  ASSETS_DIR,
  DIAGRAMS_DIR
};

