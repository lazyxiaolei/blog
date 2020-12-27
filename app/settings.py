# coding=utf-8
"""
@Description: 配置
@FilePath: /blog/app/settings.py
@Author: liu.junlei@foxmail.com
@Date: 2020-12-06 17:50:39
@LastEditTime: 2020-12-27 21:32:36
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
    'sender': '',  # 发送邮箱
    'password': '',  # 邮箱认证密码
}

UPLOAD_FACE_PATH = '/root/blog/static/upload_face'
ALLOWED_EXTENSIONS = set(['jpg', 'png', 'jpeg'])
