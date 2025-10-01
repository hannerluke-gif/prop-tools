# Prop Tools (Flask + Bootstrap + Guide System)

A comprehensive Flask project featuring a scalable guide system, modern Sass/BEM architecture, and production-ready security. Built for rapid prototyping and extension into larger applications.

## Table of Contents
- [Features](#features)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Quick Start](#quick-start)
- [📚 Documentation](#-documentation)
- [Guide System (SEO Landing Pages)](#guide-system-seo-landing-pages)
- [Development Workflow](#10-development-workflow)
- [Production Deployment](#11-production-deployment)
- [Testing](#12-testing)
- [Suggested Next Enhancements](#13-suggested-next-enhancements)
- [Maintenance](#14-maintenance)
- [Component Updates](#15-component-updates)

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
│   ├── README.md            # Documentation index
│   ├── VISION.md            # Product vision and strategic direction
│   ├── ROADMAP.md           # Implementation phases and timeline
│   ├── TECH-STACK.md        # Complete technology overview and architecture
│   ├── security.md          # Unified security guide (deployment + analytics)
│   ├── analytics/           # Analytics system documentation
│   │   ├── usage.md         # Usage guide and API reference
│   │   └── production.md    # Production setup (Heroku, Postgres)
│   ├── development/         # Development guides
│   │   ├── guides.md        # Guide system development
│   │   └── styles.md        # Sass/CSS development guide
│   └── maintenance/
│       └── project-cleanup.md # Maintenance tasks and cleanup tracking
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

Comprehensive documentation is organized in the [`docs/`](docs/) directory:

### 🚀 **Essential Docs**
- **📖 [Documentation Index](docs/README.md)** - Start here for all documentation
- **🎯 [Product Vision](docs/VISION.md)** - Strategic direction and competitive positioning  
- **🛠️ [Technical Stack](docs/TECH-STACK.md)** - Complete architecture and technology decisions

### � **Development Guides**
- **[Guide System](docs/development/guides.md)** - Creating SEO landing pages with templates and BEM
- **[Style Guide](docs/development/styles.md)** - SCSS architecture, component standards, button patterns

### 📊 **Analytics & Operations**
- **[Analytics Usage](docs/analytics/usage.md)** - Privacy-friendly tracking system and JSON API
- **[Security Guide](docs/security.md)** - Production hardening and deployment security

> **💡 Tip:** Start with the [Documentation Index](docs/README.md) to navigate by role (developer, analyst, stakeholder).

## Guide System (SEO Landing Pages)

The project includes a **scalable guide system** for creating SEO-optimized landing pages:

### ✅ **Key Features**
- **Shared Layout System**: All guides extend `templates/guides/guide_base.html`
- **Smart Navigation**: Context-aware back links with analytics tracking
- **Built-in SEO**: FAQ schema, breadcrumbs, meta descriptions
- **BEM Components**: Strict `.guide__*` naming with SCSS theming
- **Analytics Ready**: Popular guide indicators and click tracking

### 🚀 **Quick Start**
1. Create template in `templates/guides/your-guide.html` extending `guide_base.html`
2. Add route in `app.py` with title and meta_desc
3. Customize content blocks: `guide_content`, `faq_content`, `next_links`

> **📖 For complete guide system documentation:** See [Guide System Documentation](docs/development/guides.md) for detailed templates, BEM patterns, and styling guidelines.

## Privacy-Friendly Analytics

The application includes a **comprehensive analytics system** for tracking guide popularity while maintaining user privacy:

### ✅ **Core Features**
- **Click Tracking**: Automatic guide analytics with privacy-first design (no PII stored)
- **Popular Indicators**: 🔥 flame emoji for trending guides (10+ clicks in 7 days)
- **JSON API**: RESTful endpoints for accessing analytics data
- **Widget Integration**: Server-rendered `popular_guides.html` component

### � **Privacy-First Design**
- **What we track**: Guide clicks, titles, timestamps only
- **What we DON'T track**: Personal info, IP addresses, cookies, or user accounts
- **Bot filtering**: Automated traffic filtering with rate limiting
- **CSP compliant**: All scripts in external files with nonce protection

### 🛠️ **Quick Usage**
```html
<!-- Add popular guides widget to any template -->
{% include 'components/popular_guides.html' %}
```

```bash
# Get analytics data via JSON API
curl "https://yoursite.com/analytics/popular?days=30&limit=5"
```

> **📊 For complete analytics documentation:** See [Analytics Usage Guide](docs/analytics/usage.md) for detailed API reference, implementation examples, and production setup.

## 10. Development Workflow

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

## 11. Production Deployment

### Environment Configuration
- Set `APP_ENV=production` in Heroku Config Vars
- Set `SECRET_KEY` to a secure random value
- Ensure all security headers are properly configured

### Heroku Deployment
```bash
# Deploy to Heroku (after setting up remote)
git push heroku main
```

## 12. Testing

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

## 13. Suggested Next Enhancements
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

## 14. Maintenance

### Deactivate Virtual Environment
```powershell
deactivate
```

### Git Notes
The `.gitignore` excludes `.venv/` and Python bytecode. Commit `requirements.txt` for dependency tracking.

### License
Consider adding a `LICENSE` file (e.g., MIT) if making this project public.

## 15. Component Updates

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

**For additional help:** See the [complete documentation](docs/README.md) including technical guides, security hardening, and development standards.
