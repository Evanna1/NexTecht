from flask import Blueprint, request, jsonify
from __init__ import db
from db import User,Manager,Article
from datetime import datetime
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from collections import OrderedDict

# 管理员登录接口
"""输入：
        {
         "m_account":mng_id | mng_name | mng_email | mng_phone,
         "m_password":"对应的密码"
        }
"""
manager_bp = Blueprint('manager', __name__)

@manager_bp.route('/manager/login', methods=['POST'])
def manager_login():
    data = request.get_json()
    
    mng_account = data.get('m_account')
    mng_password = data.get('m_password')

    manager = Manager.query.filter(
        (Manager.mng_id == mng_account) | 
        (Manager.mng_name == mng_account) | 
        (Manager.mng_email == mng_account) | 
        (Manager.mng_phone == mng_account)
    ).first()
    
    # 验证逻辑
    if not manager:
        return jsonify({"state": 0, "message": "Manager not found"}), 401
    if not manager.check_password(mng_password):
        return jsonify({"state": 0, "message": "Invalid password"}), 401
    
    # 获得本次登录令牌
    m_token = manager.create_access_token()

    return jsonify({"state": 1, "message": "Login successful", "token": m_token, "time": datetime.utcnow()})

# 添加新的管理员接口
# 注意：只有超级管理员(id=1)才能添加管理员
"""输入：
        {
         "m_name": "new_manager",
         "m_password": "secure_password123",
         "m_gender": "男",
         "m_nickname": "NewAdmin",
         "m_avatar": "https://example.com/avatar.jpg",
         "m_phone": "13800138000",
         "m_email": "new_manager@example.com"
        }
"""
@manager_bp.route('/manager/add_mng', methods=['POST'])
@jwt_required()
def add_manager():
    data = request.get_json()
    
    # 获取当前登录的管理员id
    current_mng_id = get_jwt_identity()
    current_manager = Manager.query.get(current_mng_id)
    
    # 检查当前管理员是否是第一个管理员（第一个管理员的 ID 为 1）：只有这个管理员有权限增加新的管理员
    if current_manager.mng_id != 1:
        return jsonify({"state": 0, "message": "Only the first manager can add new managers"}), 403

    # 获取新管理员的信息
    new_mng_name = data.get('m_name')
    new_mng_password = data.get('m_password')
    new_mng_gender = data.get('m_gender')
    new_mng_nickname = data.get('m_nickname')
    new_mng_avatar = data.get('m_avatar')
    new_mng_phone = data.get('m_phone')
    new_mng_email = data.get('m_email')

    # 检查新管理员的用户名是否已存在
    if Manager.query.filter_by(mng_name=new_mng_name).first():
        return jsonify({"state": 0, "message": "name already exists"}), 400
    if Manager.query.filter_by(mng_phone=new_mng_phone).first():
        return jsonify({"state": 0, "message": "phone already exists"}), 400
    if Manager.query.filter_by(mng_email=new_mng_email).first():
        return jsonify({"state": 0, "message": "email already exists"}), 400

    # 创建新管理员
    new_manager = Manager(
        mng_name=new_mng_name,
        mng_gender=new_mng_gender,
        mng_nickname=new_mng_nickname,
        mng_avatar=new_mng_avatar,
        mng_phone=new_mng_phone,
        mng_email=new_mng_email
    )
    new_manager.set_password(new_mng_password)
    db.session.add(new_manager)
    db.session.commit()

    return jsonify({"state": 1, "message": "New manager added successfully"})


