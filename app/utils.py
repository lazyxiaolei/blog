# coding=utf-8
"""
@Description: 工具函数
@FilePath: /blog/app/utils.py
@Author: liu.junlei@foxmail.com
@Date: 2020-12-06 17:44:20
@LastEditTime: 2020-12-27 21:05:18
"""

import smtplib
import random
import re
from email.mime.text import MIMEText
from email.utils import formataddr

import settings


def gen_random_six_num():
    """生成6位随机数组合

    Returns:
        str: 6位随机数组合字符串
    """
    s = ''
    for i in range(6):
        s += str(random.choice(range(10)))
    return s


def check_password_format(password):
    """校验密码格式

    Args:
        password (str): 密码

    Returns:
        boolean: 格式符合返回True,格式错误返回False
    """
    pattern = re.compile('\w{8,16}')
    if pattern.match(password):
        if re.search('[0-9]', password) and re.search('[a-z]', password):
            return True
    return False


def mail(text, my_receiver):
    """发送邮件

    Args:
        text (str): 邮件正文
        my_receiver (list): 收件人列表
    """
    my_sender = settings.EMAIL['sender']
    my_password = settings.EMAIL['password']
    try:
        msg = MIMEText(text, 'plain', 'utf-8')
        msg['From'] = formataddr(['XL博客', my_sender])
        msg['To'] = formataddr(['you', ';'.join(my_receiver)])
        msg['Subject'] = '验证码校验'
        server = smtplib.SMTP_SSL('smtp.qq.com', 465)
        server.login(my_sender, my_password)
        server.sendmail(my_sender, my_receiver, msg.as_string())
        server.quit()
        print('邮件发送成功')
    except Exception as e:
        print(e)
        print('邮件发送失败')


def check_user_upload_face_file_type(filename):
    """校验用户上传头像的文件类型是否符合要求

    Args:
        filename (str): 文件名

    Returns:
        boolean: 文件类型符合要求返回True,否则返回False
    """
    return '.' in filename and filename.rsplit('.', 1)[1] in settings.ALLOWED_EXTENSIONS
