/** Browser QA and reproducible evidence. Run with the local server on port 4173. */
import { chromium } from "playwright";
import { writeFile } from "node:fs/promises";
import assert from "node:assert/strict";

const origin = process.env.SITE_ORIGIN || "http://127.0.0.1:4173";
const url = `${origin}/pluto-site/`;
const browser = await chromium.launch({ channel: "chrome", headless: true });
const context = await browser.newContext({
  viewport: { width: 1440, height: 1000 },
  reducedMotion: "reduce",
  permissions: ["clipboard-read", "clipboard-write"],
});
const page = await context.newPage();
const errors = [];
page.on("pageerror", (error) => errors.push(error.message));
page.on("console", (message) => {
  if (message.type() === "error") errors.push(message.text());
});
page.on("response", (response) => {
  if (response.status() >= 400)
    errors.push(`${response.status()} ${response.url()}`);
});

async function layout(width, height) {
  await page.setViewportSize({ width, height });
  await page.evaluate(() => window.scrollTo(0, 0));
  return page.evaluate(async () => {
    await document.fonts.ready;
    await new Promise((resolve) => {
      requestAnimationFrame(() => requestAnimationFrame(resolve));
    });
    return {
      width: innerWidth,
      scroll: document.documentElement.scrollWidth,
      fonts: [...document.fonts].map((font) => ({
        family: font.family,
        status: font.status,
      })),
    };
  });
}

