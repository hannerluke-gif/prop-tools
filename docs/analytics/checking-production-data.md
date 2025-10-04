# Checking Production Analytics Data

This guide explains how to view your live guide click analytics data stored in PostgreSQL on Heroku.

## Quick Summary

Your production data shows: **No clicks recorded yet** (the API returned `{"days":30,"guides":[],"limit":5}`)

## Method 1: Using the Analytics API (Easiest)

### View Popular Guides
```powershell
curl https://prop-tools-185f3549a96a.herokuapp.com/analytics/popular
```

**Response format:**
```json
{
  "days": 30,
  "guides": [
    {
      "guide_id": "/guides/what-is-a-prop-firm",
      "title": "What is a Prop Firm?",
      "clicks": 42,
      "score_30d": 42
    }
  ],
  "limit": 5
}
```

### Legacy Endpoint
```powershell
curl https://prop-tools-185f3549a96a.herokuapp.com/analytics/top-guides
```

---

## Method 2: Heroku CLI with SQL Queries (Most Powerful)

### Prerequisites

1. **Install Heroku CLI** (if not already installed):
   - Download from: https://devcenter.heroku.com/articles/heroku-cli

2. **Install PostgreSQL Tools** (psql):
   - Download from: https://www.postgresql.org/download/windows/
   - Or use: `choco install postgresql` (if you have Chocolatey)

### Common Queries

#### View Top Guides (Last 30 Days)
```powershell
heroku pg:psql postgresql-slippery-45720 --app prop-tools -c "SELECT guide_id, COUNT(*) as clicks FROM guide_clicks WHERE ts_utc >= NOW() - INTERVAL '30 days' GROUP BY guide_id ORDER BY clicks DESC LIMIT 10;"
```

#### View Daily Summary Table
```powershell
heroku pg:psql postgresql-slippery-45720 --app prop-tools -c "SELECT * FROM guide_clicks_daily ORDER BY day DESC LIMIT 10;"
```

#### Total Clicks (All Time)
```powershell
heroku pg:psql postgresql-slippery-45720 --app prop-tools -c "SELECT COUNT(*) as total_clicks FROM guide_clicks;"
```

#### Recent Clicks (Last 20)
```powershell
heroku pg:psql postgresql-slippery-45720 --app prop-tools -c "SELECT guide_id, guide_title, ts_utc FROM guide_clicks ORDER BY ts_utc DESC LIMIT 20;"
```

#### Clicks by Day (Last 7 Days)
```powershell
heroku pg:psql postgresql-slippery-45720 --app prop-tools -c "SELECT DATE(ts_utc) as day, COUNT(*) as clicks FROM guide_clicks WHERE ts_utc >= NOW() - INTERVAL '7 days' GROUP BY DATE(ts_utc) ORDER BY day DESC;"
```

---

## Method 3: Interactive PostgreSQL Session

### Start Interactive Session
```powershell
heroku pg:psql postgresql-slippery-45720 --app prop-tools
```

### Useful Commands Once Connected

```sql
-- List all tables
\dt

-- Show table structure
\d guide_clicks
\d guide_clicks_daily

-- View recent clicks
SELECT guide_id, guide_title, ts_utc 
FROM guide_clicks 
ORDER BY ts_utc DESC 
LIMIT 20;

-- Top guides last 30 days
SELECT guide_id, COUNT(*) as clicks 
FROM guide_clicks 
WHERE ts_utc >= NOW() - INTERVAL '30 days' 
GROUP BY guide_id 
ORDER BY clicks DESC;

-- Check if data exists
SELECT COUNT(*) FROM guide_clicks;

-- View daily aggregated data
SELECT * FROM guide_clicks_daily 
ORDER BY day DESC 
LIMIT 10;

-- Exit when done
\q
```

---

## Method 4: Heroku Dashboard (Web Interface)

1. Go to https://data.heroku.com/datastores/
2. Click on **postgresql-slippery-45720**
3. Navigate to the **Dataclips** tab
4. Create and save SQL queries for reuse
5. Share query results as links

**Advantages:**
- Visual interface
- Save queries for later
- Share results with team
- Schedule queries (paid plans)

---

## Understanding the Data

### Table: `guide_clicks`
Stores individual click events with:
- `id`: Auto-increment primary key
- `guide_id`: Guide identifier (e.g., "/guides/what-is-a-prop-firm")
- `guide_title`: Human-readable title
- `href`: Full URL path
- `ua`: Truncated user-agent string
- `ts_utc`: Timestamp (UTC)

### Table: `guide_clicks_daily`
Aggregated daily summary with:
- `guide_id`: Guide identifier
- `day`: Date (YYYY-MM-DD)
- `clicks`: Total clicks for that day
- Last updated: Daily via maintenance endpoint

---

## Data Retention Policy

- **Raw clicks**: Kept for 90 days, then auto-deleted
- **Daily summaries**: Kept indefinitely
- **Aggregation**: Runs daily via Heroku Scheduler

---

## Troubleshooting

### "psql command not found"
Install PostgreSQL client tools:
```powershell
# Using Chocolatey
choco install postgresql

# Or download from: https://www.postgresql.org/download/windows/
```

### "No data returned"
Check if analytics are being tracked:
1. Visit a guide page on your live site
2. Check browser console for analytics events
3. Wait a few minutes and query again

### "Permission denied"
Make sure you're authenticated with Heroku:
```powershell
heroku login
```

### Different timezone showing
All timestamps are stored in UTC. Convert if needed:
```sql
-- Convert to your local timezone (e.g., EST)
SELECT guide_id, ts_utc AT TIME ZONE 'America/New_York' as local_time
FROM guide_clicks
ORDER BY ts_utc DESC
LIMIT 10;
```

---

## Quick Reference Card

| What You Want | Command |
|---------------|---------|
| **Quick check** | `curl https://prop-tools-185f3549a96a.herokuapp.com/analytics/popular` |
| **Top 10 guides** | `heroku pg:psql postgresql-slippery-45720 --app prop-tools -c "SELECT guide_id, COUNT(*) as clicks FROM guide_clicks WHERE ts_utc >= NOW() - INTERVAL '30 days' GROUP BY guide_id ORDER BY clicks DESC LIMIT 10;"` |
| **Total count** | `heroku pg:psql postgresql-slippery-45720 --app prop-tools -c "SELECT COUNT(*) FROM guide_clicks;"` |
| **Interactive mode** | `heroku pg:psql postgresql-slippery-45720 --app prop-tools` |

---

## Related Documentation

- [Analytics Usage Guide](usage.md) - How the analytics system works
- [Production Deployment](production.md) - Environment setup and scaling
- [Heroku Postgres Docs](https://devcenter.heroku.com/articles/heroku-postgresql) - Official Heroku guide

---

## Notes

- ✅ Data persists across deployments (PostgreSQL is separate from app)
- ✅ No PII is collected (privacy-friendly)
- ✅ Bot traffic is automatically filtered
- ✅ Daily aggregation keeps database lean
