// Verification for the 9router/OpenHands strip-prefix proxy.
// Code-level (no live server needed). Run: node scripts/verify-proxy.js
const fs = require('fs');
const { execSync } = require('child_process');

const PROXY = process.argv[2] || 'C:\\Projects\\lazy-unicorn\\9router-proxy\\proxy.js';

let pass = 0, fail = 0;
const ok = (c, m) => { console.log((c ? 'PASS' : 'FAIL') + ' - ' + m); c ? pass++ : fail++; };

// 1. Syntax
try {
  execSync('node --check "' + PROXY + '"', { stdio: 'pipe' });
  ok(true, 'proxy.js syntax valid (node --check)');
} catch (e) {
  ok(false, 'proxy.js syntax error: ' + e.message);
}

// 2. Replicate the exact rewrite logic and test
const STRIP_PREFIX = 'openai/';
function strip(model) {
  if (typeof model === 'string' && model.startsWith(STRIP_PREFIX)) {
    return model.slice(STRIP_PREFIX.length);
  }
  return model;
}
const cases = [
  ['openai/oc/deepseek-v4-flash-free', 'oc/deepseek-v4-flash-free'],
  ['openai/oc/mimo-v2.5-free', 'oc/mimo-v2.5-free'],
  ['oc/deepseek-v4-flash-free', 'oc/deepseek-v4-flash-free'],
  ['anthropic/claude', 'anthropic/claude'],
];
let logicOk = true;
for (const [inp, exp] of cases) {
  const got = strip(inp);
  if (got !== exp) { logicOk = false; console.log('  mismatch: ' + inp + ' -> ' + got + ' (expected ' + exp + ')'); }
}
ok(logicOk, 'rewrite strips openai/ -> ns/ and leaves others untouched');

// 3. Source-of-truth: proxy.js must contain this logic
const src = fs.readFileSync(PROXY, 'utf-8');
ok(
  src.includes("const STRIP_PREFIX = 'openai/'") &&
  src.includes('json.model.startsWith(STRIP_PREFIX)') &&
  src.includes('json.model.slice(STRIP_PREFIX.length)'),
  'proxy.js source matches verified rewrite logic'
);

console.log('\nSUMMARY: ' + pass + ' passed, ' + fail + ' failed');
process.exit(fail === 0 ? 0 : 1);
