# Analytics Database Migration
# Add this as a temporary route to create the missing analytics tables

from flask import Blueprint, jsonify, current_app
import os

# Create a temporary blueprint for migration
migration_bp = Blueprint('migration', __name__, url_prefix='/migration')

@migration_bp.route('/create-analytics-tables', methods=['POST'])
def create_analytics_tables():
    """
    TEMPORARY MIGRATION ENDPOINT - Creates analytics tables in production
    
    Call this once: POST https://www.proptradetools.com/migration/create-analytics-tables
    Then remove this endpoint for security.
    """
    
    # Only allow in production and only if tables don't exist
    db_url = os.getenv('DATABASE_URL', '')
    if not db_url:
        return jsonify({"error": "DATABASE_URL not configured"}), 500
    
    try:
        import psycopg
        
        conn = psycopg.connect(db_url)
        cur = conn.cursor()
        
        # Check if tables already exist
        cur.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_name IN ('guide_clicks', 'guide_clicks_daily')
        """)
        existing_tables = [row[0] for row in cur.fetchall()]
        
        if 'guide_clicks' in existing_tables and 'guide_clicks_daily' in existing_tables:
            conn.close()
            return jsonify({
                "success": False,
                "message": "Analytics tables already exist",
                "existing_tables": existing_tables
            }), 200
        
        # Create main analytics table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS guide_clicks (
                id BIGSERIAL PRIMARY KEY,
                guide_id TEXT NOT NULL,
                guide_title TEXT,
                href TEXT,
                ua TEXT,
                ts_utc TIMESTAMPTZ NOT NULL
            )
        """)
        
        # Create indexes for performance
        cur.execute("CREATE INDEX IF NOT EXISTS idx_clicks_ts ON guide_clicks(ts_utc)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_clicks_gid ON guide_clicks(guide_id)")
        
        # Create daily summary table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS guide_clicks_daily (
                day DATE NOT NULL,
                guide_id TEXT NOT NULL,
                clicks INTEGER NOT NULL,
                PRIMARY KEY (day, guide_id)
            )
        """)
        
        # Create summary table indexes
        cur.execute("CREATE INDEX IF NOT EXISTS idx_daily_gid ON guide_clicks_daily(guide_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_daily_date ON guide_clicks_daily(day)")
        
        # Commit the changes
        conn.commit()
        
        # Verify tables were created
        cur.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_name IN ('guide_clicks', 'guide_clicks_daily')
        """)
        created_tables = [row[0] for row in cur.fetchall()]
        
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Analytics tables created successfully",
            "created_tables": created_tables,
            "note": "Remove this migration endpoint for security after use"
        }), 200
        
    except ImportError:
        return jsonify({"error": "psycopg not available"}), 500
    except Exception as e:
        current_app.logger.error(f"Migration failed: {e}")
        return jsonify({"error": f"Migration failed: {str(e)}"}), 500

# Instructions for use:
"""
1. Add this blueprint to your app.py temporarily:
   
   from migration import migration_bp
   app.register_blueprint(migration_bp)

2. Deploy the app with this endpoint

3. Call the migration endpoint once:
   curl -X POST https://www.proptradetools.com/migration/create-analytics-tables

4. Remove this blueprint and redeploy for security

5. Test analytics again - flame icons should work!
"""