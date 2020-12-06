import os,smtplib,random,json,traceback,re,redis,crontab
from app import creat_app, db
from flask import render_template, redirect, request, url_for, flash,session
from app.auth import auth_blueprint
from app.models import User,Post,Comment,Follow,PostLike,Collection
from werkzeug.utils import secure_filename
from email.mime.text import MIMEText
from email.utils import formataddr
from threading import Timer
from app.redisDB import red
from datetime import datetime

app = creat_app()
app.secret_key = 'fafakkkdgks/.,,,'

UPLOAD_FOLDER = r'F:\python_practice\blog_project\static\upload'
ALLOWED_EXTENSIONS = set(['jpg','png','gif','bmp','jpeg'])

my_sender = '366849574@qq.com'
my_password = 'uxmdtcgqqowbbgfe'


@app.route('/redis_send_code', methods=['POST'])
def redis_send_code():
    email = request.form['email']
    text_code = gen_random_six_num()
    red.set(email,text_code,ex=300)
    mail(text_code, [email])
    return 'send ok'

def gen_random_six_num():
    s = ''
    for i in range(6):
        s += str(random.choice(range(10)))
    return s

def expired_code():
    session.pop('code')
    print('验证码已过期,请重新发送邮件')


def check_password_format(password):
    pattern = re.compile('\w{8,16}')
    if pattern.match(password):
        if re.search('[0-9]',password) and re.search('[a-z]',password):
            return True
    return False

@app.route('/send_code',methods=['POST'])
def send_code():
    email = request.form['email']
    text_code = gen_random_six_num()
    session['code'] = text_code
    mail(text_code,[email])
    t = Timer(300,expired_code)
    t.start()
    return 'send ok'


def mail(text,my_receiver):
    try:
        msg = MIMEText(text,'plain','utf-8')
        msg['From'] = formataddr(['from me',my_sender])
        msg['To'] = formataddr(['you',';'.join(my_receiver)])
        msg['Subject'] = '注册确认邮件'
        server = smtplib.SMTP_SSL('smtp.qq.com', 465)
        server.login(my_sender, my_password)
        server.sendmail(my_sender,my_receiver,msg.as_string())
        server.quit()
        print('邮件发送成功')
    except Exception as e:
        traceback.print_exc()
        print('邮件发送失败')


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS

@app.route('/upload_file', methods=['POST'])
def upload_file():
    if 'email' in session:
        user = db.session.query(User).filter_by(email=session['email']).first()
        if request.method == 'POST':
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(UPLOAD_FOLDER,filename))
                user.photo = '/static/upload{}_{}'.format(user.username,filename)
                db.session.add(user)
                try:
                    db.session.commit()
                except:
                    db.session.rollback()
                return '上传成功'
            return '文件类型不正确'
        return ''
    return 'not login in'


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        session['email'] = request.form['email']
        user = db.session.query(User).filter_by(email=email).first()
        if user is not None and user.verify_password(password):
            return 'login in'
        else:
            return 'email or password is wrong'
    return 'login'


@app.route('/logout', methods=['POST'])
def logout():
    if 'email' in session:
        session.pop('email')
        return '已退出登录'
    return  'not login in'


@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        username = request.form['username']
        password_again = request.form['password_again']
        code = request.form['code']
        if User.query.filter_by(email=email).first():
            return '邮箱已注册'
        if User.query.filter_by(username=username).first():
            return '用户名重复，请换一个'
        if password_again != password:
            return 'password bu yi zhi'
        if not check_password_format(password):
            return '密码格式错误'
        # text_code = session['code']
        # if text_code == code:
        if code == red.get(email):
            user = User(email=email,username=username, password=password)
            db.session.add(user)
            try:
                db.session.commit()
            except:
                db.session.rollback()
            return 'register in'
        # print('code%s' %code)
        # print('验证码%s' % red.get(email))
        return '验证码错误'
    return 'register'

