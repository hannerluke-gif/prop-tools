from flask import Flask, render_template

# Create Flask application instance
app = Flask(__name__)

@app.route('/')
def dashboard():
    """Render the homepage."""
    return render_template("dashboard.html", title="Dashboard")

if __name__ == '__main__':
    # For development convenience. In production, use a proper WSGI server (e.g., gunicorn, waitress).
    app.run(debug=True)
