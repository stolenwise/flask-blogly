from flask_sqlalchemy import SQLAlchemy

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