# 删除管理员接口
# 注意：只有超级管理员（id=1)才能删除管理员
"""输入：
        {
         "delete_by":mng_id | mng_name | mng_email | mng_phone(选择字段),
         "value":"对应的id、name、phone、email"
        }
"""
@manager_bp.route('/manager/delete_mng', methods=['DELETE'])
@jwt_required()
def delete_manager():
    data = request.get_json()
    
    # 获取当前登录的管理员id
    current_mng_id = get_jwt_identity()
    current_manager = Manager.query.get(current_mng_id)
    
    # 检查当前管理员是否是第一个管理员
    if current_manager.mng_id != 1:
        return jsonify({"state": 0, "message": "Only the first manager can delete other managers"}), 403
    
    # 获取要删除的管理员的标识符
    delete_by = data.get('delete_by')  # delete_by 可以是 'mng_id', 'mng_name', 'mng_phone', 'mng_email'
    value = data.get('value')  # 对应的值

    if delete_by == 'mng_id':
        manager_to_delete = Manager.query.get(value)
    elif delete_by == 'mng_name':
        manager_to_delete = Manager.query.filter_by(mng_name=value).first()
    elif delete_by == 'mng_phone':
        manager_to_delete = Manager.query.filter_by(mng_phone=value).first()
    elif delete_by == 'mng_email':
        manager_to_delete = Manager.query.filter_by(mng_email=value).first()
    else:
        return jsonify({"state": 0, "message": "Invalid delete_by parameter"}), 400
    
    # 检查要删除的管理员是否存在
    if not manager_to_delete:
        return jsonify({"state": 0, "message": "Manager not found"}), 406
    
    # 不能删除第一个管理员
    if manager_to_delete.mng_id == 1:
        return jsonify({"state": 0, "message": "Cannot delete the first manager"}), 400

    # 删除管理员
    db.session.delete(manager_to_delete)
    db.session.commit()

    return jsonify({"state": 1, "message": "Manager deleted successfully"})


# 查看当前管理员列表接口
# 注意：只有超级管理员（id=1)才能查看其他管理员
@manager_bp.route('/manager/manager_list', methods=['GET'])
@jwt_required()
def list_managers():
    # 获取当前登录的管理员id
    current_mng_id = get_jwt_identity()
    current_manager = Manager.query.get(current_mng_id)
    
    # 检查当前管理员是否是第一个管理员
    if current_manager.mng_id != 1:
        return jsonify({"state": 0, "message": "Only the first manager can view the list of managers"}), 403
    
    # 获取所有管理员信息
    managers = Manager.query.all()
    managers_list = [
        OrderedDict([
            ("mng_id", manager.mng_id),
            ("mng_name", manager.mng_name),
            ("mng_gender", manager.mng_gender),
            ("mng_nickname", manager.mng_nickname),
            ("mng_avatar", f"/static/{current_manager.mng_avatar}" if current_manager.mng_avatar else "/static/dog.jpg"),
            ("mng_phone", manager.mng_phone),
            ("mng_email", manager.mng_email),
            ("mng_create_at", manager.mng_create_at.isoformat() if manager.mng_create_at else None)
        ])
        for manager in managers
    ]

    return jsonify({"state": 1, "message": "List of managers", "managers": managers_list})


# 管理员查看个人信息接口
@manager_bp.route('/manager/profile', methods=['GET'])
@jwt_required()
def get_manager_profile():
    # 验证当前登录的管理员id
    current_mng_id = get_jwt_identity()
    current_manager = Manager.query.get(current_mng_id)
    if not current_manager:
        return jsonify({"state": 0, "message": "管理员身份验证失败"}), 404
    
    manager_info = OrderedDict([
        ("mng_avatar", f"/static/{current_manager.mng_avatar}" if current_manager.mng_avatar else "/static/dog.jpg"),
        ("mng_id", current_manager.mng_id),
        ("mng_name", current_manager.mng_name),
        ("mng_gender", current_manager.mng_gender),
        ("mng_nickname", current_manager.mng_nickname),
        ("mng_phone", current_manager.mng_phone),
        ("mng_email", current_manager.mng_email),
        ("mng_create_at", current_manager.mng_create_at.isoformat() if current_manager.mng_create_at else None)
    ])
    
    return jsonify({"state": 1, "message": "Manager profile", "profile": manager_info})
    


