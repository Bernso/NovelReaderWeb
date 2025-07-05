import sqlite3
import os
import time
import hashlib
from datetime import datetime, timedelta

# PythonAnywhere detection
IS_PYTHONANYWHERE = 'PYTHONANYWHERE_SITE' in os.environ

def generate_device_id(ip_address, user_agent):
    """Generate a unique device identifier based on IP and user agent"""
    if not user_agent:
        user_agent = "Unknown"
    
    # Create a hash of IP + user agent to create a unique device identifier
    device_string = f"{ip_address}:{user_agent}"
    device_hash = hashlib.md5(device_string.encode('utf-8')).hexdigest()
    return device_hash

def get_comments_db_path():
    """Get the path to the comments database file with PythonAnywhere compatibility"""
    if IS_PYTHONANYWHERE:
        # Try multiple possible locations for PythonAnywhere
        possible_paths = [
            '/tmp/comments.db',  # Temporary directory (always writable)
            os.path.join(os.path.expanduser('~'), 'comments.db'),  # Home directory
            os.path.join(os.path.dirname(os.path.abspath(__file__)), 'comments.db')  # Current directory
        ]
        
        for path in possible_paths:
            try:
                # Test if we can write to this location
                test_conn = sqlite3.connect(path)
                test_conn.close()
                print(f"Using database at: {path}")
                return path
            except (sqlite3.OperationalError, PermissionError):
                continue
        
        # If all else fails, use /tmp
        print("Warning: Using /tmp/comments.db as fallback")
        return '/tmp/comments.db'
    else:
        # Local development - use current directory
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'comments.db')

