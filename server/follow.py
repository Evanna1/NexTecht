from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from __init__ import db
from db import User, Follow 

follow_bp = Blueprint('follow_api', __name__)

# """关注用户"""
@follow_bp.route('/follow/<int:user_id>', methods=['POST'])
@jwt_required()  
def follow_user(user_id):
    current_user_id = get_jwt_identity()  # 获取当前登录用户ID
    followed_user = User.query.get(user_id)

    if not followed_user:
        return jsonify({"message": "User not found"}), 404

    # 检查是否尝试自己关注自己
    if int(current_user_id) == user_id:
        return jsonify({"message": "You cannot follow yourself"}), 400

    # 检查是否已关注
    existing_follow = Follow.query.filter_by(follower_id=current_user_id, followed_id=user_id).first()
    if existing_follow:
        return jsonify({"message": "You are already following this user"}), 400

    # 创建关注关系
    new_follow = Follow(follower_id=current_user_id, followed_id=user_id)
    db.session.add(new_follow)
    db.session.commit()

    return jsonify({"message": f"You are now following {followed_user.username}","cid":current_user_id,"uid":user_id}), 201

# """取消关注用户"""
@follow_bp.route('/unfollow/<int:user_id>', methods=['DELETE'])
@jwt_required()
def unfollow_user(user_id):
    current_user_id = get_jwt_identity()
    followed_user = User.query.get(user_id)

    if not followed_user:
        return jsonify({"message": "User not found"}), 404

    # 查找关注关系
    follow = Follow.query.filter_by(follower_id=current_user_id, followed_id=user_id).first()
    if not follow:
        return jsonify({"message": "You are not following this user"}), 400

    # 删除关注关系
    db.session.delete(follow)
    db.session.commit()

    return jsonify({"message": f"You have unfollowed {followed_user.username}"}), 200

#  """获取当前用户关注的用户列表"""
@follow_bp.route('/following', methods=['GET'])
@jwt_required()
def get_following_users():
    current_user_id = get_jwt_identity()
    following = Follow.query.filter_by(follower_id=current_user_id).all()

    following_users = []
    for follow in following:
        user = User.query.get(follow.followed_id)
        following_users.append({
            'id': user.id,
            'username': user.username,
            'nickname': user.nickname,
            'avatar': user.avatar,
            'intro': user.intro
        })

    return jsonify(following_users), 200

# """获取当前用户的粉丝列表"""
@follow_bp.route('/followers', methods=['GET'])
@jwt_required()
def get_followers():
    current_user_id = get_jwt_identity()
    followers = Follow.query.filter_by(followed_id=current_user_id).all()

    follower_users = []
    for follow in followers:
        user = User.query.get(follow.follower_id)
        follower_users.append({
            'id': user.id,
            'username': user.username,
            'nickname': user.nickname,
            'avatar': user.avatar,
            'intro': user.intro
        })

    return jsonify(follower_users), 200

# """关注数 & 粉丝数统计"""
@follow_bp.route('/follow-count/<int:user_id>', methods=['GET'])
def get_follow_stats(user_id):
    follow_count = Follow.query.filter_by(follower_id=user_id).count()
    follower_count = Follow.query.filter_by(followed_id=user_id).count()
    return jsonify({ "following_count": follow_count, "follower_count": follower_count }), 200

# """互相关注（好友）识别"""
@follow_bp.route('/friends/<int:user_id>', methods=['GET'])
@jwt_required()
def get_follow_status(user_id):
    current_user_id = get_jwt_identity()

    is_following = Follow.query.filter_by(follower_id=current_user_id, followed_id=user_id).first() is not None
    is_followed_by = Follow.query.filter_by(follower_id=user_id, followed_id=current_user_id).first() is not None

    return jsonify({
        "is_following": is_following,
        "is_followed_by": is_followed_by,
        "is_mutual": is_following and is_followed_by
    }), 200

