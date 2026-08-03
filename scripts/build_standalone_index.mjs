import { readFile, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(fileURLToPath(new URL("..", import.meta.url)));
const docs = resolve(root, "docs");
const [html, css, app, data] = await Promise.all([
  readFile(resolve(docs, "index.html"), "utf8"),
  readFile(resolve(docs, "assets", "styles.css"), "utf8"),
  readFile(resolve(docs, "assets", "app.js"), "utf8"),
  readFile(resolve(docs, "data", "index.json"), "utf8")
]);

const withInlineCss = html.replace('<link rel="stylesheet" href="assets/styles.css">', `<style>\n${css}\n</style>`);
const inlineData = data.replaceAll("</script", "<\\/script");
const standalone = withInlineCss.replace(
  '<script src="assets/app.js" defer></script>',
  `<script>window.__GABA_INDEX_DATA__=${inlineData};</script><script>${app}</script>`
);

if (standalone.includes('href="assets/styles.css"') || standalone.includes('src="assets/app.js"')) {
  throw new Error("Standalone index still depends on local assets");
}

const output = resolve(docs, "standalone.html");
await writeFile(output, standalone, "utf8");
console.log(JSON.stringify({ output, bytes: Buffer.byteLength(standalone) }));
