# Analytics System Usage Guide

## Overview
The analytics system tracks guide clicks with privacy-friendly methods, displays popularity indicators, and provides admin insights. Here's how to use everything we implemented.

## 🚀 Quick Start

### 1. System is Already Running
If your Flask dev server is running, the analytics system is already active:
- Guide click tracking happens automatically when users click guide links
- Popular guides show flame indicators (🔥) on the guides index page
- Data is stored in your database and aggregated daily

### 2. Verify It's Working
Visit your guides page: `http://localhost:5000/guides/`
- Click on any guide link
- Check browser dev tools Network tab - you should see analytics requests
- Popular guides will show flame emojis

## 📊 User Experience Features

### Automatic Click Tracking
- **What happens**: When users click guide links or back navigation, analytics data is automatically sent
- **Method**: Uses `navigator.sendBeacon()` for reliability during page navigation
- **Fallback**: Falls back to regular fetch if sendBeacon isn't available
- **Rate limiting**: Max 10 clicks per user per hour to prevent abuse

### Back Link Navigation Analytics
- **Smart back links**: Context-aware navigation that links back to the previous guide when applicable
- **Fallback navigation**: Always provides "Back to Guides" option when no context is available
- **Tracking**: Separately tracks back link usage vs. "Keep Learning" link usage
- **Analytics data**: 
  - `back_context`: Smart contextual back links (e.g., "← Back to What is Futures Trading?")
  - `back_index`: Direct back to guides index (e.g., "← Back to Guides")

### Popularity Indicators
- **Visual cue**: Popular guides show 🔥 emoji next to the title
- **Threshold**: Guides with 10+ clicks in the past 7 days are marked as popular
- **Real-time**: Updates based on actual user engagement

### Popular Guides Widget
- **Component**: Reusable server-rendered widget displaying trending guides
- **Location**: Appears on guides index page and can be added to any template
- **Display**: Shows guide titles with click counts and responsive styling
- **Auto-updating**: Refreshes with each page load based on current analytics data

#### Using the Widget
```html
<!-- In any template -->
{% include 'components/popular_guides.html' %}
```

**Required Context** (add to your route):
```python
# In your Flask route function
popular_guides = get_popular_guides_widget(days=30, limit=5)
return render_template('your_template.html', popular_guides=popular_guides)
```

### Centralized Guides Catalog
All guide definitions are managed in `guides_catalog.py` for consistency:

**Key Features**:
- **Single source of truth**: All guide metadata in one place
- **Rich metadata**: IDs, titles, URLs, groupings, and descriptions
- **Helper functions**: Easy access via `get_guide_by_id()`, `get_guides_by_group()`
- **API integration**: Powers the enhanced JSON responses

**Usage Example**:
```python
from guides_catalog import get_guide_by_id, get_all_guides

# Get specific guide metadata
guide = get_guide_by_id('what-is-a-prop-firm')
print(f"{guide['title']} -> {guide['href']}")

# Get all guides by category
beginner_guides = get_guides_by_group('Beginner Basics')
```

## 🔧 Admin/Developer Features

### View Analytics Data

#### Popular Guides JSON API (Recommended)
```bash
# Get top 5 popular guides from last 30 days with full metadata
curl "http://localhost:5000/analytics/popular?days=30&limit=5"

# Get top 3 guides from last 7 days
curl "http://localhost:5000/analytics/popular?days=7&limit=3"

# PowerShell version
$response = Invoke-RestMethod -Uri "http://localhost:5000/analytics/popular?days=30&limit=5" -Method Get
$response.guides | ForEach-Object { Write-Host "$($_.title): $($_.clicks) clicks ($($_.group))" }
```

**Enhanced Response Format** (includes full metadata):
```json
{
  "days": 30,
  "limit": 5,
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

#### Legacy Top Guides API (Simple)
```bash
# Get top guides for last 7 days (default) - simple format
curl http://localhost:5000/analytics/top-guides

# Get top guides for specific time period
curl "http://localhost:5000/analytics/top-guides?days=30"

