# analytics.py - Privacy-friendly guide click analytics
from flask import Blueprint, request, jsonify, current_app, g
from datetime import datetime, timezone, timedelta
import sqlite3
import os
import re
import json
import sys

# Import guides catalog - handle import path for blueprints
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from guides_catalog import get_guide_by_id

analytics_bp = Blueprint('analytics', __name__, url_prefix='/analytics')

# Validation patterns
SLUG_RE = re.compile(r'^[a-z0-9\-]+$')  # "what-is-a-prop-firm"
BOT_UA_RE = re.compile(r'bot|spider|crawl|scraper|facebookexternalhit|twitterbot', re.IGNORECASE)

# Limits for input validation
MAX_GUIDE_ID_LENGTH = 100
MAX_TITLE_LENGTH = 200
MAX_HREF_LENGTH = 300
MAX_UA_LENGTH = 255

def _is_sqlite(url: str) -> bool:
    return not url or url.startswith('sqlite:')

def get_db():
    """
    Returns a connection bound to the request context.
    - SQLite: instance/analytics.db
    - Postgres: use DATABASE_URL env (psycopg2/pg8000/psycopg)
    """
    if 'db' in g:
        return g.db

    db_url = os.getenv('DATABASE_URL', '')
    if _is_sqlite(db_url):
        # SQLite
        os.makedirs('instance', exist_ok=True)
        path = os.path.join('instance', 'analytics.db')
        conn = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread=False)
        conn.execute("""CREATE TABLE IF NOT EXISTS guide_clicks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guide_id TEXT NOT NULL,
            guide_title TEXT,
            href TEXT,
            ua TEXT,
            ts_utc TEXT NOT NULL
        )""")
        # Useful index for time-window queries
        conn.execute("CREATE INDEX IF NOT EXISTS idx_clicks_ts ON guide_clicks(ts_utc)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_clicks_gid ON guide_clicks(guide_id)")
        g.db = conn
        # Ensure summary table exists
        ensure_summary_table(conn)
    else:
        # Postgres path (example with psycopg)
        try:
            import psycopg
            g.db = psycopg.connect(db_url)  # relies on DATABASE_URL
            with g.db.cursor() as cur:
                cur.execute("""CREATE TABLE IF NOT EXISTS guide_clicks (
                    id BIGSERIAL PRIMARY KEY,
                    guide_id TEXT NOT NULL,
                    guide_title TEXT,
                    href TEXT,
                    ua TEXT,
                    ts_utc TIMESTAMPTZ NOT NULL
                )""")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_clicks_ts ON guide_clicks(ts_utc)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_clicks_gid ON guide_clicks(guide_id)")
                g.db.commit()
            # Ensure summary table exists
            ensure_summary_table(g.db)
        except ImportError:
            # Fallback to SQLite if psycopg not available
            return get_db()  # Recursive call with empty DATABASE_URL

    return g.db

@analytics_bp.teardown_request
def _teardown(exc):
    db = g.pop('db', None)
    if db:
        db.close()

def _now_utc_iso():
    return datetime.now(timezone.utc).isoformat()

def _is_bot_request(user_agent: str) -> bool:
    """Check if request appears to be from a bot/crawler"""
    if not user_agent:
        return False
    return bool(BOT_UA_RE.search(user_agent))

def ensure_summary_table(db):
    """Ensure the daily summary table exists with proper indexes"""
    if isinstance(db, sqlite3.Connection):
        db.execute("""CREATE TABLE IF NOT EXISTS guide_clicks_daily (
            day TEXT NOT NULL,
            guide_id TEXT NOT NULL,
            clicks INTEGER NOT NULL,
            PRIMARY KEY (day, guide_id)
        )""")
        db.execute("CREATE INDEX IF NOT EXISTS idx_daily_gid ON guide_clicks_daily(guide_id)")
        db.execute("CREATE INDEX IF NOT EXISTS idx_daily_date ON guide_clicks_daily(day)")
        db.commit()
    else:
        try:
            with db.cursor() as cur:
                cur.execute("""CREATE TABLE IF NOT EXISTS guide_clicks_daily (
                    day DATE NOT NULL,
                    guide_id TEXT NOT NULL,
                    clicks INTEGER NOT NULL,
                    PRIMARY KEY (day, guide_id)
                )""")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_daily_gid ON guide_clicks_daily(guide_id)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_daily_date ON guide_clicks_daily(day)")
                db.commit()
        except Exception as e:
            current_app.logger.error(f"Summary table creation failed: {e}")

