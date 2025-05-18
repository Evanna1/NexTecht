from flask import jsonify, request, Blueprint
from config import Config
from __init__ import db
from db import User, Article, Manager, Comment, CommentLike
from flask_jwt_extended import jwt_required, get_jwt_identity
import functools
from collections import OrderedDict

commentlike_bp = Blueprint('commentlike', __name__)

# 用户评论点赞 (修改为返回 updated count 和 is_liked 状态)
@commentlike_bp.route('/comment/like/<int:comment_id>', methods=['POST'])
@jwt_required()
def like_comment(comment_id):
    comment = Comment.query.get(comment_id)
    if not comment:
        return jsonify({"state": 0, "message": "Comment not found"}), 404

    user_id = int(get_jwt_identity())

    # 检查是否已经点过赞
    existing_like = CommentLike.query.filter_by(user_id=user_id, comment_id=comment_id).first()
    if existing_like:
        # 如果已经点赞，返回成功但带上当前状态信息，方便前端确认
        return jsonify({"state": 1, "message": "Already liked", "like_count": comment.like_count, "is_liked": True}), 200 # 返回 200 OK

    # 创建新的点赞记录
    new_like = CommentLike(user_id=user_id, comment_id=comment_id)
    db.session.add(new_like)

    # 更新评论的点赞数
    comment.like_count += 1
    db.session.add(comment) # 确保 comment 对象被跟踪修改

    db.session.commit()

    # 返回成功响应，包含更新后的点赞数和状态
    return jsonify({"state": 1, "message": "Comment liked successfully", "like_count": comment.like_count, "is_liked": True}), 200 # 返回 200 OK


# 用户取消点赞 (修改为返回 updated count 和 is_liked 状态)
@commentlike_bp.route('/comment/unlike/<int:comment_id>', methods=['POST'])
@jwt_required()
def unlike_comment(comment_id):
    comment = Comment.query.get(comment_id)
    if not comment:
        return jsonify({"state": 0, "message": "Comment not found"}), 404

    user_id = int(get_jwt_identity())

    # 检查是否有点赞记录
    existing_like = CommentLike.query.filter_by(user_id=user_id, comment_id=comment_id).first()
    if not existing_like:
        # 如果没有点赞记录，返回成功但带上当前状态信息，方便前端确认
         return jsonify({"state": 1, "message": "Not liked yet", "like_count": comment.like_count, "is_liked": False}), 200 # 返回 200 OK

    db.session.delete(existing_like)

    # 更新评论的点赞数，确保不小于0
    if comment.like_count > 0:
        comment.like_count -= 1
        db.session.add(comment) # 确保 comment 对象被跟踪修改

    db.session.commit()

    # 返回成功响应，包含更新后的点赞数和状态
    return jsonify({"state": 1, "message": "Comment unliked successfully", "like_count": comment.like_count, "is_liked": False}), 200 # 返回 200 OK


# 用户获得某个评论的所有点赞数 (保留你原有的接口)
@commentlike_bp.route('/comment/likes/count/<int:comment_id>', methods=['GET'])
# 这个接口不需要 @jwt_required() 如果只是获取数量，因为数量是公开的
# 如果需要知道当前用户是否点赞，应该用上面的 get_article_comments/get_comment_replies 或者修改这个接口为可选登录并添加 is_liked
def get_comment_likes_count(comment_id):
    comment = Comment.query.get(comment_id)
    if not comment:
        return jsonify({"state": 0, "message": "Comment not found"}), 404

    # 直接从评论对象获取点赞数更高效，因为 comment.like_count 应该总是最新的
    # 如果 comment.like_count 不可靠，再查询 CommentLike 表
    likes_count = comment.like_count # 使用模型字段

    # 如果需要从 CommentLike 表查询，使用这个：
    # likes_count = CommentLike.query.filter_by(comment_id=comment_id).count()


    # 返回成功响应
    return jsonify({"state": 1, "message": "Likes count retrieved successfully", "likes_count": likes_count})


# 用户获得某个评论所有点赞的用户 (保留你原有的接口)
@commentlike_bp.route('/comment/likes/users/<int:comment_id>', methods=['GET'])
# 这个接口可以保留，用于显示点赞用户列表
def get_comment_likes_users(comment_id):
    comment = Comment.query.get(comment_id)
    if not comment:
        return jsonify({"state": 0, "message": "Comment not found"}), 404

    # 根据你的 CommentLike 模型和可能的 get_comment_likes_users 方法实现
    # 假设 CommentLike 模型有 user 关系，并且你可以高效地获取点赞用户的列表
    likes = CommentLike.query.filter_by(comment_id=comment_id).options(db.joinedload(CommentLike.user)).all()

    users_list = []
    for like in likes:
        if like.user: # 确保用户存在
            users_list.append({
                'id': like.user.id,
                'username': like.user.username,
                'nickname': like.user.nickname,
                'avatar': like.user.avatar # 假设 User 模型有 avatar 字段
            })


    # 返回成功响应
    return jsonify({"state": 1, "message": "Likes users retrieved successfully", "users": users_list})