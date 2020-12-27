# coding=utf-8
"""
@Description: 主程序
@FilePath: /blog/app/blog_app.py
@Author: liu.junlei@foxmail.com
@Date: 2020-12-06 17:39:49
@LastEditTime: 2020-12-27 20:24:12
"""

import os
import json
import datetime

from flask import render_template
from flask import redirect
from flask import request
from flask import url_for
from flask import flash
from flask import session
from werkzeug.utils import secure_filename

from models import User, Post, Comment, Follow, PostLike, Collection
from app import creat_app, db
import utils
import models
import settings
from redisDB import red
from redisDB import get_hotest_postlist_from_redis
from redisDB import get_newest_postlist_from_redis

app = creat_app()
app.secret_key = 'Liu Junlei is pretty!'


@app.route('/')
def index():
    """首页
    """
    user = models.get_current_user()
    followed_postlist = db.session.query(Post).filter(
        Post.author_id.in_([i.followed.user_id for i in user.followed.all()
                            ])).order_by(Post.create_time).limit(10).all()
    hotest_postlist = get_hotest_postlist_from_redis()
    newest_postlist = get_newest_postlist_from_redis()
    return render_template('index.html',
                           user=user,
                           hotest_postlist=hotest_postlist,
                           newest_postlist=newest_postlist,
                           followed_postlist=followed_postlist)


