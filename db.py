from __init__ import db
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import uuid
import secrets
import random
import string
from flask_mail import Message, Mail
from twilio.rest import Client
from flask import current_app

mail = Mail()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # 自增的主键
    username = db.Column(db.String(80), unique=True, nullable=False)  # 用户名，唯一
    password_hash = db.Column(db.String(512), nullable=False)  # 存储加密后的密码
    gender = db.Column(db.String(10), nullable=False)  # 性别
    nickname = db.Column(db.String(80), nullable=False)  # 昵称
    intro = db.Column(db.Text, nullable=True)  # 个人介绍，选填
    avatar = db.Column(db.String(256), nullable=True)  # 头像 URL，选填
    create_at = db.Column(db.DateTime, default=datetime.utcnow)  # 注册时间，默认当前时间
    phone = db.Column(db.String(20), unique=True, nullable=True)  # 手机号，选填
    email = db.Column(db.String(120), unique=True, nullable=False)  # 邮箱，唯一
    verification_code = db.Column(db.String(10), nullable=True)
    verification_code_expiry = db.Column(db.DateTime, nullable=True)  # 存储验证码的过期时间
    u_status = db.Column(db.Integer, default=0)  # 用户状态，0：正常（默认），1：禁止用户的所有权限
    is_publish = db.Column(db.Integer, default=1)  # 发布文章权限,1:可以（默认），0:不可以
    is_comment = db.Column(db.Integer, default=1)  # 评论权限,1:可以（默认），0:不可以
    last_login_at = db.Column(db.DateTime)  # 最后登录时间
    is_online = db.Column(db.Boolean, default=False)  # 是否在线

    def set_password(self, password):
        """加密用户的密码并存储到 password_hash 字段中"""
        self.password_hash = generate_password_hash(password)  # 使用 werkzeug 的 generate_password_hash 函数加密密码

    def check_password(self, password):
        """验证输入的密码是否与存储的加密密码匹配"""
        return check_password_hash(self.password_hash, password)  # 使用 check_password_hash 校验密码

    def create_access_token(self):
        payload = {
            'sub': str(self.id),  # 用户的唯一标识符
            'username': self.username,
            'jti': str(uuid.uuid4()),
            'exp': datetime.utcnow() + timedelta(days=1)  # 令牌有效期1天
        }
        secret_key = current_app.config['JWT_SECRET_KEY']
        token = jwt.encode(payload, secret_key, algorithm='HS256')
        return token

    # 生成验证码
    def generate_verification_code(self, length=6):
        return ''.join(random.choices(string.digits, k=length))

    # 发送邮箱验证码
    def send_email_verification_code(self, code):
        msg = Message(subject='Your verification code',
                      sender='1303370223@qq.com',
                      recipients=[self.email])
        msg.body = f'Your verification code is: {code}'
        mail.send(msg)

    def set_verification_code_expiry(self):
        self.verification_code_expiry = datetime.utcnow() + timedelta(minutes=60)

    def __repr__(self):
        return f'<User {self.username}>'