def _validate_guide_data(data: dict) -> tuple[str, str]:
    """Validate and sanitize guide click data. Returns (error_msg, guide_id)"""
    if not data:
        return "empty_payload", ""
    
    guide_id = (data.get('guide_id') or '').strip().lower()
    guide_title = (data.get('guide_title') or '').strip()
    href = (data.get('href') or '').strip()
    
    # Validate guide_id
    if not guide_id:
        return "missing_guide_id", ""
    if len(guide_id) > MAX_GUIDE_ID_LENGTH:
        return "guide_id_too_long", ""
    if not SLUG_RE.match(guide_id):
        return "invalid_guide_id", ""
    
    # Validate title length
    if len(guide_title) > MAX_TITLE_LENGTH:
        return "title_too_long", guide_id
    
    # Validate href length
    if len(href) > MAX_HREF_LENGTH:
        return "href_too_long", guide_id
    
    return "", guide_id

@analytics_bp.route('/guide-click', methods=['POST'])
def guide_click():
    """
    Accept JSON: { guide_id, guide_title, href }
    Store minimal context + timestamp. No PII.
    """
    # Validate content type
    if not request.is_json:
        return jsonify({"ok": False, "err": "invalid_content_type"}), 400
    
    # Get and validate user agent
    ua = (request.headers.get('User-Agent') or '')[:MAX_UA_LENGTH]
    
    # Filter out bot traffic
    if _is_bot_request(ua):
        return jsonify({"ok": False, "err": "bot_filtered"}), 429
    
    # Parse and validate JSON payload
    try:
        data = request.get_json(force=True)
    except (ValueError, TypeError):
        return jsonify({"ok": False, "err": "invalid_json"}), 400
    
    # Validate guide data
    error_msg, guide_id = _validate_guide_data(data)
    if error_msg:
        current_app.logger.warning(f"Analytics validation failed: {error_msg} for {data}")
        return jsonify({"ok": False, "err": error_msg}), 400
    
    # Extract sanitized data
    guide_title = (data.get('guide_title') or '').strip()[:MAX_TITLE_LENGTH]
    href = (data.get('href') or '').strip()[:MAX_HREF_LENGTH]
    ts_utc = _now_utc_iso()

    # Store to database
    db = get_db()
    try:
        if isinstance(db, sqlite3.Connection):
            db.execute(
                "INSERT INTO guide_clicks (guide_id, guide_title, href, ua, ts_utc) VALUES (?,?,?,?,?)",
                (guide_id, guide_title, href, ua, ts_utc)
            )
            db.commit()
        else:
            with db.cursor() as cur:
                cur.execute(
                    "INSERT INTO guide_clicks (guide_id, guide_title, href, ua, ts_utc) VALUES (%s,%s,%s,%s,%s)",
                    (guide_id, guide_title, href, ua, ts_utc)
                )
                db.commit()
        
        current_app.logger.info(f"Analytics recorded: {guide_id}")
        
    except Exception as e:
        # Log error but don't leak internals to clients
        current_app.logger.error(f"Analytics database error: {e}")
        return jsonify({"ok": False}), 500

    return jsonify({"ok": True})

