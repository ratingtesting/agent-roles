/**
 * Prefix-strip proxy for LiteLLM → 9router flows.
 *
 * LiteLLM preserves the provider prefix when routing to a custom api_base.
 * 9router expects its real provider prefix, so this proxy strips a leading
 * override prefix (default: `openai/`) before forwarding to 9router.
 *
 * Usage:
 *   node <this-file>                  # defaults: openai/ -> strip, dst 127.0.0.1:20128, listen :20129
 *   STRIP_PREFIX=ollama/ node <this-file>   # strip a different prefix
 *   UPSTREAM_PORT=3000 node <this-file>     # non-default upstream
 *   LISTEN_PORT=4000 node <this-file>       # non-default listen port
 */

const UPSTREAM = {
  host: '127.0.0.1',
  port: parseInt(process.env.UPSTREAM_PORT || '20128', 10),
};
const LISTEN_PORT = parseInt(process.env.LISTEN_PORT || '20129', 10);
const STRIP_PREFIX = process.env.STRIP_PREFIX || 'openai/';
const STRIP = STRIP_PREFIX.endsWith('/') ? STRIP_PREFIX : STRIP_PREFIX + '/';

const http = require('http');

const server = http.createServer((req, res) => {
  const chunks = [];
  req.on('data', c => chunks.push(c));
  req.on('end', () => {
    const body = Buffer.concat(chunks).toString('utf-8');
    let modified = body;

    try {
      const json = JSON.parse(body);
      if (json.model && typeof json.model === 'string' && json.model.startsWith(STRIP)) {
        json.model = json.model.slice(STRIP.length);
        modified = JSON.stringify(json);
        console.log(`[prefix-proxy] ${STRIP_PREFIX} -> ${json.model}`);
      }
    } catch (e) {
      // pass through
    }

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

        // Strip trailing SSE termination marker if upstream emits it
        responseBody = responseBody.replace(/data:\s*\[DONE\]\s*\n*\s*$/, '');

        const headers = { ...proxyRes.headers };
        headers['content-length'] = Buffer.byteLength(responseBody);
        res.writeHead(proxyRes.statusCode, headers);
        res.end(responseBody);
      });
    });

    proxyReq.on('error', (err) => {
      console.error(`[prefix-proxy] Error: ${err.message}`);
      res.writeHead(502, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: { message: `Proxy error: ${err.message}` } }));
    });

    proxyReq.end(modified);
  });
});

server.listen(LISTEN_PORT, '127.0.0.1', () => {
  console.log(`[prefix-proxy] :${LISTEN_PORT} -> ${UPSTREAM.host}:${UPSTREAM.port} strip=${STRIP}`);
});
