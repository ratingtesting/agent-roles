# Auth security patterns — password reset, anti-enumeration, token generation

Companion to `python-security-hardening/SKILL.md`. Covers OWASP A07 (auth)
patterns that don't fit the four core vuln classes (SQLi/eval/path-traversal/IDOR)
but are equally important in Flask/web apps.

## Password reset via email — secure pattern

### Token generation

```python
import secrets

token = secrets.token_urlsafe(48)  # ~64 chars, URL-safe, cryptographically random
```

- `secrets` (not `random`) — uses OS CSPRNG.
- `token_urlsafe(48)` produces ~64 URL-safe characters — enough entropy to
  resist brute force even at 1M guesses/sec (256 bits of entropy).
- Never use `uuid4()` for security tokens — its entropy is lower and it's
  not designed for this purpose.

### Token storage & lifecycle

```python
class PasswordResetToken(db.Model):
    token = db.Column(db.String(255), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False, nullable=False)
```

Rules:
1. **One-time use** — mark `used=True` after password change. Reject if already used.
2. **TTL** — set `expires_at = now + 1h`. Reject if expired.
3. **Single active token per user** — optionally delete old tokens when generating a new one.
4. **Cascade delete** — `on_delete='CASCADE'` so tokens are cleaned up when the user is deleted.

### Anti-enumeration (don't reveal if email exists)

```python
user = User.query.filter_by(email=email).first()
if user:
    token = PasswordResetToken.generate(user.id)
    send_reset_email(user, token.token)

# ALWAYS return success — never reveal whether the email was found
flash("If this email is registered, a reset link has been sent.")
```

- Always return the same HTTP 200 response with the same message.
- Always render the same template.
- Only send the email if the user exists — but don't tell the requester either way.
- This prevents attackers from enumerating valid emails via the reset endpoint.

### Password hashing

```python
from werkzeug.security import generate_password_hash, check_password_hash

# On password set:
user.password_hash = generate_password_hash(password)

# On login:
if check_password_hash(user.password_hash, password):
    # authenticated
```

- Werkzeug uses PBKDF2-HMAC-SHA256 by default with 16-byte salt and 600k iterations.
- For production, consider `bcrypt` or `argon2` (via `passlib`) for stronger guarantees.
- Never store plaintext passwords. Never store MD5/SHA1 hashes.

## Rate limiting (basic)

For the reset request endpoint, add a simple in-memory rate limiter:

```python
from collections import defaultdict, deque
from time import time

_reset_attempts = defaultdict(deque)
RATE_LIMIT = 5  # max attempts
RATE_WINDOW = 300  # 5 minutes

def check_rate_limit(email: str) -> bool:
    now = time()
    attempts = _reset_attempts[email]
    # Evict old entries
    while attempts and attempts[0] < now - RATE_WINDOW:
        attempts.popleft()
    if len(attempts) >= RATE_LIMIT:
        return False  # rate limited
    attempts.append(now)
    return True
```

For production, use `Flask-Limiter` with Redis backend. The in-memory version
resets on restart and doesn't work across multiple workers.

## Ad-hoc verification for auth patterns

```python
import importlib.util, sys, os, tempfile

MOD = r"C:\path\to\reset_password.py"
spec = importlib.util.spec_from_file_location("reset_pw", MOD)
mod = importlib.util.module_from_spec(spec)
sys.modules["reset_pw"] = mod  # BEFORE exec_module — see py311-importlib-dataclass.md
spec.loader.exec_module(mod)

failures = []

# 1. Token is URL-safe and sufficiently long
token = mod.PasswordResetToken.generate(user_id=1)
assert len(token.token) >= 48, f"token too short: {len(token.token)}"
assert all(c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
           for c in token.token), "token contains non-URL-safe chars"

# 2. Token is single-use
assert mod.PasswordResetToken.find_valid(token.token) is not None
token.mark_used()
assert mod.PasswordResetToken.find_valid(token.token) is None  # used token rejected

# 3. Expired token is rejected
token2 = mod.PasswordResetToken.generate(user_id=1)
token2.expires_at = mod.utcnow() - timedelta(hours=1)
db.session.commit()
assert mod.PasswordResetToken.find_valid(token2.token) is None

# 4. Password hashing works
user = User(email="test@example.com")
user.set_password("securepass123")
assert user.check_password("securepass123")
assert not user.check_password("wrongpass")

# 5. Anti-enumeration: same response for existing and non-existing emails
resp1 = client.post("/reset-password", data={"email": "exists@example.com"})
resp2 = client.post("/reset-password", data={"email": "nonexistent@example.com"})
assert resp1.status_code == resp2.status_code == 200
assert resp1.data == resp2.data  # identical response bodies

print("ALL AUTH CHECKS PASSED")
```

## Common mistakes

| Mistake | Why it fails | Fix |
|---|---|---|
| `random.random()` for token | Not cryptographically secure; predictable | Use `secrets.token_urlsafe()` |
| `uuid4().hex` for token | Lower entropy, not designed for security | Use `secrets` |
| Return different response for existing vs non-existing email | Email enumeration | Always return same response |
| Token never expires | Stolen tokens valid forever | Set TTL (1h max) |
| Token reusable | Attacker can reset password multiple times | Mark `used=True` |
| Store token in plaintext | DB leak exposes all active tokens | Hash the token before storing (like a password) |
| No rate limiting | Brute-force token guessing | Add rate limiting on reset endpoint |
| Password validation too weak | Users pick "123456" | Enforce min length, complexity |
| `generate_password_hash` with default params | May use weak algorithm in old Werkzeug | Pin Werkzeug version or use `method='pbkdf2:sha256'` |