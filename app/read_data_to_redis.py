# coding=utf-8
"""
@Description: 从mysql读取数据至redis
@FilePath: /blog/app/read_data_to_redis.py
@Author: liu.junlei@foxmail.com
@Date: 2020-12-27 20:29:57
@LastEditTime: 2020-12-27 20:32:15
"""

from app.redisDB import red
from app import creat_app
from app import db
from models import Post
from models import to_dict, DateEncoder
import json

app = creat_app()
app.app_context().push()


def read_hotest_postlist():
    """从mysql读取最热文章至redis
    """
    hotest_postlist = db.session.query(Post).order_by(
        Post.reading_num.desc()).all()[:10]
    red.delete('hotest_postlist')
    for i in hotest_postlist:
        d = to_dict(i)
        d['author'] = i.author.username
        red.zadd('hotest_postlist',
                 {json.dumps(d, cls=DateEncoder): i.reading_num})


def read_newest_postlist():
    """从mysql读取最新文章至redis
    """
    newest_postlist = db.session.query(Post).order_by(
        Post.create_time.desc()).all()[:10]
    red.delete('newest_postlist')
    for i in newest_postlist:
        d = to_dict(i)
        d['author'] = i.author.username
        red.zadd('newest_postlist',
                 {json.dumps(d, cls=DateEncoder): i.post_id})


if __name__ == '__main__':
    read_hotest_postlist()
    read_newest_postlist()
