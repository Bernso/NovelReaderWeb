# 🚀 Deployment Guide - Comments System

This guide works for both **local computer** and **PythonAnywhere free tier**.

## 📋 Prerequisites

### Local Computer:
- Python 3.7+
- Flask installed: `pip install flask flask-caching flask-limiter`

### PythonAnywhere:
- Free account at [pythonanywhere.com](https://www.pythonanywhere.com)
- Web app configured

## 🔧 Quick Setup

### Step 1: Run Setup Script
```bash
python setup_comments.py
```

This script will:
- ✅ Detect your environment (local vs PythonAnywhere)
- ✅ Create the database in the right location
- ✅ Set up the moderation key file
- ✅ Test the system

### Step 2: Start Your App

**Local:**
```bash
python app.py
```

**PythonAnywhere:**
- Go to your Web app dashboard
- Click "Reload" to restart the app

## 🔑 Access Information

### Moderation Panel:
- **URL:** `yourdomain.com/moderation`
- **Default Key:** `moderator_key_2024_secure_access_only`

### Database Location:
- **Local:** `comments.db` (in your project folder)
- **PythonAnywhere:** `/tmp/comments.db`

### Moderation Key Location:
- **Local:** `moderation.txt` (in your project folder)
- **PythonAnywhere:** `/tmp/moderation.txt`

## 🐛 Troubleshooting

### Common Issues:

**1. "Database not found" error:**
- Run `python setup_comments.py` again
- Check if the database file was created

**2. "Moderation key not found" error:**
- Run `python setup_comments.py` again
- Check if the moderation.txt file was created

**3. Session errors on PythonAnywhere:**
- The app automatically uses filesystem sessions in `/tmp`
- Restart your web app after changes

**4. Permission errors on PythonAnywhere:**
- The system automatically uses `/tmp` directory (always writable)
- No manual configuration needed

### Testing:

**Test the comment system:**
1. Go to any chapter page
2. Scroll down to the comments section
3. Try adding a comment

**Test the moderation panel:**
1. Go to `/moderation`
2. Enter the key: `moderator_key_2024_secure_access_only`
3. You should see the moderation dashboard

## 🔒 Security Notes

### For Production:
1. **Change the default moderation key** in the `moderation.txt` file
2. **Use HTTPS** (requires paid PythonAnywhere plan)
3. **Regular backups** of the database file

### Default Keys (Change These!):
- Moderation key: `moderator_key_2024_secure_access_only`
- Flask secret: Check your `config.py` file

## 📁 File Locations

### Local Computer:
```
your-project/
├── app.py
├── comments_db.py
├── setup_comments.py
├── comments.db          ← Created by setup
├── moderation.txt       ← Created by setup
└── templates/
    ├── moderation_login.html
    └── moderation_dashboard.html
```

### PythonAnywhere:
```
/home/yourusername/mysite/
├── app.py
├── comments_db.py
├── setup_comments.py
└── templates/
    ├── moderation_login.html
    └── moderation_dashboard.html

/tmp/                    ← System files
├── comments.db          ← Created by setup
├── moderation.txt       ← Created by setup
└── flask_session/       ← Session files
```

## 🎯 Quick Commands

### Setup:
```bash
python setup_comments.py
```

### Test:
```bash
python -c "import comments_db; print('Comments system ready!')"
```

### Check Environment:
```bash
python -c "import os; print('PythonAnywhere' if 'PYTHONANYWHERE_SITE' in os.environ else 'Local Computer')"
```

## 💡 Pro Tips

1. **Always restart your web app** on PythonAnywhere after making changes
2. **Check the error logs** in PythonAnywhere's Web tab if something doesn't work
3. **The system automatically adapts** to your environment - no manual configuration needed
4. **Database is in `/tmp` on PythonAnywhere** - it will be recreated if the server restarts, but that's normal for the free tier

## 🆘 Getting Help

### PythonAnywhere Support:
- [PythonAnywhere Help](https://www.pythonanywhere.com/help/)
- [Community Forum](https://www.pythonanywhere.com/forums/)

### Common Solutions:
1. **Restart your web app** after any changes
2. **Run the setup script** if you get database errors
3. **Check file permissions** if you get permission errors
4. **Clear browser cache** if changes don't appear

---

**That's it!** Your comments system should work on both local and PythonAnywhere environments. 🎉 