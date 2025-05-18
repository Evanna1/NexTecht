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

# 获取某个用户的所有收藏
@articalfavo_bp.route('/user/favorites/<int:user_id>', methods=['GET'])
@jwt_required()  # 使用 JWT 要求用户登录
def get_user_favorites(user_id):
    """
    获取某个用户的收藏文章列表，包含文章内容和作者信息。
    需要 JWT Token 进行认证，且只能获取当前认证用户的收藏。
    """
    try:
        # 从 JWT 中获取当前用户的 ID
        current_user_id = get_jwt_identity()
        # 注意：get_jwt_identity() 返回的是在创建 token 时放入的 'sub' 的值，通常是字符串
        # 如果你的 'sub' 存储的是用户 ID 的整数，这里需要转换为整数
        # 如果你的 'sub' 存储的就是字符串形式的用户 ID，则与 user_id (int) 比较前需要转换类型
        # 稳妥起见，假设 current_user_id 是字符串， user_id 是 int，进行类型转换比较
        # current_user_id = int(current_user_id) # 如果get_jwt_identity返回的是字符串ID

        print(f"Attempting to fetch favorites for user_id: {user_id}")
        print(f"Authenticated user ID from JWT: {current_user_id}")


        # 检查是否是当前认证用户在请求自己的收藏列表
        # 这里的比较取决于你的 get_jwt_identity() 返回的类型和 user_id 的类型
        # 假设 user_id 来自 URL 是 int， get_jwt_identity() 返回的是字符串
        if str(user_id) != current_user_id:
             print(f"Unauthorized attempt to access user {user_id}'s favorites by user {current_user_id}")
             return jsonify({"state": 0, "message": "Unauthorized"}), 403

        # 验证请求的用户是否存在（可选，但推荐）
        user = User.query.get(user_id)
        if not user:
             print(f"User with ID {user_id} not found.")
             return jsonify({"state": 0, "message": "User not found"}), 404


        # 获取用户的所有收藏记录
        # 使用 .all() 获取所有 ArticleFavorite 对象
        favorites = ArticleFavorite.query.filter_by(user_id=user_id).all()

        print(f"Found {len(favorites)} favorite records for user {user_id}")

        # 构建收藏文章的详细信息列表
        favorite_articles_details = []
        for favorite in favorites:
            # 通过关系访问到收藏的文章对象
            article = favorite.article
            # 确保文章存在（理论上收藏记录应该对应存在的文章）
            if article:
                # 通过文章对象访问到作者用户对象
                author = article.user
                # 确保作者存在
                if author:
                     print(f"Processing favorited article ID: {article.id}, Title: {article.title}")
                     favorite_articles_details.append({
                         "id": article.id, # 文章 ID
                         "title": article.title, # 文章标题
                         "content": article.content, # **新增：文章内容**
                         "article_create_time": article.create_time.isoformat() if article.create_time else None, # **新增：文章创建时间**
                         "author_id": author.id, # **新增：作者 ID**
                         "author_nickname": author.nickname, # **新增：作者昵称**
                         "author_avatar": author.avatar, # **新增：作者头像**
                         "favorite_time": favorite.create_time.isoformat() if favorite.create_time else None # **新增：收藏时间** (保留原有的创建时间，更名为 favorite_time 以免混淆)
                     })
                else:
                     print(f"Warning: Author not found for article ID {article.id} favorited by user {user_id}")
            else:
                 print(f"Warning: Article not found for favorite record ID {favorite.id} by user {user_id}")


        # 返回成功响应，包含详细的收藏文章信息
        return jsonify({
            "state": 1,
            "message": "Favorites retrieved successfully",
            "favorites": favorite_articles_details # 返回包含详细信息的列表
        }), 200

    except Exception as e:
        # 记录详细错误信息
        print(f"An error occurred while fetching user favorites: {e}", exc_info=True)
        # 可以在这里进行 db.session.rollback() 如果在 try 块中执行了任何数据库写操作 (虽然这个接口是 GET)
        return jsonify({"state": 0, "message": "服务器内部错误", "error": str(e)}), 500

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