@app.route('/update_email', methods=['POST'])
def update_email():
    if 'email' in session:
        user = User.query.filter_by(email=session['email']).first()
        if request.method == 'POST':
            new_email = request.form['new_email']
            code = request.form['code']
            if User.query.filter_by(email=new_email).first():
                return '邮箱已注册'
            if session['code'] == code:
                user.email = new_email
                db.session.add(user)
                try:
                    db.session.commit()
                    session['email'] = new_email
                except:
                    db.session.rollback()
                return '修改邮箱成功'
            return '验证码错误'
    return 'not login in'

@app.route('/forget_update_password', methods=['POST'])
def forget_update_password():
    if request.method == 'POST':
        email = request.form['email']
        new_password = request.form['new_password']
        new_password_again = request.form['new_password_again']
        code = request.form['code']
        user = User.query.filter_by(email=email).first()
        if not user:
            return '邮箱不存在'
        if new_password != new_password_again:
            return '密码不一致'
        if not check_password_format(new_password):
            return '密码格式错误'
        if session['code'] == code:
            user.password = new_password
            db.session.add(user)
            try:
                db.session.commit()
            except:
                db.session.rollback()
            return '修改密码成功'
        return '验证码不正确'

@app.route('/update_password', methods=['POST'])
def update_password():
    if 'email' in session:
        user = User.query.filter_by(email=session['email']).first()
        if request.method == 'POST':
            old_password = request.form['old_password']
            new_password = request.form['new_password']
            new_password_again = request.form['new_password_again']
            if not user.verify_password(old_password):
                return '旧密码错误'
            if new_password != new_password_again:
                return '密码不一致'
            if not check_password_format(new_password):
                return '密码格式错误'
            user.password = new_password
            db.session.add(user)
            try:
                db.session.commit()
            except:
                db.session.rollback()
            return '修改密码成功'
    return 'not login in'


@app.route('/update_information', methods=['POST'])
def update_information():
    if 'email' in session:
        user = User.query.filter_by(email=session['email']).first()
        if request.method == 'POST':
            new_username = request.form['new_username']
            if User.query.filter_by(username=new_username).first():
                return '用户名重复'
            user.username = new_username
            db.session.add(user)
            try:
                db.session.commit()
            except:
                db.session.rollback()
            return '修改资料成功'
    return 'not login in'


@app.route('/post', methods=['GET', 'POST'])
def write_post():
    if 'email' in session:
        if request.method == 'POST':
            title = request.form['title']
            content = request.form['content']
            label = request.form['label']
            author = db.session.query(User).filter_by(email=session['email']).first()
            post = Post(title=title, content=content, author_id=author.user_id, label=label)
            db.session.add(post)
            try:
                db.session.commit()
            except:
                db.session.rollback()
            return 'write post ok'
        return 'write post'
    return 'not login in'

@app.route('/comment/<int:id>', methods=['GET', 'POST'])
def write_comment(id):
    post = Post.query.get_or_404(id)
    if 'email' in session:
        if request.method == 'POST':
            author = db.session.query(User).filter_by(email=session['email']).first()
            content = request.form['content']
            comment = Comment(author_id=author.user_id, post_id=post.post_id, content=content)
            db.session.add(comment)
            try:
                db.session.commit()
            except:
                db.session.rollback()
            return 'write comment ok'
        return 'write comment'
    return 'not login in'


@app.route('/postlist/<username>', methods=['GET'])
def post_list(username):
    page = request.args.get('page', 1, type=int)
    author = db.session.query(User).filter_by(username=username).first()
    post_list = db.session.query(Post).filter_by(author_id=author.user_id).order_by(Post.create_time.desc()).paginate(page, error_out=False)
    return json.dumps([(i.title,i.create_time.strftime('%Y-%m-%d %H:%M:%S')) for i in post_list.items])


@app.route('/hot_postlist',methods=['GET'])
def hot_postlist():
    hot_postlist = db.session.query(Post).order_by(Post.reading_num.desc()).all()[:10]
    return  json.dumps([(i.title,i.reading_num) for i in hot_postlist])

