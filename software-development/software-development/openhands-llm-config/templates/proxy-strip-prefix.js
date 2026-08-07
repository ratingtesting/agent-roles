/**
 * Generic prefix-stripping proxy for OpenHands / LiteLLM -> custom OpenAI-compatible router.
 *
 * Problem: LiteLLM requires a known provider prefix (openai/) on the model name or it throws
 *   litellm.BadRequestError: LLM Provider NOT provided.
 * But the target router (e.g. 9router) owns its own namespace (oc/, opencode/) and rejects openai/.
 *
 * Fix: OpenHands sends model = "openai/<ns>/<model>". LiteLLM strips only "openai/" and routes via the
 * openai client. This proxy receives it, strips "openai/", and forwards "<ns>/<model>" to the router.
 *
 * Streaming (SSE) is passed through untouched (chunked) so OpenHands gets a live token stream.
 *
 * Usage:
 *   node proxy-strip-prefix.js
 *   then point OpenHands Base URL at http://localhost:<LISTEN_PORT>/v1
 *   and model at openai/<router-namespace>/<model>
 */
const http = require('http');

const UPSTREAM = { host: '127.0.0.1', port: 20128 }; // the router
const LISTEN_PORT = 20129;                            // what OpenHands points at
const STRIP_PREFIX = 'openai/';                       // LiteLLM prefix to remove

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
    } catch (_) {
      // non-JSON body -> pass through unchanged
    }

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
      delete headers['content-length']; // let client use chunked for streams
      res.writeHead(proxyRes.statusCode, headers);
      proxyRes.pipe(res);
    });

    proxyReq.on('error', (err) => {
      console.error(`[proxy] upstream error: ${err.message}`);
      if (!res.headersSent) {
        res.writeHead(502, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: { message: `upstream unreachable: ${err.message}` } }));
      } else {
        res.destroy();
      }
    });

    proxyReq.end(modified);
  });
});

server.listen(LISTEN_PORT, '127.0.0.1', () => {
  console.log(`[proxy] listening on :${LISTEN_PORT} -> ${UPSTREAM.host}:${UPSTREAM.port}`);
  console.log(`[proxy] OpenHands: Base URL http://localhost:${LISTEN_PORT}/v1 , Model openai/<ns>/<model>`);
});
