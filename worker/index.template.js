const ASSETS = __PUBLIC_ASSETS__;
const HEALTH = __PUBLIC_HEALTH__;

function decodeBase64(value) {
  const binary = atob(value);
  const bytes = new Uint8Array(binary.length);
  for (let index = 0; index < binary.length; index += 1) {
    bytes[index] = binary.charCodeAt(index);
  }
  return bytes;
}

function securityHeaders(contentType, cacheControl) {
  return {
    "content-type": contentType,
    "cache-control": cacheControl,
    "x-content-type-options": "nosniff",
    "referrer-policy": "strict-origin-when-cross-origin",
    "x-frame-options": "DENY",
    "permissions-policy": "camera=(), microphone=(), geolocation=()",
    "content-security-policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'none'"
  };
}

function response(body, status, contentType, cacheControl, extraHeaders = {}) {
  return new Response(body, {
    status,
    headers: { ...securityHeaders(contentType, cacheControl), ...extraHeaders }
  });
}

export default {
  async fetch(request) {
    if (request.method !== "GET" && request.method !== "HEAD") {
      return response("Method Not Allowed", 405, "text/plain; charset=utf-8", "no-store", { allow: "GET, HEAD" });
    }

    const url = new URL(request.url);
    let pathname;
    try {
      pathname = decodeURIComponent(url.pathname);
    } catch (_) {
      return response("Bad Request", 400, "text/plain; charset=utf-8", "no-store");
    }

    if (pathname === "/api/health") {
      const body = request.method === "HEAD" ? null : JSON.stringify(HEALTH);
      return response(body, 200, "application/json; charset=utf-8", "public, max-age=60");
    }

    if (pathname === "/" || pathname.endsWith("/")) {
      pathname = "/index.html";
    }
    const asset = ASSETS[pathname];
    if (!asset) {
      const notFound = ASSETS["/404.html"];
      return response(request.method === "HEAD" ? null : decodeBase64(notFound.body), 404, notFound.contentType, "no-store");
    }

    const cacheControl = pathname === "/index.html"
      ? "public, max-age=120"
      : pathname === "/data/index.json"
        ? "public, max-age=300"
        : "public, max-age=86400";
    const headers = {};
    if (asset.download) {
      const filename = pathname.split("/").pop();
      headers["content-disposition"] = `attachment; filename*=UTF-8''${encodeURIComponent(filename)}`;
    }
    return response(request.method === "HEAD" ? null : decodeBase64(asset.body), 200, asset.contentType, cacheControl, headers);
  }
};
