# coding=utf-8
"""
@Description: 初始化工厂函数
@FilePath: /blog/app/__init__.py
@Author: liu.junlei@foxmail.com
@Date: 2020-12-06 18:41:31
@LastEditTime: 2020-12-27 19:38:18
"""

from flask_sqlalchemy import SQLAlchemy
from flask import Flask

import settings

db = SQLAlchemy()


def creat_app():
    """工厂函数

    Returns:
        obj: flask应用
    """
    app = Flask(__name__,
                template_folder='../templates',
                static_folder='../static')
    app.config[
        'SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://{username}:{password}@{host}:{port}/{database}'.format(
            **settings.MYSQL)
    db.init_app(app)
    return app
