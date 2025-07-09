import sqlite3
import os
import datetime

def get_db_path():
    """Get the path to the database file"""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'novel_views.db')

def init_db():
    """Initialize the database with required tables (new schema)"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Create Novel table if it doesn't exist (new schema)
    c.execute('''
        CREATE TABLE IF NOT EXISTS Novel (
            novel_id INTEGER PRIMARY KEY NOT NULL,
            novel_name VARCHAR(70) NOT NULL UNIQUE,
            novel_views INTEGER NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

def increment_view(novel_name):
    """Increment the view count for a novel (new schema)"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Try to update the view count; if not present, insert a new row
    c.execute('SELECT novel_views FROM Novel WHERE novel_name = ?', (novel_name,))
    result = c.fetchone()
    if result:
        c.execute('UPDATE Novel SET novel_views = novel_views + 1 WHERE novel_name = ?', (novel_name,))
    else:
        c.execute('INSERT INTO Novel (novel_name, novel_views) VALUES (?, 1)', (novel_name,))
    
    conn.commit()
    conn.close()

def get_novel_views(novel_name):
    """Get the total views for a novel (new schema)"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    c.execute('SELECT novel_views FROM Novel WHERE novel_name = ?', (novel_name,))
    result = c.fetchone()
    
    conn.close()
    return result[0] if result else 0

def get_all_novel_views():
    """Get views for all novels (new schema)"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    c.execute('SELECT novel_name, novel_views FROM Novel ORDER BY novel_views DESC')
    results = c.fetchall()
    
    conn.close()
    return dict(results)

# Initialize the database when the module is imported
init_db()

# --- VISITS COUNTER SYSTEM ---
COUNTERS_DB_PATH = os.path.join(os.path.dirname(__file__), 'visits.sqlite3')

def get_db():
    conn = sqlite3.connect(COUNTERS_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def setup_visit_counters_table():
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS visit_counters (
            period_type TEXT NOT NULL,
            period_value TEXT NOT NULL,
            count INTEGER NOT NULL,
            PRIMARY KEY (period_type, period_value)
        )
    ''')
    # Ensure a row for total exists
    c.execute('INSERT OR IGNORE INTO visit_counters (period_type, period_value, count) VALUES (?, ?, ?)',
              ('total', 'all', 0))
    conn.commit()
    conn.close()

setup_visit_counters_table()

def increment_visit_counters():
    now = datetime.datetime.utcnow()
    periods = [
        ('hour', now.strftime('%Y-%m-%d-%H')),
        ('day', now.strftime('%Y-%m-%d')),
        ('week', f"{now.strftime('%Y')}-W{now.isocalendar()[1]:02d}"),
        ('month', now.strftime('%Y-%m')),
        ('year', now.strftime('%Y')),
        ('total', 'all')
    ]
    conn = get_db()
    c = conn.cursor()
    for period_type, period_value in periods:
        c.execute('INSERT OR IGNORE INTO visit_counters (period_type, period_value, count) VALUES (?, ?, ?)',
                  (period_type, period_value, 0))
        c.execute('UPDATE visit_counters SET count = count + 1 WHERE period_type = ? AND period_value = ?',
                  (period_type, period_value))
    conn.commit()
    conn.close()

def get_visit_count(period_type, period_value=None):
    conn = get_db()
    c = conn.cursor()
    if period_value:
        c.execute('SELECT count FROM visit_counters WHERE period_type = ? AND period_value = ?', (period_type, period_value))
        row = c.fetchone()
        conn.close()
        return row['count'] if row else 0
    else:
        # Get the latest period
        c.execute('SELECT count FROM visit_counters WHERE period_type = ? ORDER BY period_value DESC LIMIT 1', (period_type,))
        row = c.fetchone()
        conn.close()
        return row['count'] if row else 0

def get_time_series(period_type, length):
    conn = get_db()
    c = conn.cursor()
    # Get the last N periods
    c.execute('SELECT period_value, count FROM visit_counters WHERE period_type = ? ORDER BY period_value DESC LIMIT ?', (period_type, length))
    rows = c.fetchall()
    conn.close()
    # Return in chronological order
    return [(row['period_value'], row['count']) for row in reversed(rows)]

# Helper functions for stats

def get_current_period_value(period_type):
    now = datetime.datetime.utcnow()
    if period_type == 'hour':
        return now.strftime('%Y-%m-%d-%H')
    elif period_type == 'day':
        return now.strftime('%Y-%m-%d')
    elif period_type == 'week':
        return f"{now.strftime('%Y')}-W{now.isocalendar()[1]:02d}"
    elif period_type == 'month':
        return now.strftime('%Y-%m')
    elif period_type == 'year':
        return now.strftime('%Y')
    elif period_type == 'total':
        return 'all'
    return ''

def get_stats():
    stats = {}
    for period in ['hour', 'day', 'week', 'month', 'year', 'total']:
        stats[period] = get_visit_count(period, get_current_period_value(period))
    return stats
