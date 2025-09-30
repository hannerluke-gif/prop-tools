#!/usr/bin/env python3
"""
Database Schema Checker for Analytics System
Checks if production database has the required tables and schema.
"""
import os
import sys
import json

def check_database_schema():
    """Check if the analytics tables exist and have the correct structure"""
    
    # Check if DATABASE_URL is set (production uses PostgreSQL)
    db_url = os.getenv('DATABASE_URL', '')
    
    print("=" * 60)
    print("DATABASE SCHEMA CHECKER")
    print("=" * 60)
    
    if not db_url:
        print("❌ DATABASE_URL not set - will use SQLite")
        print("This means production might be using SQLite instead of PostgreSQL")
        return check_sqlite_schema()
    else:
        print(f"✅ DATABASE_URL found: {db_url[:50]}...")
        return check_postgres_schema(db_url)

def check_sqlite_schema():
    """Check SQLite database schema"""
    import sqlite3
    
    try:
        if os.path.exists('instance/analytics.db'):
            conn = sqlite3.connect('instance/analytics.db')
            cur = conn.cursor()
            
            print("\n📊 SQLITE DATABASE ANALYSIS")
            print("-" * 40)
            
            # Check if guide_clicks table exists
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='guide_clicks'")
            guide_clicks_exists = cur.fetchone()
            
            if guide_clicks_exists:
                print("✅ guide_clicks table exists")
                
                # Check table structure
                cur.execute("PRAGMA table_info(guide_clicks)")
                columns = cur.fetchall()
                print("   Columns:")
                for col in columns:
                    print(f"     - {col[1]} ({col[2]})")
                
                # Check indexes
                cur.execute("PRAGMA index_list(guide_clicks)")
                indexes = cur.fetchall()
                print("   Indexes:")
                for idx in indexes:
                    print(f"     - {idx[1]}")
                    
                # Check record count
                cur.execute("SELECT COUNT(*) FROM guide_clicks")
                count = cur.fetchone()[0]
                print(f"   Records: {count}")
                
            else:
                print("❌ guide_clicks table does NOT exist")
            
            # Check if guide_clicks_daily table exists
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='guide_clicks_daily'")
            daily_table_exists = cur.fetchone()
            
            if daily_table_exists:
                print("✅ guide_clicks_daily table exists")
                
                # Check record count
                cur.execute("SELECT COUNT(*) FROM guide_clicks_daily")
                count = cur.fetchone()[0]
                print(f"   Records: {count}")
            else:
                print("❌ guide_clicks_daily table does NOT exist")
            
            conn.close()
            
            return guide_clicks_exists and daily_table_exists
            
        else:
            print("❌ SQLite database file does not exist: instance/analytics.db")
            return False
            
    except Exception as e:
        print(f"❌ Error checking SQLite schema: {e}")
        return False

