from flask import jsonify, request, Blueprint
from config import Config
from __init__ import db
from db import User, Article, Manager, Comment, CommentLike, ArticleFavorite
from flask_jwt_extended import jwt_required, get_jwt_identity
import functools
from collections import OrderedDict

articalfavo_bp = Blueprint('articalfavo', __name__)

#收藏
@articalfavo_bp.route('/article/favorite/<int:article_id>', methods=['POST'])
@jwt_required()  # 使用 JWT 要求用户登录
def favorite_article(article_id):
    # 从 JWT 中获取当前用户的 ID
    user_id = get_jwt_identity()
    user_id = int(user_id)  # 确保 user_id 是整数类型

    # 检查是否已经收藏过
    existing_favorite = ArticleFavorite.query.filter_by(user_id=user_id, article_id=article_id).first()
    if existing_favorite:
        return jsonify({"state": 0, "message": "Already favorited"}), 400

    # 创建新的收藏记录
    new_favorite = ArticleFavorite(user_id=user_id, article_id=article_id)
    db.session.add(new_favorite)
    db.session.commit()

    # 返回成功响应
    return jsonify({"state": 1, "message": "Article favorited successfully"})

#取消收藏
@articalfavo_bp.route('/article/unfavorite/<int:article_id>', methods=['POST'])
@jwt_required()  # 使用 JWT 要求用户登录
def unfavorite_article(article_id):
    # 从 JWT 中获取当前用户的 ID
    user_id = get_jwt_identity()
    user_id = int(user_id)  # 确保 user_id 是整数类型

    # 检查是否已经收藏过
    existing_favorite = ArticleFavorite.query.filter_by(user_id=user_id, article_id=article_id).first()
    if not existing_favorite:
        return jsonify({"state": 0, "message": "Not favorited yet"}), 400

    # 删除收藏记录
    db.session.delete(existing_favorite)
    db.session.commit()

    # 返回成功响应
    return jsonify({"state": 1, "message": "Article unfavorited successfully"})

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










