# -*- coding: utf-8 -*-
"""
    :author: Grey Li (李辉)
    :url: http://greyli.com
    :copyright: © 2018 Grey Li <withlihui@gmail.com>
    :license: MIT, see LICENSE for more details.
"""
from flask import render_template, flash, redirect, url_for, Blueprint, request
from flask_login import login_user, logout_user, login_required, current_user

from ..forms import LoginForm
from ..models import Admin
from ..utils import redirect_back

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # 用户触发认证，认证过了直接返回主页面
    if current_user.is_authenticated:
        return redirect(url_for('blog.index'))
    print(request.full_path)
    # 登录效验
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember = form.remember.data
        admin = Admin.query.first()
        if admin:
            # 验证用户名和密码
            if username == admin.username and admin.validate_password(password):
                login_user(admin, remember)
                flash('Welcome back.', 'info')
                # 这里的back就是 next的路径地址
                return redirect_back()
            flash('Invalid username or password.', 'warning')
        else:
            flash('No account.', 'warning')
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout success.', 'info')
    # 这里的back就是next的地址
    return redirect_back()
