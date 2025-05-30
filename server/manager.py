from flask import Blueprint, request, jsonify
from __init__ import db
from db import User, Manager, Article,Follow, ArticleFavorite,Comment,Alike,UserBrowseRecord,CommentLike
from datetime import datetime
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from collections import OrderedDict

def truncate_filter(s, max_length=10, end='...'):
    if len(s) > max_length:
        return s[:max_length] + end
    return s

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
            (
            "mng_avatar", f"/static/{current_manager.mng_avatar}" if current_manager.mng_avatar else "/static/dog.jpg"),
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
        ("mng_avatar", f"/static/{current_manager.mng_avatar}" if current_manager.mng_avatar else "/static/my.jpg"),
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
    # 验证管理员身份
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


# 管理员查看用户列表接口
@manager_bp.route('/manager/user_list', methods=['GET'])
@jwt_required()
def list_users():
    # 验证管理员身份
    current_mng_id = get_jwt_identity()
    current_manager = Manager.query.get(current_mng_id)
    if not current_manager:
        return jsonify({"state": 0, "message": "管理员身份验证失败"}), 401

    # 查询所有用户
    users = User.query.all()

    # 将用户对象转换为字典列表，调用模型中的 to_dict() 方法
    users_list = [user.to_dict() for user in users]

    return jsonify({"state": 1, "message": "List of users", "users": users_list})


# 管理员修改用户状态接口
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
    target_user = User.query.filter(
        (User.id == user_account) | (User.username == user_account) | (User.email == user_account) | (
                    User.phone == user_account)).first()
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


