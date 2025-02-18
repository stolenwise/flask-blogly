from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

def connect_db(app):
    db.app = app
    db.init_app(app)

"""Models for Blogly."""
class Users(db.Model):
    """Users."""

    __tablename__ = "users"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    first_name = db.Column(db.String(50),
                     nullable=False)

    last_name = db.Column(db.String(50),
                     nullable=False)
    image_url = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f"<User {self.id}: {self.first_name} {self.last_name}>"
    
class Post(db.Model):
    """Posts"""
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Foreign key for User
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  
    
    # Define relationship after both classes have been defined
    user = db.relationship('Users', backref=db.backref('posts', lazy=True))  # Correct reference to 'Users'

    def __repr__(self):
        return f"<Post {self.id}: {self.title} {self.content}>"
