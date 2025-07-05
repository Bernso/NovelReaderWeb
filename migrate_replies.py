#!/usr/bin/env python3
"""
Migration script to add reply functionality to existing comment databases.
This script adds the parent_comment_id column to the Comments table.
"""

import sqlite3
import os
from comments_db import get_comments_db_path, IS_PYTHONANYWHERE

def migrate_database():
    """Migrate the database to support replies"""
    db_path = get_comments_db_path()
    print(f"Migrating database at: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # Check if parent_comment_id column already exists
        c.execute("PRAGMA table_info(Comments)")
        columns = [column[1] for column in c.fetchall()]
        
        if 'parent_comment_id' in columns:
            print("Database already has parent_comment_id column. Migration not needed.")
            return True
        
        print("Adding parent_comment_id column to Comments table...")
        
        # Add the parent_comment_id column
        c.execute('''
            ALTER TABLE Comments 
            ADD COLUMN parent_comment_id INTEGER DEFAULT NULL
        ''')
        
        # Add foreign key constraint
        c.execute('''
            CREATE INDEX IF NOT EXISTS idx_comments_parent 
            ON Comments(parent_comment_id)
        ''')
        
        conn.commit()
        print("Migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error during migration: {e}")
        return False
    finally:
        try:
            conn.close()
        except:
            pass

if __name__ == "__main__":
    print("Starting database migration for reply functionality...")
    success = migrate_database()
    if success:
        print("Migration completed successfully!")
    else:
        print("Migration failed!") 