@analytics_bp.route('/guide-back-click', methods=['POST'])
def guide_back_click():
    """
    Track back link usage: { guide_id: "back_context" | "back_index", guide_title, href }
    Helps understand navigation patterns vs. "Keep Learning" links.
    """
    # Validate content type
    if not request.is_json:
        return jsonify({"ok": False, "err": "invalid_content_type"}), 400
    
    # Get and validate user agent
    ua = (request.headers.get('User-Agent') or '')[:MAX_UA_LENGTH]
    
    # Filter out bot traffic
    if _is_bot_request(ua):
        return jsonify({"ok": False, "err": "bot_filtered"}), 429
    
    # Parse and validate JSON payload
    try:
        data = request.get_json(force=True)
    except (ValueError, TypeError):
        return jsonify({"ok": False, "err": "invalid_json"}), 400
    
    # Extract and validate back link data
    guide_id = (data.get('guide_id') or '').strip()
    guide_title = (data.get('guide_title') or '').strip()[:MAX_TITLE_LENGTH]
    href = (data.get('href') or '').strip()[:MAX_HREF_LENGTH]
    
    # Basic validation
    if not guide_id or len(guide_id) > MAX_GUIDE_ID_LENGTH:
        return jsonify({"ok": False, "err": "invalid_guide_id"}), 400
    
    # Valid back link types
    if guide_id not in ['back_context', 'back_index']:
        return jsonify({"ok": False, "err": "invalid_back_type"}), 400
    
    ts_utc = _now_utc_iso()

    # Store to database (reuse same table with special guide_id prefixes)
    db = get_db()
    try:
        if isinstance(db, sqlite3.Connection):
            db.execute(
                "INSERT INTO guide_clicks (guide_id, guide_title, href, ua, ts_utc) VALUES (?,?,?,?,?)",
                (guide_id, guide_title, href, ua, ts_utc)
            )
            db.commit()
        else:
            with db.cursor() as cur:
                cur.execute(
                    "INSERT INTO guide_clicks (guide_id, guide_title, href, ua, ts_utc) VALUES (%s,%s,%s,%s,%s)",
                    (guide_id, guide_title, href, ua, ts_utc)
                )
                db.commit()
        
        current_app.logger.info(f"Back link analytics recorded: {guide_id}")
        
    except Exception as e:
        current_app.logger.error(f"Back link analytics database error: {e}")
        return jsonify({"ok": False}), 500

    return jsonify({"ok": True})

def get_top_guides(days=7, limit=10):
    """
    Query helper to get top guides for a time window.
    Uses daily summary table for older data and raw table for recent data.
    Returns list of (guide_id, guide_title, click_count) tuples.
    """
    db = get_db()
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    
    try:
        if isinstance(db, sqlite3.Connection):
            # SQLite: Combine daily summaries with recent raw data
            cutoff_date = cutoff.date().isoformat()
            today = datetime.now(timezone.utc).date().isoformat()
            
            cursor = db.execute("""
                WITH combined_data AS (
                    -- Get aggregated data from daily summaries (older than today)
                    SELECT guide_id, SUM(clicks) as click_count
                    FROM guide_clicks_daily
                    WHERE day >= ? AND day < ?
                    GROUP BY guide_id
                    
                    UNION ALL
                    
                    -- Get raw data from today and yesterday (not yet aggregated)
                    SELECT guide_id, COUNT(*) as click_count
                    FROM guide_clicks
                    WHERE date(ts_utc) >= date('now', '-1 day')
                    AND ts_utc >= ?
                    GROUP BY guide_id
                ),
                guide_totals AS (
                    SELECT guide_id, SUM(click_count) as total_clicks
                    FROM combined_data
                    GROUP BY guide_id
                )
                SELECT gt.guide_id, gc.guide_title, gt.total_clicks
                FROM guide_totals gt
                LEFT JOIN guide_clicks gc ON gt.guide_id = gc.guide_id
                GROUP BY gt.guide_id, gc.guide_title, gt.total_clicks
                ORDER BY gt.total_clicks DESC
                LIMIT ?
            """, (cutoff_date, today, cutoff.isoformat(), limit))
            
            return cursor.fetchall()
            
        else:
            # PostgreSQL: More efficient with window functions
            with db.cursor() as cur:
                cur.execute("""
                    WITH combined_data AS (
                        -- Get aggregated data from daily summaries
                        SELECT guide_id, SUM(clicks) as click_count
                        FROM guide_clicks_daily
                        WHERE day >= (CURRENT_DATE - INTERVAL '%s days')
                        GROUP BY guide_id
                        
                        UNION ALL
                        
                        -- Get raw data from last 2 days (not yet aggregated)
                        SELECT guide_id, COUNT(*) as click_count
                        FROM guide_clicks
                        WHERE ts_utc >= (CURRENT_DATE - INTERVAL '2 days')
                        AND ts_utc >= %s
                        GROUP BY guide_id
                    ),
                    guide_totals AS (
                        SELECT guide_id, SUM(click_count) as total_clicks
                        FROM combined_data
                        GROUP BY guide_id
                    )
                    SELECT gt.guide_id, 
                           COALESCE(gc.guide_title, gt.guide_id) as guide_title,
                           gt.total_clicks
                    FROM guide_totals gt
                    LEFT JOIN (
                        SELECT DISTINCT guide_id, 
                               FIRST_VALUE(guide_title) OVER (PARTITION BY guide_id ORDER BY ts_utc DESC) as guide_title
                        FROM guide_clicks
                        WHERE guide_title IS NOT NULL AND guide_title != ''
                    ) gc ON gt.guide_id = gc.guide_id
                    ORDER BY gt.total_clicks DESC
                    LIMIT %s
                """, (days, cutoff, limit))
                
                return cur.fetchall()
                
    except Exception as e:
        current_app.logger.error(f"Analytics query error: {e}")
        # Fallback to simple raw query if summary fails
        try:
            cutoff_iso = cutoff.isoformat()
            if isinstance(db, sqlite3.Connection):
                cursor = db.execute("""
                    SELECT guide_id, guide_title, COUNT(*) as click_count 
                    FROM guide_clicks 
                    WHERE ts_utc >= ? 
                    GROUP BY guide_id, guide_title 
                    ORDER BY click_count DESC 
                    LIMIT ?
                """, (cutoff_iso, limit))
                return cursor.fetchall()
            else:
                with db.cursor() as cur:
                    cur.execute("""
                        SELECT guide_id, guide_title, COUNT(*) as click_count 
                        FROM guide_clicks 
                        WHERE ts_utc >= %s 
                        GROUP BY guide_id, guide_title 
                        ORDER BY click_count DESC 
                        LIMIT %s
                    """, (cutoff_iso, limit))
                    return cur.fetchall()
        except Exception as fallback_error:
            current_app.logger.error(f"Fallback query also failed: {fallback_error}")
            return []

