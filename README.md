# Prop Tools (Flask + Bootstrap + Guide System)

A comprehensive Flask project featuring a scalable guide system, modern Sass/BEM architecture, and production-ready security. Built for rapid prototyping and extension into larger applications.

## Table of Contents
- [Features](#features)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Quick Start](#quick-start)
- [Development Workflow](#development-workflow)
- [Guide System](#guide-system)
- [Production Deployment](#production-deployment)
- [Testing](#testing)
- [Maintenance](#maintenance)
- [Component Updates](#component-updates)

## Features
- **Flask app** with dashboard and SEO-optimized guide system
- **Guide System** with BEM components, schema markup, and responsive design
- **Modern Sass architecture** with Bootstrap 5 integration and design tokens
- **Security hardening** with CSP, HTTPS, and production-ready headers
- **VS Code integration** with tasks, Sass watch, and development workflow
- **Production deployment** ready for Heroku with proper configuration

## Project Structure
```
propfirm_bootstrap/
├── app.py                     # Flask application with routes & security
├── requirements.txt           # Python dependencies
├── Procfile                   # Heroku deployment config
├── package.json               # Node.js dependencies (Sass)
│
├── templates/
│   ├── base.html              # Main layout template
│   ├── dashboard.html         # Dashboard page
│   ├── 500.html              # Error page
│   └── guides/               # Guide system templates
│       ├── guide_base.html   # Shared guide layout
│       └── what-is-a-prop-firm.html  # Example guide page
│
├── static/
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
│   │   ├── main.js          # Entry point
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
│   │   ├── promos.json
│   │   └── slides.json
│   └── vendor/              # Third-party assets
│       └── bootstrap/
│
├── .venv/                   # Python virtual environment
├── .vscode/                 # VS Code configuration
│   └── tasks.json          # Development tasks
│
└── Documentation:
    ├── README.md            # This file
    ├── style_guide.md       # Development guidelines
    ├── security_checklist.md # Security review checklist
    └── guide_system_docs.md # Guide system documentation
```

## Requirements
- Python 3.10+ (earlier versions 3.8+ likely work, but not tested here)
- Node.js 16+ (for Sass compilation)
- PowerShell (for provided commands) / VS Code

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
npm install  # For Sass compilation
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

## Guide System (SEO Landing Pages)

The project includes a scalable guide system for creating SEO-optimized landing pages:

### Base Template System
- **Shared Layout**: All guides extend `templates/guides/guide_base.html`
- **Consistent Structure**: Header → Content → CTA (dual buttons) → FAQ → Keep Learning → Disclosure
- **Built-in SEO**: FAQ schema, breadcrumbs, meta descriptions, CSP nonce support
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
