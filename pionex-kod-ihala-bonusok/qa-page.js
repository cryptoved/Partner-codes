const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const chromePath = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const target = process.argv[2] || `file://${path.join(__dirname, "index.html").replace(/\\/g, "/")}`;
const outDir = process.argv[3] || path.join(__dirname, "..", "..", "..", "exchanges", "Pionex", "outputs", "qa", "vercel-arabic-pionex", target.startsWith("http") ? "public" : "local");
fs.mkdirSync(outDir, { recursive: true });

async function runOne(browser, name, viewport) {
  const page = await browser.newPage({ viewport, deviceScaleFactor: 1 });
  await page.goto(target, { waitUntil: "networkidle" });
  const report = await page.evaluate(() => {
    const visibleText = document.body.innerText || "";
    const wordLike = (visibleText.match(/[\p{L}\p{N}$%]+/gu) || []).length;
    const images = [...document.images].map((img) => ({
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
    return {
      title: document.title,
      lang: document.documentElement.lang,
      dir: document.documentElement.dir,
      canonical: document.querySelector("link[rel='canonical']")?.href || null,
      robots: document.querySelector("meta[name='robots']")?.content || null,
      wordLike,
      overflowX: document.documentElement.scrollWidth - window.innerWidth,
      bodyOverflowX: document.body.scrollWidth - window.innerWidth,
      images,
      sponsoredCtas: [...document.querySelectorAll("a[rel*='sponsored']")].map((a) => a.href),
      hasBonusok: visibleText.includes("BONUSOK"),
      hasDisclosure: /إفصاح|عمولة|إحالة/.test(visibleText),
      hasRisk: /مخاطر|متقلب|رافعة|خسارة/.test(visibleText),
      hasYemenWarning: /اليمن|Yemen/.test(visibleText),
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
