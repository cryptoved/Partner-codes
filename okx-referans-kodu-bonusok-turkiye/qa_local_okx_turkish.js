const { chromium } = require("../okx-code-referral-bonusok-persian/node_modules/playwright");
const path = require("path");

const fileUrl = "file:///" + path.resolve(__dirname, "index.html").replace(/\\/g, "/");

async function checkViewport(page, width, height) {
  await page.setViewportSize({ width, height });
  await page.goto(fileUrl, { waitUntil: "networkidle" });
  const result = await page.evaluate(() => {
    const body = document.body;
    const doc = document.documentElement;
    const images = [...document.images].map((img) => ({
      src: img.getAttribute("src"),
      naturalWidth: img.naturalWidth,
      naturalHeight: img.naturalHeight,
      visible: getComputedStyle(img).display !== "none",
      alt: img.getAttribute("alt") || "",
    }));
    return {
      title: document.title,
      lang: document.documentElement.lang,
      robots: document.querySelector('meta[name="robots"]')?.content || "",
      canonical: document.querySelector('link[rel="canonical"]')?.href || "",
      h1: document.querySelector("h1")?.textContent.trim() || "",
      h2Count: document.querySelectorAll("h2").length,
      h3Count: document.querySelectorAll("h3").length,
      wordCount: (body.innerText.match(/[A-Za-zÇĞİÖŞÜçğıöşü0-9][A-Za-zÇĞİÖŞÜçğıöşü0-9-]+/g) || []).length,
      scrollWidth: doc.scrollWidth,
      clientWidth: doc.clientWidth,
      overflowX: Math.max(0, doc.scrollWidth - doc.clientWidth),
      images,
      checks: {
        bonusok: body.innerText.includes("BONUSOK"),
        disclosure: body.innerText.includes("komisyon alabiliriz"),
        risk: body.innerText.includes("yatırım tavsiyesi değildir"),
        turkey: body.innerText.includes("Türkiye"),
        okxTr: body.innerText.includes("OKX TR"),
        campaignCenter: body.innerText.includes("Campaign Center"),
        agentTradeKit: body.innerText.includes("Agent Trade Kit"),
        xPerps: body.innerText.includes("X-Perps"),
        coolOff: body.innerText.includes("Futures Cool-off"),
        tryText: body.innerText.includes("TRY"),
        noBypass: body.innerText.includes("VPN") && body.innerText.includes("sahte KYC"),
      },
    };
  });
  return { viewport: { width, height }, ...result };
}

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  const desktop = await checkViewport(page, 1365, 900);
  const mobile = await checkViewport(page, 390, 844);
  await browser.close();

  const failures = [];
  for (const item of [desktop, mobile]) {
    if (item.lang !== "tr-TR") failures.push(`bad lang ${item.lang}`);
    if (!item.robots.includes("index") || item.robots.includes("noindex")) failures.push("bad robots");
    if (!item.canonical.includes("/okx-referans-kodu-bonusok-turkiye/")) failures.push("bad canonical");
    if (item.h2Count < 2) failures.push("too few h2");
    if (item.h3Count < 2) failures.push("too few h3");
    if (item.wordCount < 2000) failures.push(`word count low ${item.wordCount}`);
    if (item.overflowX > 1) failures.push(`overflow ${item.viewport.width}: ${item.overflowX}`);
    if (!Object.values(item.checks).every(Boolean)) failures.push(`missing check ${JSON.stringify(item.checks)}`);
    if (item.images.filter((img) => img.visible).some((img) => img.naturalWidth < 1 || img.naturalHeight < 1)) failures.push("visible image failed");
  }

  console.log(JSON.stringify({ desktop, mobile, failures }, null, 2));
  if (failures.length) process.exit(1);
})();
