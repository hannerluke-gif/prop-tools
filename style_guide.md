* ### 📌 Project Style Guide (Flask + Bootstrap + Sass)
**When adding new components or styles, follow these rules:**
1. **SCSS partials**
   * Create new SCSS files in `static/scss/components/` (or `layout/` for global structures).
   * Prefix filenames with `_` (e.g. `_account-card.scss`).
2. **Import order**
   * Import partials in `main.scss` *after* the Bootstrap import.
   * Keep them organized by section:
     // Layout
     @import "layout/header";
     @import "layout/footer";
     // Components
     @import "components/promo-banner";
     @import "components/hero";
     @import "components/dashboard";
     @import "components/account-card"; // new
     ```
3. **Scope styles**
   * Wrap everything under a unique wrapper class (e.g. `.account-card`, `.promo-banner`).
   * Use **BEM-ish** children (e.g. `&__title`, `&__cta`).
   * Never write raw global selectors like `h1` or `.btn` unless intentional.
   * **Exception**: The `.hero` component uses global selectors (`.hero-slide`, `.hero-headline`, etc.) for legacy compatibility. New components must follow strict BEM patterns.
4. **No overrides / no `!important`**
   * Use `_variables.scss` and `_maps.scss` (before Bootstrap import) for global changes (colors, spacing, fonts).
   * Never override Bootstrap defaults in partials.
   * **Exception**: Bootstrap integration overrides may require `!important` in rare cases where CSS specificity conflicts cannot be resolved through proper variable usage.
5. **HTML usage**
   * Apply the wrapper class to the root element of the component in its Jinja/HTML template.
   * Use Bootstrap utilities (`d-flex`, `gap-3`, `mb-4`) for spacing/layout in templates whenever possible.
6. **JavaScript**
   * Add interactive behavior in `static/js/main.js`.
   * Use `{% block scripts %}` in `base.html` for page-specific scripts.
   
   ### 📌 JavaScript Organization

   1. **Entry file stays tiny**  
      * Keep `static/js/main.js` as the single entry point.  
      * It should only `import` modules and run their `init*()` functions on `DOMContentLoaded`.

   2. **One component = one module**  
      * Place feature-specific logic in `static/js/components/` (e.g. `promoBanner.js`, `siteBannerSearch.js`).  
      * Each module must export a single `init*()` function that safely no-ops if the target element is not present.

   3. **Utilities**  
      * Put shared helpers (DOM selectors, breakpoints, timers) in `static/js/utils/`.  
      * Keep utilities pure: no DOM queries inside helpers.

   4. **Page-specific scripts**  
      * If a page has unique logic, create a file in `static/js/pages/` and load it in that template using `{% block scripts %}`.  
      * These can also be ES modules if they need imports.

   5. **Coding conventions**  
      * Always use ES modules (`export` / `import`)—no globals or `window.*`.  
      * Use `const`/`let`, never `var`.  
      * Add JSDoc comments to all exported `init*()` functions.  
      * Guard DOM queries with early returns so code is safe on pages without the element.  
      * Event listeners must be idempotent (avoid duplicates on re-init).

   6. **Loading**  
      * Load `main.js` in `base.html` once with:  
      ```html
      <script type="module" src="{{ url_for('static', filename='js/main.js') }}"></script>
      ```
      * Page-specific scripts may also be loaded as modules through `{% block scripts %}`.

   ### 📌 New Component Standards (Strict BEM)

   **For all NEW components created after September 2025, follow these strict patterns:**

   1. **SCSS Structure**
      ```scss
      .my-new-component {
        // Component root styles
        
        &__element {
          // Direct child element
        }
        
        &__element--modifier {
          // Element with modifier
        }
        
        &--variant {
          // Component variant
        }
        
        // State classes
        &.is-active,
        &.is-loading {
          // State-based styling
        }
      }
      ```

   2. **HTML Structure**
      ```html
      <div class="my-new-component">
        <div class="my-new-component__header">
          <h3 class="my-new-component__title">Title</h3>
          <button class="my-new-component__close-btn">×</button>
        </div>
        <div class="my-new-component__body">
          <p class="my-new-component__text">Content here</p>
          <button class="my-new-component__cta my-new-component__cta--primary">
            Action
          </button>
        </div>
      </div>
      ```

   3. **JavaScript Integration**
      ```javascript
      // static/js/components/myNewComponent.js
      export function initMyNewComponent(root = document.querySelector('.my-new-component')) {
        if (!root) return () => {};
        
        const title = root.querySelector('.my-new-component__title');
        const cta = root.querySelector('.my-new-component__cta');
        
        // Component logic here
      }
      ```

   4. **Prohibited Patterns**
      * ❌ Global selectors: `.my-component-title` (should be `&__title`)
      * ❌ Nested components: `.my-component .other-component` (use composition)
      * ❌ Utility overrides: `.my-component .btn { !important }` (use variables)
      * ❌ Bootstrap class modifications: `.my-component .form-control` (use custom classes)

   **Legacy Exception**: The existing `.hero` component predates these standards and uses global selectors for historical reasons. Do not replicate this pattern in new components.

---

### 📌 Debug Code & Cleanup Guidelines

**Debug and development-only code must be removed before production:**

1. **Debug Components**
   * Never commit debug-specific SCSS files (like `_debug.scss`) to production branches
   * Remove debug imports from `main.scss` before production deployment
   * Use clear naming conventions for debug files (prefix with `debug-` or `_debug`)

2. **HTML Debug Elements**
   * Remove all debug spacers, test content, and temporary elements from templates
   * Use HTML comments to mark debug sections: `{# DEBUG: description #}`
   * Always clean up debug comments before production

3. **CSS Debug Styles**
   * Debug styles should be in separate files, not mixed with production components
   * Use obvious class names like `.debug-spacer`, `.debug-outline`
   * Never leave debug styles in production CSS builds

4. **JavaScript Debug Code**
   * Remove `console.log()` statements except for legitimate error logging
   * Clean up test functions and temporary event handlers
   * Use `// DEBUG:` comments for easy identification and removal

5. **Pre-deployment Checklist**
   * Search codebase for `DEBUG`, `debug-`, `console.log`
   * Verify no debug imports in `main.scss`
   * Run `npm run build` to ensure clean compilation
   * Test production build without debug assets