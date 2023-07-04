from datetime import datetime
from vsapp import db, login_manager
from flask_login import UserMixin

# Get the user by ID for the login manager
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Database table to store the realtionship between users and liked posts
likes = db.Table('likes',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'), primary_key=True)
)


# User class (used also to create a SQLlite table)
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default user.png')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)
    comments = db.relationship('Comment', backref='author', lazy=True)
    liked_posts = db.relationship('Post', secondary=likes, lazy='subquery', backref=db.backref('liked_by', lazy=True))

    
    # the output whrn I ask the contents of the user (note that the password is not displayed)
    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


# Post class (also used to create the database table)
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False, default='')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comments = db.relationship('Comment', backref='post', lazy=True)
    public = db.Column(db.Boolean, default=True)
    like_count = db.Column(db.Integer, default=0)
    
    
    # the ouput when I ask the contents of the post
    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"

# Comment class (used to create a table in the database with all the comments)
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    
    
    # the output in the terminal when you want to glance at the table
    def __repr__(self):
        return f"Comment('{self.content}', '{self.date_posted}')"
