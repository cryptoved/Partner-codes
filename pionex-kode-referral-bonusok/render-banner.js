const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const chromePath = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const root = __dirname;
const output = path.join(root, "assets", "pionex-bonusok-indonesia-kode-referral-banner.png");
const workspace = path.join(process.cwd(), "..", "..", "..");
const workOutput = path.join(workspace, "exchanges", "Pionex", "outputs", "pionex-bonusok-indonesia-kode-referral-banner.png");
const qaOutput = path.join(workspace, "exchanges", "Pionex", "work", "pionex-indonesia-vercel", "banner-layout-qa.json");

(async () => {
  const browser = await chromium.launch({ executablePath: chromePath, headless: true });
  const page = await browser.newPage({ viewport: { width: 1600, height: 900 }, deviceScaleFactor: 1 });
  await page.goto(`file://${path.join(root, "banner.html").replace(/\\/g, "/")}`, { waitUntil: "networkidle" });

  const metrics = await page.evaluate(() => {
    const box = (selector) => {
      const r = document.querySelector(selector).getBoundingClientRect();
      return { x: Math.round(r.x), y: Math.round(r.y), width: Math.round(r.width), height: Math.round(r.height), right: Math.round(r.right), bottom: Math.round(r.bottom) };
    };
    const textBox = (selector) => {
      const el = document.querySelector(selector);
      const r = el.getBoundingClientRect();
      const range = document.createRange();
      range.selectNodeContents(el);
      const tr = range.getBoundingClientRect();
      return { selector, containerWidth: Math.round(r.width), textWidth: Math.round(tr.width), overflow: tr.width > r.width + 1 };
    };
    return {
      canvas: { width: 1600, height: 900 },
      titlePanel: box(".title-panel"),
      codePanel: box(".code-panel"),
      qrCard: box(".qr-card"),
      qrBox: box(".qr-box"),
      text: [
        textBox(".eyebrow"),
        textBox(".headline"),
        textBox(".subhead"),
        textBox(".code-label"),
        textBox(".code-value"),
        textBox(".qr-title"),
        textBox(".qr-subtitle")
      ],
      overflowX: document.documentElement.scrollWidth - window.innerWidth,
      overflowY: document.documentElement.scrollHeight - window.innerHeight
    };
  });

  await page.screenshot({ path: output, type: "png" });
  fs.copyFileSync(output, workOutput);
  fs.writeFileSync(qaOutput, JSON.stringify(metrics, null, 2), "utf8");
  await browser.close();
  console.log(JSON.stringify({ output, workOutput, qaOutput, metrics }, null, 2));
})().catch((error) => {
  console.error(error);
  process.exit(1);
});