@analytics_bp.route('/top-guides')
def top_guides():
    """
    Optional endpoint to view analytics (you might want to protect this)
    """
    days = request.args.get('days', 7, type=int)
    limit = request.args.get('limit', 10, type=int)
    
    # Sanity limits
    days = max(1, min(days, 365))
    limit = max(1, min(limit, 100))
    
    results = get_top_guides(days, limit)
    return jsonify({
        "days": days,
        "guides": [{"guide_id": r[0], "title": r[1], "clicks": r[2]} for r in results]
    })

# Helper functions for Popular Now widget
def analytics_db_connect():
    """Direct database connection for analytics queries (not request-scoped)"""
    db_url = os.getenv('DATABASE_URL', '')
    if _is_sqlite(db_url):
        os.makedirs('instance', exist_ok=True)
        return sqlite3.connect('instance/analytics.db')
    else:
        import psycopg
        return psycopg.connect(db_url)

def top_guides_simple(days: int = 30, limit: int = 5):
    """
    Returns list of tuples: (guide_id, clicks) for last N days.
    If summary table exists, it uses it; otherwise falls back to raw events.
    Lightweight version for widget use.
    
    This replaces the old get_popular_guides() function from app.py
    """
    db_url = os.getenv('DATABASE_URL', '')
    since_utc_iso = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()

    try:
        if _is_sqlite(db_url):
            conn = analytics_db_connect()
            cur = conn.cursor()

            # Check if summary table exists
            try:
                cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='guide_clicks_daily'")
                has_summary = cur.fetchone() is not None
            except Exception:
                has_summary = False

            if has_summary:
                # Sum last N days from summary + recent raw data
                cur.execute("""
                    WITH combined_data AS (
                        -- Aggregated data from summary table
                        SELECT guide_id, SUM(clicks) as click_count
                        FROM guide_clicks_daily
                        WHERE day >= date('now', ?)
                        GROUP BY guide_id
                        
                        UNION ALL
                        
                        -- Recent raw data (last 2 days, might not be in summary yet)
                        SELECT guide_id, COUNT(*) as click_count
                        FROM guide_clicks
                        WHERE date(ts_utc) >= date('now', '-2 days')
                        AND ts_utc >= ?
                        GROUP BY guide_id
                    )
                    SELECT guide_id, SUM(click_count) as total_clicks
                    FROM combined_data
                    GROUP BY guide_id
                    ORDER BY total_clicks DESC
                    LIMIT ?
                """, (f'-{days} day', since_utc_iso, limit))
            else:
                # Fallback to raw data only
                cur.execute("""
                    SELECT guide_id, COUNT(*) AS c
                    FROM guide_clicks
                    WHERE ts_utc >= ?
                    GROUP BY guide_id
                    ORDER BY c DESC
                    LIMIT ?
                """, (since_utc_iso, limit))

            rows = cur.fetchall()
            conn.close()
            return [(gid, int(c)) for gid, c in rows]

        else:
            # PostgreSQL path
            import psycopg
            conn = analytics_db_connect()
            try:
                cur = conn.cursor()
                # Check if summary table exists
                cur.execute("""
                    SELECT to_regclass('public.guide_clicks_daily')
                """)
                result = cur.fetchone()
                has_summary = result is not None and result[0] is not None

                if has_summary:
                    # Use summary + recent raw data
                    # Use proper PostgreSQL interval syntax
                    interval_str = f'{days} days'
                    cur.execute("""
                        WITH combined_data AS (
                            -- Aggregated data from summary table
                            SELECT guide_id, SUM(clicks) as click_count
                            FROM guide_clicks_daily
                            WHERE day >= CURRENT_DATE - INTERVAL %s
                            GROUP BY guide_id
                            
                            UNION ALL
                            
                            -- Recent raw data (last 2 days)
                            SELECT guide_id, COUNT(*) as click_count
                            FROM guide_clicks
                            WHERE ts_utc >= CURRENT_DATE - INTERVAL '2 days'
                            AND ts_utc >= (NOW() AT TIME ZONE 'UTC') - INTERVAL %s
                            GROUP BY guide_id
                        )
                        SELECT guide_id, SUM(click_count) as total_clicks
                        FROM combined_data
                        GROUP BY guide_id
                        ORDER BY total_clicks DESC
                        LIMIT %s
                    """, (interval_str, interval_str, limit))
                else:
                    # Fallback to raw data only
                    interval_str = f'{days} days'
                    cur.execute("""
                        SELECT guide_id, COUNT(*) AS c
                        FROM guide_clicks
                        WHERE ts_utc >= (NOW() AT TIME ZONE 'UTC') - INTERVAL %s
                        GROUP BY guide_id
                        ORDER BY c DESC
                        LIMIT %s
                    """, (interval_str, limit))

                rows = cur.fetchall()
                cur.close()
                return [(gid, int(c)) for gid, c in rows]
            finally:
                conn.close()

    except Exception as e:
        # Graceful fallback - return empty list if analytics fails
        current_app.logger.warning(f"Popular guides query failed: {e}")
        return []

