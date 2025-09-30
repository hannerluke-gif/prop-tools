# Prop Tools (Flask + Bootstrap + Guide System)

A comprehensive Flask project featuring a scalable guide system, modern Sass/BEM architecture, and production-ready security. Built for rapid prototyping and extension into larger applications.

## Table of Contents
- [Features](#features)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Quick Start](#quick-start)
- [📚 Documentation](#-documentation)
- [Guide System (SEO Landing Pages)](#guide-system-seo-landing-pages)
- [Development Workflow](#11-development-workflow)
- [Production Deployment](#12-production-deployment)
- [Testing](#13-testing)
- [Suggested Next Enhancements](#14-suggested-next-enhancements)
- [Maintenance](#15-maintenance)
- [Component Updates](#16-component-updates)

## Features
- **Flask app** with dashboard and SEO-optimized guide system
- **Dynamic sitemap** automatically generated from guides and routes
- **Guide System** with BEM components, schema markup, and responsive design
- **Privacy-friendly analytics** with guide click tracking and back link navigation analytics (no PII stored)
- **Modern Sass architecture** with Bootstrap 5 integration and design tokens
- **Security hardening** with CSP, HTTPS, and production-ready headers
- **VS Code integration** with tasks, Sass watch, and development workflow
- **Production deployment** ready for Heroku with proper configuration

## Project Structure
```
propfirm_bootstrap/
├── app.py                     # Flask application with routes & security
├── guides_catalog.py          # Centralized guide definitions and metadata
├── requirements.txt           # Python dependencies
├── Procfile                   # Heroku deployment config
├── package.json               # Node.js dependencies (Sass)
│
├── blueprints/               # Flask Blueprint modules
│   ├── __init__.py
│   └── analytics.py          # Analytics system with click tracking
│
├── templates/
│   ├── base.html              # Main layout template
│   ├── dashboard.html         # Dashboard page
│   ├── sitemap.xml           # Dynamic sitemap template
│   ├── 500.html              # Error page
│   ├── components/           # Reusable template components
│   │   └── popular_guides.html # Popular guides widget
│   └── guides/               # Guide system templates
│       ├── guide_base.html   # Shared guide layout
│       ├── index.html        # Guides index with popular widget
│       └── what-is-a-prop-firm.html  # Example guide page
│
├── static/
│   ├── robots.txt
│   ├── manifest.json
│   ├── .well-known/          # Security and metadata files
│   │   └── security.txt      # Vulnerability disclosure policy
│   ├── css/                  # Compiled CSS output
│   │   └── main.css
│   ├── scss/                 # Sass source files
│   │   ├── main.scss         # Main Sass entry point
│   │   ├── _variables.scss   # Design tokens and theming
│   │   ├── _mixins.scss     # Sass mixins
│   │   ├── _maps.scss       # Bootstrap customization
│   │   ├── components/      # Component-specific styles
│   │   │   ├── _buttons.scss
│   │   │   ├── _hero.scss
│   │   │   ├── _promo-banner.scss
│   │   │   ├── _site-banner.scss
│   │   │   ├── _dashboard.scss
│   │   │   └── _brand.scss
│   │   └── layout/          # Layout and page styles
│   │       ├── _header.scss
│   │       ├── _footer.scss
│   │       ├── _guides.scss # Guide system BEM components
│   │       └── _prose.scss  # Typography utilities
│   ├── js/                  # JavaScript modules (ES6)
│   │   ├── main.js          # Entry point with analytics tracking
│   │   ├── analytics.js     # Google Analytics initialization (CSP compliant)
│   │   ├── components/      # Component scripts
│   │   │   ├── hero.js
│   │   │   ├── promoBanner.js
│   │   │   └── siteBannerSearch.js
│   │   └── utils/           # Utility functions
│   │       ├── breakpoints.js
│   │       └── dom.js
│   ├── img/                 # Images and assets
│   │   ├── logos/
│   │   ├── banners/
│   │   └── slide/
│   ├── data/                # JSON data files
│   │   ├── firms.json
│   │   ├── firms_with_promos.json
│   │   ├── promos.json
│   │   ├── slides.json
│   │   ├── top_picks.json
│   │   └── top_picks_overrides.json
│   └── vendor/              # Third-party assets
│       └── bootstrap/
│
├── instance/                # Instance-specific data (SQLite dev database)
│   └── analytics.db         # Analytics database (development)
│
├── docs/                    # Project documentation
│   ├── README.md
│   ├── analytics/           # Analytics system documentation
│   │   ├── usage.md         # Usage guide and API reference
│   │   ├── production.md    # Production setup (Heroku, Postgres)
│   │   └── production.md    # Production setup (Heroku, Postgres)
│   ├── development/         # Development guides
│   │   ├── guides.md        # Guide system development
│   │   └── styles.md        # Sass/CSS development guide
│   ├── security.md          # Unified security guide (deployment + analytics)
│   └── deployment/          # Deployment documentation
│
├── .venv/                   # Python virtual environment
├── .vscode/                 # VS Code configuration
│   └── tasks.json          # Development tasks
│
└── README.md               # This file - project overview
```

## Requirements
- Python 3.8+ (tested with 3.10+, earlier versions 3.8+ should work)
- Node.js 16+ (for Sass compilation)
- PowerShell (for provided commands) / VS Code
- Git (for version control and deployment)

## Quick Start

### 1. Create & Activate Virtual Environment
From the project root:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```
If activation is blocked by policy:
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

### 2. Install Dependencies
```powershell
pip install -r requirements.txt
npm install  # Installs Bootstrap 5.3.3 and Sass 1.92.1
```

### 3. Run the App (Direct Python)
```powershell
.\.venv\Scripts\Activate.ps1
python app.py
```
Visit: http://127.0.0.1:5000/

### 4. Run the App (Flask CLI)
```powershell
.\.venv\Scripts\Activate.ps1
$env:FLASK_APP = "app.py"
$env:FLASK_ENV = "development"   # enables auto reload & debugger
flask run
```

### 5. VS Code Task Usage
Press: `Ctrl+Shift+P` → `Run Task...` → choose:
- `Flask: Run app.py (python)` OR
- `Flask: flask run (env vars)`

The second task keeps a background server using the Flask CLI.

### 6. Modifying Templates
- Add new pages: create `templates/yourpage.html` extending `base.html`.
- Add a route in `app.py`:
```python
@app.route('/about')
def about():
    return render_template('about.html')
```

### 7. Adding More Dependencies
Add to environment:
```powershell
pip install <package>
pip freeze > requirements.txt
```

### 8. Environment Variables (Optional Pattern)
Instead of hardcoding config, you can later use:
```python
import os
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-insecure')
```
Set in PowerShell before running:
```powershell
$env:SECRET_KEY = "some-secret"
```

### 9. Production Considerations
- Use a production WSGI server (e.g. `waitress`, `gunicorn` on Linux) instead of `app.run()`.
- Set `FLASK_ENV` (or `FLASK_DEBUG`) appropriately and avoid leaving debug mode enabled in production.
- Consider `.env` management via `python-dotenv`.

## 📚 Documentation

This project includes comprehensive documentation organized by topic in the [`docs/`](docs/) directory:

### Quick Access
- **📖 [Complete Documentation Index](docs/README.md)** - Start here for all documentation
- **🔧 [Guide System Documentation](docs/development/guides.md)** - Creating and managing SEO landing pages  
- **🎨 [Style Guide](docs/development/styles.md)** - SCSS architecture and component standards
- **📊 [Analytics Usage Guide](docs/analytics/usage.md)** - Understanding and using the analytics system
- **🚀 [Security Guide](docs/security.md)** - Comprehensive security hardening for deployment and analytics

### By Category
- **Analytics** (`docs/analytics/`) - Analytics system usage and production setup
- **Development** (`docs/development/`) - Guide system architecture, style guides, and coding standards  
- **Security** (`docs/security.md`) - Unified security guide for deployment and analytics

> **💡 Tip:** The documentation includes cross-references and examples. Start with the [Documentation Index](docs/README.md) to find what you need quickly.

## Guide System (SEO Landing Pages)

The project includes a scalable guide system for creating SEO-optimized landing pages:

### Base Template System
- **Shared Layout**: All guides extend `templates/guides/guide_base.html`
- **Smart Navigation**: Context-aware back links + always-available "Back to Guides" navigation
- **Consistent Structure**: Back Link → Header → Content → CTA → Back Link → FAQ → Keep Learning → Disclosure
- **Built-in SEO**: FAQ schema, breadcrumbs, meta descriptions, CSP nonce support
- **Analytics Ready**: Back link usage tracking for UX optimization
- **BEM Components**: Strict `.guide__*` naming with modifiers (e.g., `guide__faq-section--spacious`)

### Creating New Guides
1. Create a new template in `templates/guides/`:
```html
{% extends "guides/guide_base.html" %}

{% block guide_title %}Your Guide Title{% endblock %}
{% block guide_subtitle %}Brief description under title{% endblock %}
{% block meta_desc %}{{ meta_desc }}{% endblock %}

{% block faq_items %}[{
  "@type": "Question",
  "name": "Sample FAQ?",
  "acceptedAnswer": {
    "@type": "Answer",
    "text": "Answer for SEO schema"
  }
}]{% endblock %}

{% block guide_content %}
  <div class="guide__section">
    <h2 class="guide__section-title">How it Works</h2>
    <ol class="guide__steps">
      <li>First step with <a href="/link" class="text-link">inline link</a></li>
      <li>Second step</li>
    </ol>
  </div>
{% endblock %}

{% block faq_content %}
  <details class="guide__faq" role="group">
    <summary class="guide__faq__summary">
      <span class="h6 mb-0 d-inline-block">Common question?</span>
    </summary>
    <div class="guide__faq__content">
      Detailed answer here
    </div>
  </details>
{% endblock %}

{% block next_links %}
  <li class="guide__next__item">
    <a class="guide__next__link text-link--accent" href="/guides/related">Related Guide</a>
  </li>
{% endblock %}
```

2. Add route in `app.py`:
```python
@app.route("/guides/your-guide-slug")
def guide_your_guide_slug():
    return render_template(
        "guides/your-guide.html",
        title="SEO Page Title - Your Site",
        meta_desc="SEO meta description (150-160 chars)"
    )
```

### Styling System
- **Variables**: All guide styling centralized in `_variables.scss` with `$guide-*` prefix
- **Components**: BEM structure in `static/scss/layout/_guides.scss` with modifiers
- **Consistent Spacing**: 3rem section rhythm, responsive typography
- **Text Links**: Integrated `.text-link` and `.text-link--accent` system
- **Easy Theming**: Change colors/spacing globally via SCSS variables

## Privacy-Friendly Analytics

The application includes a comprehensive analytics system for tracking guide popularity while maintaining user privacy:

### 🚀 Core Features
- **Click Tracking**: Automatic guide click analytics with privacy-first design
- **Popular Guides Widget**: Server-rendered component showing trending content
- **JSON API**: RESTful endpoint for accessing analytics data anywhere in your app
- **Daily Rollup**: Automated data aggregation via Heroku Scheduler
- **Centralized Catalog**: Single source of truth for all guide metadata

### 📊 Data Collection
- **What we track**: Guide clicks, titles, and URLs for popularity ranking
- **What we DON'T track**: Personal information, IP addresses, cookies, or user accounts
- **Data stored**: Guide ID, title, timestamp, and truncated User-Agent (for bot filtering)
- **Retention**: Daily rollup with configurable data purging

### 🔒 Privacy Features
- **No PII**: No personally identifiable information is collected or stored
- **Bot filtering**: Automated traffic is filtered out using User-Agent patterns
- **Rate limiting**: Client-side deduplication prevents abuse (10 clicks/user/hour)
- **Local storage only**: Session data stays on user's device
- **CSP compliant**: All scripts in external files with nonce protection

### 🛠️ Technical Implementation
- **Database**: SQLite for development, Postgres for production (via `DATABASE_URL`)
- **Endpoints**: 
  - `/analytics/guide-click` (POST) - Record guide clicks
  - `/analytics/popular` (GET) - JSON API with rich metadata
  - `/analytics/maintenance/rollup` (POST) - Daily aggregation (admin only)
- **Client tracking**: Uses `navigator.sendBeacon` for reliable delivery during navigation
- **Popular indicators**: Shows 🔥 flame emoji for guides with 10+ clicks in 7 days
- **Widget Integration**: Reusable `popular_guides.html` component

### 🎯 Usage Examples

#### JSON API
```bash
# Get top 5 popular guides from last 30 days
curl "https://yoursite.com/analytics/popular?days=30&limit=5"

# Response includes full metadata
{
  "days": 30,
  "guides": [
    {
      "id": "what-is-a-prop-firm",
      "title": "What is a Prop Firm?",
      "href": "/guides/what-is-a-prop-firm",
      "group": "Beginner Basics",
      "clicks": 42
    }
  ]
}
```

#### Popular Guides Widget
```html
<!-- In any template -->
{% include 'components/popular_guides.html' %}
```

The system automatically highlights popular content and provides valuable insights while respecting user privacy.

## 11. Development Workflow

### Sass Compilation
The project uses automated Sass compilation via VS Code tasks:
```powershell
# Run Sass watch task (compiles SCSS to CSS automatically)
# In VS Code: Ctrl+Shift+P → "Run Task" → "Sass Watch"
```

### Flask Development Server
```powershell
# Run Flask dev server with auto-reload
# In VS Code: Ctrl+Shift+P → "Run Task" → "Flask Dev"
```

### Combined Development
```powershell
# Run both Sass watch and Flask server together
# In VS Code: Ctrl+Shift+P → "Run Task" → "Dev: Flask + Sass"
```

## 12. Production Deployment

### Environment Configuration
- Set `APP_ENV=production` in Heroku Config Vars
- Set `SECRET_KEY` to a secure random value
- Ensure all security headers are properly configured

### Heroku Deployment
```bash
# Deploy to Heroku (after setting up remote)
git push heroku main
```

## 13. Testing

### Simple Test That App Imports
Create `tests/test_basic.py` (future enhancement idea):
```python
def test_import():
    import app
    assert app.app is not None
```
Run (after installing pytest):
```powershell
pytest -q
```

## 14. Suggested Next Enhancements
- Add `README` badges & license
- Implement Blueprints for modularization  
- Add a `config.py` with multiple environments (Dev/Staging/Prod)
- Integrate a database (SQLite + SQLAlchemy)
- Add form handling with WTForms or Flask-WTF
- Add basic tests (`pytest` + `coverage`)
- Expand guide system with more landing pages
- Add admin dashboard for content management
- Implement user authentication and personalization
- Add analytics and tracking integration

## 15. Maintenance

### Deactivate Virtual Environment
```powershell
deactivate
```

### Git Notes
The `.gitignore` excludes `.venv/` and Python bytecode. Commit `requirements.txt` for dependency tracking.

### License
Consider adding a `LICENSE` file (e.g., MIT) if making this project public.

## 16. Component Updates

### Hero Carousel Animation
The hero carousel features a "slide in from the right" animation:

- **CSS**: `static/scss/components/_hero.scss` uses `transform: translateX(...)` with ~520ms transitions
- **JavaScript**: `static/js/components/hero.js` coordinates `.is-active` and `.is-exiting` classes
- **Navigation**: Rapid clicks are locked during transitions to prevent visual glitches

### Preview Changes
1. Ensure dev tasks are running (Sass watch + Flask dev)
2. Open `http://127.0.0.1:5000/` in browser
3. Observe auto-rotation or use next/prev arrows

---

**For additional help:** See `style_guide.md`, `security_checklist.md`, and `guide_system_docs.md`
