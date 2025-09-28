# 🔒 Security Checklist – Flask + Bootstrap + Sass (Heroku)* [ ] Add **HSTS** (1 year + preload) **only when you're sure** site is stable on HTTPS: **\[prod]** - *ready for implementation when domain is stable*

  ```python
  @app.after_request
  def _hsts(resp):
      resp.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
      return resp
  ```e this before every deploy. Mark completed items with ✅. Production-only items are tagged **\[prod]**.

## Table of Contents
- [Threat Model Snapshot](#0-threat-model-snapshot)
- [Secrets & Configuration](#1-secrets--configuration)
- [HTTPS & Security Headers](#2-https--security-headers)
- [Flask App Hardening](#3-flask-app-hardening)
- [Dependencies & Build](#4-dependencies--build)
- [Heroku Specifics](#5-heroku-specifics)
- [Monitoring, Logs, and Backups](#6-monitoring-logs-and-backups)
- [DNS & Domain Hygiene](#7-dns--domain-hygiene-namecheap)
- [Content & Robots](#8-content--robots)
- [Pre-release Security Tests](#9-pre-release-security-tests)
- [Incident Response Basics](#10-incident-response-basics)
- [Code Snippets](#11-snippets-you-can-drop-in-now)
- [Roadmap](#12-roadmap-when-features-expand)
- [Quick Verify](#quick-verify-curl-one-liners)

---

## 0) Threat model snapshot

* [x] What data do we store/handle? (currently: static pages + JSON + guide landing pages)
* [x] Are there logins, forms, payments, or file uploads? If **no**, attack surface is smaller.
* [x] Public endpoints that mutate state? List them.
* [x] Guide system endpoints (SEO pages): purely static content, no user input processing.

---

## 1) Secrets & configuration

* [x] **Never commit secrets** (API keys, tokens).
* [x] Store secrets in **Heroku Config Vars** (`heroku config:set KEY=value`).
* [x] Set a strong `SECRET_KEY` (>=32 bytes, random). **\[prod]** - *implemented in app.py*
* [x] Different keys for dev vs prod; no shared secrets across environments.
* [x] Disable Flask debug in prod (no `debug=True`). **\[prod]** - *implemented with IS_PROD check*
* [x] Trust proxy so `request.is_secure` works on Heroku: - *implemented with ProxyFix*

  ```python
  # app.py
  from werkzeug.middleware.proxy_fix import ProxyFix
  app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)
  ```

---

## 2) HTTPS & security headers

* [x] Force HTTPS redirects (Flask/Talisman or manual): **\[prod]** - *implemented in app.py*

  ```python
  @app.before_request
  def _force_https():
      if request.headers.get('X-Forwarded-Proto', 'http') != 'https':
          url = request.url.replace('http://', 'https://', 1)
          return redirect(url, code=301)
  ```
* [ ] Add **HSTS** (1 year + preload) **only when you’re sure** site is stable on HTTPS: **\[prod]**

  ```python
  @app.after_request
  def _hsts(resp):
      resp.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
      return resp
  ```
* [x] Set core security headers (can be done via Flask-Talisman or manually): - *implemented in app.py*

  ```python
  @app.after_request
  def _security_headers(resp):
      resp.headers['X-Content-Type-Options'] = 'nosniff'
      resp.headers['X-Frame-Options'] = 'DENY'
      resp.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
      resp.headers['Permissions-Policy'] = (
          'geolocation=(), microphone=(), camera=(), payment=()')
      resp.headers['Cross-Origin-Opener-Policy'] = 'same-origin'
      resp.headers['Cross-Origin-Resource-Policy'] = 'same-origin'
      return resp
  ```
* [x] **Content-Security-Policy (CSP)** (tighten as needed): - *implemented with nonce support*

  ```python
  @app.after_request
  def _csp(resp):
      # If using only local assets compiled via Sass/Bootstrap
      csp = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self'; "
        "img-src 'self' data:; "
        "font-src 'self' data:; "
        "connect-src 'self'; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; form-action 'self'"
      )
      resp.headers['Content-Security-Policy'] = csp
      return resp
  ```

  * If you must use CDNs, add them explicitly and prefer **SRI** hashes. Avoid `'unsafe-inline'`; use nonces if inline scripts are needed.

---

## 3) Flask app hardening

* [x] **Auto-escaping on** in Jinja (default). Never mark unsafe (`|safe`) for user content.
* [ ] **CSRF protection** (if forms): `Flask-WTF` with `WTF_CSRF_ENABLED = True` **\[prod]** - *N/A: no forms yet*
* [x] **Sessions**: - *implemented in app.py*

  ```python
  app.config.update(
      SESSION_COOKIE_SECURE=True,        # HTTPS-only
      SESSION_COOKIE_HTTPONLY=True,      # no JS access
      SESSION_COOKIE_SAMESITE='Lax',     # or 'Strict'
  )
  ```
* [ ] **File uploads** (if added): whitelist extensions, limit size, randomize filenames, scan if possible, never execute.
* [ ] **CORS**: default deny. If needed, scope with `Flask-CORS` to exact origins/paths/methods.
* [ ] **Rate limiting**: `Flask-Limiter` on public endpoints (e.g., scraper APIs):

  ```python
  limiter = Limiter(get_remote_address, app=app, default_limits=["60 per minute"])  # tune
  ```

---

## 4) Dependencies & build

* [x] Pin safe versions but **update regularly** (`pip-audit`, `safety`, `npm audit`). - *requirements.txt has pinned versions*
* [x] Remove unused packages and dev-only deps from production image. - *requirements.txt minimal, package.json uses devDependencies*
* [ ] Avoid `pip install --upgrade` in Heroku release without testing.
* [x] If using CDN JS/CSS, add **SRI** and explicit `integrity` + `crossorigin` attributes. - *using local Bootstrap build, no CDN dependencies*

---

## 5) Heroku specifics

* [x] `Procfile` uses **gunicorn**; no Flask dev server in prod. - *Procfile configured with gunicorn*
* [ ] Gunicorn basic hardening (tune workers/timeouts):

  ```bash
  web: gunicorn app:app --workers 2 --threads 4 --timeout 30
  ```
* [ ] **Heroku SSL** enabled (automatic on paid dynos; ensure custom domain is on SSL). **\[prod]**
* [ ] **Log drains** to Papertrail/Logtail and set alerts on 4xx/5xx spikes.
* [ ] **Review build logs** for secrets accidentally printed.

---

## 6) Monitoring, logs, and backups

* [ ] Centralize logs (request ID, method, path, status, latency, user-agent, IP). Mask PII.
* [ ] Alerting on error rate, latency, and unusual 401/403/429 patterns.
* [ ] Backup critical JSON/data (e.g., `firms.json`, scraped promo cache) on every deploy; keep 7–30 days of rotation.
* [ ] Verify recovery: can you redeploy from scratch + restore cached data?

---

## 7) DNS & domain hygiene (Namecheap)

* [ ] **A/ALIAS/CNAME** only to Heroku; remove stray records that leak origins.
* [ ] **CAA** record to limit who can issue certs for your domain.
* [ ] **SPF/DKIM/DMARC** for email domains (prevents spoofing of your brand emails).
* [ ] Enable domain lock; keep WHOIS privacy on.

---

## 8) Content & robots

* [x] `/robots.txt` denies admin/private paths (if any) and allows guide pages for SEO. - *robots.txt present in static folder*
* [x] Dynamic `/sitemap.xml` only includes existing routes and properly escapes URLs. - *implemented in app.py*
* [ ] Add a `.well-known/security.txt` with contact info for vulnerability reports.
* [x] Guide system templates use proper escaping (Jinja2 auto-escaping enabled). - *Flask default auto-escaping active*

---

## 9) Pre-release security tests

* [ ] Run `bandit -r .` (Python static analysis) and review findings.
* [ ] Run `pip-audit` and `npm audit` and fix highs/criticals.
* [ ] Basic DAST: curl your site with `--insecure` blocked, verify HTTPS redirects & headers.
* [ ] Try trivial XSS strings in any inputs (if/when forms exist).

---

## 10) Incident response basics

* [ ] Single place to rotate secrets quickly (Heroku Config Vars list).
* [ ] Playbook: how to roll back a release, revoke tokens, rotate keys, invalidate sessions.
* [ ] Keep emergency contacts (Heroku status, domain registrar, email provider) handy.

---

## 11) Snippets you can drop in now

* **Central logging**

  ```python
  import logging
  from logging.handlers import RotatingFileHandler

  handler = RotatingFileHandler('app.log', maxBytes=2_000_000, backupCount=5)
  handler.setLevel(logging.INFO)
  app.logger.addHandler(handler)
  ```
* **Error handler that won’t leak stack traces in prod**

  ```python
  @app.errorhandler(500)
  def _500(e):
      app.logger.exception('Server error')
      return render_template('500.html'), 500
  ```

---

## 12) Roadmap (when features expand)

* [ ] Authn/Authz: Flask-Login or OAuth; strong password policy; 2FA if possible; lockout & CAPTCHA on brute-force.
* [ ] DB safety: SQLAlchemy parameterized queries; migrations; least-privilege DB user.
* [ ] Queue/external jobs: sign webhook requests; verify HMAC signatures; replay protection.

---

## Quick verify (curl one-liners)

```bash
# Expect 301 to https
curl -I http://YOURDOMAIN.com

# Check headers are present
curl -sI https://YOURDOMAIN.com | grep -E 'Strict-Transport|Content-Security|X-Content-Type|X-Frame-Options|Referrer-Policy|Permissions-Policy|Cross-Origin-'
```

---

### Notes

* HSTS with preload is sticky—don’t enable until you’re fully committed to HTTPS on the apex and subdomains.
* CSP will be your biggest lever against XSS; start strict and relax only as needed.
