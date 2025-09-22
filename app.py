import os
from flask import Flask, render_template, request, redirect
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)

# -------- Environment & base config --------
# Set APP_ENV=production on Heroku (Config Vars). Anything else = dev.
APP_ENV = os.getenv("APP_ENV", "").lower()
IS_PROD = APP_ENV == "production"

# SECRET_KEY must be set in production (Heroku Config Var).
# In dev we'll fall back to a dummy value.
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-not-secret")
app.config.update(
    SESSION_COOKIE_SECURE=True,     # only over HTTPS
    SESSION_COOKIE_HTTPONLY=True,   # not accessible to JS
    SESSION_COOKIE_SAMESITE="Lax",  # or "Strict" if no cross-site POSTs
)

# Only trust proxy headers when deployed behind Heroku's proxy
if IS_PROD:
    # x_for=1 ensures request.remote_addr is the client IP Heroku passes through
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)

# -------- HTTPS redirect (prod only) --------
@app.before_request
def _force_https():
    if not IS_PROD:
        return
    # Heroku sets X-Forwarded-Proto
    if request.headers.get("X-Forwarded-Proto", "http") != "https":
        return redirect(request.url.replace("http://", "https://", 1), code=301)

# -------- Security headers (prod only) --------
@app.after_request
def _security_headers(resp):
    if IS_PROD:
        # HSTS: enable once you're fully committed to HTTPS for apex + subdomains
        resp.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"

        # Core hardening headers
        resp.headers["X-Content-Type-Options"] = "nosniff"
        resp.headers["X-Frame-Options"] = "DENY"
        resp.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        resp.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=(), payment=()"
        resp.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        resp.headers["Cross-Origin-Resource-Policy"] = "same-origin"

        # Content Security Policy (tight, local-only). Relax if you use CDNs.
        # If you load Bootstrap/JS via CDN, add those hosts and (ideally) nonces/SRI.
        csp = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "img-src 'self' data:; "
            "font-src 'self' https://fonts.gstatic.com data:; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; form-action 'self'"
        )
        resp.headers["Content-Security-Policy"] = csp
    return resp

# -------- Routes --------
@app.route("/")
def dashboard():
    return render_template("dashboard.html", title="Dashboard")

# -------- Error handling --------
@app.errorhandler(500)
def _500(e):
    # Log in server logs; don't leak stack traces to users in prod
    app.logger.exception("Server error")
    return render_template("500.html"), 500

# -------- Entrypoint --------
if __name__ == "__main__":
    # Dev server only. In prod, run via Gunicorn (Procfile).
    app.run(debug=not IS_PROD)