@app.route('/time_postlist', methods=['GET'])
def time_postlist():
    time_postlist = db.session.query(Post).order_by(Post.create_time.desc()).all()[:10]
    return json.dumps([(i.title, i.create_time.strftime('%Y-%m-%d  %H:%M:%S')) for i in time_postlist])

@app.route('/redis_hot_postlist',methods=['GET'])
def redis_hot_postlist():
    hot_postlist = [json.loads(i) for i in red.zrange('hot_postlist',0,-1,desc=True)]
    return json.dumps(hot_postlist)

@app.route('/redis_time_postlist',methods=['GET'])
def redis_time_postlist():
    time_postlist = [json.loads(i) for i in red.zrange('time_postlist',0,-1,desc=True)]
    return json.dumps(time_postlist)

@app.route('/followed_postlist', methods=['GET'])
def followed_postlist():
    if 'email' in session:
        user = db.session.query(User).filter_by(email=session['email']).first()
        followed_list = db.session.query(Follow.followed_id).filter_by(follower_id=user.user_id).all()
        followed_postlist = db.session.query(Post).filter(Post.author_id.in_([i[0] for i in followed_list])).order_by(Post.create_time.desc()).all()[:10]
        return json.dumps([(i.title, i.create_time.strftime('%Y-%m-%d  %H:%M:%S')) for i in followed_postlist])
    return  'not login in'


@app.route('/post_list_with_label/<username>/<label>',methods=['GET'])
def post_list_with_label(username, label):
    page = request.args.get('page', 1,type=int)
    author = db.session.query(User).filter_by(username=username).first()
    post_list = db.session.query(Post).filter_by(author_id=author.user_id, label=label).order_by(Post.create_time.desc()).paginate(page, error_out=False)
    return json.dumps([(i.title, i.label, i.create_time.strftime('%Y-%m-%d %H:%M:%S')) for i in post_list.items])


@app.route('/commentlist/<username>',methods=['GET'])
def comment_list(username):
    page = request.args.get('page',1,type=int)
    author = db.session.query(User).filter_by(username=username).first()
    comment_list = db.session.query(Comment).filter_by(author_id=author.user_id).order_by(Comment.create_time.desc()).paginate(page, error_out=False)
    return json.dumps([(i.content,i.create_time.strftime('%Y-%m-%d %H:%M:%S')) for i in comment_list.items])


@app.route('/get_post/<int:id>', methods=['GET'])
def get_post(id):
    post = Post.query.get_or_404(id)
    post.reading_num += 1
    db.session.add(post)
    try:
        db.session.commit()
    except:
        db.session.rollback()
    comment_list = db.session.query(Comment).filter_by(post_id=post.post_id).all()
    comment = {}
    for i in comment_list:
        if i.root_comment_id == -1 and i.comment_id not in comment:
            comment[i.comment_id] = []
        else:
            if i.root_comment_id not in comment:
                comment[i.root_comment_id] = [i.comment_id]
            else:
                comment[i.root_comment_id].append(i.comment_id)
    return comment


@app.route('/label_list/<username>', methods=['GET'])
def label_list(username):
    author = db.session.query(User).filter_by(username=username).first()
    label_list = db.session.query(Post.label).filter_by(author_id=author.user_id).distinct().all()
    return json.dumps(label_list)


@app.route('/follow', methods=['POST'])
def follow():
    username = request.get_json()['username']
    followed = db.session.query(User).filter_by(username=username).first()
    if 'email' in session:
        follower = db.session.query(User).filter_by(email=session['email']).first()
        follow = Follow(follower_id=follower.user_id, followed_id=followed.user_id)
        db.session.add(follow)
        try:
            db.session.commit()
        except:
            db.session.rollback()
        return  'follow  ok'
    return  'not login in'

@app.route('/follower_list/<username>', methods=['GET'])
def follower_list(username):
    user = db.session.query(User).filter_by(username=username).first()
    page = request.args.get('page', 1, type=int)
    follower_list = db.session.query(Follow).filter_by(followed_id=user.user_id).order_by(Follow.follow_time.desc()).paginate(page, error_out=False)
    user_list = [db.session.query(User).filter_by(user_id=i.follower_id).first()  for i in follower_list.items ]
    return json.dumps([(i.username)  for i in user_list])


