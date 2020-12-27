# coding=utf-8
"""
@Description: 配置
@FilePath: /blog/app/settings.py
@Author: liu.junlei@foxmail.com
@Date: 2020-12-06 17:50:39
@LastEditTime: 2020-12-26 22:42:55
"""

MYSQL = {
    'host': 'localhost',
    'port': 3306,
    'username': 'root',
    'password': 'lei@123',
    'database': 'blog',
}


REDIS = {
    'host': 'localhost',
    'port': 6379,
    'db': 0,
}


EMAIL = {
    'sender': 'liu.junlei@foxmail.com',
    'password': 'aixwpypxxuuxbgfe',
}


UPLOAD_FACE_PATH = '/root/blog/static/upload_face'
ALLOWED_EXTENSIONS = set(['jpg', 'png', 'jpeg'])
