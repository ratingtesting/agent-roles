/**
 * LiteLLM ↔ custom-router bridge proxy.
 *
 * Problem: LiteLLM (in OpenHands / Agent Canvas / litellm SDK) requires a known
 * provider prefix (openai/, anthropic/, ...) or it throws
 *   litellm.BadRequestError: LLM Provider NOT provided
 * But a custom router (9router, freellmapi, local vLLM) routes by its OWN
 * namespace (oc/, opencode/, ...) and does NOT understand openai/.
 *
 * Fix: client sends model = "openai/<ns>/<model>" so LiteLLM is happy; this
 * proxy strips the leading "openai/" and forwards "<ns>/<model>" to the router.
 *
 * Streaming (SSE) is piped through unchanged (chunked) so live token streams work.
 *
 *   Client -> http://localhost:20129/v1 (this proxy) -> router :UPSTREAM_PORT
 *
 * Run:  node 9router-bridge-proxy.js
 */
const http = require('http');

const UPSTREAM = { host: '127.0.0.1', port: 20128 }; // the custom router
const LISTEN_PORT = 20129;                            // what the client points Base URL at
const STRIP_PREFIX = 'openai/';

process.on('uncaughtException', (e) => console.error('[bridge][uncaught]', e.message));
process.on('unhandledRejection', (e) => console.error('[bridge][unhandled]', e));

const server = http.createServer((req, res) => {
  const chunks = [];
  req.on('data', (c) => chunks.push(c));
  req.on('end', () => {
    let body = Buffer.concat(chunks).toString('utf-8');
    let modified = body;

    try {
      const json = JSON.parse(body);
      if (typeof json.model === 'string' && json.model.startsWith(STRIP_PREFIX)) {
        json.model = json.model.slice(STRIP_PREFIX.length);
        modified = JSON.stringify(json);
        console.log(`[bridge] rewrote model -> ${json.model}`);
      }
    } catch (_) { /* non-JSON body: pass through */ }

    const options = {
      hostname: UPSTREAM.host,
      port: UPSTREAM.port,
      path: req.url,
      method: req.method,
      headers: {
        ...req.headers,
        host: `${UPSTREAM.host}:${UPSTREAM.port}`,
        'content-length': Buffer.byteLength(modified),
      },
    };

    const proxyReq = http.request(options, (proxyRes) => {
      const headers = { ...proxyRes.headers };
      delete headers['content-length']; // let client use chunked transfer (SSE safe)
      res.writeHead(proxyRes.statusCode, headers);
      proxyRes.pipe(res);
    });

    proxyReq.on('error', (err) => {
      console.error(`[bridge] upstream error: ${err.message}`);
      if (!res.headersSent) {
        res.writeHead(502, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: { message: `router unreachable: ${err.message}` } }));
      } else {
        res.destroy();
      }
    });

    proxyReq.end(modified);
  });
});

server.listen(LISTEN_PORT, '127.0.0.1', () => {
  console.log(`[bridge] listening on :${LISTEN_PORT} -> router :${UPSTREAM.port}`);
  console.log(`[bridge] client Base URL: http://localhost:${LISTEN_PORT}/v1`);
  console.log(`[bridge] client model:    openai/<namespace>/<model>  (e.g. openai/oc/deepseek-v4-flash-free)`);
});
