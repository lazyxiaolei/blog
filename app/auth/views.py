from flask import render_template, redirect, request, url_for, flash
# from app.auth import auth_blueprint
from app.models import User
from app import db
from flask import  Blueprint
auth_blueprint = Blueprint('auth', __name__)


@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = db.session.query(User).filter_by(email=email).first()
        if user is not None and user.verify_password(password):
            return 'login in'
    return 'login'


@auth_blueprint.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        username = request.form['username']
        password_again = request.form['password_again']
        if password_again != password:
            return 'password bu yi zhi'
        user = User(email=email,username=username, password=password, password_again=password_again)
        db.session.add(user)
        try:
            db.session.commit()
        except:
            db.rollback()
        return 'register in'
    return 'register'
