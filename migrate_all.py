import sqlite3
import os
import hashlib

IS_PYTHONANYWHERE = 'PYTHONANYWHERE_SITE' in os.environ

def get_comments_db_path():
    if IS_PYTHONANYWHERE:
        possible_paths = [
            '/tmp/comments.db',
            os.path.join(os.path.expanduser('~'), 'comments.db'),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), 'comments.db')
        ]
        for path in possible_paths:
            try:
                test_conn = sqlite3.connect(path)
                test_conn.close()
                print(f"Using database at: {path}")
                return path
            except (sqlite3.OperationalError, PermissionError):
                continue
        print("Warning: Using /tmp/comments.db as fallback")
        return '/tmp/comments.db'
    else:
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'comments.db')

def add_device_id_columns(conn):
    c = conn.cursor()
    # Reactions
    c.execute("PRAGMA table_info(Reactions)")
    columns = [col[1] for col in c.fetchall()]
    if 'device_id' not in columns:
        print("Adding device_id column to Reactions table...")
        c.execute('ALTER TABLE Reactions ADD COLUMN device_id VARCHAR(255)')
        c.execute('SELECT reaction_id, ip_address FROM Reactions WHERE device_id IS NULL')
        for reaction_id, ip_address in c.fetchall():
            device_id = hashlib.md5(f"{ip_address}:LegacyDevice".encode('utf-8')).hexdigest()
            c.execute('UPDATE Reactions SET device_id = ? WHERE reaction_id = ?', (device_id, reaction_id))
    # ChapterReactions
    c.execute("PRAGMA table_info(ChapterReactions)")
    columns = [col[1] for col in c.fetchall()]
    if 'device_id' not in columns:
        print("Adding device_id column to ChapterReactions table...")
        c.execute('ALTER TABLE ChapterReactions ADD COLUMN device_id VARCHAR(255)')
        c.execute('SELECT reaction_id, ip_address FROM ChapterReactions WHERE device_id IS NULL')
        for reaction_id, ip_address in c.fetchall():
            device_id = hashlib.md5(f"{ip_address}:LegacyDevice".encode('utf-8')).hexdigest()
            c.execute('UPDATE ChapterReactions SET device_id = ? WHERE reaction_id = ?', (device_id, reaction_id))

def deduplicate_reactions(conn):
    c = conn.cursor()
    print("Deduplicating Reactions table...")
    c.execute('''
        DELETE FROM Reactions
        WHERE (comment_id, device_id, timestamp) NOT IN (
            SELECT comment_id, device_id, MAX(timestamp)
            FROM Reactions
            GROUP BY comment_id, device_id
        )
    ''')
    print("Deduplication complete for Reactions.")

def deduplicate_chapter_reactions(conn):
    c = conn.cursor()
    print("Deduplicating ChapterReactions table...")
    c.execute('''
        DELETE FROM ChapterReactions
        WHERE (novel_name, chapter_number, device_id, timestamp) NOT IN (
            SELECT novel_name, chapter_number, device_id, MAX(timestamp)
            FROM ChapterReactions
            GROUP BY novel_name, chapter_number, device_id
        )
    ''')
    print("Deduplication complete for ChapterReactions.")

def add_unique_constraints(conn):
    c = conn.cursor()
    print("Adding unique constraints...")
    try:
        c.execute('DROP INDEX IF EXISTS idx_reactions_unique')
    except:
        pass
    try:
        c.execute('DROP INDEX IF EXISTS idx_chapter_reactions_unique')
    except:
        pass
    c.execute('''
        CREATE UNIQUE INDEX IF NOT EXISTS idx_reactions_unique
        ON Reactions(comment_id, device_id)
    ''')
    c.execute('''
        CREATE UNIQUE INDEX IF NOT EXISTS idx_chapter_reactions_unique
        ON ChapterReactions(novel_name, chapter_number, device_id)
    ''')
    print("Unique constraints added.")

def main():
    db_path = get_comments_db_path()
    print(f"Migrating database at: {db_path}")
    conn = sqlite3.connect(db_path)
    try:
        add_device_id_columns(conn)
        deduplicate_reactions(conn)
        deduplicate_chapter_reactions(conn)
        add_unique_constraints(conn)
        conn.commit()
        print("✅ All migrations complete!")
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    main() 