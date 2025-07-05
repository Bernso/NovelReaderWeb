#!/usr/bin/env python3
"""
Debug script for comments system
Run this on PythonAnywhere to diagnose issues
"""

import os
import sqlite3
import sys

def check_environment():
    """Check the environment"""
    print("🔍 Environment Check")
    print("=" * 40)
    print(f"PythonAnywhere: {'PYTHONANYWHERE_SITE' in os.environ}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Home directory: {os.path.expanduser('~')}")
    print(f"Python version: {sys.version}")
    print()

def check_database_path():
    """Check database path detection"""
    print("🗄️ Database Path Check")
    print("=" * 40)
    
    try:
        import comments_db
        print("✅ comments_db module imported successfully")
        
        # Test the path detection
        db_path = comments_db.get_comments_db_path()
        print(f"Database path: {db_path}")
        
        # Check if file exists
        if os.path.exists(db_path):
            print(f"✅ Database file exists at: {db_path}")
            file_size = os.path.getsize(db_path)
            print(f"File size: {file_size} bytes")
        else:
            print(f"❌ Database file does not exist at: {db_path}")
        
        return db_path
    except Exception as e:
        print(f"❌ Error importing comments_db: {e}")
        return None

def test_database_connection(db_path):
    """Test database connection"""
    print("\n🔌 Database Connection Test")
    print("=" * 40)
    
    if not db_path:
        print("❌ No database path available")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"Found {len(tables)} tables:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Check if Comments table exists
        if ('Comments',) in tables:
            print("✅ Comments table exists")
            
            # Check table structure
            cursor.execute("PRAGMA table_info(Comments)")
            columns = cursor.fetchall()
            print(f"Comments table has {len(columns)} columns:")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
        else:
            print("❌ Comments table does not exist")
        
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_comment_operations():
    """Test comment operations"""
    print("\n💬 Comment Operations Test")
    print("=" * 40)
    
    try:
        import comments_db
        
        # Test adding a comment
        print("Testing add_comment...")
        success, message = comments_db.add_comment(
            novel_name="Test Novel",
            chapter_number="1",
            user_name="Test User",
            comment_text="Test comment for debugging",
            ip_address="127.0.0.1"
        )
        
        if success:
            print("✅ Comment added successfully")
            
            # Test getting comments
            print("Testing get_comments...")
            comments = comments_db.get_comments("Test Novel", "1")
            print(f"✅ Retrieved {len(comments)} comments")
            
            # Test comment count
            print("Testing get_comment_count...")
            count = comments_db.get_comment_count("Test Novel", "1")
            print(f"✅ Comment count: {count}")
            
            return True
        else:
            print(f"❌ Failed to add comment: {message}")
            return False
            
    except Exception as e:
        print(f"❌ Comment operations test failed: {e}")
        return False

def check_file_permissions():
    """Check file permissions"""
    print("\n📁 File Permissions Check")
    print("=" * 40)
    
    test_locations = [
        '.',  # Current directory
        '/tmp',  # Temporary directory
        os.path.expanduser('~')  # Home directory
    ]
    
    for location in test_locations:
        try:
            test_file = os.path.join(location, 'test_write.tmp')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            print(f"✅ Writable: {location}")
        except Exception as e:
            print(f"❌ Not writable: {location} ({e})")

def main():
    """Run all diagnostic tests"""
    print("🚀 Comments System Diagnostic")
    print("=" * 50)
    
    # Run tests
    check_environment()
    db_path = check_database_path()
    conn_success = test_database_connection(db_path)
    check_file_permissions()
    comment_success = test_comment_operations()
    
    # Summary
    print("\n📋 Diagnostic Summary")
    print("=" * 50)
    print(f"Database connection: {'✅ PASS' if conn_success else '❌ FAIL'}")
    print(f"Comment operations: {'✅ PASS' if comment_success else '❌ FAIL'}")
    
    if conn_success and comment_success:
        print("\n🎉 All tests passed! Your comments system should work.")
    else:
        print("\n⚠️ Some tests failed. Here are the next steps:")
        print("1. Run: python setup_comments.py")
        print("2. Restart your web app on PythonAnywhere")
        print("3. Try the diagnostic again")

if __name__ == "__main__":
    main() 