/**
 * 9router → LiteLLM Bridge Proxy
 *
 * PURPOSE:
 *   LiteLLM (embedded in OpenHands, Agent Canvas, etc.) requires a known
 *   provider prefix on the model name (e.g. `openai/...`). When sent directly
 *   to 9router, the prefix is NOT stripped — 9router sees `openai/oc/...`
 *   and fails with "No active credentials for provider: openai".
 *
 *   This proxy intercepts requests from LiteLLM, strips the `openai/` prefix
 *   from the model field, then forwards the clean request to 9router.
 *
 * USAGE:
 *   1. Start: node 9router-litellm-proxy.js
 *   2. In Agent Canvas / OpenHands, set:
 *        Base URL:    http://localhost:20129/v1
 *        Custom Model: openai/oc/deepseek-v4-flash-free
 *        API Key:     your-9router-key
 *   3. Proxy strips `openai/` → sends `oc/deepseek-v4-flash-free` → 9router
 *
 * PORTS:
 *   Proxy binds :20129 → 9router at :20128
 *
 * KNOWN ISSUES HANDLED:
 *   - Strips `openai/` prefix from model name
 *   - Strips trailing SSE marker `data: [DONE]\n\n` that 9router appends
 *     even to non-streaming responses (breaks JSON parsers)
 *   - Recalculates Content-Length after modifications
 *
 * LICENSE: MIT (part of Hermes custom-provider-setup skill)
 */

const http = require('http');
const UPSTREAM = { host: '127.0.0.1', port: 20128 };
const LISTEN_PORT = 20129;

const server = http.createServer((req, res) => {
  const chunks = [];
  req.on('data', c => chunks.push(c));
  req.on('end', () => {
    const body = Buffer.concat(chunks).toString('utf-8');
    let modified = body;

    try {
      const json = JSON.parse(body);
      if (json.model && json.model.startsWith('openai/')) {
        json.model = json.model.slice('openai/'.length);
        modified = JSON.stringify(json);
        console.log(`[proxy] Rewrote model: ${json.model}`);
      }
    } catch (_) { /* pass through raw */ }

    const options = {
      hostname: UPSTREAM.host,
      port: UPSTREAM.port,
      path: req.url,
      method: req.method,
      headers: { ...req.headers, 'content-length': Buffer.byteLength(modified) },
    };

    const proxyReq = http.request(options, (proxyRes) => {
      const respChunks = [];
      proxyRes.on('data', c => respChunks.push(c));
      proxyRes.on('end', () => {
        let responseBody = Buffer.concat(respChunks).toString('utf-8');
        // 9router appends SSE terminator even to non-streaming responses
        responseBody = responseBody.replace(/data:\s*\[DONE\]\s*\n*\s*$/, '');
        const headers = { ...proxyRes.headers };
        headers['content-length'] = Buffer.byteLength(responseBody);
        res.writeHead(proxyRes.statusCode, headers);
        res.end(responseBody);
      });
    });

    proxyReq.on('error', (err) => {
      console.error(`[proxy] Error: ${err.message}`);
      res.writeHead(502, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: { message: `Proxy error: ${err.message}` } }));
    });

    proxyReq.end(modified);
  });
});

server.listen(LISTEN_PORT, '127.0.0.1', () => {
  console.log(`[9router-proxy] Listening on :${LISTEN_PORT} -> 9router :${UPSTREAM.port}`);
  console.log(`[9router-proxy] Set Base URL to http://localhost:${LISTEN_PORT}/v1`);
});
