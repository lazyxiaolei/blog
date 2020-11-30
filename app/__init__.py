from flask_sqlalchemy import SQLAlchemy
from flask import Flask
# from app.auth.views import auth_blueprint

db = SQLAlchemy()


def creat_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost:3306/practice'
    db.init_app(app)

    # app.register_blueprint(auth_blueprint, url_prefix='/auth')
    return app
