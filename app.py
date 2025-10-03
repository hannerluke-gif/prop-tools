# Stdlib
import os, secrets, json
import datetime
from datetime import timedelta, timezone

# Third-party
from flask import Flask, render_template, request, redirect, g, Response, url_for
from urllib.parse import urljoin, urlparse
from werkzeug.middleware.proxy_fix import ProxyFix

# Local imports
from blueprints.analytics import analytics_bp, top_guides_simple
from guides_catalog import GUIDES_CATALOG, get_all_guides, get_guide_by_id

app = Flask(__name__)

# Register blueprints
app.register_blueprint(analytics_bp)

# Custom Jinja2 filter to convert guide URLs to IDs for analytics
@app.template_filter('guide_id')
def guide_id_filter(url):
    """Convert guide URL to ID for analytics tracking"""
    if url and url.startswith('/guides/'):
        return url.replace('/guides/', '')
    return url

@app.before_request
def _csp_nonce():
    g.csp_nonce = secrets.token_urlsafe(16)

@app.context_processor
def _inject_csp_nonce():
    return {"csp_nonce": getattr(g, "csp_nonce", "")}

# -------- Helper functions --------
GUIDES_PREFIX = "/guides/"

def _safe_context_back_link() -> dict:
    """
    Return a dict {href, label} for the top 'Back' link on guide pages.
    Rules:
      - If referrer is same-origin AND starts with /guides/ (and not this page),
        link back to that guide by title.
      - Otherwise, link to the Guide Index.
    """
    # Defaults
    default = {"href": url_for("guides_index"), "label": "← Back to Guides"}

    # Only show on actual guide detail pages (not /guides index)
    if not request.path.startswith(GUIDES_PREFIX) or request.path == GUIDES_PREFIX:
        return {}

    ref = request.referrer or ""
    if not ref:
        return default

    # Same-origin check
    ref_url = urlparse(ref)
    here_url = urlparse(request.url)
    if (ref_url.scheme, ref_url.netloc) != (here_url.scheme, here_url.netloc):
        return default

    # Must be a guide page (not the index) and not the same page
    if not ref_url.path.startswith(GUIDES_PREFIX) or ref_url.path == GUIDES_PREFIX or ref_url.path == request.path:
        return default

    # Derive guide_id from /guides/<slug>
    slug = ref_url.path.replace(GUIDES_PREFIX, "", 1).strip("/")
    guide = get_guide_by_id(slug)
    if not guide:
        return default

    # Nice label: Back to "Title"
    return {
        "href": guide["href"],
        "label": f"← Back to \"{guide['title']}\""
    }

@app.context_processor
def _inject_guide_back():
    try:
        return {"guide_back": _safe_context_back_link()}
    except Exception:
        return {"guide_back": {}}

@app.context_processor
def _inject_global_popular_guides():
    """Make popular guides available in all templates for footer/sidebar use"""
    try:
        return {"global_popular_guides": get_popular_guides_widget(days=30, limit=3)}
    except Exception:
        return {"global_popular_guides": []}

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

# Guide flame icon threshold (30-day clicks needed to show 🔥)
# Can be overridden with FLAME_ICON_THRESHOLD environment variable
FLAME_ICON_THRESHOLD = int(os.getenv("FLAME_ICON_THRESHOLD", "5"))

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
        resp.headers["Content-Security-Policy"] = csp
    return resp

# -------- Analytics Helper --------
# Popular guides functionality now handled by blueprints/analytics.py
# This section provides template-friendly formatting for the analytics data

def get_popular_guides_widget(days=30, limit=5):
    """
    Get popular guides data formatted for the popular_guides.html widget.
    Returns a list of dicts with id, title, href, clicks for template use.
    """
    try:
        # Get raw popularity data
        popular_tuples = top_guides_simple(days=days, limit=limit)
        
        # Format for widget template using centralized catalog
        widget_guides = []
        used_guide_ids = set()
        
        for guide_id, clicks in popular_tuples:
            guide_info = get_guide_by_id(guide_id)
            if guide_info:  # Only include guides that still exist in catalog
                widget_guides.append({
                    "id": guide_id,
                    "title": guide_info["title"],
                    "href": guide_info["href"],
                    "clicks": clicks
                })
                used_guide_ids.add(guide_id)
        
        # If we don't have enough guides from analytics, fill with popular fallbacks
        if len(widget_guides) < limit:
            fallback_guides = [
                "what-is-a-prop-firm",
                "best-account-size-to-start", 
                "personal-vs-prop-account",
                "what-is-futures-trading",
                "best-prop-firm-to-start"
            ]
            
            for guide_id in fallback_guides:
                if len(widget_guides) >= limit:
                    break
                if guide_id not in used_guide_ids:
                    guide_info = get_guide_by_id(guide_id)
                    if guide_info:
                        widget_guides.append({
                            "id": guide_id,
                            "title": guide_info["title"],
                            "href": guide_info["href"],
                            "clicks": 0  # No analytics data, so 0 clicks
                        })
        
        return widget_guides[:limit]  # Ensure we don't exceed the limit
    except Exception as e:
        # Graceful fallback - return empty list if analytics fails
        app.logger.warning(f"Popular guides widget failed: {e}")
        return []

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