@app.route('/followed_list/<username>', methods=['GET'])
def followed_list(username):
    user = db.session.query(User).filter_by(username=username).first()
    page = request.args.get('page', 1, type=int)
    followed_list = db.session.query(Follow).filter_by(follower_id=user.user_id).order_by(Follow.follow_time.desc()).paginate(page, error_out=False)
    user_list = [db.session.query(User).filter_by(user_id=i.followed_id).first()  for i in followed_list.items ]
    return json.dumps([(i.username)  for i in user_list])


@app.route('/post_like', methods=['POST'])
def post_like():
    post_id = request.get_json()['post_id']
    post = Post.query.get_or_404(post_id)
    if 'email' in session:
        author = db.session.query(User).filter_by(email=session['email']).first()
        post_like = PostLike(author_id=author.user_id, post_id=post.post_id)
        db.session.add(post_like)
        try:
            db.session.commit()
        except:
            db.session.rollback()
        return '你点赞了这篇文章'
    return 'not  login  in'

@app.route('/redis_post_like',methods=['POST'])
def redis_post_like():
    post_id = request.get_json()['post_id']
    if 'email' in session:
        author = db.session.query(User).filter_by(email=session['email']).first()
        k = '{user_id}_{post_id}'.format(user_id=author.user_id,post_id=post_id)
        red.hset('postlike',k,datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        return '你点赞了'
    return 'not login in'




@app.route('/post_unlike', methods=['POST'])
def post_unlike():
    post_id = request.get_json()['post_id']
    post = Post.query.get_or_404(post_id)
    if 'email' in session:
        author = db.session.query(User).filter_by(email=session['email']).first()
        post_like = db.session.query(PostLike).filter_by(author_id=author.user_id, post_id=post.post_id).first()
        db.session.delete(post_like)
        try:
            db.session.commit()
        except:
            db.session.rollback()
        return '你取消点赞了这篇文章'
    return 'not  login  in'


@app.route('/post_like_list/<username>', methods=['GET'])
def post_like_list(username):
    user = db.session.query(User).filter_by(username=username).first()
    post_like_list = db.session.query(PostLike).filter_by(author_id=user.user_id).all()[:10]
    return json.dumps([(i.post.title, i.post.create_time.strftime('%Y-%m-%d %H:%M:%S')) for i in post_like_list])


@app.route('/collection', methods=['POST'])
def collection():
    post_id = request.get_json()['post_id']
    post = Post.query.get_or_404(post_id)
    if 'email' in session:
        author = db.session.query(User).filter_by(email=session['email']).first()
        collection = Collection(author_id=author.user_id, post_id=post.post_id)
        db.session.add(collection)
        try:
            db.session.commit()
        except:
            db.session.rollback()
        return '你收藏了这篇文章'
    return 'not  login  in'


@app.route('/uncollection', methods=['POST'])
def uncollection():
    post_id = request.get_json()['post_id']
    post = Post.query.get_or_404(post_id)
    if 'email' in session:
        author = db.session.query(User).filter_by(email=session['email']).first()
        uncollection = db.session.query(Collection).filter_by(author_id=author.user_id, post_id=post.post_id).first()
        db.session.delete(uncollection)
        try:
            db.session.commit()
        except:
            db.session.rollback()
        return '你取消收藏了这篇文章'
    return 'not  login  in'


@app.route('/collection_list/<username>', methods=['GET'])
def collection_list(username):
    user = db.session.query(User).filter_by(username=username).first()
    collection_list = db.session.query(Collection).filter_by(author_id=user.user_id).all()[:10]
    return json.dumps([(i.post.title, i.post.create_time.strftime('%Y-%m-%d %H:%M:%S')) for i in collection_list])


app.run(debug=True)
# mail(['366849574@qq.com'])
# check_code()
# update_email()