# 管理员修改用户权限接口
"""输入：
    {
        "u_account": "...",
        "is_publish": 1,
        "is_comment": 0
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

    # 参数校验：必须有 u_account，其他权限字段为可选
    if 'u_account' not in data:
        return jsonify({"state": 0, "message": "缺少必要参数 u_account"}), 400

    user_account = data.get('u_account')

    # 验证目标用户
    target_user = User.query.filter(
        (User.id == user_account) |
        (User.username == user_account) |
        (User.email == user_account) |
        (User.phone == user_account)
    ).first()

    if not target_user:
        return jsonify({"state": 0, "message": "用户不存在"}), 404

    if target_user.u_status != 0:
        return jsonify({"state": 0, "message": "用户已被封禁，无法修改权限"}), 400

    updated_permissions = {}
    valid_fields = ['is_publish', 'is_comment']

    try:
        for field in valid_fields:
            if field in data:
                val = data[field]
                if val not in [0, 1]:
                    return jsonify({"state": 0, "message": f"无效的权限值 {field}，只能是0或1"}), 400
                setattr(target_user, field, val)
                updated_permissions[field] = val

        if not updated_permissions:
            return jsonify({"state": 0, "message": "未提供有效的权限字段"}), 400

        db.session.commit()
        return jsonify({
            "state": 1,
            "message": "用户权限更新成功",
            "user_account": user_account,
            "updated_permission": updated_permissions
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "state": 0,
            "message": f"用户权限更新失败: {str(e)}"
        }), 500
    

# 管理员获取指定用户的名字
@manager_bp.route('/manager/user/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_detail(user_id):
    # 验证管理员身份
    current_mng_id = get_jwt_identity()
    current_manager = Manager.query.get(current_mng_id)
    if not current_manager:
        return jsonify({"state": 0, "message": "管理员身份验证失败"}), 401

    # 检查目标用户是否存在
    target_user = User.query.get(user_id)
    if not target_user:
        return jsonify({"state": 0, "message": "目标用户不存在"}), 404

    # 返回用户详细信息
    return jsonify({
        "state": 1,
        "message": "用户信息获取成功",
        "user": target_user.username
    }), 200
    
# 管理员查看特定用户发布过的文章列表
@manager_bp.route('/manager/user/<int:user_id>/published-articles', methods=['GET'])
@jwt_required()
def get_user_published_articles(user_id):
    # 验证管理员身份
    current_mng_id = get_jwt_identity()
    current_manager = Manager.query.get(current_mng_id)
    if not current_manager:
        return jsonify({"state": 0, "message": "管理员身份验证失败"}), 401

    # 检查目标用户是否存在
    target_user = User.query.get(user_id)
    if not target_user:
        return jsonify({"state": 0, "message": "目标用户不存在"}), 404

    # 查找该用户发布过的所有文章
    user_articles = Article.query.filter_by(user_id=user_id).all()

    # 按创建时间排序（从新到旧）
    user_articles.sort(key=lambda x: x.create_time, reverse=True)

    # 转换文章对象为字典格式
    articles = [article.mng_to_dict() for article in user_articles]

    return jsonify({
        "state": 1,
        "message": "List of articles",
        "articles": articles
    })


# 管理员查看特定用户的评论记录
@manager_bp.route('/manager/user/<int:user_id>/comments', methods=['GET'])
@jwt_required()
def get_user_comments(user_id):
    # 验证管理员身份
    current_mng_id = get_jwt_identity()
    current_manager = Manager.query.get(current_mng_id)
    if not current_manager:
        return jsonify({"state": 0, "message": "管理员身份验证失败"}), 401

    # 检查目标用户是否存在
    target_user = User.query.get(user_id)
    if not target_user:
        return jsonify({"state": 0, "message": "目标用户不存在"}), 404

    # 查找该用户的所有评论
    user_comments = Comment.query.filter_by(user_id=user_id).all()

    # 获取评论的详细信息，包括文章标题
    user_comments_list = []
    for comment in user_comments:
        article = Article.query.get(comment.article_id)
        if article:
            user_comments_list.append({
                "comment_id": comment.id,
                "article_id": article.id,
                "article_title": article.title,
                "comment_content": comment.content,
                "comment_create_time": comment.create_time.isoformat(),
                "comment_update_time": comment.update_time.isoformat() if comment.update_time else None,
                "comment_status": comment.status,
                "comment_like_count": comment.like_count,
                "comment_reply_count": comment.reply_count,
                "comment_is_approved": comment.is_approved,
                'depth': comment.depth,
                "user_info": target_user.to_dict()
            })

    # 按评论时间排序（从新到旧）
    user_comments_list.sort(key=lambda x: x["comment_create_time"], reverse=True)

    return jsonify({
        "state": 1,
        "message": f"用户 {user_id} 的评论记录",
        "user_nickname": target_user.nickname,
        "comment_count": len(user_comments_list),
        "comments": user_comments_list
    }), 200

# 管理员查看特定用户的点赞文章列表
@manager_bp.route('/manager/user/<int:user_id>/liked-articles', methods=['GET'])
@jwt_required()
def get_user_liked_articles(user_id):
    # 验证管理员身份
    current_mng_id = get_jwt_identity()
    current_manager = Manager.query.get(current_mng_id)
    if not current_manager:
        return jsonify({"state": 0, "message": "管理员身份验证失败"}), 401

    # 检查目标用户是否存在
    target_user = User.query.get(user_id)
    if not target_user:
        return jsonify({"state": 0, "message": "目标用户不存在"}), 404

    # 查找该用户点赞的所有文章记录
    user_likes = Alike.query.filter_by(user_id=user_id).all()

    # 获取点赞文章的详细信息
    liked_articles = []
    for like in user_likes:
        article = Article.query.get(like.article_id)
        if article:
            liked_articles.append({
                "article_info": article.to_dict(),
                "like_create_time": like.create_time.isoformat()
            })

    # 按点赞时间排序（从新到旧）
    liked_articles.sort(key=lambda x: x["like_create_time"], reverse=True)

    return jsonify({
        "state": 1,
        "message": f"用户 {user_id} 的点赞文章列表",
        "user_nickname": target_user.nickname,
        "like_count": len(liked_articles),
        "liked_articles": liked_articles
    }), 200
    
# 管理员获取指定用户的粉丝列表，返回完整用户信息。
@manager_bp.route('/manager/followers/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_followers(user_id):
    # 验证管理员身份
    current_mng_id = get_jwt_identity()
    current_manager = Manager.query.get(current_mng_id)
    if not current_manager:
        return jsonify({"state": 0, "message": "管理员身份验证失败"}), 401

    # 检查目标用户是否存在
    target_user = User.query.get(user_id)
    if not target_user:
        return jsonify({"state": 0, "message": "目标用户不存在"}), 404

    # 查找所有关注该用户的记录（即粉丝）
    follower_relationships = Follow.query.filter_by(followed_id=user_id).all()

    # 构造粉丝用户列表，调用每个用户的 to_dict()
    followers_list = []
    for rel in follower_relationships:
        follower_user = User.query.get(rel.follower_id)
        if follower_user:
            followers_list.append(follower_user.to_dict())

    return jsonify({
        "state": 1,
        "message": f"用户 {user_id} 的粉丝列表",
        "followers": followers_list
    }), 200

# 管理员获取指定用户的关注列表，返回完整用户信息。
@manager_bp.route('/manager/following/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_following(user_id):

    # 验证管理员身份
    current_mng_id = get_jwt_identity()
    current_manager = Manager.query.get(current_mng_id)
    if not current_manager:
        return jsonify({"state": 0, "message": "管理员身份验证失败"}), 401

    # 检查目标用户是否存在
    target_user = User.query.get(user_id)
    if not target_user:
        return jsonify({"state": 0, "message": "目标用户不存在"}), 404

    # 查找该用户关注的所有人（即关注列表）
    following_relationships = Follow.query.filter_by(follower_id=user_id).all()

    following_users_list = []
    for rel in following_relationships:
        followed_user = User.query.get(rel.followed_id)
        if followed_user:
            following_users_list.append(followed_user.to_dict())

    return jsonify({
        "state": 1,
        "message": f"用户 {user_id} 的关注列表",
        "following": following_users_list
    }), 200

# 管理员获取指定文章的收藏列表，返回收藏该文章的用户信息。
@manager_bp.route('/manager/favorites/<int:article_id>', methods=['GET'])
@jwt_required()
def get_article_favorites(article_id):
    # 验证管理员身份
    current_mng_id = get_jwt_identity()
    current_manager = Manager.query.get(current_mng_id)
    if not current_manager:
        return jsonify({"state": 0, "message": "管理员身份验证失败"}), 401

    # 检查目标文章是否存在
    target_article = Article.query.get(article_id)
    if not target_article:
        return jsonify({"state": 0, "message": "目标文章不存在"}), 404

    # 查找收藏该文章的所有收藏记录
    favorite_relationships = ArticleFavorite.query.filter_by(article_id=article_id).all()

    # 获取收藏该文章的用户信息
    favorite_users_list = []
    for favorite in favorite_relationships:
        user = User.query.get(favorite.user_id)
        if user:
            favorite_users_list.append(user.to_dict())

    # 按收藏时间排序（可选）
    favorite_users_list.sort(key=lambda x: x['create_at'], reverse=True)

    return jsonify({
        "state": 1,
        "message": f"文章 {article_id} 的收藏列表",
        "favorites_count": len(favorite_users_list),
        "favorites": favorite_users_list
    }), 200

# 管理员查看特定文章的评论用户列表
@manager_bp.route('/manager/article/<int:article_id>/comment-users', methods=['GET'])
@jwt_required()
def get_article_comment_users(article_id):
    # 验证管理员身份
    current_mng_id = get_jwt_identity()
    current_manager = Manager.query.get(current_mng_id)
    if not current_manager:
        return jsonify({"state": 0, "message": "管理员身份验证失败"}), 401

    # 检查目标文章是否存在
    target_article = Article.query.get(article_id)
    if not target_article:
        return jsonify({"state": 0, "message": "目标文章不存在"}), 404

    # 查找该文章的所有评论
    comments = Comment.query.filter_by(article_id=article_id).all()

    # 获取评论用户的详细信息
    comment_users = []
    for comment in comments:
        user = User.query.get(comment.user_id)
        if user:
            comment_users.append({
                "user_info": user.to_dict(),
                "comment_content": truncate_filter(comment.content, max_length=10, end='...'),
                "comment_create_time": comment.create_time.isoformat(),
                "comment_update_time": comment.update_time.isoformat() if comment.update_time else None,
                "comment_id": comment.id
            })

    # 按评论时间排序（从新到旧）
    comment_users.sort(key=lambda x: x["comment_create_time"], reverse=True)

    return jsonify({
        "state": 1,
        "message": f"文章 {article_id} 的评论用户列表",
        "article_title": target_article.title,
        "comment_count": len(comment_users),
        "comment_users": comment_users
    }), 200


# 管理员查看特定文章的点赞用户列表
@manager_bp.route('/manager/article/<int:article_id>/like-users', methods=['GET'])
@jwt_required()
def get_article_like_users(article_id):
    # 验证管理员身份
    current_mng_id = get_jwt_identity()
    current_manager = Manager.query.get(current_mng_id)
    if not current_manager:
        return jsonify({"state": 0, "message": "管理员身份验证失败"}), 401

    # 检查目标文章是否存在
    target_article = Article.query.get(article_id)
    if not target_article:
        return jsonify({"state": 0, "message": "目标文章不存在"}), 404

    # 查找该文章的所有点赞记录
    likes = Alike.query.filter_by(article_id=article_id).all()

    # 获取点赞用户的详细信息
    like_users = []
    for like in likes:
        user = User.query.get(like.user_id)
        if user:
            like_users.append({
                "user_info": user.to_dict(),
                "like_create_time": like.create_time.isoformat()
            })

    # 按点赞时间排序（从新到旧）
    like_users.sort(key=lambda x: x["like_create_time"], reverse=True)

    return jsonify({
        "state": 1,
        "message": f"文章 {article_id} 的点赞用户列表",
        "article_title": target_article.title,
        "like_count": len(like_users),
        "like_users": like_users
    }), 200

# 管理员查看特定文章的浏览者列表
@manager_bp.route('/manager/article/<int:article_id>/browsers', methods=['GET'])
@jwt_required()
def get_article_browsers(article_id):
    # 验证管理员身份
    current_mng_id = get_jwt_identity()
    current_manager = Manager.query.get(current_mng_id)
    if not current_manager:
        return jsonify({"state": 0, "message": "管理员身份验证失败"}), 401

    # 检查目标文章是否存在
    target_article = Article.query.get(article_id)
    if not target_article:
        return jsonify({"state": 0, "message": "目标文章不存在"}), 404

    # 查找该文章的所有浏览记录
    browsers = UserBrowseRecord.query.filter_by(article_id=article_id).all()

    # 获取浏览者的详细信息
    browser_users = []
    for record in browsers:
        user = User.query.get(record.user_id)
        if user:
            browser_users.append({
                "user_info": user.to_dict(),
                "browse_time": record.browse_time.isoformat()
            })

    # 按浏览时间排序（从新到旧）
    browser_users.sort(key=lambda x: x["browse_time"], reverse=True)

    return jsonify({
        "state": 1,
        "message": f"文章 {article_id} 的浏览者列表",
        "article_title": target_article.title,
        "browse_count": len(browser_users),
        "browser_users": browser_users
    }), 200

# 管理员根据用户 ID 或用户名查看用户信息
@manager_bp.route('/manager/user/search', methods=['GET'])
@jwt_required()
def search_user():
    # 验证管理员身份
    current_mng_id = get_jwt_identity()
    current_manager = Manager.query.get(current_mng_id)
    if not current_manager:
        return jsonify({"state": 0, "message": "管理员身份验证失败"}), 401

    # 获取查询参数
    user_id = request.args.get('user_id', type=int)
    username = request.args.get('username', type=str)

    # 根据用户 ID 或用户名查询用户
    if user_id:
        user = User.query.get(user_id)
    elif username:
        user = User.query.filter_by(username=username).first()
    else:
        return jsonify({"state": 0, "message": "请提供用户 ID 或用户名"}), 400

    if not user:
        return jsonify({"state": 0, "message": "用户不存在"}), 404

    # 返回用户信息
    return jsonify({
        "state": 1,
        "message": "用户信息获取成功",
        "user": user.to_dict()
    }), 200

# 获取所有评论列表（管理员专用）
@manager_bp.route('/manager/comment_list', methods=['GET'])
@jwt_required()
def get_all_comments():
    comments = Comment.query.all()
    comments_list = [comment.to_dict() for comment in comments]
    return jsonify({
        "state": 1,
        "message": "List of comments",
        "comments_list": comments_list
    })

# 管理员获取评论内容
@manager_bp.route('/manager/comment/<int:comment_id>/content', methods=['GET'])
@jwt_required()
def get_comment_content(comment_id):
    # 验证管理员身份
    current_mng_id = get_jwt_identity()
    current_manager = Manager.query.get(current_mng_id)
    if not current_manager:
        return jsonify({"state": 0, "message": "管理员身份验证失败"}), 401

    # 查询评论
    comment = Comment.query.get(comment_id)
    if not comment:
        return jsonify({"state": 0, "message": "评论不存在"}), 404

     # 返回评论内容
    return jsonify({
        "state": 1,
        "message": "获取评论内容成功",
        "content": comment.content,
        "author": comment.user.nickname,
        "create_time": comment.create_time,
        "update_time": comment.update_time
    }), 200

# 管理员修改评论状态（屏蔽/恢复评论）
@manager_bp.route('/manager/comment/<int:comment_id>/status', methods=['POST'])
@jwt_required()
def update_comment_status(comment_id):
    # 验证管理员身份
    current_mng_id = get_jwt_identity()
    current_manager = Manager.query.get(current_mng_id)
    if not current_manager:
        return jsonify({"state": 0, "message": "管理员身份验证失败"}), 401

    # 检查目标评论是否存在
    target_comment = Comment.query.get(comment_id)
    if not target_comment:
        return jsonify({"state": 0, "message": "目标评论不存在"}), 404

    # 获取新状态
    data = request.get_json()
    if not data or 'status' not in data:
        return jsonify({"state": 0, "message": "请求数据格式错误"}), 400

    action = data['status']  # 0: 不屏蔽, 1: 屏蔽

    # 更新评论状态
    if action == 1:
        # 屏蔽评论
        target_comment.status = 2  # 假设 status=2 表示屏蔽
    elif action == 0:
        # 不屏蔽评论，恢复为正常状态（如果之前是屏蔽或已举报）
        if target_comment.status in [2, 3]:  # 假设 status=2 屏蔽，status=3 已举报
            target_comment.status = 0  # 恢复为正常状态
    else:
        return jsonify({"state": 0, "message": "无效的操作参数"}), 400

    db.session.commit()

    # 返回更新结果
    return jsonify({
        "state": 1,
        "message": "评论状态更新成功",
        "comment_id": target_comment.id,
        "new_status": target_comment.status
    }), 200

# 管理员删除评论
@manager_bp.route('/manager/comment/<int:comment_id>/delete', methods=['POST'])
@jwt_required()
def delete_comment(comment_id):
    # 验证管理员身份
    current_mng_id = get_jwt_identity()
    current_manager = Manager.query.get(current_mng_id)
    if not current_manager:
        return jsonify({"state": 0, "message": "管理员身份验证失败"}), 401

    # 检查目标评论是否存在
    target_comment = Comment.query.get(comment_id)
    if not target_comment:
        return jsonify({"state": 0, "message": "目标评论不存在"}), 404

    # 更新评论的状态为已删除
    target_comment.status = 1  # 假设 status=1 表示已删除
    db.session.commit()

    # 返回删除结果和评论内容
    return jsonify({
        "state": 1,
        "message": "评论删除成功",
        "comment_id": target_comment.id
    }), 200

# 管理员查看特定评论的回复列表
@manager_bp.route('/manager/comment/<int:comment_id>/replies', methods=['GET'])
@jwt_required()
def get_comment_replies(comment_id):
    # 验证管理员身份
    current_mng_id = get_jwt_identity()
    current_manager = Manager.query.get(current_mng_id)
    if not current_manager:
        return jsonify({"state": 0, "message": "管理员身份验证失败"}), 401

    # 检查目标评论是否存在
    target_comment = Comment.query.get(comment_id)
    if not target_comment:
        return jsonify({"state": 0, "message": "目标评论不存在"}), 404

    # 查找该评论的所有回复（子评论）
    replies = Comment.query.filter_by(parent_id=comment_id).all()

    # 获取回复的详细信息
    replies_list = []
    for reply in replies:
        replies_list.append({
            "reply_id": reply.id,
            "content": reply.content,
            "article_id": reply.article_id,
            "create_time": reply.create_time.isoformat(),
            "update_time": reply.update_time.isoformat() if reply.update_time else None,
            "status": reply.status,
            "like_count": reply.like_count,
            "reply_count": reply.reply_count,
            "depth": reply.depth,
            "user": {
                "id": reply.user.id,
                "username": reply.user.username,
                "nickname": reply.user.nickname,
                "avatar": reply.user.avatar
            }
        })

    # 按创建时间排序（从新到旧）
    replies_list.sort(key=lambda x: x["create_time"], reverse=True)

    return jsonify({
        "state": 1,
        "message": f"评论 {comment_id} 的回复列表",
        "comment_content": target_comment.content,
        "reply_count": len(replies_list),
        "replies": replies_list
    }), 200

# 管理员查看特定评论
@manager_bp.route('/manager/comment/<int:comment_id>', methods=['GET'])
@jwt_required()
def get_commen(comment_id):
    # 验证管理员身份
    current_mng_id = get_jwt_identity()
    current_manager = Manager.query.get(current_mng_id)
    if not current_manager:
        return jsonify({"state": 0, "message": "管理员身份验证失败"}), 401

    # 检查目标评论是否存在
    target_comment = Comment.query.get(comment_id)
    if not target_comment:
        return jsonify({"state": 0, "message": "目标评论不存在"}), 404

    # 返回评论信息
    return jsonify({
        "state": 1,
        "message": "评论获取成功",
        "target_comment": target_comment.to_dict()
    }), 200

# 管理员查看特定评论的点赞用户列表
@manager_bp.route('/manager/comment/<int:comment_id>/likes', methods=['GET'])
@jwt_required()
def get_comment_likes(comment_id):
    # 验证管理员身份
    current_mng_id = get_jwt_identity()
    current_manager = Manager.query.get(current_mng_id)
    if not current_manager:
        return jsonify({"state": 0, "message": "管理员身份验证失败"}), 401

    # 检查目标评论是否存在
    target_comment = Comment.query.get(comment_id)
    if not target_comment:
        return jsonify({"state": 0, "message": "目标评论不存在"}), 404

    # 查找该评论的所有点赞记录
    like_records = CommentLike.query.filter_by(comment_id=comment_id).all()

    # 获取点赞用户的指定信息
    like_users = []
    for like in like_records:
        user = User.query.get(like.user_id)
        if user:
            like_users.append({
                "user_id": user.id,
                "username": user.username,
                "nickname": user.nickname,
                "avatar": user.avatar,
                "like_time": like.created_at.isoformat()
            })

    # 按点赞时间排序（从新到旧）
    like_users.sort(key=lambda x: x["like_time"], reverse=True)

    return jsonify({
        "state": 1,
        "message": f"评论 {comment_id} 的点赞用户列表",
        "comment_content": target_comment.content,
        "like_count": len(like_users),
        "like_users": like_users
    }), 200

