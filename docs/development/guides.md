# 📚 Guide System Documentation

> Comprehensive documentation for the scalable guide/landing page system built with Flask + Jinja2 + Sass/BEM

## Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Creating New Guides](#creating-new-guides)
- [Available Template Blocks](#available-template-blocks)
- [BEM Class Reference](#bem-class-reference)
- [Styling Customization](#styling-customization)
- [SEO Best Practices](#seo-best-practices)
- [Troubleshooting](#troubleshooting)
- [Examples](#examples)
- [Migration from Legacy Guides](#migration-from-legacy-guides)

## Overview

The guide system provides a consistent, SEO-optimized framework for creating landing pages. All guides share a common structure while allowing flexible content customization through Jinja2 template blocks.

---

## Architecture

### 1. Base Template (`templates/guides/guide_base.html`)

**Provides consistent structure for all guides:**
- Smart back navigation (context-aware)
- Header with title and subtitle
- Horizontal divider
- Main content sections
- Call-to-action card
- Bottom back navigation (always "Back to Guides")
- FAQ section with schema markup
- "Keep Learning" navigation
- Disclosure/fine print

**Built-in SEO features:**
- FAQ schema for rich snippets
- Breadcrumb schema
- Meta description inheritance
- CSP nonce support

**Navigation Features:**
- **Smart top back link**: Context-aware navigation that links back to the previous guide when applicable
- **Bottom back link**: Always provides "← Back to Guides" after the CTA section
- **Analytics tracking**: Both back links are tracked separately for usage analysis
- **Fallback logic**: Safe referrer checking with same-origin validation

### 2. BEM Component System (`static/scss/layout/_guides.scss`)

**Strict BEM structure for maintainability:**
```scss
.guide                     // Root component
├── .guide__back-nav       // Top back navigation
├── .guide__back-nav-bottom// Bottom back navigation
├── .guide__back-link      // Back link styling
├── .guide__header         // Title + subtitle section
├── .guide__section        // Content sections
├── .guide__section-title  // Section headings
├── .guide__cta            // Call-to-action card
├── .guide__faq            // FAQ items
├── .guide__next           // Keep Learning section
└── .guide__disclosure     // Fine print
```

### 3. Centralized Variables (`static/scss/_variables.scss`)

**All guide styling controlled by variables:**
```scss
// Typography
$text-color: #f5f5f5
$guide-headline-size: clamp(1.6rem, 4vw, 2.2rem)
$guide-body-size: 1.05rem

// Spacing (3rem rhythm)
$guide-section-spacing: 3rem
$guide-content-spacing: 1.5rem

// Component-specific tokens
$guide-faq-padding: 1.25rem
$guide-cta-bg: rgba(255, 255, 255, 0.06)
$guide-next-link-padding: 0.5rem 0.75rem
```

---

## Creating New Guides

### Step 1: Create Template File

Create `templates/guides/your-guide-name.html`:

```html
{% extends "guides/guide_base.html" %}

{# Required blocks #}
{% block guide_title %}Your Guide Title{% endblock %}
{% block guide_subtitle %}
Brief description that appears under the title
{% endblock %}

{# SEO and Schema #}
{% block meta_desc %}{{ meta_desc }}{% endblock %}
{% block faq_items %}[{
  "@type": "Question",
  "name": "Sample FAQ question?",
  "acceptedAnswer": {
    "@type": "Answer", 
    "text": "FAQ answer for search engines"
  }
}]{% endblock %}

{# Main content sections #}
{% block guide_content %}
  <div class="guide__section">
    <h2 class="guide__section-title">How it Works</h2>
    <ol class="guide__steps">
      <li>First step in the process</li>
      <li>Second step with details</li>
      <li>Final step and outcome</li>
    </ol>
  </div>

  <div class="guide__section">
    <h2 class="guide__section-title">Key Points</h2>
    <ul class="guide__bullets">
      <li><strong>Point 1:</strong> Important detail</li>
      <li><strong>Point 2:</strong> Another key concept</li>
    </ul>
  </div>
{% endblock %}

{# FAQ section - can use guide__faq-section--spacious for extra spacing #}
{% block guide_faq %}
<div class="guide__faq-section guide__faq-section--spacious">
  <h2 class="guide__section-title">Common questions</h2>
  {% block faq_content %}
    <details class="guide__faq" role="group">
      <summary class="guide__faq__summary">
        <span class="h6 mb-0 d-inline-block">Your FAQ question?</span>
      </summary>
      <div class="guide__faq__content">
        Your detailed answer here. Can include HTML, links, buttons, etc.
        <div class="mt-3">
          <a href="/related-page" class="btn btn-sm btn-tertiary">Related Action</a>
        </div>
      </div>
    </details>
  {% endblock %}
</div>
{% endblock %}

{# Related guides navigation #}
{% block next_links %}
  <li class="guide__next__item">
    <a class="guide__next__link" href="/guides/related-guide-1">Related Guide 1</a>
  </li>
  <li class="guide__next__item">
    <a class="guide__next__link" href="/guides/related-guide-2">Related Guide 2</a>
  </li>
{% endblock %}

{# Optional: Customize CTA #}
{% block cta_title %}Ready to get started?{% endblock %}
{% block cta_text %}Custom call-to-action message{% endblock %}
{% block cta_link %}/custom-destination{% endblock %}
{% block cta_button %}Custom Button Text{% endblock %}
{% block cta_secondary_link %}/secondary-destination{% endblock %}
{% block cta_secondary_button %}Secondary Button Text{% endblock %}
```

### Step 2: Add Flask Route

Add to `app.py`:

```python
@app.route("/guides/your-guide-slug")
def guide_your_guide_slug():
    return render_template(
        "guides/your-guide-name.html",
        title="SEO Page Title - Your Site",
        meta_desc="SEO meta description for search engines (150-160 chars)"
    )
```

### Step 3: Test and Deploy

1. Run Flask dev server: `python app.py`
2. Visit: `http://127.0.0.1:5000/guides/your-guide-slug`
3. Validate HTML structure and responsive design
4. Test FAQ expand/collapse functionality
5. Verify schema markup with Google's Rich Results Test

---

## Available Template Blocks

### Required Blocks
- `guide_title` - Main page heading
- `guide_subtitle` - Descriptive text under title
- `guide_content` - Main content sections
- `faq_content` - FAQ items
- `next_links` - Related guide navigation

### Optional Blocks
- `meta_desc` - SEO meta description
- `faq_items` - JSON-LD FAQ schema
- `cta_title` - CTA card headline (default: "Ready to Start?")
- `cta_text` - CTA card description (default: "Compare top firms, pick your path, and start trading.")
- `cta_link` - Primary CTA button destination (default: "/compare")
- `cta_button` - Primary CTA button text (default: "Start Trading")
- `cta_secondary_link` - Secondary CTA button destination (default: "/")
- `cta_secondary_button` - Secondary CTA button text (default: "Compare Firms")
- `disclosure_text` - Custom disclosure text

### Advanced Customization
- `faq_schema` - Override entire FAQ schema block
- `guide_cta` - Replace entire CTA section
- `guide_faq` - Replace entire FAQ section

### Available Context Variables

All guide templates automatically have access to these context variables:

#### `guide_back` Dictionary
Smart back navigation data provided by the `_inject_guide_back()` context processor:
- `guide_back.href` - URL for the back link (empty if no back navigation should show)
- `guide_back.label` - Display text for the back link (e.g., "← Back to Guides" or "← Back to \"Guide Title\"")

**Usage in templates:**
```jinja2
{% if guide_back.href %}
  <a href="{{ guide_back.href }}">{{ guide_back.label }}</a>
{% endif %}
```

**Logic:**
- **Context-aware**: If user came from another guide, links back to that specific guide
- **Safe fallback**: Always defaults to "← Back to Guides" if no valid referrer
- **Same-origin only**: Only links back to same-domain referrers for security
- **Analytics ready**: Back links include `guide-back__link` class for tracking
- `guide_next` - Replace entire Keep Learning section
- `guide_disclosure` - Replace disclosure section

---

## BEM Class Reference

### Layout Components
```html
<div class="guide">                          <!-- Root component -->
  <header class="guide__header">             <!-- Title section -->
    <h1 class="guide__title">Title</h1>
    <p class="guide__subtitle">Subtitle</p>
  </header>
  
  <div class="guide__section">               <!-- Content section -->
    <h2 class="guide__section-title">Section</h2>
    <ol class="guide__steps">                <!-- Numbered list -->
      <li>Step item</li>
    </ol>
    <ul class="guide__bullets">              <!-- Bullet list -->
      <li>Bullet item</li>
    </ul>
  </div>
</div>
```

### Interactive Components
```html
<!-- CTA Card -->
<div class="guide__cta">
  <div class="d-flex flex-column flex-md-row align-items-md-center gap-3">
    <div class="flex-grow-1">
      <h3 class="guide__cta__title h5">CTA Title</h3>
      <p class="guide__cta__text">CTA description</p>
    </div>
    <div class="d-flex flex-column flex-sm-row gap-3">
      <a href="/primary-link" class="btn btn-primary">Primary Button</a>
      <a href="/secondary-link" class="btn btn-secondary">Secondary Button</a>
    </div>
  </div>
</div>

<!-- FAQ Item -->
<details class="guide__faq" role="group">
  <summary class="guide__faq__summary">
    <span class="h6 mb-0 d-inline-block">Question?</span>
  </summary>
  <div class="guide__faq__content">
    Answer content
    <div class="mt-3">
      <a href="/related-action" class="btn btn-sm btn-tertiary">Related Action</a>
    </div>
  </div>
</details>

<!-- Keep Learning Navigation -->
<nav class="guide__next" aria-label="Related guide links">
  <h2 class="guide__next__title">Keep learning</h2>
  <ul class="guide__next__list">
    <li class="guide__next__item">
      <a class="guide__next__link text-link--accent" href="/guide">Related Guide</a>
    </li>
  </ul>
</nav>
```

### Utility Components
```html
<hr class="guide__divider">                 <!-- Section divider -->
<p class="guide__disclosure">Fine print</p>  <!-- Disclosure text -->

<!-- FAQ Section with modifier for extra spacing -->
<div class="guide__faq-section guide__faq-section--spacious">
  <!-- FAQ content -->
</div>
```

---

## Styling Customization

### Global Theme Changes

Edit `static/scss/_variables.scss`:

```scss
// Change all guide text color
$text-color: #ffffff; // Pure white instead of off-white

// Adjust section spacing
$guide-section-spacing: 4rem; // More space between sections

// Modify FAQ styling
$guide-faq-divider: rgba(255, 255, 255, 0.4); // Stronger dividers
$guide-faq-hover-color: #00ff88; // Different accent color
```

### Component-Specific Changes

Edit `static/scss/layout/_guides.scss`:

```scss
.guide {
  // Override specific component styling
  &__cta {
    border-radius: 1rem; // More rounded CTA cards
    padding: 2rem; // More padding
  }
  
  &__faq__summary {
    font-size: 1.1rem; // Larger FAQ questions
    
    &::before {
      font-size: 0.9rem; // Larger disclosure arrow
    }
  }
  
  &__next__link {
    padding: 0.75rem 1rem; // More generous link padding
  }
}
```

---

## SEO Best Practices

### Schema Markup
- FAQ schema automatically generated from `faq_items` block
- Breadcrumb schema includes proper site navigation
- Use descriptive FAQ questions and complete answers

### Meta Data
- Keep meta descriptions 150-160 characters
- Use unique, descriptive page titles
- Include target keywords naturally

### Content Structure
- Use semantic HTML5 elements (`<section>`, `<article>`, `<nav>`)
- Maintain heading hierarchy (H1 → H2 → H3)
- Include internal links to related guides

### Performance
- CSS compiled and minified via Sass
- Images optimized and properly sized
- Minimal JavaScript for better Core Web Vitals

---

## Troubleshooting

### Common Issues

**Sass compilation errors:**
- Check variable names match `_variables.scss` exactly
- Ensure BEM nesting doesn't exceed 3 levels deep
- Verify all SCSS files end with newline

**Template inheritance errors:**
- Confirm template extends `guides/guide_base.html`
- Check all block names match exactly (case-sensitive)
- Ensure Jinja2 syntax is correct (no missing `%}`)
- Remember the CTA section has both primary and secondary button blocks

**FAQ schema validation:**
- Use Google's Rich Results Test tool
- Ensure JSON-LD is valid (no trailing commas)
- Include both question and answer in schema

**Route conflicts:**
- Use unique route paths for each guide
- Follow consistent URL slug naming (kebab-case)
- Test routes with Flask's URL routing debugger

### Development Tips

1. **Use browser dev tools** to inspect BEM classes and spacing
2. **Test responsive design** at mobile, tablet, and desktop breakpoints  
3. **Validate HTML** with W3C validator for semantic correctness
4. **Check accessibility** with screen reader simulation
5. **Monitor Core Web Vitals** with Lighthouse audits

---

## Examples

See `templates/guides/what-is-a-prop-firm.html` for a complete working example demonstrating all system features.

---

## Migration from Legacy Guides

If you have existing guide pages not using this system:

1. **Create new template** extending `guide_base.html`
2. **Copy content** into appropriate template blocks
3. **Replace utility classes** with BEM classes
4. **Add FAQ schema** for SEO benefits
5. **Test thoroughly** before removing old template
6. **Update internal links** to use new BEM navigation

The system is designed to be backwards-compatible, so migration can be done incrementally.