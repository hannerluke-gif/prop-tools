# Button Spacing Guide

## Multiple Buttons in FAQ Sections

When you have multiple buttons in FAQ content sections, always use the proper flexbox spacing pattern:

### ✅ Correct Pattern
```html
<div class="mt-3 d-flex flex-wrap gap-3">
  <a href="/link1" class="btn btn-sm btn-tertiary">Primary Action</a>
  <a href="/link2" class="btn btn-sm btn-secondary">Secondary Action</a>
</div>
```

### ❌ Incorrect Pattern
```html
<div class="mt-3">
  <a href="/link1" class="btn btn-sm btn-tertiary">Primary Action</a>
  <a href="/link2" class="btn btn-sm btn-secondary">Secondary Action</a>
</div>
```

## Key Classes Explained

- `d-flex` - Creates flexbox container
- `flex-wrap` - Allows buttons to wrap on smaller screens
- `gap-3` - Bootstrap utility for consistent spacing between buttons
- `mt-3` - Standard top margin for button containers in FAQ sections

## Examples in Codebase

1. **what-is-a-prop-firm.html** - FAQ section "Personal account vs. prop account"
2. **futures-trading-products.html** - FAQ section "What are the most popular futures for beginners?"

## CTA Section Pattern

The main CTA section uses a more complex pattern for different screen sizes:

```html
<div class="d-flex flex-column flex-sm-row gap-3 flex-shrink-0">
  <a href="/primary" class="btn btn-primary">Primary Action</a>
  <a href="/secondary" class="btn btn-secondary">Secondary Action</a>
</div>
```

This ensures proper stacking on mobile and side-by-side layout on larger screens.