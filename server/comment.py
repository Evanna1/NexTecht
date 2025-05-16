from flask import jsonify, request, Blueprint
from config import Config
from __init__ import db
from db import User, Article, Manager, Comment
from flask_jwt_extended import jwt_required, get_jwt_identity
import functools
from collections import OrderedDict

comment_bp = Blueprint('comment', __name__)

#用户创建评论，已经实现父评论功能
@comment_bp.route('/comment/<int:article_id>/create', methods=['POST'])
@jwt_required()
def create_comment(article_id):
    data = request.json
    content = data.get('content')
    parent_id = data.get('parent_id', None)

    if not content:
        return jsonify({"state": 0, "message": "Invalid input"}), 400

    if not isinstance(article_id, int) or article_id <= 0:
        return jsonify({"state": 0, "message": "Invalid article ID"}), 400

    article = Article.query.get_or_404(article_id)
    parent_comment = Comment.query.get(parent_id) if parent_id else None

    depth = 1 if not parent_comment else parent_comment.depth + 1

    # 从 JWT 中获取用户 ID
    user_id = get_jwt_identity()

    new_comment = Comment(
        content=content,
        user_id=user_id,  # 使用从 JWT 中获取的用户 ID
        article_id=article_id,
        parent_id=parent_id,
        depth=depth
    )
    db.session.add(new_comment)
    if parent_comment:
        parent_comment.reply_count += 1
        db.session.add(parent_comment)

        # 提交数据库会话
    db.session.commit()

    return jsonify({"state": 1, "message": "Comment created successfully", "comment_id": new_comment.id})

#用户更新自己的评论

@comment_bp.route('/comment/update/<int:comment_id>', methods=['PUT'])
@jwt_required()  # 使用 JWT 要求用户登录
def update_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)

    user_id = get_jwt_identity()
    user_id =int(user_id)
    if comment.user_id != user_id:
        return jsonify({"state": 0, "message": "Unauthorized","comment.user_id":comment.user_id,"user_id":user_id}), 403

    # 从请求中获取 JSON 数据
    data = request.json
    new_content = data.get('content')

    # 检查新内容是否为空
    if not new_content:
        return jsonify({"state": 0, "message": "Invalid input"}), 400

    # 更新评论内容
    comment.content = new_content
    db.session.commit()

    # 返回成功响应
    return jsonify({"state": 1, "message": "Comment updated successfully"})


# 用户删除自己的评论
@comment_bp.route('/comment/delete/<int:comment_id>', methods=['DELETE'])
@jwt_required()  # 使用 JWT 要求用户登录
def delete_comment(comment_id):
    # 获取评论对象，如果评论不存在则返回 404 错误
    comment = Comment.query.get_or_404(comment_id)

    # 从 JWT 中获取当前用户的 ID
    user_id = get_jwt_identity()
    user_id = int(user_id)  # 确保 user_id 是整数类型

    # 检查当前用户是否有权限删除该评论
    if comment.user_id != user_id:
        return jsonify({"state": 0, "message": "Unauthorized"}), 403

    # 如果该评论是子评论，更新父评论的回复数
    if comment.parent_id:
        parent_comment = Comment.query.get(comment.parent_id)
        if parent_comment:
            parent_comment.reply_count -= 1
            db.session.add(parent_comment)

    # 删除评论
    db.session.delete(comment)
    db.session.commit()

    # 返回成功响应
    return jsonify({"state": 1, "message": "Comment deleted successfully"})

#用户举报评论(目前只有置位举报，没有记录其他信息)
@comment_bp.route('/comment/report/<int:comment_id>', methods=['POST'])
@jwt_required()
def report_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    comment.report_comment()
    return jsonify({"state": 1, "message": "Comment reported successfully"})



#用户获取自己发布的所有评论
@comment_bp.route('/comment/listall', methods=['GET'])
@jwt_required()  # 使用 JWT 要求用户登录
def get_user_comments():
    # 从 JWT 中获取当前用户的 ID
    user_id = get_jwt_identity()
    user_id = int(user_id)  # 确保 user_id 是整数类型

    # 获取当前用户发布的所有评论
    comments = Comment.query.filter_by(user_id=user_id).all()

    # 将评论转换为字典列表
    comments_list = [
        OrderedDict([
            ("id", comment.id),
            ("content", comment.content),
            ("article_id", comment.article_id),
            ("create_time", comment.create_time.isoformat() if comment.create_time else None),
            ("update_time", comment.update_time.isoformat() if comment.update_time else None),
            ("status", comment.status),
            ("is_approved", comment.is_approved),
            ("like_count", comment.like_count),
            ("reply_count", comment.reply_count),
            ("depth", comment.depth),
            ("parent_id", comment.parent_id)
        ])
        for comment in comments
    ]

    # 返回成功响应
    return jsonify({"state": 1, "message": "User comments", "comments": comments_list})

#用户获取自己所有被举报的评论

@comment_bp.route('/comment/reported_comments', methods=['GET'])
@jwt_required()  # 使用 JWT 要求用户登录
def get_user_reported_comments():
    # 从 JWT 中获取当前用户的 ID
    user_id = get_jwt_identity()
    user_id = int(user_id)  # 确保 user_id 是整数类型

    # 获取当前用户发布的所有被举报的评论
    reported_comments = Comment.query.filter_by(user_id=user_id, status=3).all()

    # 将评论转换为字典列表
    comments_list = [
        OrderedDict([
            ("id", comment.id),
            ("content", comment.content),
            ("article_id", comment.article_id),
            ("create_time", comment.create_time.isoformat() if comment.create_time else None),
            ("update_time", comment.update_time.isoformat() if comment.update_time else None),
            ("status", comment.status),
            ("is_approved", comment.is_approved),
            ("like_count", comment.like_count),
            ("reply_count", comment.reply_count),
            ("depth", comment.depth),
            ("parent_id", comment.parent_id)
        ])
        for comment in reported_comments
    ]

    # 返回成功响应
    return jsonify({"state": 1, "message": "User reported comments", "comments": comments_list})







