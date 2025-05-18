from flask import Blueprint, request, jsonify
from __init__ import db
from db import User
from tokenblock import TokenBlocklist
from werkzeug.security import generate_password_hash
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from datetime import datetime
from werkzeug.utils import secure_filename
import os
import uuid
from flask_mail import Message, Mail
from twilio.rest import Client

# 创建蓝图
user_bp = Blueprint('user', __name__)

@user_bp.route('/user/register', methods=['POST'])
def register_user():
    data = request.form
    avatar_file = request.files.get('avatar')

    username = data.get('u_nickname')  # 注意字段名要跟前端传的一致
    password = data.get('u_password')
    gender = data.get('gender')
    nickname = data.get('u_nickname')
    intro = data.get('u_intro', '')
    phone = data.get('phone')
    email = data.get('u_email')

    # 这里检查用户名和邮箱是否存在，用户名字段用 nickname 就好，或者你统一用 username
    if User.query.filter_by(nickname=nickname).first():
        return jsonify({"state": 0, "message": "用户名已存在"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"state": 0, "message": "邮箱已存在"}), 400

    # 头像文件处理，如果需要保存文件，写你的逻辑
    if avatar_file:
        avatar_filename = secure_filename(avatar_file.filename)

        # 获取当前文件（register模块）所在的目录
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # 拼接出 blog/public/img 的绝对路径
        save_path = os.path.abspath(os.path.join(current_dir, '..', '..', '..', 'blog', 'public', 'img'))
        os.makedirs(save_path, exist_ok=True)

        avatar_file.save(os.path.join(save_path, avatar_filename))

        avatar_path = f'/img/{avatar_filename}'
    else:
        avatar_path = '/img/default-avatar.png'

    new_user = User(
        username=nickname,
        gender=gender,
        nickname=nickname,
        intro=intro,
        avatar=avatar_path,
        create_at=datetime.utcnow(),
        phone=phone,
        email=email
    )

    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"state": 1, "message": "注册成功"})


@user_bp.route('/user/login', methods=['POST'])
def login_user():
    data = request.get_json()

    account = data.get('u_account')
    password = data.get('u_password')

    user = User.query.filter(
        (User.username == account) |
        (User.email == account) |
        (User.phone == account)
    ).first()

    if not user:
        return jsonify({"state": 0, "message": "User not found"}), 400

    if not user.check_password(password):
        return jsonify({"state": 0, "message": "Invalid password"}), 400

    if user.u_status == 1:
        return jsonify({"state": 0, "message": "User is not allowed to login"}), 403

    # 更新登录状态
    user.last_login_at = datetime.utcnow()
    user.is_online = True
    token = user.create_access_token()
    print(f"[DEBUG] 登录成功，生成的 token: {token}")
    db.session.commit()

    # 返回头像地址
    avatar_url = user.avatar if user.avatar else "/default-avatar.png"

    return jsonify({
        "state": 1,
        "message": "Login successful",
        "token": token,
        "id": user.id,
        "avatar": avatar_url
    })

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

    avatar_url = user.avatar if user.avatar else "/default-avatar.png"

    return jsonify({
        "state": 1,
        "message": "Login successful",
        "token": token,
        "avatar": avatar_url
    }), 200


