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
  ["/data/index.json", "data/index.json", "application/json; charset=utf-8"],
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
const health = {
  ok: true,
  generated_at: indexData.meta.generated_at,
  readiness_score: indexData.readiness.score,
  signals: indexData.signals.length,
  source_health: indexData.automation.source_health
};

const template = await readFile(templatePath, "utf8");
const worker = template
  .replace("__PUBLIC_ASSETS__", JSON.stringify(assets).replaceAll("<", "\\u003c"))
  .replace("__PUBLIC_HEALTH__", JSON.stringify(health).replaceAll("<", "\\u003c"));

if (worker.includes("__PUBLIC_ASSETS__") || worker.includes("__PUBLIC_HEALTH__")) {
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
  generated_at: health.generated_at
}));
