import sqlite3
import os
from datetime import datetime

def get_db_path():
    """Get the path to the database file"""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'novel_views.db')

def init_db():
    """Initialize the database with required tables"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Create views table if it doesn't exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS novel_views (
            novel_name TEXT PRIMARY KEY,
            total_views INTEGER DEFAULT 0,
            last_updated TIMESTAMP
        )
    ''')
    
    # Create view history table for detailed tracking
    c.execute('''
        CREATE TABLE IF NOT EXISTS view_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            novel_name TEXT,
            view_type TEXT,
            timestamp TIMESTAMP,
            FOREIGN KEY (novel_name) REFERENCES novel_views(novel_name)
        )
    ''')
    
    conn.commit()
    conn.close()

def increment_view(novel_name, view_type='page_view'):
    """Increment the view count for a novel"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Update or insert the novel view count
    c.execute('''
        INSERT INTO novel_views (novel_name, total_views, last_updated)
        VALUES (?, 1, ?)
        ON CONFLICT(novel_name) DO UPDATE SET
        total_views = total_views + 1,
        last_updated = ?
    ''', (novel_name, current_time, current_time))
    
    # Add entry to view history
    c.execute('''
        INSERT INTO view_history (novel_name, view_type, timestamp)
        VALUES (?, ?, ?)
    ''', (novel_name, view_type, current_time))
    
    conn.commit()
    conn.close()

def get_novel_views(novel_name):
    """Get the total views for a novel"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    c.execute('SELECT total_views FROM novel_views WHERE novel_name = ?', (novel_name,))
    result = c.fetchone()
    
    conn.close()
    return result[0] if result else 0

def get_all_novel_views():
    """Get views for all novels"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    c.execute('SELECT novel_name, total_views FROM novel_views ORDER BY total_views DESC')
    results = c.fetchall()
    
    conn.close()
    return dict(results)

# Initialize the database when the module is imported
init_db() 