# PowerShell version
$response = Invoke-RestMethod -Uri "http://localhost:5000/analytics/top-guides?days=30" -Method Get
$response.guides | ForEach-Object { Write-Host "$($_.guide_id): $($_.clicks) clicks" }
```

#### Response Format
```json
{
  "guides": [
    {
      "guide_id": "what-is-a-prop-firm",
      "guide_title": "What is a Prop Firm?",
      "clicks": 45,
      "rank": 1
    }
  ],
  "period_days": 7,
  "total_guides": 3
}
```

### Database Maintenance

#### Daily Rollup (Aggregation)
Run this daily to keep your database lean:
```bash
# Trigger manual rollup
curl -X POST http://localhost:5000/analytics/maintenance/rollup

# PowerShell version
Invoke-RestMethod -Uri "http://localhost:5000/analytics/maintenance/rollup" -Method POST
```

**What it does**:
- Aggregates individual clicks into daily summaries
- Removes individual click records older than 30 days
- Keeps summary data for historical analysis
- Should be run via cron job in production

#### Check Database Tables
```sql
-- Individual clicks (recent data)
SELECT guide_id, guide_title, COUNT(*) as clicks 
FROM guide_clicks 
WHERE timestamp > datetime('now', '-7 days')
GROUP BY guide_id, guide_title
ORDER BY clicks DESC;

-- Aggregated summaries (historical data)
SELECT guide_id, guide_title, SUM(click_count) as total_clicks
FROM guide_click_summaries 
WHERE date > date('now', '-30 days')
GROUP BY guide_id, guide_title
ORDER BY total_clicks DESC;
```

## 🛡️ Security Features

### Bot Protection
- **User-Agent filtering**: Blocks common bot patterns
- **Rate limiting**: Max 10 clicks per IP per hour
- **Validation**: All inputs validated and sanitized

### Privacy Protection
- **No personal data**: Only tracks guide IDs and anonymous clicks
- **No cookies**: Uses localStorage for rate limiting only
- **CSP compliant**: All JavaScript is CSP-safe

## 📈 Production Deployment

### Environment Variables
Set these in production:
```bash
# Required for admin endpoints
ANALYTICS_ADMIN_KEY=your-secure-random-key

# Database (Heroku sets this automatically)
DATABASE_URL=postgresql://...
```

### Heroku Deployment
1. **Set admin key**:
   ```bash
   heroku config:set ANALYTICS_ADMIN_KEY=$(openssl rand -hex 32)
   ```

2. **Set up daily rollup**:
   ```bash
   # Add Heroku Scheduler addon
   heroku addons:create scheduler:standard
   
   # Configure daily job
   heroku addons:open scheduler
   # Add job: curl -X POST https://yourapp.herokuapp.com/analytics/maintenance/rollup
   ```

3. **Monitor logs**:
   ```bash
   heroku logs --tail | grep analytics
   ```

## 🔍 Monitoring & Troubleshooting

### Check System Health
```bash
# Test guide click endpoint
curl -X POST http://localhost:5000/analytics/guide-click \
  -H "Content-Type: application/json" \
  -d '{"guide_id": "test", "guide_title": "Test Guide", "href": "/guides/test"}'

# Test back link click endpoint
curl -X POST http://localhost:5000/analytics/guide-back-click \
  -H "Content-Type: application/json" \
  -d '{"guide_id": "back_context", "guide_title": "← Back to Test Guide", "href": "/guides"}'

curl -X POST http://localhost:5000/analytics/guide-back-click \
  -H "Content-Type: application/json" \
  -d '{"guide_id": "back_index", "guide_title": "← Back to Guides", "href": "/guides"}'

# Should return: {"ok": true}
```

### Common Issues

#### No flame indicators showing
- Check if guides have enough clicks: `curl http://localhost:5000/analytics/popular`
- Verify database has data: check `guide_clicks` table
- Ensure popularity threshold is met (10+ clicks in 7 days)

#### Analytics requests failing
- Check browser console for errors
- Verify Content Security Policy allows analytics requests
- Check rate limiting (max 10 clicks per hour per user)

#### Bot requests getting through
- Review bot patterns in `analytics.py`
- Check logs for suspicious User-Agent strings
- Adjust rate limiting if needed

