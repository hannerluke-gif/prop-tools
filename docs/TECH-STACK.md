# 🛠️ Technical Stack & Tools

**Current Architecture Overview**

This document provides a comprehensive overview of all technologies, tools, and services used in the Prop Tools platform.

---

## 🏗️ Core Architecture

### **Backend API**
- **Framework:** Flask 3.0+ (Python web framework)
- **Database:** 
  - **Development:** SQLite (local file-based)
  - **Production:** PostgreSQL (via Heroku Postgres)
- **Analytics Storage:** Custom SQLite/PostgreSQL schema with privacy-friendly design
- **API Pattern:** Server-side rendered with REST endpoints for analytics

### **Frontend**
- **CSS Framework:** Bootstrap 5.3.3
- **Preprocessor:** Sass 1.92.1 (SCSS syntax)
- **Architecture:** BEM (Block Element Modifier) component system
- **JavaScript:** Vanilla ES6+ with modular components
- **Build Process:** Sass compilation via npm scripts and VS Code tasks

### **Data Management**
- **Configuration:** JSON-based data files (`firms.json`, `promos.json`)
- **Content:** Jinja2 templates with Flask routing
- **Schema:** Custom analytics database with indexed queries
- **State Management:** Server-side sessions, client-side localStorage for preferences

---

## 🚀 Deployment & Infrastructure

### **Hosting**
- **Platform:** Heroku (Platform as a Service)
- **Environment:** Production app with config vars
- **Database:** Heroku Postgres addon
- **Static Assets:** Served via Heroku with WhiteNoise middleware

### **Security**
- **HTTPS:** Enforced redirects in production
- **Headers:** Content Security Policy (CSP), security headers
- **Secrets Management:** Heroku Config Vars
- **Session Security:** Flask secure sessions with proper configuration

### **Performance**
- **CDN:** Heroku routing (future: CloudFlare integration planned)
- **Caching:** Browser caching headers, static asset optimization
- **Database:** Indexed queries, connection pooling via SQLAlchemy

---

## 📊 Analytics & SEO Tools

### **Current Analytics Stack**
- **Custom Analytics:** Privacy-friendly Flask blueprint with:
  - Click tracking via `navigator.sendBeacon()`
  - Popular content identification
  - Bot filtering and rate limiting
- **Client Tracking:** `static/js/analytics.js` (CSP compliant)
- **Data Visualization:** Server-rendered popular guides widget

### **SEO & Content**
- **Schema Markup:** JSON-LD for FAQ rich snippets
- **Meta Management:** Dynamic meta descriptions, Open Graph tags
- **Sitemap:** Auto-generated XML sitemap from Flask routes
- **Performance:** Core Web Vitals optimization focus

### **Planned Analytics Integrations**
- **Google Analytics 4** - Comprehensive user behavior tracking
- **Google Search Console** - Search performance and indexing
- **Core Web Vitals** - Performance monitoring dashboard

---

## 🛠️ Development Tools

### **Local Development**
- **Runtime:** Python 3.8+ (recommended 3.10+)
- **Package Manager:** pip with virtual environments (.venv)
- **Node.js:** 16+ for Sass compilation
- **Editor:** VS Code with integrated tasks
- **Version Control:** Git with GitHub integration

### **Build & Automation**
- **Sass Compilation:** `sass --watch` via npm scripts
- **Flask Development:** Hot reload with `FLASK_ENV=development`
- **Task Runner:** VS Code tasks.json for unified workflow
- **Linting:** (Planned) flake8, black, isort for Python

### **VS Code Integration**
```json
{
  "Sass Watch": "sass --watch static/scss:static/css",
  "Flask Dev": "python app.py",
  "Dev: Flask + Sass": "Parallel execution of both"
}
```

---

## 📦 Dependency Management

### **Python Dependencies** (`requirements.txt`)
```python
Flask==3.0+           # Web framework
SQLAlchemy==2.0+      # Database ORM
psycopg==3.1+         # PostgreSQL adapter (production)
Werkzeug==3.0+        # WSGI utilities
```

### **Node.js Dependencies** (`package.json`)
```json
{
  "bootstrap": "5.3.3",    // CSS framework
  "sass": "1.92.1"         // CSS preprocessor
}
```