def check_postgres_schema(db_url):
    """Check PostgreSQL database schema"""
    try:
        import psycopg
        
        print("\n🐘 POSTGRESQL DATABASE ANALYSIS")
        print("-" * 40)
        
        conn = psycopg.connect(db_url)
        cur = conn.cursor()
        
        # Check if guide_clicks table exists
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'guide_clicks'
            )
        """)
        result = cur.fetchone()
        guide_clicks_exists = result[0] if result else False
        
        if guide_clicks_exists:
            print("✅ guide_clicks table exists")
            
            # Check table structure
            cur.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'guide_clicks'
                ORDER BY ordinal_position
            """)
            columns = cur.fetchall()
            print("   Columns:")
            for col in columns:
                print(f"     - {col[0]} ({col[1]}, nullable: {col[2]})")
            
            # Check indexes
            cur.execute("""
                SELECT indexname, indexdef
                FROM pg_indexes 
                WHERE tablename = 'guide_clicks'
            """)
            indexes = cur.fetchall()
            print("   Indexes:")
            for idx in indexes:
                print(f"     - {idx[0]}")
                
            # Check record count
            cur.execute("SELECT COUNT(*) FROM guide_clicks")
            result = cur.fetchone()
            count = result[0] if result else 0
            print(f"   Records: {count}")
            
        else:
            print("❌ guide_clicks table does NOT exist")
        
        # Check if guide_clicks_daily table exists
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'guide_clicks_daily'
            )
        """)
        result = cur.fetchone()
        daily_table_exists = result[0] if result else False
        
        if daily_table_exists:
            print("✅ guide_clicks_daily table exists")
            
            # Check record count
            cur.execute("SELECT COUNT(*) FROM guide_clicks_daily")
            result = cur.fetchone()
            count = result[0] if result else 0
            print(f"   Records: {count}")
        else:
            print("❌ guide_clicks_daily table does NOT exist")
        
        conn.close()
        
        return guide_clicks_exists and daily_table_exists
        
    except ImportError:
        print("❌ psycopg not installed - cannot connect to PostgreSQL")
        print("   Install with: pip install psycopg[binary]")
        return False
    except Exception as e:
        print(f"❌ Error connecting to PostgreSQL: {e}")
        return False

def create_missing_tables():
    """Create missing analytics tables"""
    db_url = os.getenv('DATABASE_URL', '')
    
    print("\n🔧 CREATING MISSING TABLES")
    print("-" * 40)
    
    if not db_url:
        create_sqlite_tables()
    else:
        create_postgres_tables(db_url)

def create_sqlite_tables():
    """Create SQLite analytics tables"""
    import sqlite3
    
    try:
        os.makedirs('instance', exist_ok=True)
        conn = sqlite3.connect('instance/analytics.db')
        
        # Create main table
        conn.execute("""CREATE TABLE IF NOT EXISTS guide_clicks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guide_id TEXT NOT NULL,
            guide_title TEXT,
            href TEXT,
            ua TEXT,
            ts_utc TEXT NOT NULL
        )""")
        
        # Create indexes
        conn.execute("CREATE INDEX IF NOT EXISTS idx_clicks_ts ON guide_clicks(ts_utc)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_clicks_gid ON guide_clicks(guide_id)")
        
        # Create daily summary table
        conn.execute("""CREATE TABLE IF NOT EXISTS guide_clicks_daily (
            day TEXT NOT NULL,
            guide_id TEXT NOT NULL,
            clicks INTEGER NOT NULL,
            PRIMARY KEY (day, guide_id)
        )""")
        
        # Create summary table indexes
        conn.execute("CREATE INDEX IF NOT EXISTS idx_daily_gid ON guide_clicks_daily(guide_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_daily_date ON guide_clicks_daily(day)")
        
        conn.commit()
        conn.close()
        
        print("✅ SQLite tables created successfully")
        
    except Exception as e:
        print(f"❌ Error creating SQLite tables: {e}")

def create_postgres_tables(db_url):
    """Create PostgreSQL analytics tables"""
    try:
        import psycopg
        
        conn = psycopg.connect(db_url)
        cur = conn.cursor()
        
        # Create main table
        cur.execute("""CREATE TABLE IF NOT EXISTS guide_clicks (
            id BIGSERIAL PRIMARY KEY,
            guide_id TEXT NOT NULL,
            guide_title TEXT,
            href TEXT,
            ua TEXT,
            ts_utc TIMESTAMPTZ NOT NULL
        )""")
        
        # Create indexes
        cur.execute("CREATE INDEX IF NOT EXISTS idx_clicks_ts ON guide_clicks(ts_utc)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_clicks_gid ON guide_clicks(guide_id)")
        
        # Create daily summary table
        cur.execute("""CREATE TABLE IF NOT EXISTS guide_clicks_daily (
            day DATE NOT NULL,
            guide_id TEXT NOT NULL,
            clicks INTEGER NOT NULL,
            PRIMARY KEY (day, guide_id)
        )""")
        
        # Create summary table indexes
        cur.execute("CREATE INDEX IF NOT EXISTS idx_daily_gid ON guide_clicks_daily(guide_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_daily_date ON guide_clicks_daily(day)")
        
        conn.commit()
        conn.close()
        
        print("✅ PostgreSQL tables created successfully")
        
    except ImportError:
        print("❌ psycopg not installed - cannot create PostgreSQL tables")
    except Exception as e:
        print(f"❌ Error creating PostgreSQL tables: {e}")

if __name__ == "__main__":
    print("Checking database schema for analytics system...")
    
    schema_ok = check_database_schema()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    if schema_ok:
        print("✅ Database schema is correct!")
        print("   Analytics tables exist and are properly structured.")
    else:
        print("❌ Database schema has issues!")
        print("   Some analytics tables are missing or incorrectly structured.")
        
        response = input("\nWould you like me to create the missing tables? (y/N): ")
        if response.lower() in ['y', 'yes']:
            create_missing_tables()
            print("\n✅ Tables created! Try testing analytics again.")
        else:
            print("\n💡 Run this script again with the 'fix' argument to create tables:")
            print("   python check_database_schema.py fix")
    
    print("\n🔍 Next steps:")
    print("   1. If using production, set DATABASE_URL environment variable")
    print("   2. Test analytics again after fixing schema issues")
    print("   3. Check production logs for any database connection errors")