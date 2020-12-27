# coding=utf-8
"""
@Description: gunicorn启动配置
@FilePath: /blog/gunicorn_conf.py
@Author: liu.junlei@foxmail.com
@Date: 2020-12-27 19:04:33
@LastEditTime: 2020-12-27 20:36:06
"""

import multiprocessing


bind = "0.0.0.0:8888"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'gevent'
timeout = 500
accesslog = '/root/blog/logs/gunicorn.log'
errorlog = '/root/blog/logs/gunicorn.error.log'