# --- GET /following/<int:user_id> ---
@follow_bp.route('/following/<int:user_id>', methods=['GET'])
# This endpoint is public, anyone can see who a user is following
# If you want to restrict it (e.g., only logged-in users can see lists), add @jwt_required(optional=True) or @jwt_required()
# For now, making it public as per common social media patterns for viewing profiles
def get_user_following(user_id):
    """
    获取指定用户 (user_id) 关注的用户列表。
    """
    # Check if the target user exists
    target_user = User.query.get(user_id)
    if not target_user:
        return jsonify({"message": "User not found"}), 404

    # Query the Follow table to find all entries where the follower is the target user
    following_relationships = Follow.query.filter_by(follower_id=user_id).all()

    following_users_list = []
    for follow_rel in following_relationships:
        # Get the user object for the followed user
        followed_user = User.query.get(follow_rel.followed_id)
        # Ensure the user exists before adding to the list (should ideally always exist due to foreign key)
        if followed_user:
            following_users_list.append({
                'id': followed_user.id, # Include user ID as requested
                'username': followed_user.username,
                # 'nickname': followed_user.nickname, # Include if your User model has nickname
                'avatar': followed_user.avatar,
                'intro': followed_user.intro,
                # Note: is_following/is_followed_by status relative to the *viewer* is handled by the /friends endpoint
            })

    # Return the list of users the target user is following
    # Returning just the list is fine, or wrap in {"data": ...} for consistency
    return jsonify(following_users_list), 200
    # Or for consistency with article list: return jsonify({"data": following_users_list}), 200


# --- GET /followers/<int:user_id> ---
@follow_bp.route('/followers/<int:user_id>', methods=['GET'])
# This endpoint is public, anyone can see who is following a user
# If you want to restrict it, add @jwt_required(optional=True) or @jwt_required()
# For now, making it public
def get_user_followers(user_id):
    """
    获取关注指定用户 (user_id) 的用户列表 (粉丝列表)。
    """
    # Check if the target user exists
    target_user = User.query.get(user_id)
    if not target_user:
        return jsonify({"message": "User not found"}), 404

    # Query the Follow table to find all entries where the followed is the target user
    follower_relationships = Follow.query.filter_by(followed_id=user_id).all()

    follower_users_list = []
    for follow_rel in follower_relationships:
        # Get the user object for the follower user
        follower_user = User.query.get(follow_rel.follower_id)
         # Ensure the user exists
        if follower_user:
            follower_users_list.append({
                'id': follower_user.id, # Include user ID as requested
                'username': follower_user.username,
                # 'nickname': follower_user.nickname, # Include if your User model has nickname
                'avatar': follower_user.avatar,
                'intro': follower_user.intro,
                 # Note: is_following/is_followed_by status relative to the *viewer* is handled by the /friends endpoint
            })

    # Return the list of users who are following the target user
    return jsonify(follower_users_list), 200
    # Or for consistency: return jsonify({"data": follower_users_list}), 200


# --- GET /friends/<int:user_id> ---
# This endpoint checks the follow status *between the CURRENT authenticated user* and the specified user_id
@follow_bp.route('/friends/<int:user_id>', methods=['GET'])
# This endpoint requires authentication because it's about the CURRENT user's relationship
@jwt_required()
# Renamed the function to avoid endpoint name conflict
def get_user_follow_status(user_id):
    """
    获取当前登录用户与指定用户 (user_id) 之间的关注状态。
    返回 is_following (当前用户是否关注了 user_id),
    is_followed_by (user_id 是否关注了当前用户),
    is_mutual (是否互相关注)。
    """
    # Get the ID of the currently authenticated user from the JWT
    current_user_id = get_jwt_identity()

    # Check if the target user exists
    target_user = User.query.get(user_id)
    if not target_user:
        return jsonify({"message": "Target user not found"}), 404

    # Prevent checking status against self (optional, frontend should ideally handle this)
    if int(current_user_id) == user_id:
         # You might return a specific status or just the counts in this case
         # For simplicity, let's return a status indicating it's the same user
         return jsonify({
             "is_following": False, # You don't follow yourself in this context
             "is_followed_by": False, # You are not followed by yourself
             "is_mutual": False,
             "is_self": True # Indicate it's the current user
         }), 200


    # Check if the current user is following the target user
    is_following = Follow.query.filter_by(
        follower_id=current_user_id,
        followed_id=user_id
    ).first() is not None

    # Check if the target user is following the current user
    is_followed_by = Follow.query.filter_by(
        follower_id=user_id,
        followed_id=current_user_id
    ).first() is not None

    # Determine if they are mutually following
    is_mutual = is_following and is_followed_by

    # Return the status
    return jsonify({
        "is_following": is_following,
        "is_followed_by": is_followed_by,
        "is_mutual": is_mutual
    }), 200



