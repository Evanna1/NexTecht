from flask import Blueprint, request, jsonify
from __init__ import db
from db import User
from tokenblock import TokenBlocklist
from werkzeug.security import generate_password_hash
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from datetime import datetime
from flask_mail import Message, Mail
from twilio.rest import Client

# 创建蓝图
user_bp = Blueprint('user', __name__)

@user_bp.route('/user/register', methods=['POST'])
def register_user():
    data = request.get_json()  # 获取请求的JSON数据

    # 获取输入字段
    username = data.get('username')
    password = data.get('u_password')
    gender = data.get('gender')
    nickname = data.get('u_nickname')
    intro = data.get('u_intro', '')  # 个人介绍，默认为空
    avatar = data.get('avatar', '')  # 头像，默认为空
    phone = data.get('phone', None)  # 手机号，选填
    email = data.get('u_email')


    if User.query.filter_by(username=username).first():
        return jsonify({"state": 0, "message": "Username already exists"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"state": 0, "message": "Email already exists"}), 400

    # 创建新用户
    new_user = User(
        username=username,
        gender=gender,
        nickname=nickname,
        intro=intro,
        avatar=avatar,
        create_at=datetime.utcnow(),
        phone=phone,
        email=email
    )

    # 设置加密密码
    new_user.set_password(password)

    # 将用户数据保存到数据库
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"state": 1, "message": "Account created successfully"})

@user_bp.route('/user/login', methods=['POST'])
def login_user():
    data = request.get_json()  # 获取请求的JSON数据

    account = data.get('u_account')
    password = data.get('u_password')

    user = User.query.filter((User.username == account) | (User.email == account) | (User.phone == account)).first()

    if not user:
        return jsonify({"state": 0, "message": "User not found"}), 400

    if not user.check_password(password):
        return jsonify({"state": 0, "message": "Invalid password"}), 400

    if user.u_status == 1:
        return jsonify({"state": 0, "message": "User is not allowed to login"}), 403

    # 更新最后登录时间和在线状态
    user.last_login_at = datetime.utcnow()
    user.is_online = True
    token = user.create_access_token()
    db.session.commit()

    return jsonify({"state": 1, "message": "Login successful", "token": token})

# 发送验证码接口（发送邮件或短信验证码）
@user_bp.route('/user/sendEmailCode', methods=['POST'])
def send_verification_code():
    data = request.get_json()
    email = data.get('u_email')

    user = User.query.filter((User.email == email)).first()
    if not user:
        return jsonify({"state": 0, "message": "Email not found"}), 400

    # 生成验证码
    verification_code = user.generate_verification_code()

    # 假设验证码存储在用户模型中（可以通过数据库或缓存存储）
    user.verification_code = verification_code

    # 发送验证码
    user.send_email_verification_code(verification_code)

    user.set_verification_code_expiry()

    db.session.commit()

    return jsonify({"state": 1, "message": "Verification code sent successfully"}), 200

@user_bp.route('/user/verifyEmailCode', methods=['POST'])
def verify_code():
    data = request.get_json()
    email = data.get('u_email')
    code = data.get('code')

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"state": 0, "message": "Email not found"}), 400

    # 校验验证码是否过期
    if datetime.utcnow() > user.verification_code_expiry:
        return jsonify({"state": 0, "message": "Verification code has expired"}), 400

    if user.verification_code != code:
        return jsonify({"state": 0, "message": "Invalid verification code"}), 400

    token = user.create_access_token()

    return jsonify({"state": 1, "message": "Login successful", "token": token})

# 更新用户信息接口
@user_bp.route('/user/updateProfile', methods=['POST'])
@jwt_required()  # 需要验证 JWT
def update_profile():
    # 从 JWT 获取当前用户的身份信息
    current_user_id = get_jwt_identity()

    # 获取请求数据
    data = request.get_json()
    u_nickname = data.get('u_nickname')
    gender = data.get('gender')
    u_intro = data.get('u_intro', '')  # 个人介绍，默认为空
    avatar = data.get('avatar', '')  # 头像，默认为空

    # 查询数据库中当前用户
    user = User.query.filter_by(id=current_user_id).first()

    if not user:
        return jsonify({"state": 0, "message": "User not found"}), 404

    if user.u_status == 1:
        return jsonify({"state": 0, "message": "User is not allowed to operate"}), 403

    # 更新用户信息
    if u_nickname:
        user.nickname = u_nickname
    if gender:
        user.gender = gender
    if u_intro:
        user.intro = u_intro
    if avatar:
        user.avatar = avatar

    # 提交更新到数据库
    db.session.commit()

    return jsonify({"state": 1, "message": "Profile updated successfully"}), 200

# 查看用户信息接口
@user_bp.route('/user/getProfile', methods=['GET'])
@jwt_required()  # 需要验证 JWT
def get_profile():
    # 从 JWT 获取当前用户的身份信息
    current_user_id = get_jwt_identity()

    # 查询数据库中当前用户
    user = User.query.filter_by(id=current_user_id).first()

    if not user:
        return jsonify({"state": 0, "message": "User not found"}), 404

    if user.u_status == 1:
        return jsonify({"state": 0, "message": "User is not allowed to access this data"}), 403

    # 构造用户信息字典
    user_info = {
        "username": user.username,
        "gender": user.gender,
        "intro": user.intro,
        "avatar": user.avatar,
        "email": user.email,
        "register_time": user.create_at.strftime('%Y-%m-%d %H:%M:%S') if user.create_at else None,

    }

    return jsonify({"state": 1, "message": "Profile fetched successfully", "data": user_info}), 200


#用户退出登录
@user_bp.route('/user/logout', methods=['POST'])
@jwt_required()
def logout_user():

    identity = get_jwt_identity()
    jti = get_jwt()["jti"]         # 获取当前 Token 的唯一标识

    user = User.query.filter_by(id=identity).first()
    if not user:
        return jsonify({"state": 0, "message": "User not found"}), 404

    # 更新用户状态
    user.is_online = False
    db.session.commit()

    # 拉黑 Token
    db.session.add(TokenBlocklist(jti=jti, created_at=datetime.utcnow()))
    db.session.commit()

    return jsonify({"state": 1, "message": "Logout successful"}), 200