# 管理员修改个人信息接口
@manager_bp.route('/manager/update_profile', methods=['PUT'])
@jwt_required()
def update_manager_profile():
    #验证管理员身份
    current_mng_id = get_jwt_identity()
    current_manager = Manager.query.get(current_mng_id)
    if not current_manager:
        return jsonify({"state": 0, "message": "管理员身份验证失败"}), 404
    
    data = request.get_json()
    
    # 更新管理员信息
    if 'm_name' in data:
        # 检查用户名是否已存在
        if data['m_name'] != current_manager.mng_name:
            existing_manager = Manager.query.filter_by(mng_name=data['m_name']).first()
            if existing_manager:
                return jsonify({"state": 0, "message": "用户名已存在"}), 400
            current_manager.mng_name = data['m_name']
    
    if 'm_nickname' in data:
        current_manager.mng_nickname = data['m_nickname']
    
    if 'm_gender' in data:
        current_manager.mng_gender = data['m_gender']
    
    if 'm_avatar' in data:
        current_manager.mng_avatar = data['m_avatar']
    
    if 'm_email' in data:
        # 只有当邮箱被修改时才进行唯一性检查
        if data['m_email'] != current_manager.mng_email:
            existing_manager = Manager.query.filter_by(mng_email=data['m_email']).first()
            if existing_manager:
                return jsonify({"state": 0, "message": "邮箱已存在"}), 400
            current_manager.mng_email = data['m_email']
    
    if 'm_phone' in data:
        # 只有当手机号被修改时才进行唯一性检查
        if data['m_phone'] != current_manager.mng_phone:
            existing_manager = Manager.query.filter_by(mng_phone=data['m_phone']).first()
            if existing_manager:
                return jsonify({"state": 0, "message": "手机号已存在"}), 400
            current_manager.mng_phone = data['m_phone']
    
    if 'm_password' in data and 'current_password' in data:
        # 确保原始密码和新密码都不为空
        if not data['current_password'] or not data['m_password']:
            return jsonify({"state": 0, "message": "原始密码和新密码都不能为空"}), 400
        
        # 验证原始密码
        if not current_manager.check_password(data['current_password']):
            return jsonify({"state": 0, "message": "原始密码不正确"}), 400
        
        # 确保新密码与原始密码不同
        if data['current_password'] == data['m_password']:
            return jsonify({"state": 0, "message": "新密码不能与原始密码相同"}), 400
        
        current_manager.set_password(data['m_password'])
    
    db.session.commit()
    
    return jsonify({"state": 1, "message": "个人信息更新成功"})


#管理员查看用户列表接口
@manager_bp.route('/manager/user_list', methods=['GET'])
@jwt_required()
def list_users():
    # 验证管理员身份
    current_mng_id = get_jwt_identity()
    current_manager = Manager.query.get(current_mng_id)
    if not current_manager:
        return jsonify({"state": 0, "message": "管理员身份验证失败"}), 401
    
    # 获取所有用户信息
    users = User.query.all()
    users_list = [
        OrderedDict([
            ("id", user.id),
            ("username", user.username),
            ("nickname", user.nickname),
            ("avatar", f"/static/{user.avatar}" if user.avatar else "/static/dog.jpg"),
            ("gender", user.gender),
            ("email", user.email),
            ("phone", user.phone),
            ("create_at", user.create_at.isoformat() if user.create_at else None),
            ("last_login_at", user.last_login_at.isoformat() if user.last_login_at else None),
            ("is_online", user.is_online if hasattr(user, 'is_online') else 0),
            ("u_status", user.u_status),
            ("is_publish", user.is_publish),
            ("is_comment", user.is_comment),
            ("article_count", len(user.articles) if hasattr(user, 'articles') else 0),
            ("comment_count", user.comment_count if hasattr(user, 'comment_count') else 0),
            ("like_count", user.like_count if hasattr(user, 'like_count') else 0)
            #("notes", user.notes if hasattr(user, 'notes') else "无")
        ])
        for user in users
    ]

    return jsonify({"state": 1, "message": "List of users", "users": users_list})


