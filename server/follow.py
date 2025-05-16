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