try {
  await page.goto(url, { waitUntil: "networkidle" });
  const desktop = await layout(1440, 1000);
  assert.equal(desktop.scroll, desktop.width, "Desktop overflow");
  assert.ok(desktop.fonts.every((font) => font.status === "loaded"));
  await page.screenshot({ path: "evidence/desktop.png" });
  await page.screenshot({ path: "evidence/desktop-full.png", fullPage: true });

  await page.getByRole("tab", { name: "02 Contract" }).click();
  await page.getByRole("tabpanel").filter({ visible: true }).waitFor();
  assert.equal(await page.locator("#panel-contract").isVisible(), true);
  await page.keyboard.press("ArrowRight");
  assert.equal(
    await page.locator("#tab-operation").getAttribute("aria-selected"),
    "true",
  );
  await page.keyboard.press("Home");
  assert.equal(
    await page.locator("#tab-scaffold").getAttribute("aria-selected"),
    "true",
  );
  await page.locator("#tab-scaffold").evaluate((element) => element.blur());
  await page
    .locator(".practice")
    .screenshot({ path: "evidence/code-demo.png" });

  await page.getByRole("button", { name: "Copy CLI install command" }).click();
  await page
    .getByRole("status")
    .filter({ hasText: "Install command copied" })
    .waitFor();
  assert.equal(
    await page.evaluate(() => navigator.clipboard.readText()),
    "go install github.com/plutoframework/cli/cmd/pluto@latest",
  );
  await page.evaluate(() => {
    Object.defineProperty(navigator, "clipboard", {
      configurable: true,
      value: {
        writeText: async () => {
          throw new Error("QA denied");
        },
      },
    });
  });
  await page.getByRole("button", { name: "Copy CLI install command" }).click();
  await page
    .getByRole("status")
    .filter({ hasText: "copy it manually" })
    .waitFor();
  assert.ok(
    (await page.evaluate(() => getSelection().toString())).startsWith(
      "go install",
    ),
  );
  await page.reload({ waitUntil: "networkidle" });

  for (const [width, height] of [
    [320, 750],
    [390, 844],
    [768, 1024],
    [1024, 900],
  ]) {
    const result = await layout(width, height);
    assert.equal(result.scroll, result.width, `Overflow at ${width}px`);
  }
  await layout(390, 844);
  await page.getByRole("button", { name: "Menu" }).click();
  assert.equal(
    await page.locator(".menu-toggle").getAttribute("aria-expanded"),
    "true",
  );
  await page.keyboard.press("Escape");
  assert.equal(
    await page.locator(".menu-toggle").getAttribute("aria-expanded"),
    "false",
  );
  await page.getByRole("button", { name: "Menu" }).click();
  await page
    .locator("#site-nav")
    .getByRole("link", { name: "Start building" })
    .click();
  assert.equal(new URL(page.url()).hash, "#quickstart");
  assert.equal(
    await page.locator(".menu-toggle").getAttribute("aria-expanded"),
    "false",
  );
  await page.getByText("What does Pluto generate?", { exact: false }).click();
  assert.equal(await page.locator("details").first().getAttribute("open"), "");
  await page.getByText("What does Pluto generate?", { exact: false }).click();
  await page.goto(url, { waitUntil: "networkidle" });
  await layout(390, 844);
  await page.screenshot({ path: "evidence/mobile.png" });
  await page.screenshot({ path: "evidence/mobile-full.png", fullPage: true });
  await page.locator("#tab-scaffold").evaluate((element) => element.blur());
  await page
    .locator(".practice")
    .screenshot({ path: "evidence/mobile-code.png" });
  await page
    .locator(".quickstart")
    .screenshot({ path: "evidence/mobile-guide.png" });
  await page.goto(url, { waitUntil: "networkidle" });

  await page.keyboard.press("Tab");
  assert.equal(
    await page.evaluate(() => document.activeElement.textContent.trim()),
    "Skip to content",
  );
  const focusOutline = await page
    .locator(".skip-link")
    .evaluate((element) => getComputedStyle(element).outlineStyle);
  assert.equal(focusOutline, "solid");
  await page.keyboard.press("Enter");
  assert.equal(new URL(page.url()).hash, "#main");
  const motion = await page.locator(".hero-copy").evaluate((element) => ({
    reduced: matchMedia("(prefers-reduced-motion: reduce)").matches,
    duration: getComputedStyle(element).animationDuration,
    focus: document.activeElement.tagName,
  }));
  assert.equal(motion.reduced, true);
  assert.equal(motion.duration, "1e-05s");
  assert.equal(errors.length, 0, errors.join("\n"));

  const svg = await page.locator(".orbital").evaluate((node) => node.outerHTML);
  const social = await context.newPage();
  await social.setViewportSize({ width: 1200, height: 630 });
  await social.setContent(
    `<!doctype html><html><head>
    <link rel="stylesheet" href="${url}styles.css">
    <style>
      body { width:1200px; height:630px; position:relative; overflow:hidden; }
      .social { padding:58px 66px; }
      .brand { font-size:48px; }
      h1 { font-size:83px; margin-top:65px; position:relative; z-index:1; }
      .tag { font:12px var(--mono); margin-top:30px; }
      .orbital { position:absolute; width:600px; right:-42px; top:30px; }
      .bottom { position:absolute; bottom:35px; left:66px; right:66px;
        border-top:1px solid var(--line); padding-top:16px;
        font:10px var(--mono); letter-spacing:.07em; }
    </style></head><body><div class="social">
    <div class="brand">pluto<span class="brand-period">.</span></div>
    <h1>Small framework.<br>Wide open<br><em>possibilities.</em></h1>
    <p class="tag">THE GO API FRAMEWORK + CLI</p>${svg}
    <div class="bottom">SMALL BY DESIGN. OPEN BY NATURE.</div>
    </div></body></html>`,
    { waitUntil: "networkidle" },
  );
  await social.evaluate(() => document.fonts.ready);
  await social.screenshot({ path: "assets/social.png" });
  const report = {
    url,
    desktop,
    widths: [320, 390, 768, 1024, 1440],
    errors,
    interactions: [
      "code tabs",
      "arrow keys and Home",
      "copy success",
      "copy failure/manual selection",
      "mobile menu",
      "Escape focus return",
      "quickstart anchor",
      "guide disclosure",
      "skip link",
    ],
    motion,
    focusOutline,
  };
  await writeFile(
    "evidence/browser-check.json",
    `${JSON.stringify(report, null, 2)}\n`,
  );
  console.log(JSON.stringify(report, null, 2));
} finally {
  await browser.close();
}
