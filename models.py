from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    novel_name = db.Column(db.String(200), nullable=False)
    chapter_number = db.Column(db.Float, nullable=False)
    username = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)
    pinned = db.Column(db.Boolean, default=False)
    
    # Add relationship for replies
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]),
                            lazy='dynamic', cascade='all, delete-orphan')