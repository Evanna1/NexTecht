from flask import jsonify, request, Blueprint
from config import Config
from __init__ import db
from db import User, Article, Manager, Comment, CommentLike, ArticleFavorite
from flask_jwt_extended import jwt_required, get_jwt_identity
import functools
from collections import OrderedDict

articalfavo_bp = Blueprint('articalfavo', __name__)

# 收藏
@articalfavo_bp.route('/article/favorite/<int:article_id>', methods=['POST'])
@jwt_required()
def favorite_article(article_id):
    user_id = int(get_jwt_identity()) # 确保获取到整数类型的用户ID
    article = Article.query.get(article_id)
    if not article:
        return jsonify({"state": 0, "message": "Article not found"}), 404
    existing_favorite = ArticleFavorite.query.filter_by(user_id=user_id, article_id=article_id).first()
    if existing_favorite:
        return jsonify({
            "state": 0, # 或者你可以设计为 state: 1, 只是 message 不同
            "message": "Already favorited",
            "favorite_count": article.favorite_count, # 返回当前收藏数
            "is_favorited": True # 返回当前用户已收藏状态
        }), 200 # 200 OK 或 400 Bad Request
    new_favorite = ArticleFavorite(user_id=user_id, article_id=article_id)
    db.session.add(new_favorite)
    article.favorite_count += 1
    db.session.commit()
    return jsonify({
        "state": 1,
        "message": "Article favorited successfully",
        "favorite_count": article.favorite_count, # 返回更新后的收藏数
        "is_favorited": True # 返回当前用户已收藏状态
    }), 200

# 取消收藏
@articalfavo_bp.route('/article/unfavorite/<int:article_id>', methods=['POST'])
@jwt_required()
def unfavorite_article(article_id):
    user_id = int(get_jwt_identity()) # 确保获取到整数类型的用户ID
    article = Article.query.get(article_id)
    if not article:
        return jsonify({"state": 0, "message": "Article not found"}), 404
    existing_favorite = ArticleFavorite.query.filter_by(user_id=user_id, article_id=article_id).first()
    if not existing_favorite:
        # 没有找到收藏记录，返回当前状态和计数
        return jsonify({
            "state": 0, # 或者你可以设计为 state: 1, 只是 message 不同
            "message": "Not favorited yet",
            "favorite_count": article.favorite_count, # 返回当前收藏数
            "is_favorited": False # 返回当前用户未收藏状态
        }), 200 # 200 OK 或 400 Bad Request
    db.session.delete(existing_favorite)
    article.favorite_count = max(0, article.favorite_count - 1)
    db.session.commit()
    return jsonify({
        "state": 1,
        "message": "Article unfavorited successfully",
        "favorite_count": article.favorite_count, # 返回更新后的收藏数
        "is_favorited": False # 返回当前用户未收藏状态
    }), 200

#获取某个用户的所有收藏
@articalfavo_bp.route('/user/favorites/<int:user_id>', methods=['GET'])
@jwt_required()  # 使用 JWT 要求用户登录
def get_user_favorites(user_id):
    # 从 JWT 中获取当前用户的 ID
    current_user_id = get_jwt_identity()
    current_user_id = int(current_user_id)  # 确保 user_id 是整数类型

    # 检查是否是当前用户
    if current_user_id != user_id:
        return jsonify({"state": 0, "message": "Unauthorized"}), 403

    # 获取用户的所有收藏记录
    favorites = ArticleFavorite.query.filter_by(user_id=user_id).all()

    favorite_articles = [
        {
            "id": favorite.article.id,
            "title": favorite.article.title,
            "create_time": favorite.article.create_time.isoformat()
        }
        for favorite in favorites
    ]

    # 返回成功响应
    return jsonify({"state": 1, "message": "Favorites retrieved successfully", "favorites": favorite_articles})

#获取某个文章的收藏数
@articalfavo_bp.route('/article/favorites/count/<int:article_id>', methods=['GET'])
def get_article_favorites_count(article_id):
    # 获取文章的收藏数
    count = ArticleFavorite.query.filter_by(article_id=article_id).count()

    # 返回成功响应
    return jsonify({"state": 1, "message": "Favorites count retrieved successfully", "favorites_count": count})