### View Raw Data
```python
# In Flask shell or Python script
from app import app, get_db_connection

with app.app_context():
    conn = get_db_connection()
    
    # Recent clicks
    clicks = conn.execute("""
        SELECT * FROM guide_clicks 
        WHERE timestamp > datetime('now', '-1 day')
        ORDER BY timestamp DESC
    """).fetchall()
    
    # Popular guides
    popular = conn.execute("""
        SELECT guide_id, guide_title, COUNT(*) as clicks
        FROM guide_clicks 
        WHERE timestamp > datetime('now', '-7 days')
        GROUP BY guide_id, guide_title
        HAVING COUNT(*) >= 10
        ORDER BY clicks DESC
    """).fetchall()
    
    conn.close()
```

## 📋 Regular Maintenance Tasks

### Daily (Automated)
- Run rollup aggregation to clean old data
- Monitor error logs for issues

### Weekly (Manual)
- Review top guides analytics
- Check for new bot patterns in logs
- Verify flame indicators are showing correctly

### Monthly (Manual)
- Review overall analytics trends
- Clean up any test data
- Update bot filtering patterns if needed

## 🎯 Advanced Usage

### Custom Analytics Queries
```python
# Get click trends over time
def get_click_trends(days=30):
    conn = get_db_connection()
    
    # Combine recent clicks with historical summaries
    trends = conn.execute("""
        SELECT DATE(timestamp) as date, COUNT(*) as clicks
        FROM guide_clicks 
        WHERE timestamp > datetime('now', '-{} days')
        GROUP BY DATE(timestamp)
        
        UNION ALL
        
        SELECT date, SUM(click_count) as clicks
        FROM guide_click_summaries
        WHERE date > date('now', '-{} days')
        AND date < date('now', '-30 days')
        GROUP BY date
        
        ORDER BY date DESC
    """.format(days, days)).fetchall()
    
    conn.close()
    return trends
```

### Integration with Other Systems
The analytics system provides a simple REST API that can be integrated with:
- Business intelligence tools
- Marketing analytics platforms  
- Content management systems
- A/B testing frameworks

## ✅ Verification Checklist

Before going live, verify:
- [ ] Guide clicks are being tracked
- [ ] Popular guides show flame indicators
- [ ] Bot requests are being filtered
- [ ] Rate limiting is working
- [ ] Daily rollup is scheduled
- [ ] Admin endpoints are secured
- [ ] Database is optimized
- [ ] Monitoring is set up

---

## 🎨 Popular Guides Widget & API

### JSON API Endpoint
**Endpoint:** `/analytics/popular`

**Parameters:**
- `days` (optional): Time window in days (default: 30, max: 365)
- `limit` (optional): Maximum number of guides (default: 5, max: 20)

**Example Usage:**
```bash
curl "https://proptradetools.com/analytics/popular?days=7&limit=5"
```

**Response:**
```json
{
  "days": 7,
  "limit": 5,
  "guides": [
    {
      "id": "what-is-a-prop-firm",
      "clicks": 42
    },
    {
      "id": "best-account-size-to-start", 
      "clicks": 28
    }
  ]
}
```

### Server-Rendered Widget
**Template:** `components/popular_guides.html`

**Usage in any template:**
```html
<!-- Include the widget -->
{% include 'components/popular_guides.html' %}
```

**Required context:**
```python
# In your route function
popular_guides = get_popular_guides_widget(days=30, limit=5)
return render_template('your_template.html', popular_guides=popular_guides)
```

### Implementation Details

**Backend Functions:**
- **`top_guides_simple(days, limit)`** - Lightweight query function using daily summary tables
- **`get_popular_guides_widget(days, limit)`** - Formats data for template consumption with titles and URLs

**Frontend Integration:**
- Analytics tracking: All guide links automatically tracked via `main.js`
- Styling: Bootstrap-compatible CSS in `_popular-guides.scss`
- Responsive design with dark mode support

**Data Flow:**
1. Click tracking → `/analytics/guide-click`
2. Storage in `guide_clicks` table
3. Daily rollup to `guide_clicks_daily`
4. Widget queries optimized combined data
5. Display with click counts and hover effects

## Support
If you encounter issues:
1. Check the troubleshooting section above
2. Review the security guide for configuration
3. Check application logs for specific error messages
4. Verify all environment variables are set correctly

The system is designed to fail gracefully - if analytics fail, your main application continues working normally.