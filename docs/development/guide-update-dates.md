# Guide Last Updated Dates

## Overview
Guide pages now display a subtle "Last updated" date at the bottom of each guide (after the disclosure statement). This helps with SEO trust signals and content freshness without cluttering the guides index page.

## Location
The update date appears on individual guide pages only, positioned after the disclosure text at the very bottom of the article.

**Example:**
```
Disclosure: Prop Tools partners with select firms...

Last updated: Sept 2025
```

## How to Update Dates

### Single Guide Update
To update the date for a specific guide, edit `guides_catalog.py`:

```python
"what-is-a-prop-firm": {
    "title": "What is a Prop Firm?",
    "href": "/guides/what-is-a-prop-firm",
    "group": "Beginner Basics",
    "updated": "Oct 2025",  # <-- Change this
},
```

### Bulk Update (All Guides)
To update the default date for all guides at once, modify the `DEFAULT_UPDATED` constant at the top of `guides_catalog.py`:

```python
# Default update date for all guides (can be overridden per-guide)
DEFAULT_UPDATED = "Oct 2025"  # <-- Change this
```

All guides inherit this default unless they have a specific `updated` value set.

### Date Format
- Use a simple, readable format: `"Sept 2025"`, `"Oct 2025"`, etc.
- Avoid overly precise dates (no need for exact days unless significant)
- Keep it consistent across all guides

## Implementation Details

### Files Modified
1. **`guides_catalog.py`**: Added `DEFAULT_UPDATED` constant and `updated` field to each guide
2. **`app.py`**: Updated all guide route handlers to fetch and pass `guide_updated` to templates
3. **`templates/guides/guide_base.html`**: Added conditional display of update date
4. **`static/scss/layout/_guides.scss`**: Added subtle styling for `.guide__updated`

### Why This Approach?
- **Centralized**: All dates managed in one place (`guides_catalog.py`)
- **Optional**: Guides without an `updated` value simply don't display the date
- **Non-intrusive**: Only shows on individual guides, not on the index page
- **SEO-friendly**: Provides freshness signal without being spammy

### Template Logic
The date only displays when `guide_updated` is passed to the template:
```jinja
{% if guide_updated %}
<p class="guide__updated text-muted small mt-3">
  Last updated: {{ guide_updated }}
</p>
{% endif %}
```

### Styling
The date uses subtle styling to maintain trust without drawing excessive attention:
- Small font size (0.813rem)
- Low opacity white text (40%)
- Normal font style (not italic like the disclosure)
- Left-aligned with modest top margin

## Best Practices

### When to Update Dates
1. **Major Content Revisions**: When you significantly rewrite or expand a guide
2. **Data Updates**: When firm information, products, or rules change
3. **Seasonal Reviews**: Quarterly or semi-annual freshness updates
4. **New Information**: When adding new sections or updating recommendations

### When NOT to Update
- Typo fixes or minor wording tweaks
- CSS/styling changes
- Link updates (unless substantial)
- Small clarifications

### Recommended Update Schedule
- **Quarterly bulk update**: Update `DEFAULT_UPDATED` every 3 months
- **Individual guide updates**: As content changes warrant
- **Major changes**: Update within 1 week of publishing changes

## Future Enhancements (Optional)
- Add `published` date field for original publication date
- Consider ISO date format for Schema.org markup
- Add "Updated" badge to guides index for recently updated guides
- Track update history for editorial purposes
