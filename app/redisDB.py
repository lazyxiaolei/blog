# coding=utf-8
"""
@Description: redis模块
@FilePath: /blog/app/redisDB.py
@Author: liu.junlei@foxmail.com
@Date: 2020-12-11 21:29:36
@LastEditTime: 2020-12-27 20:34:18
"""

import json
import redis

import settings


def create_redis(host, port, db):
    """工厂函数
    """
    pool = redis.ConnectionPool(host=host, port=port, db=db, decode_responses=True)
    return redis.Redis(connection_pool=pool)


red = create_redis(**settings.REDIS)


def get_hotest_postlist_from_redis():
    """获取最热文章列表
    """
    hotest_postlist = [
        json.loads(i) for i in red.zrange('hotest_postlist', 0, -1, desc=True)
    ]
    return hotest_postlist


def get_newest_postlist_from_redis():
    """获取最新文章列表
    """
    newest_postlist = [
        json.loads(i) for i in red.zrange('newest_postlist', 0, -1, desc=True)
    ]
    return newest_postlist
