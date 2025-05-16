from flask import jsonify, request, Blueprint
from config import Config
from __init__ import db
from db import User, Article, Manager, Comment, CommentLike
from flask_jwt_extended import jwt_required, get_jwt_identity
import functools
from collections import OrderedDict

commentlike_bp = Blueprint('commentlike', __name__)

#用户评论点赞
@commentlike_bp.route('/comment/like/<int:comment_id>', methods=['POST'])
@jwt_required()  # 使用 JWT 要求用户登录
def like_comment(comment_id):
    # 获取评论对象，如果评论不存在则返回 404 错误
    comment = Comment.query.get_or_404(comment_id)

    # 从 JWT 中获取当前用户的 ID
    user_id = get_jwt_identity()
    user_id = int(user_id)  # 确保 user_id 是整数类型

    # 检查是否已经点过赞
    existing_like = CommentLike.query.filter_by(user_id=user_id, comment_id=comment_id).first()
    if existing_like:
        return jsonify({"state": 0, "message": "Already liked"}), 400

    # 创建新的点赞记录
    new_like = CommentLike(user_id=user_id, comment_id=comment_id)
    db.session.add(new_like)

    # 更新评论的点赞数
    comment.like_count += 1
    db.session.add(comment)

    # 提交数据库操作
    db.session.commit()

    # 返回成功响应
    return jsonify({"state": 1, "message": "Comment liked successfully"})

#用户取消点赞
@commentlike_bp.route('/comment/unlike/<int:comment_id>', methods=['POST'])
@jwt_required()  # 使用 JWT 要求用户登录
def unlike_comment(comment_id):
    # 获取评论对象，如果评论不存在则返回 404 错误
    comment = Comment.query.get_or_404(comment_id)

    # 从 JWT 中获取当前用户的 ID
    user_id = get_jwt_identity()
    user_id = int(user_id)  # 确保 user_id 是整数类型

    # 检查是否有点赞记录
    existing_like = CommentLike.query.filter_by(user_id=user_id, comment_id=comment_id).first()
    if not existing_like:
        return jsonify({"state": 0, "message": "Not liked yet"}), 400

    # 删除点赞记录
    db.session.delete(existing_like)

    # 更新评论的点赞数
    if comment.like_count > 0:
        comment.like_count -= 1
        db.session.add(comment)

    # 提交数据库操作
    db.session.commit()

    # 返回成功响应
    return jsonify({"state": 1, "message": "Comment unliked successfully"})

#用户获得某个评论的所有点赞数
@commentlike_bp.route('/comment/likes/count/<int:comment_id>', methods=['GET'])
@jwt_required()
def get_comment_likes_count(comment_id):
    # 获取评论对象，如果评论不存在则返回 404 错误
    comment = Comment.query.get_or_404(comment_id)

    # 获取该评论的所有点赞数
    likes_count = CommentLike.query.filter_by(comment_id=comment_id).count()

    # 返回成功响应
    return jsonify({"state": 1, "message": "Likes count retrieved successfully", "likes_count": likes_count})

#用户获得某个评论所有点赞的用户
@commentlike_bp.route('/comment/likes/users/<int:comment_id>', methods=['GET'])
def get_comment_likes_users(comment_id):
    # 获取评论对象，如果评论不存在则返回 404 错误
    comment = Comment.query.get_or_404(comment_id)

    # 获取该评论的所有点赞用户
    likes_users = CommentLike.get_comment_likes_users(comment_id)

    # 返回成功响应
    return jsonify({"state": 1, "message": "Likes users retrieved successfully", "users": likes_users})