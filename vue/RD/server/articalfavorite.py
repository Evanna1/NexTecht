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

# 获取用户的所有收藏记录
@articalfavo_bp.route('/favorite/user/records', methods=['GET'])
@jwt_required()
def get_user_favorites():
    user_id = get_jwt_identity()  # 获取当前用户的 ID
    favorites = ArticleFavorite.query.filter_by(user_id=user_id).all()

    # 提取点赞文章的详细信息
    favorites_articles = []
    for favorite in favorites:
        article = favorite.article  # 获取文章对象（通过 Alike 的 relationship）
        favorites_articles.append({
            "article_id": article.id,
            "title": article.title,
            "content": article.content,
            "create_time": article.create_time,
            "author_nickname": article.user.nickname,
            "author_avatar": article.user.avatar,
            "like_time": favorite.create_time
        })

    return jsonify({
        "state": 1,
        "message": "User like records fetched successfully",
        "data": favorites_articles
    }), 200

#获取某个文章的收藏数
@articalfavo_bp.route('/article/favorites/count/<int:article_id>', methods=['GET'])
def get_article_favorites_count(article_id):
    # 获取文章的收藏数
    count = ArticleFavorite.query.filter_by(article_id=article_id).count()

    # 返回成功响应
    return jsonify({"state": 1, "message": "Favorites count retrieved successfully", "favorites_count": count})

# 获取文章的点赞用户
@articalfavo_bp.route('/article/favorite/list/<int:article_id>', methods=['GET'])
@jwt_required()
def get_favorites(article_id):
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
    favorites = ArticleFavorite.query.filter_by(article_id=article_id).all()
    favorites_info = [{
        "nickname": favorite.user.nickname,
        "avatar": favorite.user.avatar,
        "time": favorite.create_time
    } for favorite in favorites]

    return jsonify({
        "state": 1,
        "message": "favorites list fetched successfully",
        "data": favorites_info
    }), 200

# --- 新增接口 2: 检查用户是否收藏某文章 ---
@articalfavo_bp.route('/favorites/check_favorited/<int:article_id>', methods=['GET'])
@jwt_required() # 需要JWT认证
def check_article_favorited(article_id):
    """
    检查当前用户是否收藏了指定的文章
    """
    current_user_id = get_jwt_identity() # 获取当前登录用户的ID

     # 确保 user_id 是正确的类型
    try:
        user_id = int(current_user_id)
    except (ValueError, TypeError):
        return jsonify({"state": 0, "message": "Invalid user identity"}), 401

    article = Article.query.get(article_id)
    if not article:
        return jsonify({"state": 0, "message": "Article not found"}), 404

    # 查询 ArticleFavorite 表，判断当前用户是否收藏了这篇文章
    favorite_record = ArticleFavorite.query.filter_by(user_id=user_id, article_id=article_id).first()

    is_favorited = favorite_record is not None # 如果找到了记录，说明已收藏

    return jsonify({
        "state": 1,
        "message": "Favorite status checked successfully",
        "is_favorited": is_favorited
    }), 200