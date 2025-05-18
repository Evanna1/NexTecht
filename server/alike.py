from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from __init__ import db
from db import Alike, Article

alike_bp = Blueprint('alike', __name__)

@alike_bp.route('/alike/like/<int:article_id>', methods=['POST'])
@jwt_required()
def like_article(article_id):
    user_id = int(get_jwt_identity()) # 确保获取到整数类型的用户ID
    article = Article.query.get(article_id)
    if not article:
        return jsonify({"state": 0, "message": "Article not found"}), 404
    existing_like = Alike.query.filter_by(user_id=user_id, article_id=article_id).first()
    if existing_like:
        # 已经点赞过，返回当前状态和计数
        return jsonify({
            "state": 0, # 或者你可以设计为 state: 1, 只是 message 不同
            "message": "Already liked",
            "like_count": article.like_count, # 返回当前点赞数
            "is_liked": True # 返回当前用户已点赞状态
        }), 200 # 200 OK 或 400 Bad Request, 取决于你的 API 设计
    new_like = Alike(user_id=user_id, article_id=article_id, create_time=datetime.utcnow())
    db.session.add(new_like)
    article.like_count += 1
    db.session.commit()
    return jsonify({
        "state": 1,
        "message": "Liked successfully",
        "like_count": article.like_count, # 返回更新后的点赞数
        "is_liked": True # 返回当前用户已点赞状态
    }), 200

@alike_bp.route('/alike/unlike/<int:article_id>', methods=['POST'])
@jwt_required()
def unlike_article(article_id):
    user_id = int(get_jwt_identity()) # 确保获取到整数类型的用户ID
    article = Article.query.get(article_id)
    if not article:
        return jsonify({"state": 0, "message": "Article not found"}), 404
    like = Alike.query.filter_by(user_id=user_id, article_id=article_id).first()
    if not like:
        return jsonify({
            "state": 0, # 或者你可以设计为 state: 1, 只是 message 不同
            "message": "Like not found",
            "like_count": article.like_count, # 返回当前点赞数
            "is_liked": False # 返回当前用户未点赞状态
        }), 200 # 200 OK 或 400 Bad Request
    db.session.delete(like)
    article.like_count = max(0, article.like_count - 1)
    db.session.commit()
    return jsonify({
        "state": 1,
        "message": "Unliked successfully",
        "like_count": article.like_count, # 返回更新后的点赞数
        "is_liked": False # 返回当前用户未点赞状态
    }), 200

# 获取文章的点赞数
@alike_bp.route('/alike/count/<int:article_id>', methods=['GET'])
def get_like_count(article_id):
    count = Alike.query.filter_by(article_id=article_id).count()
    return jsonify({"state": 1, "like_count": count}), 200

# 获取文章的点赞用户
@alike_bp.route('/alike/list/<int:article_id>', methods=['GET'])
@jwt_required()
def get_likers(article_id):
    user_id = get_jwt_identity()

    if not article_id:
        return jsonify({"state": 0, "message": "Article ID is required"}), 400

    # 获取文章
    article = Article.query.filter_by(id=article_id).first()
    if not article:
        return jsonify({"state": 0, "message": "Article not found"}), 404

    # 仅允许文章作者查看
    if str(article.user_id) != user_id:
        return jsonify({"state": 0, "message": "Permission denied"}), 403

    # 获取点赞者
    likes = Alike.query.filter_by(article_id=article_id).all()
    likers_info = [{
        "nickname": like.user.nickname,
        "avatar": like.user.avatar,
        "time": like.create_time
    } for like in likes]

    return jsonify({
        "state": 1,
        "message": "Liker list fetched successfully",
        "data": likers_info
    }), 200

# 获取用户的所有点赞记录
@alike_bp.route('/alike/user/records', methods=['GET'])
@jwt_required()
def get_user_likes():
    user_id = get_jwt_identity()  # 获取当前用户的 ID

    # 获取当前用户所有的点赞记录
    likes = Alike.query.filter_by(user_id=user_id).all()

    # 提取点赞文章的详细信息
    liked_articles = []
    for like in likes:
        article = like.article  # 获取文章对象（通过 Alike 的 relationship）
        liked_articles.append({
            "article_id": article.id,
            "title": article.title,
            "content": article.content,
            "create_time": article.create_time,
            "author_nickname": article.user.nickname,
            "author_avatar": article.user.avatar,
            "like_time": like.create_time
        })

    return jsonify({
        "state": 1,
        "message": "User like records fetched successfully",
        "data": liked_articles
    }), 200