class Manager(db.Model):
    mng_id = db.Column(db.Integer, primary_key=True)  # 自增的主键  1
    mng_name = db.Column(db.String(40), unique=True, nullable=False)  # 用户名，唯一  2
    mng_phone = db.Column(db.String(20), unique=True, nullable=False)  # 手机号，选填,唯一 3
    mng_email = db.Column(db.String(120), unique=True, nullable=False)  # 邮箱，唯一 4
    mng_password_hash = db.Column(db.String(512), nullable=False)  # 存储加密后的密码 5
    mng_gender = db.Column(db.String(10), nullable=False)  # 性别 6
    mng_nickname = db.Column(db.String(80), nullable=False)  # 昵称 7
    mng_avatar = db.Column(db.String(256), nullable=True)  # 头像 URL，选填 8
    mng_create_at = db.Column(db.DateTime, default=datetime.utcnow)  # 注册时间，默认当前时间 9

    def set_password(self, m_password):
        # """加密用户的密码并存储到 password_hash 字段中"""
        self.mng_password_hash = generate_password_hash(m_password)  # 使用 werkzeug 的 generate_password_hash 函数加密密码

    def check_password(self, m_password):
        # """验证输入的密码是否与存储的加密密码匹配"""
        return check_password_hash(self.mng_password_hash, m_password)  # 使用 check_password_hash 校验密码

    # 产生令牌
    def create_access_token(self):
        payload = {
            'sub': str(self.mng_id),  # 管理员的唯一标识符
            'managername': self.mng_name,
            'exp': datetime.utcnow() + timedelta(days=1)  # 令牌有效期1天
        }
        secret_key = current_app.config['JWT_SECRET_KEY']
        token = jwt.encode(payload, secret_key, algorithm='HS256')
        return token


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # 自增的主键，文章 ID
    title = db.Column(db.String(256), nullable=False)  # 文章标题
    content = db.Column(db.Text, nullable=False)  # 文章内容
    create_time = db.Column(db.DateTime, default=datetime.utcnow)  # 文章创建时间，默认为当前时间
    update_time = db.Column(db.DateTime, onupdate=datetime.utcnow)  # 文章更新时间
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # 关联用户 ID，外键
    user = db.relationship('User', backref=db.backref('articles', lazy=True))  # 建立与用户模型的关联

    permission = db.Column(db.Integer, default=0)  # 文章权限位，0表示公开，1表示屏蔽
    status = db.Column(db.Integer, default=0)  # 文章状态位，0表示已发布，1表示已删除，2表示被举报
    read_count = db.Column(db.Integer, default=0)
    image_path = db.Column(db.String(256))  # 图片路径字段
    tag = db.Column(db.String(128))  # 文章分类标签字段

    def to_dict(self):  # 字典，方便转为json
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'create_time': self.create_time.isoformat() if self.create_time else None,  # Handle potential None
            'update_time': self.update_time.isoformat() if self.update_time else None,
            'author': self.user.username if self.user else 'Unknown',  # Handle potential missing user
            'permission': self.permission,
            'status': self.status,
            'read_count': self.read_count,
            'image_path': self.image_path,
            'tag': self.tag
            # Future: Add 'like_count': self.like_count if hasattr(self, 'like_count') else 0,
            # Future: Add 'favorite_count': self.favorite_count if hasattr(self, 'favorite_count') else 0,
        }

    def update_article(self, new_title=None, new_content=None, new_permission=None, new_status=None,
                       new_image_path=None, new_tag=None):  # 更新文章的标题和内容
        if new_title:
            self.title = new_title
        if new_content:
            self.content = new_content
        if new_permission is not None:  # 更新权限位
            self.permission = new_permission
        if new_status is not None:  # 更新状态位
            self.status = new_status
        if new_image_path is not None:
            self.image_path = new_image_path
        if new_tag is not None:
            self.tag = new_tag
        db.session.commit()

    def delete_article(self):  # 删除文章
        self.status = 2  # 标记为已删除状态
        db.session.commit()

    @classmethod
    def get_articles_by_status(cls, status):
        """根据状态获取文章"""
        return cls.query.filter_by(status=status).all()

    @classmethod
    def get_articles_by_permission(cls, permission):
        """根据权限获取文章"""
        return cls.query.filter_by(permission=permission).all()

    def set_permission(self, permission_level):
        """设置文章权限"""
        self.permission = permission_level
        db.session.commit()

    def set_status(self, status_code):
        """设置文章状态"""
        self.status = status_code
        db.session.commit()

    def __repr__(self):
        return f'<Article {self.title}>'


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # 自增的主键，评论 ID
    content = db.Column(db.Text, nullable=False)  # 评论内容
    create_time = db.Column(db.DateTime, default=datetime.utcnow)  # 评论创建时间，默认为当前时间
    update_time = db.Column(db.DateTime, onupdate=datetime.utcnow)  # 评论更新时间
    status = db.Column(db.Integer, default=0)  # 评论状态，0: 正常，1: 已删除，2: 屏蔽，3: 举报
    is_approved = db.Column(db.Integer, default=0)  # 审核状态，0: 待审核，1: 已通过，2: 未通过
    like_count = db.Column(db.Integer, default=0)  # 点赞数
    reply_count = db.Column(db.Integer, default=0)  # 回复数
    depth = db.Column(db.Integer, default=0)  # 评论深度，用于区分顶级评论和回复

    # 关联字段
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # 关联用户 ID，外键
    user = db.relationship('User', backref=db.backref('comments', lazy=True))  # 与用户模型的关联
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'), nullable=False)  # 关联文章 ID，外键
    article = db.relationship('Article', backref=db.backref('comments', lazy=True))  # 与文章模型的关联
    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)  # 父评论 ID，用于回复
    parent_comment = db.relationship('Comment', backref=db.backref('replies', lazy=True), remote_side=[id])  # 与父评论的关联

    def to_dict(self):
        """将评论转换为字典,方便转为JSON"""
        return {
            'id': self.id,
            'content': self.content,
            'create_time': self.create_time.isoformat(),
            'update_time': self.update_time.isoformat() if self.update_time else None,
            'status': self.status,
            'is_approved': self.is_approved,
            'like_count': self.like_count,
            'reply_count': self.reply_count,
            'depth': self.depth,
            'user': {
                'id': self.user.id,
                'username': self.user.username,
                'nickname': self.user.nickname,
                'avatar': self.user.avatar
            },
            'article_id': self.article_id,
            'parent_id': self.parent_id
        }

    def update_comment(self, new_content=None):
        """更新评论内容"""
        if new_content:
            self.content = new_content
            self.update_time = datetime.utcnow()
        db.session.commit()

    def delete_comment(self):
        """删除评论"""
        self.status = 1  # 标记为已删除
        db.session.commit()

    def report_comment(self):
        """举报评论"""
        self.status = 3  # 标记为已举报
        db.session.commit()

    def approve_comment(self, approved=True):
        """审核评论"""
        self.is_approved = 1 if approved else 2
        db.session.commit()

    def like_comment(self):
        """点赞评论"""
        self.like_count += 1
        db.session.commit()

    def __repr__(self):
        return f'<Comment {self.id} on Article {self.article_id}>'