#管理员修改用户状态接口
"""输入：
       {
        "u_account": 123,               // 必填,要修改的用户名
        "new_status": 0                 //必填,新状态值(0/1)
       }
"""
@manager_bp.route('/manager/update_user_status', methods=['POST'])
@jwt_required()
def update_user_status():
    # 验证管理员身份
    current_mng_id = get_jwt_identity()
    current_manager = Manager.query.get(current_mng_id)
    if not current_manager:
        return jsonify({"state": 0, "message": "管理员身份验证失败"}), 401

    data = request.get_json()
    
    # 参数校验
    required_fields = ['u_account', 'new_status']
    if not all(field in data for field in required_fields):
        return jsonify({"state": 0, "message": "缺少必要参数"}), 400

    user_account = data.get('u_account')
    new_status = data.get('new_status')

    # 验证目标用户
    target_user = User.query.filter((User.id == user_account) | (User.username == user_account) | (User.email == user_account) | (User.phone == user_account)).first()
    if not target_user:
        return jsonify({"state": 0, "message": "用户不存在"}), 404

    # 验证状态值有效性
    if new_status not in [0, 1]:
        return jsonify({
            "state": 0,
            "message": "无效的状态值，只能设置为 0(正常)、1(禁止所有权限)"
        }), 400

    # 执行状态更新
    try:
        target_user.u_status = new_status

        if new_status != 0:
            target_user.is_publish = 0
            target_user.is_comment = 0
        else:
            # 如果用户恢复正常状态，恢复所有的权限
            target_user.is_publish = 1
            target_user.is_comment = 1
        db.session.commit()
        return jsonify({
            "state": 1,
            "message": "用户状态更新成功",
            "user_account": user_account,
            "updated_status": new_status
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "state": 0,
            "message": f"用户状态更新失败: {str(e)}"
        }), 500

#管理员修改用户权限接口
"""输入：
    {
        "u_account": 123,                 // 必填,要修改的用户名
        "permission_type": "is_publish",  //必填,权限类型(is_publish/is_comment)
        "new_value": 0                    //必填,新权限值(0/1)
    }
"""
@manager_bp.route('/manager/update_user_permission', methods=['POST'])
@jwt_required()
def update_user_permission():
    # 验证管理员身份
    current_mng_id = get_jwt_identity()
    current_manager = Manager.query.get(current_mng_id)
    if not current_manager:
        return jsonify({"state": 0, "message": "管理员身份验证失败"}), 401

    data = request.get_json()
    
    # 参数校验
    required_fields = ['u_account', 'permission_type', 'new_value']
    if not all(field in data for field in required_fields):
        return jsonify({"state": 0, "message": "缺少必要参数"}), 400

    user_account = data.get('u_account')
    perm_type = data.get('permission_type')
    new_value = data.get('new_value')

    # 验证目标用户
    target_user = User.query.filter((User.id == user_account) | (User.username == user_account) | (User.email == user_account) | (User.phone == user_account)).first()
    if not target_user:
        return jsonify({"state": 0, "message": "用户不存在"}), 404
    
    # 验证权限类型有效性
    if perm_type not in ['is_publish', 'is_comment']:
        return jsonify({
            "state": 0,
            "message": "无效的权限类型,可选值:is_publish/is_comment"
        }), 400

    # 验证权限值有效性
    if new_value not in [0, 1]:
        return jsonify({
            "state": 0,
            "message": "无效的权限值,只能设置为0或1"
        }), 400

    # 执行权限更新
    try:
        setattr(target_user, perm_type, new_value)
        db.session.commit()
        return jsonify({
            "state": 1,
            "message": "用户权限更新成功",
            "user_account": user_account,
            "updated_permission": {
                perm_type: new_value
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "state": 0,
            "message": f"用户权限更新失败: {str(e)}"
        }), 500
    