@analytics_bp.route('/popular', methods=['GET'])
def popular_guides_api():
    """
    JSON API endpoint for popular guides widget.
    Usage: GET /analytics/popular?days=30&limit=5
    Returns: {"guides": [{"id": "guide-id", "clicks": 42}, ...]}
    """
    days = request.args.get('days', 30, type=int)
    limit = request.args.get('limit', 5, type=int)
    
    # Sanity limits
    days = max(1, min(days, 365))
    limit = max(1, min(limit, 20))
    
    try:
        results = top_guides_simple(days=days, limit=limit)
        
        # Enrich with guide metadata from catalog
        guides = []
        for guide_id, clicks in results:
            guide_info = get_guide_by_id(guide_id)
            if guide_info:  # Only include guides that exist in catalog
                guides.append({
                    "id": guide_id,
                    "title": guide_info["title"],
                    "href": guide_info["href"],
                    "group": guide_info["group"],
                    "clicks": clicks
                })
        
        return jsonify({
            "guides": guides,
            "days": days,
            "limit": limit
        })
    except Exception as e:
        current_app.logger.error(f"Popular guides API error: {e}")
        return jsonify({
            "guides": [],
            "days": days,
            "limit": limit,
            "error": "analytics_unavailable"
        }), 500

@analytics_bp.route('/maintenance/rollup', methods=['POST'])
def rollup():
    """
    Daily rollup maintenance endpoint - aggregates raw clicks into daily summaries
    and purges old raw data. Requires ADMIN_SECRET header for security.
    """
    # Require admin secret for security
    secret = request.headers.get('X-Admin-Secret')
    admin_secret = os.getenv('ADMIN_SECRET')
    
    if not admin_secret:
        current_app.logger.error("ADMIN_SECRET not configured")
        return jsonify({"ok": False, "error": "not_configured"}), 500
    
    if secret != admin_secret:
        current_app.logger.warning(f"Unauthorized rollup attempt from {request.remote_addr}")
        return jsonify({"ok": False, "error": "unauthorized"}), 403

    db = get_db()
    ensure_summary_table(db)
    
    try:
        if isinstance(db, sqlite3.Connection):
            # SQLite implementation
            from datetime import date, timedelta
            yesterday = (date.today() - timedelta(days=1)).isoformat()
            
            # Aggregate yesterday's data
            cursor = db.execute("""
                SELECT guide_id, COUNT(*) as clicks
                FROM guide_clicks
                WHERE date(ts_utc) = ?
                GROUP BY guide_id
            """, (yesterday,))
            
            rows = cursor.fetchall()
            aggregated_guides = 0
            
            for guide_id, clicks in rows:
                db.execute("""
                    INSERT INTO guide_clicks_daily (day, guide_id, clicks)
                    VALUES (?, ?, ?)
                    ON CONFLICT(day, guide_id) DO UPDATE SET 
                    clicks = clicks + excluded.clicks
                """, (yesterday, guide_id, clicks))
                aggregated_guides += 1
            
            # Purge raw data older than 90 days
            purge_result = db.execute("""
                DELETE FROM guide_clicks 
                WHERE date(ts_utc) < date('now', '-90 days')
            """)
            purged_records = purge_result.rowcount
            
            db.commit()
            
        else:
            # PostgreSQL implementation
            with db.cursor() as cur:
                # Aggregate yesterday's data
                cur.execute("""
                    INSERT INTO guide_clicks_daily (day, guide_id, clicks)
                    SELECT 
                        (ts_utc AT TIME ZONE 'UTC')::date AS day, 
                        guide_id, 
                        COUNT(*) as clicks
                    FROM guide_clicks
                    WHERE (ts_utc AT TIME ZONE 'UTC')::date = CURRENT_DATE - INTERVAL '1 day'
                    GROUP BY day, guide_id
                    ON CONFLICT (day, guide_id) 
                    DO UPDATE SET clicks = guide_clicks_daily.clicks + EXCLUDED.clicks
                """)
                
                aggregated_guides = cur.rowcount
                
                # Purge raw data older than 90 days
                cur.execute("""
                    DELETE FROM guide_clicks 
                    WHERE ts_utc < (CURRENT_DATE - INTERVAL '90 days')
                """)
                
                purged_records = cur.rowcount
                db.commit()
        
        current_app.logger.info(f"Rollup complete: {aggregated_guides} guides aggregated, {purged_records} records purged")
        
        return jsonify({
            "ok": True,
            "aggregated_guides": aggregated_guides,
            "purged_records": purged_records
        })
        
    except Exception as e:
        current_app.logger.error(f"Rollup failed: {e}")
        return jsonify({"ok": False, "error": "rollup_failed"}), 500

