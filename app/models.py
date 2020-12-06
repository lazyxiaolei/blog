from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class Follow(db.Model):
    __tablename__ = 'follow'
    follower_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True)
    follow_time = db.Column(db.DateTime, default=datetime.now)

class PostLike(db.Model):
    __tablename__ = 'postlike'
    author_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.post_id'), primary_key=True)
    create_time = db.Column(db.DateTime, default=datetime.now)


class Collection(db.Model):
    __tablename__ = 'collection'
    author_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.post_id'), primary_key=True)
    create_time = db.Column(db.DateTime, default=datetime.now)


class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True, index=True)
    username = db.Column(db.String(20), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    photo = db.Column(db.String(128), default='static/default.jpg')
    post = db.relationship('Post', backref='author', lazy='dynamic')
    comment = db.relationship('Comment', backref='author', lazy='dynamic')
    followed = db.relationship('Follow', foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower', lazy='joined',),
                               lazy='dynamic', cascade='all, delete-orphan')
    follower = db.relationship('Follow', foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed', lazy='joined'),
                               lazy='dynamic', cascade='all, delete-orphan')
    like_post = db.relationship('PostLike',backref=db.backref('auhtor',lazy='joined', order_by=PostLike.create_time.desc()),
                                lazy='dynamic', cascade='all, delete-orphan')
    collection = db.relationship('Collection', backref=db.backref('author', lazy='joined', order_by=Collection.create_time.desc()),
                                 lazy='dynamic', cascade='all, delete-orphan')

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self,password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self,password):
        return check_password_hash(self.password_hash,password)


class Post(db.Model):
    __tablename__ = 'posts'
    post_id = db.Column(db.Integer,primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    title = db.Column(db.String(100), index=True)
    content = db.Column(db.Text)
    create_time = db.Column(db.DateTime, index=True, default=datetime.now)
    update_time = db.Column(db.DateTime, default=datetime.now)
    comment = db.relationship('Comment', backref='post', lazy='dynamic')
    label = db.Column(db.String(20),index=True, default='')
    reading_num = db.Column(db.Integer, default=0)
    liked_user = db.relationship('PostLike', backref=db.backref('post', lazy='joined',
                                                                order_by=PostLike.create_time.desc()),
                                lazy='dynamic', cascade='all, delete-orphan')
    collection = db.relationship('Collection', backref=db.backref('post', lazy='joined',
                                                                order_by=Collection.create_time.desc()),
                                 lazy='dynamic', cascade='all, delete-orphan')


class Comment(db.Model):
    __tablename__= 'comment'
    comment_id = db.Column(db.Integer,primary_key=True)
    author_id = db.Column(db.Integer,db.ForeignKey('user.user_id'))
    post_id = db.Column(db.Integer,db.ForeignKey('posts.post_id'))
    content = db.Column(db.String(500))
    create_time = db.Column(db.DateTime, default=datetime.now)
    root_comment_id = db.Column(db.Integer, default=-1)
    to_comment_id = db.Column(db.Integer, default=-1)


def to_dict(model):
    return {c.name: getattr(model, c.name) for c in model.__table__.columns}