class Alike(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # 自增的主键，点赞 ID
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # 外键，指向 User 表
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'), nullable=False)  # 外键，指向 Article 表
    create_time = db.Column(db.DateTime, default=datetime.utcnow)  # 点赞时间

    user = db.relationship('User', backref=db.backref('likes', lazy=True))  # 与 User 的关系
    article = db.relationship('Article', backref=db.backref('likes', lazy=True))  # 与 Article 的关系

    @classmethod
    def get_user_likes(cls, user_id):
        """获取某用户所有点赞的文章"""
        return cls.query.filter_by(user_id=user_id).all()

    @classmethod
    def get_article_likes(cls, article_id):
        """获取某篇文章所有点赞的用户"""
        return cls.query.filter_by(article_id=article_id).all()

    def __repr__(self):
        return f'<Like User {self.user_id} on Article {self.article_id}>'


class Follow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    followed_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)  # 关注的时间戳

    def __repr__(self):
        return f'<Follow follower: {self.follower_id}, followed: {self.followed_id}>'


class UserBrowseRecord(db.Model):
    __tablename__ = 'user_browse_record'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'), nullable=False)
    browse_time = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('records', lazy=True))  # 与 User 的关系
    article = db.relationship('Article', backref=db.backref('records', lazy=True))  # 与 Article 的关系

    def __repr__(self):
        return f'<BrowseRecord User {self.user_id} viewed Article {self.article_id} at {self.browse_time.isoformat()}>'


class CommentLike(db.Model):
    __tablename__ = 'comment_like'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('user_id', 'comment_id', name='_user_comment_uc'),)

    user = db.relationship('User', backref=db.backref('comment_likes', lazy='dynamic'))
    comment = db.relationship('Comment', backref=db.backref('comment_likes', lazy='dynamic'))