@analytics_bp.route('/migrate-tables', methods=['POST'])
def migrate_tables():
    """
    TEMPORARY MIGRATION ENDPOINT - Creates missing analytics tables in production
    
    Usage: POST /analytics/migrate-tables
    Remove this endpoint after running once for security.
    """
    
    db_url = os.getenv('DATABASE_URL', '')
    if not db_url:
        return jsonify({"error": "DATABASE_URL not configured, using SQLite"}), 400
    
    try:
        import psycopg
        
        conn = psycopg.connect(db_url)
        cur = conn.cursor()
        
        # Check existing tables
        cur.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_name IN ('guide_clicks', 'guide_clicks_daily')
        """)
        existing_tables = [row[0] for row in cur.fetchall()]
        
        results = {
            "existing_tables": existing_tables,
            "created_tables": [],
            "created_indexes": []
        }
        
        # Create guide_clicks table if missing
        if 'guide_clicks' not in existing_tables:
            cur.execute("""
                CREATE TABLE guide_clicks (
                    id BIGSERIAL PRIMARY KEY,
                    guide_id TEXT NOT NULL,
                    guide_title TEXT,
                    href TEXT,
                    ua TEXT,
                    ts_utc TIMESTAMPTZ NOT NULL
                )
            """)
            results["created_tables"].append("guide_clicks")
        
        # Create guide_clicks_daily table if missing
        if 'guide_clicks_daily' not in existing_tables:
            cur.execute("""
                CREATE TABLE guide_clicks_daily (
                    day DATE NOT NULL,
                    guide_id TEXT NOT NULL,
                    clicks INTEGER NOT NULL,
                    PRIMARY KEY (day, guide_id)
                )
            """)
            results["created_tables"].append("guide_clicks_daily")
        
        # Create indexes (IF NOT EXISTS handles duplicates)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_clicks_ts ON guide_clicks(ts_utc)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_clicks_gid ON guide_clicks(guide_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_daily_gid ON guide_clicks_daily(guide_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_daily_date ON guide_clicks_daily(day)")
        
        results["created_indexes"] = ["idx_clicks_ts", "idx_clicks_gid", "idx_daily_gid", "idx_daily_date"]
        
        conn.commit()
        
        # Verify final state
        cur.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_name IN ('guide_clicks', 'guide_clicks_daily')
        """)
        final_tables = [row[0] for row in cur.fetchall()]
        
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Migration completed successfully",
            "results": results,
            "final_tables": final_tables,
            "note": "SECURITY: Remove this endpoint after use"
        }), 200
        
    except ImportError:
        return jsonify({"error": "psycopg not available"}), 500
    except Exception as e:
        current_app.logger.error(f"Migration failed: {e}")
        return jsonify({"error": f"Migration failed: {str(e)}"}), 500