### **Browser Support**
- **Modern Browsers:** Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- **JavaScript:** ES6+ features with graceful degradation
- **CSS:** Modern flexbox, grid, custom properties with fallbacks

---

## 🔄 Alternative Architectures Considered

### **Original Core Idea Tools vs. Current Choice**

| **Category** | **Original Suggestion** | **Current Choice** | **Why** |
|--------------|------------------------|-------------------|---------|
| **Backend** | Flask or FastAPI | **Flask** | Mature ecosystem, simpler for server-rendered approach |
| **Frontend** | HTML/CSS + Tailwind or Bootstrap | **Bootstrap 5** | Rapid prototyping, comprehensive component library |
| **Hosting** | Vercel (frontend) + Render/Fly.io (API) | **Heroku** | Unified deployment, integrated Postgres, simpler config |
| **Database** | Not specified | **SQLite → PostgreSQL** | Easy development transition to production scaling |
| **Analytics** | Google Search Console, GA4 | **Custom + Planned GA4** | Privacy-first approach with external tool integration |

### **Future Architecture Evolution**

#### **Phase 2 Enhancements** (Q1-Q2 2026)
- **Frontend Framework:** Vue.js or React for interactive comparison tables
- **API Layer:** RESTful endpoints for mobile app support
- **Real-time Updates:** WebSocket or Server-Sent Events for live promo updates
- **Search:** Client-side search with Fuse.js or similar

#### **Phase 3 Scaling** (Q3-Q4 2026)
- **CDN:** CloudFlare for global performance
- **Monitoring:** DataDog or New Relic for application monitoring
- **Caching:** Redis for session storage and frequently accessed data
- **Load Balancing:** Multiple Heroku dynos with load distribution

---

## 🔧 Development Workflow

### **Local Development Setup**
1. **Python Environment:** `python -m venv .venv` + activation
2. **Dependencies:** `pip install -r requirements.txt`
3. **Node.js:** `npm install` for Sass compilation
4. **Database:** SQLite auto-created in `instance/` directory
5. **Development Server:** Flask dev server with hot reload

### **Production Deployment**
1. **Environment Variables:** Set via Heroku Config Vars
2. **Database Migration:** Automatic table creation on first request
3. **Static Assets:** Compiled Sass served via WhiteNoise
4. **Monitoring:** Heroku logs and metrics dashboard

### **Testing Strategy** (Planned)
- **Unit Tests:** pytest for core functionality
- **Integration Tests:** Flask test client for route testing
- **Performance Tests:** Lighthouse CI for Core Web Vitals
- **Security Tests:** OWASP ZAP for vulnerability scanning

---

## 📈 Monitoring & Maintenance

### **Current Monitoring**
- **Application:** Heroku application metrics
- **Database:** Heroku Postgres performance insights
- **Analytics:** Custom dashboard via Flask admin routes
- **Security:** Manual security header verification

### **Planned Monitoring Stack**
- **Performance:** Core Web Vitals tracking
- **Uptime:** Heroku status + external monitoring
- **Analytics:** GA4 integration with custom events
- **Error Tracking:** Sentry for application error monitoring

### **Maintenance Schedule**
- **Dependencies:** Monthly updates (documented in project-cleanup.md)
- **Security:** Quarterly security reviews
- **Performance:** Ongoing optimization based on Core Web Vitals
- **Content:** Regular guide updates and SEO optimization

---

## 🎯 Technology Decisions & Rationale

### **Why Flask over FastAPI?**
- **Server-side rendering:** Better for SEO-focused content
- **Mature ecosystem:** Extensive plugin ecosystem
- **Template integration:** Native Jinja2 support for guide system
- **Gradual scaling:** Easy to add API endpoints later

### **Why Bootstrap over Tailwind?**
- **Rapid development:** Pre-built components accelerate MVP
- **Component consistency:** Unified design system out of the box
- **BEM integration:** Works well with component-based architecture
- **Customization:** Sass variables allow full theme control

### **Why Heroku over Vercel/Render?**
- **Unified deployment:** Single platform for app + database
- **Postgres integration:** Seamless database provisioning
- **Config management:** Environment variables built-in
- **Scaling path:** Clear upgrade path for traffic growth

---

**This stack is optimized for rapid development, SEO performance, and gradual scaling while maintaining simplicity and developer productivity.**