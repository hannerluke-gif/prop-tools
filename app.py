from flask import Flask, render_template, request, redirect
from werkzeug.middleware.proxy_fix import ProxyFix

# Create Flask application instance
app = Flask(__name__)

# Trust proxy headers from Heroku (important so Flask sees HTTPS correctly)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Force HTTPS redirect
@app.before_request
def _force_https():
    # If the request did not come in over HTTPS, redirect it
    if request.headers.get("X-Forwarded-Proto", "http") != "https":
        return redirect(request.url.replace("http://", "https://", 1), code=301)

@app.route('/')
def dashboard():
    """Render the homepage."""
    return render_template("dashboard.html", title="Dashboard")

if __name__ == '__main__':
    # For development convenience. In production, use a proper WSGI server (e.g., gunicorn, waitress).
    app.run(debug=True)
