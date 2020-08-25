# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     extensions
   Description :   extension init
   Author :       ybw
   date：          2020/8/13
-------------------------------------------------
   Change Activity:
                   2020/8/13:
-------------------------------------------------
"""
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

bootstrap = Bootstrap()
db = SQLAlchemy()
ckeditor = CKEditor()
mail = Mail()
moment = Moment()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()
ckeditor = CKEditor()

@login_manager.user_loader
def load_user(user_id):
    """
    登录加载，保护
    :param user_id: 用户id
    :return:
    """
    from .models import Admin
    user = Admin.query.get(int(user_id))
    return user


login_manager.login_view = 'auth.login'
login_manager.login_message = u'请先登录！'
login_manager.login_message_category = 'warning'