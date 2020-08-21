# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     forms
   Description :    forms information
   Author :       ybw
   date：          2020/8/13
-------------------------------------------------
   Change Activity:
                   2020/8/13:
-------------------------------------------------
"""
from flask_ckeditor import CKEditorField
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField, ValidationError, HiddenField, \
    BooleanField, PasswordField
from wtforms.validators import DataRequired, Email, Length, Optional, URL

from .models import Category


class LoginForm(FlaskForm):
    """
    登录表单
    """
    username = StringField('Username', validators=[DataRequired(), Length(1, 20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(1, 128)])
    remember = BooleanField('Remember me')
    submit = SubmitField('Log in')


class SettingForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(1, 30)])
    blog_title = StringField('Blog Title', validators=[DataRequired(), Length(1, 60)])
    blog_sub_title = StringField('Blog Sub Title', validators=[DataRequired(), Length(1, 100)])
    about = CKEditorField('About Page', validators=[DataRequired()])
    submit = SubmitField()


class PostForm(FlaskForm):
    """
    文章表单
    """
    title = StringField('Title', validators=[DataRequired(), Length(1, 60)])
    # selectfield 表示 HTML中的 <select> 控件提供选项菜单
    # coerce 指定数据类型，default 指定默认id的值为1
    category = SelectField('Category', coerce=int, default=1)
    body = CKEditorField('Body', validators=[DataRequired()])
    submit = SubmitField()

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        # choices 代表 <option> 必须包含两元素元组的列表，元组包含选项值和选项标签
        # 而Flask-SQLAlchemy又依赖于程序上下文才能工作，所以内部使用current_app获取配置信息
        # 所以这个查询调用要放在构造函数中执行，这里与类中实例化SelectField设置choices参数相同
        self.category.choices = [(category.id, category.name)
                                 for category in Category.query.order_by(Category.name).all()]


class CategoryForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(1, 30)])
    submit = SubmitField()

    # 避免类型重名，自定义行内验证器，它将在验证name字段时和其他验证函数一起调用。
    def validate_name(self, field):
        if Category.query.filter_by(name=field.data).first():
            raise ValidationError('Name already in use.')


class CommentForm(FlaskForm):
    """
    评论类表单
    """
    author = StringField('Name', validators=[DataRequired(), Length(1, 30)])
    # 验证器使用了验证电子邮箱地址的Email验证器
    email = StringField('Email', validators=[DataRequired(), Email(), Length(1, 254)])
    # 可以留空使用了Optional验证器
    site = StringField('Site', validators=[Optional(), URL(), Length(0, 255)])
    body = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField()


class AdminCommentForm(CommentForm):
    """
    管理员不需要填写诸如姓名，电子邮箱等字段。单独为管理员创建一个表单类，继承自评论类
    """
    # 使用HiddenField重新定义，隐藏字段 <input type="hidden">
    # 可以使用hidden_tag()方法来渲染所有隐藏字段，而不用逐个调用三个属性
    author = HiddenField()
    email = HiddenField()
    site = HiddenField()


class LinkForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(1, 30)])
    url = StringField('URL', validators=[DataRequired(), URL(), Length(1, 255)])
    submit = SubmitField()