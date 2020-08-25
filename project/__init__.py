import logging
from logging.handlers import RotatingFileHandler, SMTPHandler

import click
from flask import Flask, render_template, request
from flask_wtf.csrf import CSRFError
from flask_login import current_user

from .blueprints.admin import admin_bp
from .blueprints.auth import auth_bp
from .models import Admin, Post, Category, Comment, Link
from .setting import config, basedir
from .blueprints.blog import blog_bp
from .extensions import *
import os


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')

    app = Flask(__name__)
    app.config.from_object(config[config_name])
    # app.logger.level = "INFO"

    register_logging(app)  # 注册日志处理器
    register_extensions(app)  # 注册扩展（扩展初始化）
    register_blueprints(app)  # 注册蓝本
    register_commands(app)
    register_errors(app)
    register_shell_context(app)
    register_template_context(app)
    # register_request_handlers(app)
    return app


def register_logging(app):
    pass
    # class RequestFormatter(logging.Formatter):
    #
    #     def format(self, record):
    #         record.url = request.url
    #         record.remote_addr = request.remote_addr
    #         return super(RequestFormatter, self).format(record)
    #
    # request_formatter = RequestFormatter(
    #     '[%(asctime)s] %(remote_addr)s requested %(url)s\n'
    #     '%(levelname)s in %(module)s: %(message)s'
    # )
    #
    # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    #
    # file_handler = RotatingFileHandler(os.path.join(basedir, 'logs/bluelog.log'),
    #                                    maxBytes=10 * 1024 * 1024, backupCount=10)
    # file_handler.setFormatter(formatter)
    # file_handler.setLevel(logging.INFO)
    #
    # mail_handler = SMTPHandler(
    #     mailhost=app.config['MAIL_SERVER'],
    #     fromaddr=app.config['MAIL_USERNAME'],
    #     toaddrs=['ADMIN_EMAIL'],
    #     subject='Bluelog Application Error',
    #     credentials=(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD']))
    # mail_handler.setLevel(logging.ERROR)
    # mail_handler.setFormatter(request_formatter)
    #
    # if not app.debug:
    #     app.logger.addHandler(mail_handler)
    #     app.logger.addHandler(file_handler)


def register_extensions(app):
    bootstrap.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    ckeditor.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    # toolbar.init_app(app)
    migrate.init_app(app, db)


def register_blueprints(app):
    app.register_blueprint(blog_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)


# 因为扩展初始化操作分离，db.create_all()将依赖于程序上下文才能正常执行
# 执行flask shell启动的python shell会自动激活程序上下文
def register_shell_context(app):
    @app.shell_context_processor
    def make_shell_context():
        return dict(db=db, Admin=Admin, Post=Post, Category=Category, Comment=Comment)


# 为模板增加上下文admin.categories
def register_template_context(app):
    @app.context_processor
    def make_template_context():
        admin = Admin.query.first()
        categories = Category.query.order_by(Category.name).all()
        links = Link.query.order_by(Link.name).all()
        if current_user.is_authenticated:
            unread_comments = Comment.query.filter_by(reviewed=False).count()
        else:
            unread_comments = None
        return dict(
            admin=admin, categories=categories,
            links=links, unread_comments=unread_comments)


def register_commands(app):
    @app.cli.command()
    @click.option('--drop', is_flag=True, help='Create after drop.')
    def initdb(drop):
        """Initialize the database."""
        if drop:
            click.confirm('This operation will delete the database, do you want to continue?', abort=True)
            db.drop_all()
            click.echo('Drop tables.')
        db.create_all()
        click.echo('Initialized database.')

    @app.cli.command()
    @click.option('--username', prompt=True, help='The username used to login.')
    @click.option('--password', prompt=True, hide_input=True,
                  confirmation_prompt=True, help='The password used to login.')
    def init(username, password):
        """
        Building Bluelog, just for you  prompt 必须填写的参数 ， hide_input 会隐藏输入，也可以使用@click.password_option装饰器
        :param username:
        :param password:
        :return:
        """

        click.echo('Initializing the database...')
        db.create_all()

        admin = Admin.query.first()
        if admin is not None:
            click.echo('The administrator already exists, updating...')
            admin.username = username
            admin.set_password(password)
        else:
            click.echo('Creating the temporary administrator account...')
            admin = Admin(
                username=username,
                blog_title='Bluelog',
                blog_sub_title="No, I'm the real thing.",
                name='Admin',
                about='Anything about you.'
            )
            admin.set_password(password)
            db.session.add(admin)

        category = Category.query.first()
        if category is None:
            click.echo('Creating the default category...')
            category = Category(name='Default')
            db.session.add(category)

        db.session.commit()
        click.echo('Done.')

    @app.cli.command()
    @click.option('--category', default=10, help='Quantity of categories, default is 10.')
    @click.option('--post', default=50, help='Quantity of posts, default is 50.')
    @click.option('--comment', default=500, help='Quantity of comments, default is 500.')
    def forge(category, post, comment):
        """Generate fake data."""
        from .fakes import fake_admin, fake_categories, fake_posts, fake_comments

        db.drop_all()
        db.create_all()

        click.echo('Generating the administrator...')
        fake_admin()

        click.echo('Generating %d categories...' % category)
        fake_categories(category)

        click.echo('Generating %d posts...' % post)
        fake_posts(post)

        click.echo('Generating %d comments...' % comment)
        fake_comments(comment)

        # click.echo('Generating links...')
        # fake_links()

        click.echo('Done.')


def register_errors(app):
    @app.errorhandler(400)
    def bad_request(e):
        return render_template('errors/400.html'), 400

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        return render_template('errors/400.html', description=e.description), 400
