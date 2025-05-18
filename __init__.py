from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_cors import CORS # 引入 Flask-CORS


# 初始化数据库实例
db = SQLAlchemy()
mail = Mail()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # 初始化扩展
    db.init_app(app)
    mail.init_app(app)
    jwt.init_app(app)

    # 启用 Flask-CORS
    CORS(app, resources={r"/*": {"origins": "*"}})  # 允许所有来源的跨域请求

    from tokenblock import TokenBlocklist

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        jti = jwt_payload["jti"]
        return db.session.query(TokenBlocklist.id).filter_by(jti=jti).first() is not None

    # ✅ 自定义被拉黑的 token 返回
    @jwt.revoked_token_loader
    def revoked_callback(jwt_header, jwt_payload):
        return {"msg": "Token has been revoked"}, 401

    # 注册蓝图
    from server.user import user_bp
    from server.artical import artical_bp
    from server.manager import manager_bp
    from server.alike import alike_bp
    from server.comment import comment_bp
    from server.follow import follow_bp
    from server.commentlike import commentlike_bp
    app.register_blueprint(user_bp)
    app.register_blueprint(artical_bp)
    app.register_blueprint(manager_bp)
    app.register_blueprint(alike_bp)
    app.register_blueprint(comment_bp)
    app.register_blueprint(follow_bp)
    app.register_blueprint(commentlike_bp)
 
    return app