from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Create Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///comments.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Define Comment model
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    novel_name = db.Column(db.String(200), nullable=False)
    chapter_number = db.Column(db.Float, nullable=False)
    username = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)
    pinned = db.Column(db.Boolean, default=False, nullable=False)
    
    
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]))
    

# Create database tables
with app.app_context():
    db.create_all()
    print("Database tables created successfully!")