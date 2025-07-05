#!/usr/bin/env python3
"""
Simple setup script for comments system
Works on both local computer and PythonAnywhere free tier
"""

import os
import sqlite3

def detect_environment():
    """Detect if we're running on PythonAnywhere"""
    is_pythonanywhere = 'PYTHONANYWHERE_SITE' in os.environ
    print(f"Environment: {'PythonAnywhere' if is_pythonanywhere else 'Local Computer'}")
    return is_pythonanywhere

def setup_database():
    """Setup the comments database"""
    print("\n🗄️ Setting up database...")
    
    is_pa = detect_environment()
    
    if is_pa:
        # PythonAnywhere - use /tmp directory
        db_path = '/tmp/comments.db'
        print(f"Using database at: {db_path}")
    else:
        # Local - use current directory
        db_path = 'comments.db'
        print(f"Using database at: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create Comments table
        cursor.execute('''
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
        cursor.execute('''
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
        cursor.execute('''
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
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS RateLimit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip_address VARCHAR(45) NOT NULL,
                action_type VARCHAR(50) NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_comments_novel_chapter ON Comments(novel_name, chapter_number)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_rate_limit_ip_action ON RateLimit(ip_address, action_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_rate_limit_timestamp ON RateLimit(timestamp)')
        
        conn.commit()
        conn.close()
        print("✅ Database setup complete!")
        return True
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

def setup_moderation_key():
    """Setup moderation key file"""
    print("\n🔐 Setting up moderation key...")
    
    is_pa = detect_environment()
    
    if is_pa:
        # PythonAnywhere - use /tmp directory
        key_path = '/tmp/moderation.txt'
    else:
        # Local - use current directory
        key_path = 'moderation.txt'
    
    try:
        with open(key_path, 'w') as f:
            f.write('moderator_key_2024_secure_access_only')
        print(f"✅ Moderation key created at: {key_path}")
        print("🔑 Default key: moderator_key_2024_secure_access_only")
        print("⚠️  IMPORTANT: Change this key in production!")
        return True
    except Exception as e:
        print(f"❌ Failed to create moderation key: {e}")
        return False

def test_system():
    """Test the comments system"""
    print("\n🧪 Testing comments system...")
    
    try:
        import comments_db
        
        # Test adding a comment
        success, message = comments_db.add_comment(
            novel_name="Test Novel",
            chapter_number="1",
            user_name="Test User",
            comment_text="Test comment",
            ip_address="127.0.0.1"
        )
        
        if success:
            print("✅ Comment system test passed!")
            
            # Clean up test data
            try:
                comments = comments_db.get_comments("Test Novel", "1")
                if comments:
                    # Delete test comment (you might need to add a delete function)
                    print("✅ Test comment added and retrieved successfully")
            except:
                pass
        else:
            print(f"❌ Comment system test failed: {message}")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Comments system test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Comments System Setup")
    print("=" * 40)
    
    # Detect environment
    is_pa = detect_environment()
    
    # Setup database
    db_success = setup_database()
    
    # Setup moderation key
    key_success = setup_moderation_key()
    
    # Test system
    test_success = test_system()
    
    # Summary
    print("\n📋 Setup Summary")
    print("=" * 40)
    print(f"Database setup: {'✅ PASS' if db_success else '❌ FAIL'}")
    print(f"Moderation key: {'✅ PASS' if key_success else '❌ FAIL'}")
    print(f"System test: {'✅ PASS' if test_success else '❌ FAIL'}")
    
    if db_success and key_success and test_success:
        print("\n🎉 Setup complete! Your comments system is ready.")
        print("\n📝 Access information:")
        print("- Moderation URL: /moderation")
        print("- Default key: moderator_key_2024_secure_access_only")
        if is_pa:
            print("- Database: /tmp/comments.db")
            print("- Moderation key: /tmp/moderation.txt")
        else:
            print("- Database: comments.db")
            print("- Moderation key: moderation.txt")
    else:
        print("\n⚠️ Some setup steps failed. Check the output above for details.")

if __name__ == "__main__":
    main() 