@app.route("/guides")
def guides_index():
    # Get popular guides widget data (includes click counts)
    popular_guides = get_popular_guides_widget(days=30, limit=5)
    
    # Convert to simple map for template compatibility
    popular_map = {guide["id"]: guide["clicks"] for guide in popular_guides}
    
    # Get all guides from catalog with popularity scores
    guides_with_groups = []
    for guide in get_all_guides():
        guide_with_group = guide.copy()
        # Add popularity score
        guide_with_group["score_30d"] = popular_map.get(guide["id"], 0)
        guides_with_groups.append(guide_with_group)
    
    # Optional: reorder each group by popularity
    # guides_with_groups.sort(key=lambda g: g["score_30d"], reverse=True)
    
    return render_template(
        "guides/index.html",
        title="Trading Guides & Prop Firm 101",
        meta_desc="Learn prop firm basics, futures trading, evaluations, sim-funded, and how to choose the right account size and firm.",
        guides=guides_with_groups,
        popular_map=popular_map,
        popular_guides=popular_guides,
        flame_threshold=FLAME_ICON_THRESHOLD,
    )

@app.route("/guides/what-is-a-prop-firm")
def guide_what_is_a_prop_firm():
    guide_meta = get_guide_by_id("what-is-a-prop-firm")
    return render_template(
        "guides/what-is-a-prop-firm.html",
        title="What is a Prop Firm? (Beginner’s Guide)",
        meta_desc="A quick beginner’s guide: how prop firms work, how evaluations and sim-funded accounts differ, and how to choose your first account.",
        guide_updated=guide_meta.get("updated") if guide_meta else None,
    )

@app.route("/guides/what-is-futures-trading")
def guide_what_is_futures_trading():
    guide_meta = get_guide_by_id("what-is-futures-trading")
    return render_template(
        "guides/what-is-futures-trading.html",
        title="What is Futures Trading? (Simple Explanation)",
        meta_desc="Futures trading basics: what contracts are, how margin and leverage work, and common risks beginners should know.",
        guide_updated=guide_meta.get("updated") if guide_meta else None,
    )

@app.route("/guides/best-way-to-start-trading-futures")
def guide_best_way_to_start_trading_futures():
    guide_meta = get_guide_by_id("best-way-to-start-trading-futures")
    return render_template(
        "guides/best-way-to-start-trading-futures.html",
        title="Best Way to Start Trading Futures (Beginner Roadmap)",
        meta_desc="A simple step-by-step path to start trading futures: tools, accounts, risk, and practice options.",
        guide_updated=guide_meta.get("updated") if guide_meta else None,
    )

@app.route("/guides/best-prop-firm-to-start")
def guide_best_prop_firm_to_start():
    guide_meta = get_guide_by_id("best-prop-firm-to-start")
    return render_template(
        "guides/best-prop-firm-to-start.html",
        title="Best Prop Firm to Start With (For Beginners)",
        meta_desc="Compare beginner-friendly prop firms by rules, cost, and payouts. Learn what matters most on day one.",
        guide_updated=guide_meta.get("updated") if guide_meta else None,
    )

@app.route("/guides/best-account-size-to-start")
def guide_best_account_size_to_start():
    guide_meta = get_guide_by_id("best-account-size-to-start")
    return render_template(
        "guides/best-account-size-to-start.html",
        title="What Account Size Should I Start With?",
        meta_desc="How to pick your first account size based on risk, drawdown, and trade plan—plus common beginner mistakes.",
        guide_updated=guide_meta.get("updated") if guide_meta else None,
    )

@app.route("/guides/should-i-skip-evaluation")
def guide_should_i_skip_evaluation():
    guide_meta = get_guide_by_id("should-i-skip-evaluation")
    return render_template(
        "guides/should-i-skip-evaluation.html",
        title="Should I Skip the Evaluation and Go Straight to Sim-Funded?",
        meta_desc="Pros and cons of skipping an evaluation for straight-to-sim-funded accounts—costs, speed, and rules.",
        guide_updated=guide_meta.get("updated") if guide_meta else None,
    )

