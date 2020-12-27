# coding=utf-8
"""
@Description: 模型
@FilePath: /blog/app/models.py
@Author: liu.junlei@foxmail.com
@Date: 2020-12-27 20:24:58
@LastEditTime: 2020-12-27 20:29:05
"""
import json

from flask import session

from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class Follow(db.Model):
    """用户关注关系表
    """
    __tablename__ = 'follow'
    follower_id = db.Column(db.Integer,
                            db.ForeignKey('user.user_id'),
                            primary_key=True)
    followed_id = db.Column(db.Integer,
                            db.ForeignKey('user.user_id'),
                            primary_key=True)
    follow_time = db.Column(db.DateTime, default=datetime.now)


class PostLike(db.Model):
    """点赞关系表
    """
    __tablename__ = 'postlike'
    author_id = db.Column(db.Integer,
                          db.ForeignKey('user.user_id'),
                          primary_key=True)
    post_id = db.Column(db.Integer,
                        db.ForeignKey('posts.post_id'),
                        primary_key=True)
    create_time = db.Column(db.DateTime, default=datetime.now)


class Collection(db.Model):
    """收藏关系表
    """
    __tablename__ = 'collection'
    author_id = db.Column(db.Integer,
                          db.ForeignKey('user.user_id'),
                          primary_key=True)
    post_id = db.Column(db.Integer,
                        db.ForeignKey('posts.post_id'),
                        primary_key=True)
    create_time = db.Column(db.DateTime, default=datetime.now)


class User(db.Model):
    """用户表
    """
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True, index=True)
    username = db.Column(db.String(20), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    photo = db.Column(db.String(128), default='/static/default.jpg')
    post = db.relationship('Post', backref='author', lazy='dynamic')
    comment = db.relationship('Comment', backref='author', lazy='dynamic')
    followed = db.relationship('Follow',
                               foreign_keys=[Follow.follower_id],
                               backref=db.backref(
                                   'follower',
                                   lazy='joined',
                               ),
                               lazy='dynamic',
                               cascade='all, delete-orphan')
    follower = db.relationship('Follow',
                               foreign_keys=[Follow.followed_id],
                               backref=db.backref('followed', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')
    like_post = db.relationship('PostLike',
                                backref=db.backref(
                                    'auhtor',
                                    lazy='joined',
                                    order_by=PostLike.create_time.desc()),
                                lazy='dynamic',
                                cascade='all, delete-orphan')
    collection = db.relationship('Collection',
                                 backref=db.backref(
                                     'author',
                                     lazy='joined',
                                     order_by=Collection.create_time.desc()),
                                 lazy='dynamic',
                                 cascade='all, delete-orphan')

    @property
    def password(self):
        """自定义password属性
        """
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        """password属性赋值方法
        """
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """验证密码
        """
        return check_password_hash(self.password_hash, password)


class Post(db.Model):
    """文章表
    """
    __tablename__ = 'posts'
    post_id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    title = db.Column(db.String(100), index=True)
    content = db.Column(db.Text)
    create_time = db.Column(db.DateTime, index=True, default=datetime.now)
    update_time = db.Column(db.DateTime, default=datetime.now)
    comment = db.relationship('Comment', backref='post', lazy='dynamic')
    label = db.Column(db.String(20), index=True, default='')
    reading_num = db.Column(db.Integer, default=0)
    liked = db.relationship('PostLike',
                            backref=db.backref(
                                'post',
                                lazy='joined',
                                order_by=PostLike.create_time.desc()),
                            lazy='dynamic',
                            cascade='all, delete-orphan')
    collected = db.relationship('Collection',
                                backref=db.backref(
                                    'post',
                                    lazy='joined',
                                    order_by=Collection.create_time.desc()),
                                lazy='dynamic',
                                cascade='all, delete-orphan')


class Comment(db.Model):
    """评论表
    """
    __tablename__ = 'comment'
    comment_id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.post_id'))
    content = db.Column(db.String(500))
    create_time = db.Column(db.DateTime, default=datetime.now)
    root_comment_id = db.Column(db.Integer, default=-1)
    to_comment_id = db.Column(db.Integer, default=-1)


def to_dict(model):
    """数据库查询结果对象转字典
    """
    return {c.name: getattr(model, c.name) for c in model.__table__.columns}


class DateEncoder(json.JSONEncoder):
    """日期对象json编码方法
    """
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return json.JSONEncoder.default(self, obj)


def get_user(email=None, username=None):
    """查询用户
    """
    if email:
        return db.session.query(User).filter_by(email=email).first()
    if username:
        return db.session.query(User).filter_by(username=username).first()
    return None


def get_current_user():
    """获取当前用户
    """
    return get_user(email=session['email']) if 'email' in session else None


def add_or_update(row):
    """插入或更新行记录
    """
    db.session.add(row)
    try:
        db.session.commit()
    except:
        db.session.rollback()


def delete(row):
    """删除行记录
    """
    db.session.delete(row)
    try:
        db.session.commit()
    except:
        db.session.rollback()