@user_bp.route('/user/updateProfile', methods=['PUT'])
@jwt_required() # 确保只有认证用户才能访问此接口
def update_user_profile():
    """
    更新用户个人信息接口
    需要 JWT Token 进行认证
    接收 multipart/form-data，包含用户信息和可选头像文件
    """
    try:
        # 获取当前认证用户的身份 (假设 JWT payload 中的 'sub' 存储了用户 ID)
        current_user_id = get_jwt_identity()
        user_to_update = User.query.get(current_user_id)

        if not user_to_update:
            # 理论上 jwt_required 会处理无效 token，但这里做个双重检查
            return jsonify({"state": 0, "message": "用户不存在或认证无效"}), 404

        data = request.form
        avatar_file = request.files.get('avatar')

        # --- 获取并验证要更新的字段 ---
        updated_data = {}
        errors = {}

        # 用户名 (Username/Nickname) - 必填，且如果修改需要检查唯一性
        # 假设你统一使用 nickname 作为用户在前端显示的名字和唯一的标识
        # 如果 username 字段是后台唯一标识，nickname 是可显示的名字，则需要分开处理
        # 这里按照你的注册接口逻辑，假设 username 和 nickname 是同一个字段
        new_nickname = data.get('username') # 前端传来的可能是 username 或 nickname，根据前端实际字段名调整
        if new_nickname is not None: # 允许前端不传某个字段，只更新部分信息
            new_nickname = new_nickname.strip()
            if not new_nickname:
                errors['username'] = '用户名不能为空'
            elif new_nickname != user_to_update.nickname: # 只有当用户名改变时才检查唯一性
                if User.query.filter_by(nickname=new_nickname).first():
                    errors['username'] = '用户名已存在'
                else:
                    updated_data['nickname'] = new_nickname
                    # 如果你的 username 字段也需要更新且与 nickname 保持一致，也在这里更新
                    # updated_data['username'] = new_nickname # 仅当 username/nickname 是一致的
        else:
             # 如果前端没有传 username 字段，保持原值
             pass # 或者你可以强制要求用户名必传

        # 个人简介 (Intro) - 可选
        new_intro = data.get('intro')
        if new_intro is not None:
             updated_data['intro'] = new_intro.strip()

        # 邮箱 (Email) - 必填，且如果修改需要检查唯一性
        new_email = data.get('email')
        if new_email is not None:
            new_email = new_email.strip()
            if not new_email:
                 errors['email'] = '邮箱不能为空'
            # 简单的邮箱格式验证 (更严格的验证可以在客户端和后端都做)
            # import re
            # email_regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
            # if not re.match(email_regex, new_email):
            #     errors['email'] = '邮箱格式不正确'
            elif new_email != user_to_update.email: # 只有当邮箱改变时才检查唯一性
                if User.query.filter_by(email=new_email).first():
                    errors['email'] = '邮箱已存在'
                else:
                    updated_data['email'] = new_email
        # else: # 如果前端没有传 email 字段，通常邮箱是必填项，这里保持原值或报错，取决于你的需求
        #      errors['email'] = '邮箱不能为空' # 例如强制必填


        # 性别 (Gender) - 可选 (你的模型中是 nullable=False，前端应始终提供)
        new_gender = data.get('gender')
        if new_gender is not None:
            # 可以在这里验证性别是否是有效值 ('男', '女', '未知')
            valid_genders = ['男', '女', '未知', ''] # 假设空字符串也是允许的
            if new_gender not in valid_genders:
                 errors['gender'] = '性别输入无效'
            else:
                updated_data['gender'] = new_gender

        # 手机号 (Phone) - 可选，且如果修改需要检查唯一性
        new_phone = data.get('phone')
        if new_phone is not None:
            new_phone = new_phone.strip()
            # 可以在这里添加手机号格式验证
            if new_phone != user_to_update.phone: # 只有当手机号改变时才检查唯一性
                if User.query.filter_by(phone=new_phone).first():
                     errors['phone'] = '手机号已存在'
                else:
                     updated_data['phone'] = new_phone # 允许手机号为空字符串清空
        # else: # 如果前端没有传 phone 字段，保持原值
        #      pass


        # --- 密码修改逻辑 ---
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        # 客户端已经验证了 confirmNewPassword，这里只处理 current_password 和 new_password

        if new_password: # 如果提供了新密码，说明尝试修改密码
            if not current_password:
                errors['current_password'] = '修改密码需要输入当前密码'
            else:
                # 验证当前密码
                if not user_to_update.check_password(current_password):
                    errors['current_password'] = '当前密码不正确'

            if not new_password:
                 errors['new_password'] = '新密码不能为空'
            # 可以在这里添加新密码的复杂度验证 (长度、字符类型等)
            # 例如： if len(new_password) < 6: errors['new_password'] = '新密码至少需要6个字符'


            if 'current_password' not in errors and 'new_password' not in errors:
                # 如果当前密码正确且新密码验证通过，则加密新密码
                updated_data['password_hash'] = generate_password_hash(new_password)
                # 清空密码字段，避免在返回数据中暴露
                updated_data.pop('current_password', None)
                updated_data.pop('new_password', None) # 移除，避免意外存入其他字段
        # else: # 如果没有提供新密码，忽略密码相关的字段更新
        #     pass

        # 如果存在任何验证错误，返回错误信息
        if errors:
            # 可以在这里返回更详细的字段错误信息
            return jsonify({"state": 0, "message": "更新失败", "errors": errors}), 400 # 使用 400 Bad Request

        # 头像文件处理，如果需要保存文件，写你的逻辑
        if avatar_file:
            avatar_filename = secure_filename(avatar_file.filename)

            # 获取当前文件（register模块）所在的目录
            current_dir = os.path.dirname(os.path.abspath(__file__))

            # 拼接出 blog/public/img 的绝对路径
            save_path = os.path.abspath(os.path.join(current_dir, '..', '..', '..', 'blog', 'public', 'img'))
            os.makedirs(save_path, exist_ok=True)

            avatar_file.save(os.path.join(save_path, avatar_filename))

            avatar_path = f'/img/{avatar_filename}'
            print(f"Generated avatar URL path: {avatar_path}")
            updated_data['avatar'] = avatar_path

        else:
            avatar_path = '/img/default-avatar.png'
            updated_data['avatar'] = avatar_path


        # --- 更新数据库中的用户信息 ---
        if updated_data:
            for key, value in updated_data.items():
                setattr(user_to_update, key, value)

            db.session.commit()

            # 返回更新后的用户信息 (不包含敏感信息如密码hash)
            # 你可以构建一个字典来返回用户的一些公开或修改后的信息
            updated_user_info = {
                "id": user_to_update.id,
                "username": user_to_update.username,
                "nickname": user_to_update.nickname, # 确保返回 nickname
                "intro": user_to_update.intro,
                "email": user_to_update.email,
                "gender": user_to_update.gender,
                "phone": user_to_update.phone,
                "avatar": user_to_update.avatar,
                "create_at": user_to_update.create_at.isoformat() if user_to_update.create_at else None,
                # 注意：关注/粉丝数可能需要单独查询并添加到返回中
                # "follower_count": user_to_update.followers.count(), # 假设你在模型中定义了关系
                # "following_count": user_to_update.followed.count(), # 假设你在模型中定义了关系
            }
             # 为了方便前端更新，这里假设你直接返回 user 模型的部分字段
             # 你可能需要一个序列化函数来规范化返回数据
             # 例如: updated_user_info = user_to_update.to_dict() # 如果你的 User 模型有 to_dict 方法

            # 简单构造返回数据，包含前端可能需要更新的字段
            response_data = {
                "id": user_to_update.id,
                "username": user_to_update.username,
                "intro": user_to_update.intro,
                "email": user_to_update.email,
                "gender": user_to_update.gender,
                "phone": user_to_update.phone,
                "avatar": user_to_update.avatar,
                "register_time": user_to_update.create_at.strftime('%Y-%m-%d %H:%M:%S') if user_to_update.create_at else None,
            }

            return jsonify({"state": 1, "message": "个人信息更新成功", "data": response_data}), 200

        else:
            # 如果没有任何字段需要更新，返回成功但无更新的信息
            return jsonify({"state": 1, "message": "个人信息未做修改"}), 200

    except Exception as e:
        db.session.rollback() # 发生异常时回滚数据库操作
        print(f"Error updating user profile: {e}")
        return jsonify({"state": 0, "message": "服务器内部错误", "error": str(e)}), 500

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

