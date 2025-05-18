import os
import secrets

class Config:
    # MySQL 连接配置
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "mysql+pymysql://root:xjn040623@localhost:3306/myblog")

    # 邮件服务器配置
    MAIL_SERVER = 'smtp.qq.com'  # 替换为你的 SMTP 服务器
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = "1303370223@qq.com"
    MAIL_PASSWORD = "gkgxufndyfhfjdgc"
    MAIL_DEBUG = True

    #JWT配置
    JWT_SECRET_KEY = "qAJBf3DCR2nXyHcd6PpHEmukC3FaYb4L6PVDJUul6T4" # 用你自己的密钥
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'

    # 启用 Token 黑名单支持
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access']
