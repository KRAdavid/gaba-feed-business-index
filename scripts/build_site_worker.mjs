import { mkdir, readFile, rm, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(fileURLToPath(new URL("..", import.meta.url)));
const docs = resolve(root, "docs");
const dist = resolve(root, "dist");
const templatePath = resolve(root, "worker", "index.template.js");
const hostingPath = resolve(root, ".openai", "hosting.json");

const publicFiles = [
  ["/index.html", "index.html", "text/html; charset=utf-8"],
  ["/404.html", "404.html", "text/html; charset=utf-8"],
  ["/assets/styles.css", "assets/styles.css", "text/css; charset=utf-8"],
  ["/assets/app.js", "assets/app.js", "text/javascript; charset=utf-8"],
  ["/assets/inquiry-form.css", "assets/inquiry-form.css", "text/css; charset=utf-8"],
  ["/assets/inquiry-form.js", "assets/inquiry-form.js", "text/javascript; charset=utf-8"],
  ["/assets/inquiry-apps-script.js", "assets/inquiry-apps-script.js", "text/javascript; charset=utf-8"],
  ["/assets/calculator-scenarios.css", "assets/calculator-scenarios.css", "text/css; charset=utf-8"],
  ["/assets/calculator-scenarios.js", "assets/calculator-scenarios.js", "text/javascript; charset=utf-8"],
  ["/assets/order-guide.css", "assets/order-guide.css", "text/css; charset=utf-8"],
  ["/assets/order-guide.js", "assets/order-guide.js", "text/javascript; charset=utf-8"],
  ["/assets/visitor-decision-cards.css", "assets/visitor-decision-cards.css", "text/css; charset=utf-8"],
  ["/assets/visitor-decision-cards.js", "assets/visitor-decision-cards.js", "text/javascript; charset=utf-8"],
  ["/assets/cta-emphasis.css", "assets/cta-emphasis.css", "text/css; charset=utf-8"],
  ["/assets/cta-emphasis.js", "assets/cta-emphasis.js", "text/javascript; charset=utf-8"],
  ["/assets/hero-banner-rotator.css", "assets/hero-banner-rotator.css", "text/css; charset=utf-8"],
  ["/assets/hero-title-focus.css", "assets/hero-title-focus.css", "text/css; charset=utf-8"],
  ["/assets/hero-banner-rotator.js", "assets/hero-banner-rotator.js", "text/javascript; charset=utf-8"],
  ["/assets/product-split-selector.css", "assets/product-split-selector.css", "text/css; charset=utf-8"],
  ["/assets/product-split-selector.js", "assets/product-split-selector.js", "text/javascript; charset=utf-8"],
  ["/assets/lab-section.css", "assets/lab-section.css", "text/css; charset=utf-8"],
  ["/assets/lab-section.js", "assets/lab-section.js", "text/javascript; charset=utf-8"],
  ["/assets/material-page.css", "assets/material-page.css", "text/css; charset=utf-8"],
  ["/assets/technical-documents.css", "assets/technical-documents.css", "text/css; charset=utf-8"],
  ["/assets/technical-documents.js", "assets/technical-documents.js", "text/javascript; charset=utf-8"],
  ["/assets/b2b-operations.css", "assets/b2b-operations.css", "text/css; charset=utf-8"],
  ["/assets/b2b-operations.js", "assets/b2b-operations.js", "text/javascript; charset=utf-8"],
  ["/data/index.json", "data/index.json", "application/json; charset=utf-8"],
  ["/data/auto_intelligence.json", "data/auto_intelligence.json", "application/json; charset=utf-8"],
  ["/data/knowledge_base.json", "data/knowledge_base.json", "application/json; charset=utf-8"],
  ["/data/update_status.json", "data/update_status.json", "application/json; charset=utf-8"],
  ["/data/technical_documents.json", "data/technical_documents.json", "application/json; charset=utf-8"],
  ["/data/b2b_operations.json", "data/b2b_operations.json", "application/json; charset=utf-8"],
  ["/data/platform_health.json", "data/platform_health.json", "application/json; charset=utf-8"],
  ["/materials/gaba-crude-specification.html", "materials/gaba-crude-specification.html", "text/html; charset=utf-8"],
  ["/materials/breeder-pig-gaba-proposal.html", "materials/breeder-pig-gaba-proposal.html", "text/html; charset=utf-8"],
  ["/materials/australia-wagyu-gaba-assessment.html", "materials/australia-wagyu-gaba-assessment.html", "text/html; charset=utf-8"],
  ["/materials/gaba-feed-introduction.html", "materials/gaba-feed-introduction.html", "text/html; charset=utf-8"],
  ["/materials/cellpinda-life-science-lab.html", "materials/cellpinda-life-science-lab.html", "text/html; charset=utf-8"],
  ["/downloads/GABA_Feed_Business_Model_Speech_Deck_v1.pdf", "downloads/GABA_Feed_Business_Model_Speech_Deck_v1.pdf", "application/pdf"],
  ["/downloads/GABA_Crude_Specification_v1.pdf", "downloads/GABA_Crude_Specification_v1.pdf", "application/pdf"],
  ["/downloads/GABA_Caremix_Specification_v1.pdf", "downloads/GABA_Caremix_Specification_v1.pdf", "application/pdf"]
];

const assets = {};
for (const [publicPath, relativePath, contentType] of publicFiles) {
  const body = await readFile(resolve(docs, relativePath));
  assets[publicPath] = {
    body: body.toString("base64"),
    contentType,
    download: publicPath.startsWith("/downloads/")
  };
}

const indexData = JSON.parse(await readFile(resolve(docs, "data", "index.json"), "utf8"));
const platformHealth = JSON.parse(await readFile(resolve(docs, "data", "platform_health.json"), "utf8"));
const health = {
  ok: platformHealth.status !== "degraded",
  generated_at: indexData.meta.generated_at,
  readiness_score: indexData.readiness.score,
  signals: indexData.signals.length,
  source_health: indexData.automation.source_health,
  b2b_platform_status: platformHealth.status,
  b2b_platform_checks: platformHealth.summary
};
const buildId = `${indexData.meta.generated_at}-${Buffer.byteLength(JSON.stringify(assets))}`;

const template = await readFile(templatePath, "utf8");
const worker = template
  .replace("__PUBLIC_ASSETS__", JSON.stringify(assets).replaceAll("<", "\\u003c"))
  .replace("__PUBLIC_HEALTH__", JSON.stringify(health).replaceAll("<", "\\u003c"))
  .replace("__PUBLIC_BUILD_ID__", JSON.stringify(buildId));

if (worker.includes("__PUBLIC_ASSETS__") || worker.includes("__PUBLIC_HEALTH__") || worker.includes("__PUBLIC_BUILD_ID__")) {
  throw new Error("Worker template placeholders were not replaced");
}

await rm(dist, { recursive: true, force: true });
await mkdir(resolve(dist, "server"), { recursive: true });
await mkdir(resolve(dist, ".openai"), { recursive: true });
await writeFile(resolve(dist, "server", "index.js"), worker, "utf8");
await writeFile(resolve(dist, ".openai", "hosting.json"), await readFile(hostingPath));

console.log(JSON.stringify({
  output: resolve(dist, "server", "index.js"),
  assets: Object.keys(assets).length,
  bytes: Buffer.byteLength(worker),
  generated_at: health.generated_at,
  b2b_platform_status: health.b2b_platform_status
}));
