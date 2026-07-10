const path = require("path");
const { chromium } = require("../okx-code-referral-bonusok-persian/node_modules/playwright");

const fileUrl = "file:///" + path.resolve(__dirname, "index.html").replace(/\\/g, "/");

async function check(viewport) {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport });
  await page.goto(fileUrl, { waitUntil: "networkidle" });
  const result = await page.evaluate(() => {
    const bodyText = document.body.innerText;
    const wordLikeCount = (bodyText.match(/[A-Za-zÄÖÜäöüß0-9][A-Za-zÄÖÜäöüß0-9-]+/g) || []).length;
    const images = [...document.images].map((img) => ({
      src: img.getAttribute("src"),
      complete: img.complete,
      naturalWidth: img.naturalWidth,
      naturalHeight: img.naturalHeight,
      alt: img.alt,
    }));
    return {
      title: document.title,
      lang: document.documentElement.lang,
      robots: document.querySelector('meta[name="robots"]')?.content || "",
      canonical: document.querySelector('link[rel="canonical"]')?.href || "",
      h1: document.querySelector("h1")?.innerText || "",
      h2Count: document.querySelectorAll("h2").length,
      h3Count: document.querySelectorAll("h3").length,
      wordLikeCount,
      overflowX: Math.max(0, document.documentElement.scrollWidth - window.innerWidth),
      images,
      checks: {
        hasReferral: bodyText.includes("BONUSOK"),
        hasDisclosure: /Provision|Referral-Hinweis|Empfehlung/.test(bodyText),
        hasRisk: /Risiko|Verlust|keine Anlageberatung/.test(bodyText),
        hasGermany: /Deutschland|MiCA|EEA/.test(bodyText),
        hasAgentTradeKit: bodyText.includes("Agent Trade Kit"),
        hasXPerps: bodyText.includes("X-Perps"),
        hasCoolOff: bodyText.includes("Cool-off"),
        hasCampaignCenter: bodyText.includes("Campaign Center"),
      },
    };
  });
  await browser.close();
  return result;
}

(async () => {
  const desktop = await check({ width: 1365, height: 950 });
  const mobile = await check({ width: 390, height: 900 });
  console.log(JSON.stringify({ target: fileUrl, desktop, mobile }, null, 2));
})();
