import os
from flask import Flask, render_template, request, redirect
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)

# Are we in production? (set APP_ENV=production on Heroku)
IS_PROD = os.getenv("APP_ENV", "").lower() == "production"

# Only trust proxy headers in prod (Heroku adds X-Forwarded-Proto/Host)
if IS_PROD:
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

@app.before_request
def _force_https():
    if IS_PROD:
        # Behind proxy, honor X-Forwarded-Proto
        if request.headers.get("X-Forwarded-Proto", "http") != "https":
            return redirect(request.url.replace("http://", "https://", 1), code=301)

@app.after_request
def _hsts(resp):
    if IS_PROD:
        resp.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
    return resp

@app.route('/')
def dashboard():
    return render_template("dashboard.html", title="Dashboard")

if __name__ == '__main__':
    app.run(debug=True)  # visit http://127.0.0.1:5000 (no s)