@analytics_bp.route('/debug-db', methods=['GET'])
def debug_db():
    """
    TEMPORARY DEBUG ENDPOINT - Check database contents
    Remove after debugging is complete.
    """
    
    db_url = os.getenv('DATABASE_URL', '')
    if not db_url:
        return jsonify({"error": "DATABASE_URL not configured"}), 400
    
    try:
        import psycopg
        
        conn = psycopg.connect(db_url)
        cur = conn.cursor()
        
        # Check record count
        cur.execute("SELECT COUNT(*) FROM guide_clicks")
        result = cur.fetchone()
        total_count = result[0] if result else 0
        
        # Get recent records
        cur.execute("""
            SELECT guide_id, guide_title, ts_utc 
            FROM guide_clicks 
            ORDER BY ts_utc DESC 
            LIMIT 10
        """)
        recent_records = cur.fetchall()
        
        # Check daily summary
        cur.execute("SELECT COUNT(*) FROM guide_clicks_daily")
        result = cur.fetchone()
        daily_count = result[0] if result else 0
        
        conn.close()
        
        # Test the top_guides_simple function directly
        try:
            simple_results = top_guides_simple(days=30, limit=10)
            debug_simple = [{"guide_id": gid, "clicks": clicks} for gid, clicks in simple_results]
        except Exception as e:
            debug_simple = f"Error: {str(e)}"
        
        # Also test a simple raw query that should definitely work
        try:
            # Use a fresh connection for this test
            fresh_conn = psycopg.connect(db_url)
            fresh_cur = fresh_conn.cursor()
            fresh_cur.execute("""
                SELECT guide_id, COUNT(*) as clicks
                FROM guide_clicks 
                WHERE ts_utc >= NOW() - INTERVAL '30 days'
                GROUP BY guide_id 
                ORDER BY clicks DESC 
                LIMIT 10
            """)
            raw_results = fresh_cur.fetchall()
            debug_raw = [{"guide_id": r[0], "clicks": int(r[1])} for r in raw_results]
            fresh_conn.close()
        except Exception as e:
            debug_raw = f"Raw query error: {str(e)}"
        
        return jsonify({
            "total_clicks": total_count,
            "daily_summary_count": daily_count,
            "recent_records": [
                {"guide_id": r[0], "title": r[1], "timestamp": str(r[2])}
                for r in recent_records
            ],
            "top_guides_simple_test": debug_simple,
            "raw_query_test": debug_raw,
            "note": "SECURITY: Remove this debug endpoint after use"
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Debug failed: {str(e)}"}), 500