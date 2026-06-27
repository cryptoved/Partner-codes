const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright-core");

const chromePath = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const target = process.argv[2] || `file://${path.join(__dirname, "index.html").replace(/\\/g, "/")}`;
const outDir = process.argv[3] || path.join(__dirname, "..", "..", "..", "exchanges", "Pionex", "outputs", "qa", "vercel-mandarin-pionex", target.startsWith("http") ? "public" : "local");
fs.mkdirSync(outDir, { recursive: true });

async function runOne(browser, name, viewport) {
  const page = await browser.newPage({ viewport, deviceScaleFactor: 1 });
  await page.goto(target, { waitUntil: "load", timeout: 45000 });
  await page.waitForTimeout(1200);
  const report = await page.evaluate(() => {
    const visibleText = document.body.innerText || "";
    const latinTokens = (visibleText.match(/[A-Za-zÀ-ž0-9$%]+/g) || []).length;
    const cjkChars = (visibleText.match(/[\u4e00-\u9fff]/g) || []).length;
    const wordLike = latinTokens + cjkChars;
    const allImages = [...document.images].map((img) => ({
      src: img.currentSrc || img.src,
      alt: img.alt,
      complete: img.complete,
      naturalWidth: img.naturalWidth,
      naturalHeight: img.naturalHeight,
      rect: (() => {
        const r = img.getBoundingClientRect();
        return { width: Math.round(r.width), height: Math.round(r.height) };
      })()
    }));
    const sponsoredCtas = [...document.querySelectorAll("a[rel*='sponsored']")].map((a) => a.href);
    return {
      title: document.title,
      lang: document.documentElement.lang,
      canonical: document.querySelector("link[rel='canonical']")?.href || null,
      robots: document.querySelector("meta[name='robots']")?.content || null,
      wordLike,
      overflowX: document.documentElement.scrollWidth - window.innerWidth,
      bodyOverflowX: document.body.scrollWidth - window.innerWidth,
      images: allImages,
      sponsoredCtas,
      hasBonusok: visibleText.includes("BONUSOK"),
      hasDisclosure: /联盟|推荐|佣金|披露/i.test(visibleText),
      hasRisk: /风险|波动|爆仓|亏损/i.test(visibleText),
      hasRegionWarning: /中国大陆|受限地区|KYC|VPN/i.test(visibleText),
      h1: document.querySelector("h1")?.innerText || null
    };
  });
  await page.screenshot({ path: path.join(outDir, `${name}.png`), fullPage: true, type: "png" });
  await page.close();
  return { name, viewport, report };
}

(async () => {
  const browser = await chromium.launch({ executablePath: chromePath, headless: true });
  const results = [];
  results.push(await runOne(browser, "desktop", { width: 1366, height: 900 }));
  results.push(await runOne(browser, "mobile", { width: 390, height: 844, isMobile: true }));
  await browser.close();
  const output = path.join(outDir, "qa-report.json");
  fs.writeFileSync(output, JSON.stringify({ target, results }, null, 2), "utf8");
  console.log(JSON.stringify({ target, output, results }, null, 2));
})().catch((error) => {
  console.error(error);
  process.exit(1);
});
