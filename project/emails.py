# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     emails
   Description :
   Author :       ybw
   date：          2020/8/16
-------------------------------------------------
   Change Activity:
                   2020/8/16:
-------------------------------------------------
"""
from threading import Thread

from flask import url_for, current_app
from flask_mail import Message

from .extensions import mail


def _send_async_mail(app, message):
    with app.app_context():
        mail.send(message)

# 异步发送
def send_mail(subject, to, html):
    # 获取代理的程序实例，放入线程的参数
    app = current_app._get_current_object()
    message = Message(subject, recipients=[to], html=html)
    thr = Thread(target=_send_async_mail, args=[app, message])
    thr.start()
    return thr


def send_new_comment_email(post):
    """
    发送新评论提醒邮件，通过url_for()的external参数设为True来构建外部连接。#comments（片段标识符）
    用来跳转到页面评论部分的URL片段(URL fragment),comments 是评论部分div元素的id值

    :param post: 这个函数接收表示文章的post对象作为参数，从而生成文章正文的标题和链接
    :return:
    """
    post_url = url_for('blog.show_post', post_id=post.id, _external=True) + '#comments'
    send_mail(subject='New comment', to=current_app.config['BLUELOG_EMAIL'],
              html='<p>New comment in post <i>%s</i>, click the link below to check:</p>'
                   '<p><a href="%s">%s</a></P>'
                   '<p><small style="color: #868e96">Do not reply this email.</small></p>'
                   % (post.title, post_url, post_url))


def send_new_reply_email(comment):
    """
    发送新回复提醒邮件。接收comment对象作为参数，用来构建邮件正文，所属文章的主键值通过comment.post_id
    属性获取，标题则通过comment.post.title属性获取
    :param comment:
    :return:
    """
    post_url = url_for('blog.show_post', post_id=comment.post_id, _external=True) + '#comments'
    send_mail(subject='New reply', to=comment.email,
              html='<p>New reply for the comment you left in post <i>%s</i>, click the link below to check: </p>'
                   '<p><a href="%s">%s</a></p>'
                   '<p><small style="color: #868e96">Do not reply this email.</small></p>'
                   % (comment.post.title, post_url, post_url))
