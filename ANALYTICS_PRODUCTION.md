# Analytics Production Deployment Guide

## Environment Setup

### Required Environment Variables
```bash
# Production Flask settings
APP_ENV=production
SECRET_KEY=your-secure-random-key-here

# Database (optional - defaults to SQLite)
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Analytics maintenance (required for data retention)
ADMIN_SECRET=your-secure-admin-secret-here

# Security (handled automatically in production)
# HTTPS redirect and security headers are auto-enabled when APP_ENV=production
```

### Database Setup

#### SQLite (Default - Good for small to medium traffic)
- Automatically creates `instance/analytics.db`
- Includes proper indexes for performance
- Thread-safe configuration enabled

#### PostgreSQL (Recommended for high traffic)
1. Set `DATABASE_URL` environment variable
2. Install psycopg: `pip install psycopg`
3. Tables and indexes created automatically on first request

### Performance Considerations

#### Current Optimizations
- ✅ Database indexes on `ts_utc` and `guide_id`
- ✅ Navigator.sendBeacon for reliable tracking
- ✅ Keepalive fetch fallback for older browsers
- ✅ Client-side rate limiting (3 clicks/minute/session)
- ✅ Bot filtering to reduce noise
- ✅ Input validation to prevent abuse

#### Scaling Recommendations
- **< 10k clicks/month**: SQLite is sufficient
- **10k-100k clicks/month**: Consider PostgreSQL
- **> 100k clicks/month**: Add connection pooling, read replicas

### Security Features

#### Privacy Protection
- ✅ No PII collection (no names, emails, IP addresses)
- ✅ No cookies required
- ✅ User-Agent truncated to 255 characters
- ✅ Only stores: guide_id, title, href, truncated UA, timestamp

#### Abuse Prevention
- ✅ Bot filtering (blocks crawlers, scrapers)
- ✅ Input validation (strict guide_id patterns)
- ✅ Rate limiting (client-side session-based)
- ✅ SQL injection protection (parameterized queries)
- ✅ XSS protection (no user input rendered without escaping)

### Monitoring

#### Key Metrics to Monitor
```sql
-- Top guides by clicks (last 30 days)
SELECT guide_id, COUNT(*) as clicks 
FROM guide_clicks 
WHERE ts_utc >= datetime('now', '-30 days') 
GROUP BY guide_id 
ORDER BY clicks DESC 
LIMIT 10;

-- Click volume by day
SELECT date(ts_utc) as day, COUNT(*) as clicks
FROM guide_clicks 
WHERE ts_utc >= datetime('now', '-7 days')
GROUP BY date(ts_utc)
ORDER BY day DESC;

-- Bot filtering effectiveness
SELECT 
  SUM(CASE WHEN ua LIKE '%bot%' OR ua LIKE '%spider%' OR ua LIKE '%crawl%' THEN 1 ELSE 0 END) as filtered,
  COUNT(*) as total
FROM guide_clicks 
WHERE ts_utc >= datetime('now', '-1 day');
```

#### Health Checks
- Monitor `/analytics/top-guides` endpoint response time
- Check database connection health
- Watch for unusual traffic spikes (potential abuse)

### Data Retention & Aggregation

#### Automated Daily Rollup
The system includes automatic data aggregation to keep the database lean:

- **Raw data**: Stored for up to 90 days
- **Daily summaries**: Stored indefinitely (much smaller footprint)
- **Automatic cleanup**: Old raw data is purged during rollup

#### Maintenance Endpoint
Daily maintenance is handled by the `/analytics/maintenance/rollup` endpoint:

```bash
# Manual rollup (for testing)
curl -X POST \
  -H "X-Admin-Secret: your-secure-admin-secret-here" \
  https://your-app.herokuapp.com/analytics/maintenance/rollup
```

#### Heroku Scheduler Setup
1. Add Heroku Scheduler addon: `heroku addons:create scheduler:standard`
2. Configure daily job:
```bash
heroku addons:open scheduler
# Add job: curl -X POST -H "X-Admin-Secret: $ADMIN_SECRET" https://your-app.herokuapp.com/analytics/maintenance/rollup
# Schedule: Daily at 02:00
```

#### GitHub Actions Alternative
```yaml
# .github/workflows/analytics-rollup.yml
name: Analytics Rollup
on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM UTC
jobs:
  rollup:
    runs-on: ubuntu-latest
    steps:
      - name: Trigger rollup
        run: |
          curl -X POST \
            -H "X-Admin-Secret: ${{ secrets.ADMIN_SECRET }}" \
            https://your-app.herokuapp.com/analytics/maintenance/rollup
```

#### Manual Cleanup (Fallback)
If automated rollup fails, manual cleanup script:
```python
# emergency_cleanup.py
import os
import requests

response = requests.post(
    f"{os.getenv('APP_URL')}/analytics/maintenance/rollup",
    headers={"X-Admin-Secret": os.getenv('ADMIN_SECRET')}
)
print(f"Rollup result: {response.json()}")
```

### Testing the Rollup System

#### Local Development Test
```bash
# Set environment variable
export ADMIN_SECRET="test-secret-123"

# Test rollup endpoint
curl -X POST \
  -H "X-Admin-Secret: test-secret-123" \
  http://localhost:5000/analytics/maintenance/rollup

# Expected response
{"ok": true, "aggregated_guides": 2, "purged_records": 0}
```

#### Production Validation
```bash
# Check if summary table exists (SQLite)
echo ".tables" | sqlite3 instance/analytics.db

# Check summary data
echo "SELECT * FROM guide_clicks_daily ORDER BY day DESC LIMIT 5;" | sqlite3 instance/analytics.db

# Monitor rollup success
heroku logs --tail | grep "Rollup complete"
```

### Troubleshooting

#### Common Issues
1. **ADMIN_SECRET not configured**: Set environment variable in production
2. **Rollup timing out**: Consider reducing retention period from 90 to 30 days
3. **High memory usage**: Ensure rollup is running daily to prevent data buildup
4. **Slow queries**: Verify both raw and summary table indexes exist
5. **Missing data**: Check bot filtering isn't too aggressive
6. **CORS errors**: Ensure same-origin requests only

#### Debug Mode
Set `FLASK_DEBUG=1` to see detailed analytics logging in development:
```
[INFO] Analytics recorded: what-is-a-prop-firm
[WARNING] Analytics validation failed: invalid_guide_id
[INFO] Rollup complete: 5 guides aggregated, 150 records purged
```

### Cost Estimates

#### Heroku Postgres
- **Hobby**: Free tier, good for development/testing
- **Basic**: $9/month, suitable for production up to 100k clicks/month
- **Standard**: $50/month+, for higher volume applications

#### Storage Requirements

**With Daily Rollup (Recommended)**:
- Daily summary: ~50 bytes per guide per day
- Raw data: 90-day retention (~6MB for 10k clicks/month)
- Long-term growth: ~20KB/month (summaries only)

**Without Rollup (Not Recommended)**:
- Raw data only: ~200 bytes per click record
- 10k clicks/month = ~2MB/month storage growth
- With 1-year retention: ~24MB total

**Performance Benefits**:
- Queries on summaries are 10-100x faster
- Database size stays manageable
- Backup/restore times remain reasonable