@app.route("/guides/what-is-a-sim-account")
def guide_what_is_a_sim_account():
    guide_meta = get_guide_by_id("what-is-a-sim-account")
    return render_template(
        "guides/what-is-a-sim-account.html",
        title="What is a Sim Account?",
        meta_desc="Sim accounts explained: practice risk-free, learn rules, and prepare for funded trading the right way.",
        guide_updated=guide_meta.get("updated") if guide_meta else None,
    )

@app.route("/guides/what-is-an-evaluation")
def guide_what_is_an_evaluation():
    guide_meta = get_guide_by_id("what-is-an-evaluation")
    return render_template(
        "guides/what-is-an-evaluation.html",
        title="What is a Prop Firm Evaluation?",
        meta_desc="How prop firm evaluations work: profit targets, drawdown limits, time windows, and passing criteria.",
        guide_updated=guide_meta.get("updated") if guide_meta else None,
    )

@app.route("/guides/what-is-straight-to-sim-funded")
def guide_what_is_straight_to_sim_funded():
    guide_meta = get_guide_by_id("what-is-straight-to-sim-funded")
    return render_template(
        "guides/what-is-straight-to-sim-funded.html",
        title="What is a Straight-to-Sim-Funded Account?",
        meta_desc="Understand straight-to-sim-funded accounts, how payouts work, and when they’re worth the extra cost.",
        guide_updated=guide_meta.get("updated") if guide_meta else None,
    )

@app.route("/guides/personal-vs-prop-account")
def guide_personal_vs_prop_account():
    guide_meta = get_guide_by_id("personal-vs-prop-account")
    return render_template(
        "guides/personal-vs-prop-account.html",
        title="Personal Account vs Prop Account — Which Should I Start With?",
        meta_desc="Pros/cons of personal futures accounts vs prop accounts: capital, rules, risk, taxes, and control.",
        guide_updated=guide_meta.get("updated") if guide_meta else None,
    )

@app.route("/guides/futures-trading-products")
def guide_futures_trading_products():
    # Load products data from JSON file
    static_folder = app.static_folder or 'static'
    products_path = os.path.join(static_folder, 'data', 'products.json')
    try:
        with open(products_path, 'r', encoding='utf-8') as f:
            products_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Fallback to empty data if file issues
        products_data = {"disclaimer": "", "categories": []}
    
    guide_meta = get_guide_by_id("futures-trading-products")
    
    return render_template(
        "guides/futures-trading-products.html",
        title="Futures Trading Products — Complete Reference Guide",
        meta_desc="Complete reference guide to futures trading products available at prop firms. Index, currency, energy, metal, agricultural, and crypto futures.",
        products=products_data,
        guide_updated=guide_meta.get("updated") if guide_meta else None,
    )

# Guides data now centralized in guides_catalog.py

def _abs_url(path: str) -> str:
    return urljoin(request.url_root, path.lstrip('/'))

def _iso_utc(ts: float) -> str:
    return datetime.datetime.utcfromtimestamp(ts).replace(microsecond=0).isoformat() + "Z"

@app.route("/sitemap.xml")
def sitemap():
    # Base URLs you want indexed
    core = [
        {"loc": _abs_url("/"), "changefreq": "daily", "priority": "1.0"},
        {"loc": _abs_url("/guides"), "changefreq": "weekly", "priority": "0.90"},
        # Add other core pages here when they exist:
        # {"loc": _abs_url("/compare"), "changefreq": "daily", "priority": "0.95"},
    ]

    # Guide pages (optionally compute lastmod from template files)
    guide_entries = []
    for g in get_all_guides():
        loc = _abs_url(g["href"])
        lastmod = None
        # Try to map a template path (adjust if your paths differ)
        # e.g., templates/guides/what-is-a-prop-firm.html
        tpl_path = os.path.join(
            os.path.dirname(__file__),
            "templates",
            g["href"].lstrip("/"),
        ) + ".html"
        if os.path.exists(tpl_path):
            lastmod = _iso_utc(os.path.getmtime(tpl_path))

        guide_entries.append({
            "loc": loc,
            "changefreq": "monthly",
            "priority": "0.85",
            "lastmod": lastmod,
        })

    urls = core + guide_entries
    xml = render_template("sitemap.xml", urls=urls)
    return Response(xml, mimetype="application/xml")

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