def init_comments_db():
    """Initialize the comments database with required tables"""
    db_path = get_comments_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Create Comments table
    c.execute('''
        CREATE TABLE IF NOT EXISTS Comments (
            comment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            novel_name VARCHAR(255) NOT NULL,
            chapter_number VARCHAR(50) NOT NULL,
            user_name VARCHAR(100) NOT NULL,
            comment_text TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            ip_address VARCHAR(45),
            user_agent TEXT
        )
    ''')
    
    # Create Reactions table
    c.execute('''
        CREATE TABLE IF NOT EXISTS Reactions (
            reaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            comment_id INTEGER NOT NULL,
            reaction_type VARCHAR(20) NOT NULL,
            device_id VARCHAR(255) NOT NULL,
            ip_address VARCHAR(45) NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (comment_id) REFERENCES Comments (comment_id) ON DELETE CASCADE
        )
    ''')
    
    # Create Chapter Reactions table
    c.execute('''
        CREATE TABLE IF NOT EXISTS ChapterReactions (
            reaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            novel_name VARCHAR(255) NOT NULL,
            chapter_number VARCHAR(50) NOT NULL,
            reaction_type VARCHAR(20) NOT NULL,
            device_id VARCHAR(255) NOT NULL,
            ip_address VARCHAR(45) NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create Rate Limiting table
    c.execute('''
        CREATE TABLE IF NOT EXISTS RateLimit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip_address VARCHAR(45) NOT NULL,
            action_type VARCHAR(50) NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create indexes for faster queries
    c.execute('''
        CREATE INDEX IF NOT EXISTS idx_comments_novel_chapter 
        ON Comments(novel_name, chapter_number)
    ''')
    
    c.execute('''
        CREATE INDEX IF NOT EXISTS idx_rate_limit_ip_action 
        ON RateLimit(ip_address, action_type)
    ''')
    
    c.execute('''
        CREATE INDEX IF NOT EXISTS idx_rate_limit_timestamp 
        ON RateLimit(timestamp)
    ''')
    
    conn.commit()
    conn.close()

def check_rate_limit(ip_address, action_type='comment', max_attempts=3, window_minutes=5):
    """
    Check if user is rate limited
    Returns: (is_limited, remaining_attempts, reset_time)
    """
    db_path = get_comments_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    try:
        # Clean old rate limit entries (older than window_minutes)
        cutoff_time = datetime.now() - timedelta(minutes=window_minutes)
        c.execute('''
            DELETE FROM RateLimit 
            WHERE timestamp < ? AND action_type = ?
        ''', (cutoff_time, action_type))
        
        # Count recent attempts
        c.execute('''
            SELECT COUNT(*) FROM RateLimit 
            WHERE ip_address = ? AND action_type = ?
        ''', (ip_address, action_type))
        
        current_attempts = c.fetchone()[0]
        
        # Check if rate limited
        is_limited = current_attempts >= max_attempts
        remaining_attempts = max(0, max_attempts - current_attempts)
        
        # Calculate reset time (when oldest entry expires)
        if current_attempts > 0:
            c.execute('''
                SELECT timestamp FROM RateLimit 
                WHERE ip_address = ? AND action_type = ?
                ORDER BY timestamp ASC LIMIT 1
            ''', (ip_address, action_type))
            oldest_entry = c.fetchone()
            if oldest_entry:
                oldest_time = datetime.fromisoformat(oldest_entry[0])
                reset_time = oldest_time + timedelta(minutes=window_minutes)
            else:
                reset_time = datetime.now()
        else:
            reset_time = datetime.now()
        
        conn.commit()
        return is_limited, remaining_attempts, reset_time
        
    except Exception as e:
        print(f"Error checking rate limit: {e}")
        return False, max_attempts, datetime.now()
    finally:
        conn.close()

def record_rate_limit_attempt(ip_address, action_type='comment'):
    """Record a rate limit attempt"""
    db_path = get_comments_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    try:
        c.execute('''
            INSERT INTO RateLimit (ip_address, action_type, timestamp)
            VALUES (?, ?, ?)
        ''', (ip_address, action_type, datetime.now()))
        
        conn.commit()
    except Exception as e:
        print(f"Error recording rate limit attempt: {e}")
    finally:
        conn.close()

def add_comment(novel_name, chapter_number, user_name, comment_text, ip_address=None, user_agent=None):
    """Add a new comment to the database"""
    db_path = get_comments_db_path()
    print(f"Adding comment to database at: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # Check if Comments table exists
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Comments'")
        if not c.fetchone():
            print("Comments table does not exist, initializing database...")
            init_comments_db()
            # Reconnect after initialization
            conn.close()
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
        
        c.execute('''
            INSERT INTO Comments (novel_name, chapter_number, user_name, comment_text, ip_address, user_agent)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (novel_name, chapter_number, user_name, comment_text, ip_address, user_agent))
        
        conn.commit()
        print("Comment added successfully")
        return True, "Comment added successfully"
    except Exception as e:
        print(f"Error adding comment: {e}")
        print(f"Database path: {db_path}")
        print(f"Novel: {novel_name}, Chapter: {chapter_number}")
        print(f"User: {user_name}, Text length: {len(comment_text) if comment_text else 0}")
        return False, f"Database error: {str(e)}"
    finally:
        try:
            conn.close()
        except:
            pass

def get_comments(novel_name, chapter_number, limit=50):
    """Get comments for a specific novel and chapter"""
    db_path = get_comments_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    try:
        c.execute('''
            SELECT comment_id, user_name, comment_text, timestamp, ip_address
            FROM Comments 
            WHERE novel_name = ? AND chapter_number = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (novel_name, chapter_number, limit))
        
        results = c.fetchall()
        comments = []
        for row in results:
            comments.append({
                'id': row[0],
                'name': row[1],
                'text': row[2],
                'timestamp': row[3],
                'ip_address': row[4]
            })
        
        return comments
    except Exception as e:
        print(f"Error getting comments: {e}")
        return []
    finally:
        conn.close()

def get_comment_count(novel_name, chapter_number):
    """Get the total number of comments for a chapter"""
    db_path = get_comments_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    try:
        c.execute('''
            SELECT COUNT(*) FROM Comments 
            WHERE novel_name = ? AND chapter_number = ?
        ''', (novel_name, chapter_number))
        
        result = c.fetchone()
        return result[0] if result else 0
    except Exception as e:
        print(f"Error getting comment count: {e}")
        return 0
    finally:
        conn.close()

def get_comment_reactions(comment_id):
    """Get reactions for a specific comment"""
    db_path = get_comments_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    try:
        c.execute('''
            SELECT reaction_type, COUNT(*) as count
            FROM Reactions 
            WHERE comment_id = ?
            GROUP BY reaction_type
        ''', (comment_id,))
        
        results = c.fetchall()
        reactions = {}
        for row in results:
            reactions[row[0]] = row[1]
        
        return reactions
    except Exception as e:
        print(f"Error getting comment reactions: {e}")
        return {}
    finally:
        conn.close()

def get_user_reactions_for_comment(comment_id, device_id):
    """Get user's reactions for a specific comment"""
    db_path = get_comments_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    try:
        c.execute('''
            SELECT reaction_type
            FROM Reactions 
            WHERE comment_id = ? AND device_id = ?
        ''', (comment_id, device_id))
        
        results = c.fetchall()
        user_reactions = [row[0] for row in results]
        return user_reactions
    except Exception as e:
        print(f"Error getting user reactions: {e}")
        return []
    finally:
        conn.close()

def add_reaction(comment_id, reaction_type, device_id, ip_address):
    """Add or update a reaction to a comment (one per device per comment)"""
    db_path = get_comments_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    try:
        # Remove any previous reaction from this device for this comment
        c.execute('''
            DELETE FROM Reactions 
            WHERE comment_id = ? AND device_id = ?
        ''', (comment_id, device_id))
        
        # If the user is toggling off (clicked the same reaction), don't add a new one
        # But since the frontend always sends the new type, we always add
        c.execute('''
            INSERT INTO Reactions (comment_id, reaction_type, device_id, ip_address)
            VALUES (?, ?, ?, ?)
        ''', (comment_id, reaction_type, device_id, ip_address))
        action = 'added'
        
        conn.commit()
        return True, action
    except Exception as e:
        print(f"Error adding reaction: {e}")
        return False, 'error'
    finally:
        conn.close()

def get_chapter_reactions(novel_name, chapter_number):
    """Get reactions for a specific chapter"""
    db_path = get_comments_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    try:
        c.execute('''
            SELECT reaction_type, COUNT(*) as count
            FROM ChapterReactions 
            WHERE novel_name = ? AND chapter_number = ?
            GROUP BY reaction_type
        ''', (novel_name, chapter_number))
        
        results = c.fetchall()
        reactions = {}
        for row in results:
            reactions[row[0]] = row[1]
        
        return reactions
    except Exception as e:
        print(f"Error getting chapter reactions: {e}")
        return {}
    finally:
        conn.close()

def get_user_chapter_reactions(novel_name, chapter_number, device_id):
    """Get user's reactions for a specific chapter"""
    db_path = get_comments_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    try:
        c.execute('''
            SELECT reaction_type
            FROM ChapterReactions 
            WHERE novel_name = ? AND chapter_number = ? AND device_id = ?
        ''', (novel_name, chapter_number, device_id))
        
        results = c.fetchall()
        user_reactions = [row[0] for row in results]
        return user_reactions
    except Exception as e:
        print(f"Error getting user chapter reactions: {e}")
        return []
    finally:
        conn.close()

def add_chapter_reaction(novel_name, chapter_number, reaction_type, device_id, ip_address):
    """Add or update a reaction to a chapter (one per device per chapter)"""
    db_path = get_comments_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    try:
        # Remove any previous reaction from this device for this chapter
        c.execute('''
            DELETE FROM ChapterReactions 
            WHERE novel_name = ? AND chapter_number = ? AND device_id = ?
        ''', (novel_name, chapter_number, device_id))
        
        # Always add the new reaction
        c.execute('''
            INSERT INTO ChapterReactions (novel_name, chapter_number, reaction_type, device_id, ip_address)
            VALUES (?, ?, ?, ?, ?)
        ''', (novel_name, chapter_number, reaction_type, device_id, ip_address))
        action = 'added'
        
        conn.commit()
        return True, action
    except Exception as e:
        print(f"Error adding chapter reaction: {e}")
        return False, 'error'
    finally:
        conn.close()

def get_comments_with_reactions(novel_name, chapter_number, limit=50, device_id=None):
    """Get comments with reaction counts and user's reactions"""
    db_path = get_comments_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    try:
        c.execute('''
            SELECT comment_id, user_name, comment_text, timestamp, ip_address
            FROM Comments 
            WHERE novel_name = ? AND chapter_number = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (novel_name, chapter_number, limit))
        
        results = c.fetchall()
        comments = []
        for row in results:
            comment_id = row[0]
            
            # Get reaction counts
            reactions = get_comment_reactions(comment_id)
            
            # Get user's reactions if device_id provided
            user_reactions = []
            if device_id:
                user_reactions = get_user_reactions_for_comment(comment_id, device_id)
            
            comments.append({
                'id': comment_id,
                'name': row[1],
                'text': row[2],
                'timestamp': row[3],
                'ip_address': row[4],
                'reactions': reactions,
                'user_reactions': user_reactions
            })
        
        return comments
    except Exception as e:
        print(f"Error getting comments with reactions: {e}")
        return []
    finally:
        conn.close()

def cleanup_old_rate_limits():
    """Clean up old rate limit entries (older than 1 hour)"""
    db_path = get_comments_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    try:
        cutoff_time = datetime.now() - timedelta(hours=1)
        c.execute('DELETE FROM RateLimit WHERE timestamp < ?', (cutoff_time,))
        conn.commit()
    except Exception as e:
        print(f"Error cleaning up rate limits: {e}")
    finally:
        conn.close()

def get_all_comments_for_moderation(limit=100):
    """Get all comments for moderation purposes"""
    db_path = get_comments_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    try:
        c.execute('''
            SELECT comment_id, novel_name, chapter_number, user_name, comment_text, timestamp, ip_address
            FROM Comments 
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        results = c.fetchall()
        comments = []
        for row in results:
            comments.append({
                'id': row[0],
                'novel_name': row[1],
                'chapter_number': row[2],
                'name': row[3],
                'text': row[4],
                'timestamp': row[5],
                'ip_address': row[6]
            })
        
        return comments
    except Exception as e:
        print(f"Error getting comments for moderation: {e}")
        return []
    finally:
        conn.close()

def delete_comment(comment_id):
    """Delete a comment by ID"""
    db_path = get_comments_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    try:
        # Delete associated reactions first
        c.execute('DELETE FROM Reactions WHERE comment_id = ?', (comment_id,))
        
        # Delete the comment
        c.execute('DELETE FROM Comments WHERE comment_id = ?', (comment_id,))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Error deleting comment: {e}")
        return False
    finally:
        conn.close()

def edit_comment(comment_id, new_text):
    """Edit a comment's text"""
    db_path = get_comments_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    try:
        c.execute('''
            UPDATE Comments 
            SET comment_text = ? 
            WHERE comment_id = ?
        ''', (new_text, comment_id))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Error editing comment: {e}")
        return False
    finally:
        conn.close()

# Initialize the database when the module is imported
init_comments_db() 