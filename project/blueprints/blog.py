# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     blog
   Description :
   Author :       ybw
   date：          2020/8/13
-------------------------------------------------
   Change Activity:
                   2020/8/13:
-------------------------------------------------
"""
from flask import render_template, flash, redirect, url_for, request, current_app, Blueprint, abort, make_response
from flask_login import current_user

# from ..emails import send_new_comment_email, send_new_reply_email
from ..emails import send_new_reply_email, send_new_comment_email
from ..extensions import db
# from ..forms import CommentForm, AdminCommentForm
from ..forms import AdminCommentForm, CommentForm
from ..models import Post, Category, Comment

# from .utils import redirect_back
from ..utils import redirect_back

blog_bp = Blueprint('blog', __name__)


# pagination = Post.query.order_by(Post.timestamp.desc()).paginate(1, per_page=10)

@blog_bp.route('/')
def index():
    """
    显示主页内容
    :return:
    """
    # 参数出现了类型错误,会返回1首页
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BLUELOG_POST_PER_PAGE']
    # 为了实现分类, 不再是all , 而是 paginate 返回page页的记录,把记录分成几页
    # paginate(error_out=True),如果页面超过最大值,page或per_page为负数或非整数会返回404,如果是false,返回空记录.. max_per_page参数用来设置每页数量的最大值
    # pagination 对象是一个链表,每一个节点元素是pages . pagination.pages=5 pagination.total=50
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page, per_page=per_page)
    posts = pagination.items
    return render_template('blog/index.html', pagination=pagination, posts=posts)


@blog_bp.route('/about')
def about():
    """
    admin about
    :return:
    """
    return render_template('blog/about.html')


@blog_bp.route('/category/<int:category_id>')
def show_category(category_id):
    """
    显示分类列表
    :param category_id:
    :return:
    """
    category = Category.query.get_or_404(category_id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BLUELOG_POST_PER_PAGE']
    # posts = category.posts 这样只是获取所有列表,而我们需要对这些文章记录附加其他查询过滤器和方法
    # Post.query.with_parent(category)获取了跟category相关的5个Post，且还是query对象可以执行order_by
    pagination = Post.query.with_parent(category).order_by(Post.timestamp.desc()).paginate(page, per_page)
    posts = pagination.items
    return render_template('blog/category.html', category=category, pagination=pagination, posts=posts)


@blog_bp.route('/post/<int:post_id>', methods=['GET', 'POST'])
def show_post(post_id):
    """
    显示文章正文
    :param post_id:
    :return:
    """
    # get_or_404 没有找到抛出 abort(404) 错误
    post = Post.query.get_or_404(post_id)
    page = request.args.get('page', 1, type=int)
    # 评论分页
    per_page = current_app.config['BLUELOG_COMMENT_PER_PAGE']
    pagination = Comment.query.with_parent(post).filter_by(reviewed=True).order_by(Comment.timestamp.asc()).paginate(
        page, per_page)
    # 拿到跟页面相关所有reviewed = true 的评论
    comments = pagination.items
    # 如果当前用户已登录，使用管理员表单
    if current_user.is_authenticated:
        form = AdminCommentForm()
        form.author.data = current_user.name
        form.email.data = current_app.config['BLUELOG_EMAIL']
        form.site.data = url_for('.index')
        from_admin = True
        reviewed = True
    else: # 未登录则使用普通表单
        form = CommentForm()
        from_admin = False
        reviewed = False
    # 用户填写Comment表单，POST到后端，填入数据库内
    if form.validate_on_submit():
        author = form.author.data
        email = form.email.data
        site = form.site.data
        body = form.body.data
        # 这里需要注意post赋值的是Post对象，因为post表的字段是relationship
        comment = Comment(
            author=author, email=email, site=site, body=body,
            from_admin=from_admin, post=post, reviewed=reviewed)
        replied_id = request.args.get('reply')
        # 获取
        if replied_id:
            replied_comment = Comment.query.get_or_404(replied_id)
            comment.replied = replied_comment
            send_new_reply_email(replied_comment)
        db.session.add(comment)
        db.session.commit()
        if current_user.is_authenticated:  # send message based on authentication status
            flash('Comment published.', 'success')
        else:
            flash('Thanks, your comment will be published after reviewed.', 'info')
            send_new_comment_email(post)  # send notification email to admin
        # 提及表单，返回到原页面
        return redirect(url_for('.show_post', post_id=post_id))
    return render_template('blog/post.html', post=post, pagination=pagination, form=form, comments=comments)


@blog_bp.route('/reply/comment/<int:comment_id>')
def reply_comment(comment_id):
    """
    reply comment
    :param comment_id: 触发评论的id
    :return:
    """
    comment = Comment.query.get_or_404(comment_id)
    if not comment.post.can_comment:
        flash('Comment is disabled.', 'warning')
        # 跳回该文章
        return redirect(url_for('.show_post', post_id=comment.post.id))
    # 跳回
    return redirect(
        url_for('.show_post', post_id=comment.post_id, reply=comment_id, author=comment.author) + '#comment-form')


@blog_bp.route('/change-theme/<theme_name>')
def change_theme(theme_name):
    if theme_name not in current_app.config['BLUELOG_THEMES'].keys():
        abort(404)

    response = make_response(redirect_back())
    response.set_cookie('theme', theme_name, max_age=30 * 24 * 60 * 60)
    return response
