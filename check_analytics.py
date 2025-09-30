#!/usr/bin/env python3
import sqlite3
import os

try:
    if os.path.exists('instance/analytics.db'):
        conn = sqlite3.connect('instance/analytics.db')
        cur = conn.cursor()
        
        # Check if table exists
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='guide_clicks'")
        table_exists = cur.fetchone()
        
        if table_exists:
            # Get total records
            cur.execute('SELECT COUNT(*) FROM guide_clicks')
            total_clicks = cur.fetchone()[0]
            print(f'Total guide clicks in database: {total_clicks}')
            
            # Get recent clicks (last 30 days)
            cur.execute('SELECT guide_id, COUNT(*) as clicks FROM guide_clicks WHERE ts_utc >= datetime("now", "-30 days") GROUP BY guide_id ORDER BY clicks DESC LIMIT 10')
            results = cur.fetchall()
            
            print('\nAnalytics data (last 30 days):')
            if results:
                for gid, clicks in results:
                    print(f'  {gid}: {clicks} clicks')
            else:
                print('  No clicks found in last 30 days')
                
            # Check for any clicks at all
            cur.execute('SELECT guide_id, COUNT(*) as clicks FROM guide_clicks GROUP BY guide_id ORDER BY clicks DESC LIMIT 10')
            all_results = cur.fetchall()
            
            print('\nAll-time analytics data:')
            if all_results:
                for gid, clicks in all_results:
                    print(f'  {gid}: {clicks} clicks')
            else:
                print('  No clicks found at all')
        else:
            print('guide_clicks table does not exist')
        
        conn.close()
    else:
        print('Analytics database file does not exist: instance/analytics.db')
        
except Exception as e:
    print(f'Error checking analytics: {e}')