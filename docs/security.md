# 🔒 Security Guide - Flask + Analytics System

## Table of Contents
- [Deployment Security](#deployment-security)
- [Analytics Security](#analytics-security)
- [Quick Security Tests](#quick-security-tests)

---

## Deployment Security

### Threat Model Overview
* [x] **Data handling**: Static pages + JSON + guide landing pages + privacy-friendly analytics
* [x] **Attack surface**: No logins, forms, payments, or file uploads (low risk)
* [x] **Public endpoints**: Analytics click tracking (minimal user input)
* [x] **Guide system**: Purely static content, no user input processing

### 1. Secrets & Configuration
* [x] **Never commit secrets** (API keys, tokens)
* [x] Store secrets in **Heroku Config Vars** (`heroku config:set KEY=value`)
* [x] Set a strong `SECRET_KEY` (>=32 bytes, random) **[prod]** - *implemented in app.py*
* [x] Different keys for dev vs prod; no shared secrets across environments
* [x] Disable Flask debug in prod (no `debug=True`) **[prod]** - *implemented with IS_PROD check*
* [x] Trust proxy so `request.is_secure` works on Heroku - *implemented with ProxyFix*

```python
# app.py
from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)
```

### 2. HTTPS & Security Headers
* [x] **Force HTTPS redirects** **[prod]** - *implemented in app.py*

```python
@app.before_request
def _force_https():
    if request.headers.get('X-Forwarded-Proto', 'http') != 'https':
        url = request.url.replace('http://', 'https://', 1)
        return redirect(url, code=301)
```

* [ ] **Add HSTS** (1 year + preload) **only when you're sure** site is stable on HTTPS **[prod]**

```python
@app.after_request
def _hsts(resp):
    resp.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
    return resp
```

* [x] **Core security headers** - *implemented in app.py*

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

* [x] **Content-Security-Policy (CSP)** - *implemented with nonce support and Google services allowlist*

```python
@app.after_request
def _csp(resp):
    nonce = getattr(g, "csp_nonce", "")
    csp = (
        "default-src 'self'; "
        f"script-src 'self' 'nonce-{nonce}' https://www.googletagmanager.com; "
        f"script-src-elem 'self' 'nonce-{nonce}' https://www.googletagmanager.com; "
        "script-src-attr 'none'; "
        f"style-src 'self' 'nonce-{nonce}' https://fonts.googleapis.com; "
        "img-src 'self' data:; "
        "font-src 'self' https://fonts.gstatic.com data:; "
        "connect-src 'self' https://www.google-analytics.com https://analytics.google.com; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; form-action 'self'"
    )
    resp.headers['Content-Security-Policy'] = csp
    return resp
```

**CSP Security Notes:**
- ✅ **Nonce-based**: All inline scripts/styles must use server-generated nonces
- ✅ **No unsafe-inline**: Prevents XSS from injected inline content
- ✅ **script-src-attr 'none'**: Blocks inline event handlers (onclick, etc.)
- ✅ **frame-ancestors 'none'**: Prevents clickjacking attacks
- ✅ **Minimal allowlist**: Only trusted Google services for analytics and fonts
- ⚠️ **Google services**: GTM, GA, and Google Fonts are allowlisted for functionality

### 3. Flask App Hardening
* [x] **Disable server banners** (no Flask version leaks)
* [x] **Session configuration** with secure cookies **[prod]**
* [x] **Error handling** - Custom 500 pages, no debug info in production
* [x] **Request size limits** - Prevent large payload attacks

---

## Analytics Security

### Input Validation & Sanitization

#### Guide ID Validation
* ✅ **Strict regex pattern**: Only allows `[a-z0-9\-]+` (no special chars, paths, or injections)
* ✅ **Length limits**: Maximum 100 characters to prevent buffer issues
* ✅ **Required field**: Empty guide_id rejected with 400 error
* ✅ **Case normalization**: Automatically converted to lowercase

```python
SLUG_RE = re.compile(r'^[a-z0-9\-]+$')  # "what-is-a-prop-firm"
MAX_GUIDE_ID_LENGTH = 100
```

#### String Truncation (Prevent Log Bloat)
* ✅ **Guide title**: Truncated to 200 characters
* ✅ **URL href**: Truncated to 300 characters  
* ✅ **User-Agent**: Truncated to 255 characters
* ✅ **Database constraints**: Enforced at storage level

```python
MAX_TITLE_LENGTH = 200
MAX_HREF_LENGTH = 300
MAX_UA_LENGTH = 255
```

#### JSON Payload Validation
* ✅ **Content-Type check**: Requires `application/json`
* ✅ **Malformed JSON rejection**: Returns 400 for invalid JSON
* ✅ **Empty payload rejection**: Returns 400 for empty requests
* ✅ **SQL injection protection**: Uses parameterized queries only

### Privacy Protection (No PII)

#### Zero Personal Information
* ✅ **No IP addresses**: Client IP never stored or logged
* ✅ **No cookies**: System works without any cookie tracking
* ✅ **No user accounts**: No authentication or user identification
* ✅ **No session tracking**: Only local browser analytics session UUID
* ✅ **No cross-site data**: Analytics limited to same origin only

#### Data Minimization
* ✅ **Guide context only**: Only guide_id, title, href stored
* ✅ **Anonymous metrics**: No way to identify individual users
* ✅ **Truncated UA**: User-Agent limited to bot detection only
* ✅ **Timestamp only**: UTC timestamps with no timezone fingerprinting

```python
# What we store (privacy-friendly):
guide_id: "what-is-a-prop-firm"
guide_title: "What is a Prop Firm?"
href: "/guides/what-is-a-prop-firm"
ua: "Mozilla/5.0 (Windows NT 10.0...)..."[:255]  # truncated
ts_utc: "2025-09-28T18:30:15.123456+00:00"

# What we DON'T store:
# - IP addresses, Cookies, User names/emails
# - Device fingerprints, Location data
```

### CSP Compliance & Bot Protection

#### No Inline Scripts
* ✅ **External JS files only**: Analytics tracking in separate files
* ✅ **No inline event handlers**: Uses `addEventListener` patterns
* ✅ **No eval() usage**: All code statically analyzable
* ✅ **Nonce support**: CSP nonce system preserved

#### JavaScript Style Manipulation Rules (CSP-Compliant)

**Critical:** With `script-src-attr 'none'` in our CSP, we must avoid inline style violations.

**Prohibited Patterns:**
* ❌ **Inline `style=` attributes in HTML**: Violates `style-src` CSP directive
* ❌ **Direct `.style.property = value`**: Creates inline styles, blocked by CSP
* ❌ **Template literals with styles**: `<div style="${dynamicStyle}">` blocked

**Allowed Patterns:**
* ✅ **CSS Custom Properties**: `element.style.setProperty('--var-name', value)`
* ✅ **Class Toggling**: `element.classList.add('active-state')`
* ✅ **Data Attributes + CSS**: `element.dataset.state = 'open'` with `[data-state="open"]` selector

**Code Examples:**
```javascript
// ❌ BAD - Violates CSP, creates inline styles
element.style.transform = 'translateX(100px)';
element.style.opacity = '0.5';
element.style.overflow = 'hidden';

// ✅ GOOD - CSS custom properties (CSP-compliant)
element.style.setProperty('--offset-x', '100px');
// In CSS: transform: var(--offset-x);

// ✅ BETTER - Class toggling with predefined CSS
element.classList.add('is-transformed');
element.classList.add('is-faded');
document.body.classList.add('scroll-locked');
// Define .is-transformed, .is-faded, .scroll-locked in SCSS

// ✅ BEST - Data attributes for state management
element.dataset.state = 'active';
element.dataset.position = 'top';
// In CSS: [data-state="active"] { opacity: 1; }
//         [data-position="top"] { top: 0; }
```

**Implementation Examples from Codebase:**

```javascript
// Footer reveal animation (footerReveal.js)
// ✅ Uses CSS custom property for dynamic transform
pageWrapper.style.setProperty('--footer-reveal-offset', `translateY(${translateY}px)`);
pageWrapper.classList.add('footer-reveal-active');

// Mobile menu scroll lock (hamburgerMenu.js)
// ✅ Uses class toggle instead of style.overflow
document.body.classList.add('mobile-menu-open');

// Guide animations (guideAnimations.js)
// ✅ Uses class toggle for visibility
el.classList.add('animation-visible');

// Banner offsets (bannerOffsets.js)
// ✅ CSS custom property for dynamic positioning
banner.style.setProperty('--mobile-menu-top', `${offset}px`);
```

**HTML Template Rules:**
```html
<!-- ❌ BAD - Inline styles violate CSP -->
<section style="padding-top: 8rem; padding-bottom: 12rem;">
  <div style="min-height: 100vh;">Content</div>
</section>

<!-- ✅ GOOD - Use CSS classes -->
<section class="dashboard__future-content">
  <div class="dashboard__future-content-inner">Content</div>
</section>
```

```scss
// Define styles in SCSS
.dashboard {
  &__future-content {
    padding-top: 8rem;
    padding-bottom: 12rem;
    
    &-inner {
      min-height: 100vh;
    }
  }
}
```

#### Bot & Abuse Protection
* ✅ **User-Agent bot filtering**: Blocks common bots and crawlers
* ✅ **Rate limiting**: Max 3 clicks per guide per minute per session
* ✅ **Session-based controls**: Client-side deduplication

```python
BOT_UA_RE = re.compile(r'bot|spider|crawl|scraper|facebookexternalhit|twitterbot', re.IGNORECASE)
```

---

## Quick Security Tests

### CSP Validation
```bash
curl -I https://yourdomain.com | grep -i "content-security-policy"
```

### Security Headers Check
```bash
curl -I https://yourdomain.com | grep -E "(X-Frame-Options|X-Content-Type-Options|Strict-Transport-Security)"
```

### Analytics Endpoint Test
```bash
# Should return 400 for invalid JSON
curl -X POST https://yourdomain.com/analytics/guide-click \
  -H "Content-Type: application/json" \
  -d "invalid-json"
```

### Bot Protection Test
```bash
# Should return 429 for bot user agents
curl https://yourdomain.com/analytics/guide-click \
  -H "User-Agent: Googlebot/2.1"
```

## Security Maintenance

### Regular Tasks
- [ ] **Monthly**: Review analytics data for anomalies
- [ ] **Quarterly**: Update dependencies and security headers
- [ ] **Annually**: Rotate SECRET_KEY and review CSP policies

### Monitoring
- Monitor for failed analytics requests (potential attacks)
- Watch for unusual traffic patterns
- Review Core Web Vitals for performance impacts

**For detailed implementation:** See `app.py` and `blueprints/analytics.py`