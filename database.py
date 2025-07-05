import sqlite3
import os

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