@app.route('/about')
def about():
    """关于页
    """
    return render_template('about.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """登录
    """
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        session['email'] = request.form['email']
        user = models.get_user(email=email)
        if user is not None and user.verify_password(password):
            return redirect('/')
        else:
            return '用户名或密码错误'
    return render_template('login.html')


@app.route('/logout')
def logout():
    """退出登录
    """
    if 'email' in session:
        session.pop('email')
        return redirect('/')
    return '您还未登录'


@app.route('/register', methods=['GET', 'POST'])
def register():
    """注册
    """
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        username = request.form['username']
        password_again = request.form['password_again']
        code = request.form['code']
        if models.get_user(email=email):
            return '邮箱已注册'
        if models.get_user(username=username):
            return '用户名重复，请换一个'
        if password_again != password:
            return '密码不一致'
        if not utils.check_password_format(password):
            return '密码格式不正确'
        if code == red.get(email):
            user = User(email=email, username=username, password=password)
            models.add_or_update(user)
            return render_template('index.html')
        return '验证码错误'
    return render_template('register.html')


@app.route('/send_code', methods=['POST'])
def send_code():
    """发送验证码
    """
    email = request.get_json()['email']
    text_code = utils.gen_random_six_num()
    red.set(email, text_code, ex=300)
    utils.mail(text_code, [email])
    return '已向邮箱{}发送验证码'.format(email)


@app.route('/update_userinfo', methods=['GET', 'POST'])
def update_userinfo():
    """更新用户信息
    """
    user = models.get_current_user()
    if user:
        if request.method == 'POST':
            file = request.files['face']
            email = request.form['email'] or user.email
            password = request.form['password']
            username = request.form['username']
            password_again = request.form['password_again']
            code = request.form['code']
            if password and password_again != password:
                return '密码不一致'
            if file and utils.check_user_upload_face_file_type(file.filename):
                filename = str(user.user_id) + '.' + secure_filename(
                    file.filename).split('.')[1]
                file.save(os.path.join(settings.UPLOAD_FACE_PATH, filename))
                user.photo = '/static/upload_face/{}'.format(filename)
            if username:
                if db.session.query(User).filter_by(username=username).first():
                    return '用户名已被注册'
                user.username = username
            if request.form['email']:
                if db.session.query(User).filter_by(
                        email=request.form['email']).first():
                    return '邮箱已被注册'
                if code == red.get(email):
                    user.email = request.form['email']
            if password and code == red.get(email):
                user.password = password
            models.add_or_update(user)
            return redirect('/')
        return render_template('updateinfo.html', user=user)
    return '请先登录！'


@app.route('/writepost', methods=['GET', 'POST'])
def write_post():
    """写文章
    """
    author = models.get_current_user()
    if author:
        if request.method == 'POST':
            title = request.form['title']
            content = request.form['content']
            label = request.form['label']
            post = Post(title=title,
                        content=content,
                        author_id=author.user_id,
                        label=label)
            db.session.add(post)
            db.session.flush()
            post_id = post.post_id
            try:
                db.session.commit()
            except:
                db.session.rollback()
            return redirect(url_for('get_post', id=post_id))
        return render_template('writepost.html', user=author)
    return '请先登录'


@app.route('/modifypost', methods=['GET', 'POST'])
def modify_post():
    """修改文章
    """
    user = models.get_current_user()
    if user:
        post_id = request.args.get('post_id')
        post = db.session.query(Post).filter_by(post_id=post_id).first()
        if post.author.email != user.email:
            return '您没有编辑权限'
        if request.method == 'POST':
            title = request.form['title']
            content = request.form['content']
            label = request.form['label']
            post.title = title
            post.content = content
            post.label = label
            post.update_time = datetime.datetime.now().strftime(
                '%H-%m-%d %H:%M:%S')
            models.add_or_update(post)
            return redirect(url_for('get_post', id=post_id))
        return render_template('writepost.html', user=user, post=post)
    return '请先登录'


@app.route('/writecomment', methods=['POST'])
def write_comment():
    """写评论
    """
    author = models.get_current_user()
    if author:
        post_id = int(request.args.get('post_id'))
        root_comment_id = request.args.get('root_comment_id', None)
        to_comment_id = request.args.get('to_comment_id', None)
        post = Post.query.get_or_404(post_id)
        author = models.get_user(email=session['email'])
        content = request.form['comment']
        if root_comment_id and to_comment_id:
            comment = Comment(author_id=author.user_id,
                              post_id=post.post_id,
                              content=content,
                              root_comment_id=root_comment_id,
                              to_comment_id=to_comment_id)
        else:
            comment = Comment(author_id=author.user_id,
                              post_id=post.post_id,
                              content=content)
        models.add_or_update(comment)
        return redirect('/post/{id}'.format(id=post_id))
    return '请先登录'


@app.route('/postlist/<username>')
def post_list(username):
    """用户的文章列表
    """
    current_user = models.get_current_user()
    page = request.args.get('page', 1, type=int)
    author = models.get_user(username=username)
    post_list = db.session.query(Post).filter_by(
        author_id=author.user_id).order_by(Post.create_time.desc()).paginate(
            page, error_out=False)
    return render_template('user.html',
                           page=page,
                           user=author,
                           current_user=current_user,
                           post_list=[i for i in post_list.items])


@app.route('/post_list_with_label/<username>/<label>')
def post_list_with_label(username, label):
    """用户指定标签下的文章列表
    """
    page = request.args.get('page', 1, type=int)
    author = models.get_user(username=username)
    post_list = db.session.query(Post).filter_by(
        author_id=author.user_id, label=label).order_by(
            Post.create_time.desc()).paginate(page, error_out=False)
    return json.dumps([models.to_dict(i) for i in post_list.items],
                      cls=models.DateEncoder)


@app.route('/commentlist/<username>')
def comment_list(username):
    """评论列表
    """
    current_user = models.get_current_user()
    page = request.args.get('page', 1, type=int)
    author = models.get_user(username=username)
    comment_list = db.session.query(Comment).filter_by(
        author_id=author.user_id).order_by(
            Comment.create_time.desc()).paginate(page, error_out=False)
    return render_template('user.html',
                           page=page,
                           user=author,
                           current_user=current_user,
                           comment_list=[i for i in comment_list.items])


@app.route('/post/<int:id>')
def get_post(id):
    """获取文章
    """
    post = Post.query.get_or_404(id)
    post.reading_num += 1
    models.add_or_update(post)
    root_comment_list = db.session.query(Comment).filter_by(
        post_id=post.post_id, root_comment_id=-1).all()
    comment = {
        i: db.session.query(Comment).filter_by(
            root_comment_id=i.comment_id).all()
        for i in root_comment_list
    }
    user = models.get_current_user()
    if user:
        like_status = db.session.query(PostLike).filter_by(
            author_id=user.user_id, post_id=post.post_id).first() or red.hget(
                'postlike', '{}_{}'.format(user.user_id, post.post_id))
        collect_status = db.session.query(Collection).filter_by(
            author_id=user.user_id, post_id=post.post_id).first()
    else:
        like_status = None
        collect_status = None
    return render_template('post.html',
                           user=user,
                           like_status=like_status,
                           collect_status=collect_status,
                           post=post,
                           comment=comment)


@app.route('/user/<username>')
def user_home(username):
    """用户主页
    """
    current_user = models.get_current_user()
    user = models.get_user(username=username)
    return render_template('user.html', user=user, current_user=current_user)


@app.route('/label_list/<username>')
def label_list(username):
    """用户拥有的标签列表
    """
    author = models.get_user(username=username)
    label_list = db.session.query(
        Post.label).filter_by(author_id=author.user_id).distinct().all()
    return json.dumps(label_list)


@app.route('/follow', methods=['POST'])
def follow():
    """关注
    """
    user = models.get_current_user()
    if user:
        username = request.get_json()['username']
        followed = models.get_user(username=username)
        follow = Follow(follower_id=user.user_id, followed_id=followed.user_id)
        models.add_or_update(follow)
        return '关注成功'
    return '请先登录'


@app.route('/follower_list/<username>')
def follower_list(username):
    """粉丝列表
    """
    current_user = models.get_current_user()
    user = models.get_user(username=username)
    page = request.args.get('page', 1, type=int)
    follower_list = user.follower.paginate(page, error_out=False)
    user_list = [i.follower for i in follower_list.items]
    return render_template('user.html',
                           page=page,
                           user=user,
                           current_user=current_user,
                           follower_list=user_list)


@app.route('/followed_list/<username>')
def followed_list(username):
    """关注列表
    """
    current_user = models.get_current_user()
    user = models.get_user(username=username)
    page = request.args.get('page', 1, type=int)
    followed_list = user.followed.paginate(page, error_out=False)
    user_list = [i.followed for i in followed_list.items]
    return render_template('user.html',
                           page=page,
                           user=user,
                           current_user=current_user,
                           followed_list=user_list)


@app.route('/post_like', methods=['POST'])
def post_like():
    """点赞
    """
    author = models.get_current_user()
    if author:
        post_id = request.get_json()['post_id']
        post = Post.query.get_or_404(post_id)
        post_like = PostLike(author_id=author.user_id, post_id=post.post_id)
        models.add_or_update(post_like)
        return '你已点赞这篇文章'
    return '请先登录'


@app.route('/redis_post_like', methods=['POST'])
def redis_post_like():
    """redis-点赞
    """
    author = models.get_current_user()
    if author:
        post_id = request.get_json()['post_id']
        k = '{user_id}_{post_id}'.format(user_id=author.user_id,
                                         post_id=post_id)
        red.hset('postlike', k,
                 datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        return '你已点赞这篇文章'
    return '请先登录'


@app.route('/redis_post_unlike', methods=['POST'])
def redis_post_unlike():
    """redis-取消点赞
    """
    author = models.get_current_user()
    if author:
        post_id = request.get_json()['post_id']
        k = '{user_id}_{post_id}'.format(user_id=author.user_id,
                                         post_id=post_id)
        red.hdel('postlike', k)
        return '你取消点赞了这篇文章'
    return '请先登录'


@app.route('/post_unlike', methods=['POST'])
def post_unlike():
    """取消点赞
    """
    author = models.get_current_user()
    if author:
        post_id = request.get_json()['post_id']
        post = Post.query.get_or_404(post_id)
        post_like = PostLike(author_id=author.user_id, post_id=post.post_id)
        models.delete(post_like)
        return '你取消点赞了这篇文章'
    return '请先登录'


@app.route('/post_like_list/<username>')
def post_like_list(username):
    """点赞文章列表
    """
    current_user = models.get_current_user()
    user = models.get_user(username=username)
    page = request.args.get('page', 1, type=int)
    post_like_list = user.like_post.paginate(page, error_out=False)
    post_list = [i.post for i in post_like_list.items]
    return render_template('user.html',
                           page=page,
                           user=user,
                           current_user=current_user,
                           post_like_list=post_list)


@app.route('/collection', methods=['POST'])
def collection():
    """收藏文章
    """
    author = models.get_current_user()
    if author:
        post_id = request.get_json()['post_id']
        post = Post.query.get_or_404(post_id)
        collection = Collection(author_id=author.user_id, post_id=post.post_id)
        models.add_or_update(collection)
        return '你收藏了这篇文章'
    flash('请先登录')
    return


@app.route('/uncollection', methods=['POST'])
def uncollection():
    """取消收藏文章
    """
    author = models.get_current_user()
    if author:
        post_id = request.get_json()['post_id']
        post = Post.query.get_or_404(post_id)
        collection = Collection(author_id=author.user_id, post_id=post.post_id)
        models.delete(collection)
        return '你取消收藏了这篇文章'
    flash('请先登录')
    return


@app.route('/collection_list/<username>')
def collection_list(username):
    """收藏文章列表
    """
    current_user = models.get_current_user()
    user = models.get_user(username=username)
    page = request.args.get('page', 1, type=int)
    collection_list = user.collection.paginate(page, error_out=False)
    post_list = [i.post for i in collection_list.items]
    return render_template('user.html',
                           page=page,
                           user=user,
                           current_user=current_user,
                           collection_list=post_list)


@app.route('/search', methods=['POST'])
def search():
    """搜索
    """
    current_user = models.get_current_user()
    word = request.form['word']
    user_list = db.session.query(User).filter(
        User.username.like('%{}%'.format(word))).limit(10).all()
    post_list = db.session.query(Post).filter(
        Post.title.like('%{}%'.format(word))).order_by(
            Post.reading_num.desc()).limit(10).all()
    return render_template('search.html',
                           current_user=current_user,
                           user_list=user_list,
                           post_list=post_list)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