@user_bp.route('/user/getProfile', methods=['GET'])
@jwt_required()
def get_profile():
    current_user_id = get_jwt_identity()
    user = User.query.filter_by(id=current_user_id).first()

    if not user:
        return jsonify({"state": 0, "message": "User not found"}), 404

    if user.u_status == 1:
        return jsonify({"state": 0, "message": "User is not allowed to access this data"}), 403

    user_info = {
        "id": user.id,  # <--- ADD THIS LINE
        "username": user.username,
        "gender": user.gender,
        "intro": user.intro,
        "avatar": user.avatar,
        "email": user.email,
        "phone": user.phone,
        "register_time": user.create_at.strftime('%Y-%m-%d %H:%M:%S') if user.create_at else None,
    }

    return jsonify({"state": 1, "message": "Profile fetched successfully", "data": user_info}), 200

@user_bp.route('/user/profile/<int:user_id>', methods=['GET'])
def get_public_profile(user_id):

    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    if user.u_status == 1:
         return jsonify({"message": "User not found"}), 404
    user_info = {
        "id": user.id, # 重要：这里必须包含用户ID
        "username": user.username,
        "intro": user.intro,
        "avatar": user.avatar,
        "email": user.email,
        "register_time": user.create_at.strftime('%Y-%m-%d %H:%M:%S') if user.create_at else None,
        "gender": user.gender
    }
    return jsonify(user_info), 200