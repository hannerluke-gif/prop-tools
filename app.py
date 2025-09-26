# Stdlib
import os
import secrets

# Third-party
from flask import Flask, render_template, request, redirect, g
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)

@app.before_request
def _csp_nonce():
    g.csp_nonce = secrets.token_urlsafe(16)

@app.context_processor
def _inject_csp_nonce():
    return {"csp_nonce": getattr(g, "csp_nonce", "")}

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

        # CSP: adjust as needed
        # Note: using 'nonce-{nonce}' for styles to allow inline styles with nonce
        nonce = getattr(g, "csp_nonce", "")
        csp = (
            "default-src 'self'; "
            "script-src 'self'; "
            "script-src-elem 'self'; "
            "script-src-attr 'none'; "
            f"style-src 'self' 'nonce-{nonce}' https://fonts.googleapis.com; "
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

@app.route("/not-found")
def not_found_placeholder():
    # Temporary placeholder target for hero CTAs until real pages exist.
    # Returns a 404 status intentionally so analytics can distinguish visits.
    return ("<h1>Not Found</h1><p>This destination page has not been built yet.</p>", 404, {"Content-Type": "text/html; charset=utf-8"})

@app.route("/robots.txt")
def robots_txt():
    return app.send_static_file("robots.txt")

@app.route("/.well-known/security.txt")
def security_txt():
    return app.send_static_file(".well-known/security.txt")

# --- Guides / SEO pages ---
from flask import render_template

@app.route("/guides/what-is-a-prop-firm")
def guide_what_is_a_prop_firm():
    return render_template(
        "guides/what-is-a-prop-firm.html",
        title="What is a Prop Firm? (Beginner’s Guide)",
        meta_desc="A quick beginner’s guide: how prop firms work, how evaluations and sim-funded accounts differ, and how to choose your first account.",
    )

@app.route("/guides/what-is-futures-trading")
def guide_what_is_futures_trading():
    return render_template(
        "guides/what-is-futures-trading.html",
        title="What is Futures Trading? (Simple Explanation)",
        meta_desc="Futures trading basics: what contracts are, how margin and leverage work, and common risks beginners should know.",
    )

@app.route("/guides/best-way-to-start-trading-futures")
def guide_best_way_to_start_trading_futures():
    return render_template(
        "guides/best-way-to-start-trading-futures.html",
        title="Best Way to Start Trading Futures (Beginner Roadmap)",
        meta_desc="A simple step-by-step path to start trading futures: tools, accounts, risk, and practice options.",
    )

@app.route("/guides/best-prop-firm-to-start")
def guide_best_prop_firm_to_start():
    return render_template(
        "guides/best-prop-firm-to-start.html",
        title="Best Prop Firm to Start With (For Beginners)",
        meta_desc="Compare beginner-friendly prop firms by rules, cost, and payouts. Learn what matters most on day one.",
    )

@app.route("/guides/best-account-size-to-start")
def guide_best_account_size_to_start():
    return render_template(
        "guides/best-account-size-to-start.html",
        title="What Account Size Should I Start With?",
        meta_desc="How to pick your first account size based on risk, drawdown, and trade plan—plus common beginner mistakes.",
    )

@app.route("/guides/should-i-skip-evaluation")
def guide_should_i_skip_evaluation():
    return render_template(
        "guides/should-i-skip-evaluation.html",
        title="Should I Skip the Evaluation and Go Straight to Sim-Funded?",
        meta_desc="Pros and cons of skipping an evaluation for straight-to-sim-funded accounts—costs, speed, and rules.",
    )

@app.route("/guides/what-is-a-sim-account")
def guide_what_is_a_sim_account():
    return render_template(
        "guides/what-is-a-sim-account.html",
        title="What is a Sim Account?",
        meta_desc="Sim accounts explained: practice risk-free, learn rules, and prepare for funded trading the right way.",
    )

@app.route("/guides/what-is-an-evaluation")
def guide_what_is_an_evaluation():
    return render_template(
        "guides/what-is-an-evaluation.html",
        title="What is a Prop Firm Evaluation?",
        meta_desc="How prop firm evaluations work: profit targets, drawdown limits, time windows, and passing criteria.",
    )

@app.route("/guides/what-is-straight-to-sim-funded")
def guide_what_is_straight_to_sim_funded():
    return render_template(
        "guides/what-is-straight-to-sim-funded.html",
        title="What is a Straight-to-Sim-Funded Account?",
        meta_desc="Understand straight-to-sim-funded accounts, how payouts work, and when they’re worth the extra cost.",
    )

@app.route("/guides/personal-vs-prop-account")
def guide_personal_vs_prop_account():
    return render_template(
        "guides/personal-vs-prop-account.html",
        title="Personal Account vs Prop Account — Which Should I Start With?",
        meta_desc="Pros/cons of personal futures accounts vs prop accounts: capital, rules, risk, taxes, and control.",
    )

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

