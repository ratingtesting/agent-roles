/**
 * Local prefix-strip proxy for LiteLLM tools (OpenHands / Agent Canvas) talking to a
 * custom OpenAI-compatible gateway (e.g. 9router) that uses its OWN model namespace (oc/, etc.).
 *
 * Problem: LiteLLM requires a known provider prefix (openai/) or throws
 *   "litellm.BadRequestError: LLM Provider NOT provided".
 * But the gateway does not know an openai/ prefix.
 *
 * Fix: tool sends model = "openai/oc/<model>". LiteLLM routes via openai client (OK).
 * This proxy strips the leading "openai/" and forwards "oc/<model>" to the gateway.
 *
 * Tool config: Base URL http://localhost:20129/v1 , Model openai/oc/<model>
 *
 * Streaming (SSE) is passed through untouched (chunked) so the tool gets a live token stream.
 * Run:  node C:/path/to/proxy.js     (NOTE: in git-bash use FORWARD slashes or the path collapses)
 */
const http = require('http');
const UPSTREAM = { host: '127.0.0.1', port: 20128 };   // real gateway
const LISTEN_PORT = 20129;                              // what the tool points at
const STRIP_PREFIX = 'openai/';

process.on('uncaughtException', (e) => console.error('[proxy][uncaught]', e.message));
process.on('unhandledRejection', (e) => console.error('[proxy][unhandled]', e));

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
        console.log(`[proxy] rewrote model -> ${json.model}`);
      }
    } catch (_) { /* non-JSON passthrough */ }

    const options = {
      hostname: UPSTREAM.host,
      port: UPSTREAM.port,
      path: req.url,
      method: req.method,
      headers: { ...req.headers, host: `${UPSTREAM.host}:${UPSTREAM.port}`, 'content-length': Buffer.byteLength(modified) },
    };

    const proxyReq = http.request(options, (proxyRes) => {
      const headers = { ...proxyRes.headers };
      delete headers['content-length'];   // let chunked stream through
      res.writeHead(proxyRes.statusCode, headers);
      proxyRes.pipe(res);
    });

    proxyReq.on('error', (err) => {
      console.error(`[proxy] upstream error: ${err.message}`);
      if (!res.headersSent) {
        res.writeHead(502, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: { message: `upstream unreachable: ${err.message}` } }));
      } else res.destroy();
    });

    proxyReq.end(modified);
  });
});

server.listen(LISTEN_PORT, '127.0.0.1', () => {
  console.log(`[proxy] listening on :${LISTEN_PORT} -> gateway :${UPSTREAM.port}`);
  console.log(`[proxy] tool Base URL http://localhost:${LISTEN_PORT}/v1 , Model openai/oc/<model>`);
});
