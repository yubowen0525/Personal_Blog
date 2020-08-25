# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     models
   Description :   ORM database
   Author :       ybw
   date：          2020/8/13
-------------------------------------------------
   Change Activity:
                   2020/8/13:
-------------------------------------------------
"""
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from .extensions import db


class Admin(db.Model, UserMixin):
    """
    管理员表，用户信息，博客资料
    @id：主键
    @username：
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    password_hash = db.Column(db.String(128))
    blog_title = db.Column(db.String(60))
    blog_sub_title = db.Column(db.String(100))
    name = db.Column(db.String(30))
    about = db.Column(db.Text)

    def set_password(self, password):
        """
        将密码散列计算生成hash值，默认加salt长度为8，增加随机性。method$salt$hash
        :param password:
        :return:
        """
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)


class Category(db.Model):
    """
    Categories of stored articles

    1. Category and Article need to establish a one-to-many relationship
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)

    posts = db.relationship('Post', back_populates='category')

    def delete(self):
        default_category = Category.query.get(1)
        posts = self.posts[:]
        for post in posts:
            post.category = default_category
        db.session.delete(self)
        db.session.commit()


class Post(db.Model):
    """
    存储文章Post模型

    1. Category and Article need to establish a one-to-many relationship（会在多的地方定义外键）
    2. Post and Comment need to establish a one-to-many relationship

    """
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    can_comment = db.Column(db.Boolean, default=True)   # 设置该文章是否可以评论
    # 外键字段指向分类模型地外键，存储分类记录地主键值
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))

    category = db.relationship('Category', back_populates='posts')
    comments = db.relationship('Comment', back_populates='post', cascade='all, delete-orphan')


class Comment(db.Model):
    """
    邻接列表关系，评论要支持存储回复，要为评论添加回复，并在获取某个评论时通过关系属性获取相对应的回复
    而对于回复，当然可以在创建一个表，但可以使用更简单的方法，因为回复本身也是一种评论

    具体来说，要创建一个外键指向自己，得到一种层级关系：每个评论对象都可以包含多个子评论，即回复
    但一对多关系两侧都在同一个模型下，所以通过remote_side设为id，即远端侧。replied_id为本地侧
    """
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(30))
    email = db.Column(db.String(254))
    site = db.Column(db.String(255))
    body = db.Column(db.Text)
    from_admin = db.Column(db.Boolean, default=False)  # 判断评论是否是管理员地评论
    reviewed = db.Column(db.Boolean, default=False)  # 判断评论是否通过审核，防止垃圾和不当言论
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    # 邻接列表
    replied_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    # 存储Post记录地主键值。设置了级联删除，某个文章记录被删除，该文章所属地所有评论也会一并被删除
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

    post = db.relationship('Post', back_populates='comments')
    # 表示父对象的标量关系属性
    replied = db.relationship('Comment', back_populates='replies', remote_side=[id])
    replies = db.relationship('Comment', back_populates='replied', cascade='all, delete-orphan')  # 父评论删除，所有子评论也被删除

class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    url = db.Column(db.String(255))