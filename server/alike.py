from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from __init__ import db
from db import Alike, Article

alike_bp = Blueprint('alike', __name__)

@alike_bp.route('/alike/like/<int:article_id>', methods=['POST'])
@jwt_required()
def like_article(article_id):
    user_id = get_jwt_identity()

    new_like = Alike(user_id=user_id, article_id=article_id, create_time=datetime.utcnow())
    db.session.add(new_like)
    db.session.commit()

    return jsonify({"state": 1, "message": "Liked successfully"}), 200

@alike_bp.route('/alike/unlike/<int:article_id>', methods=['POST'])
@jwt_required()
def unlike_article(article_id):
    user_id = get_jwt_identity()

    like = Alike.query.filter_by(user_id=user_id, article_id=article_id).first()
    if not like:
        return jsonify({"state": 0, "message": "Like not found"}), 404

    db.session.delete(like)
    db.session.commit()

    return jsonify({"state": 1, "message": "Unliked successfully"}), 200

# 获取文章的点赞数
@alike_bp.route('/alike/count/<int:article_id>', methods=['GET'])
def get_like_count(article_id):
    count = Alike.query.filter_by(article_id=article_id).count()
    return jsonify({"state": 1, "like_count": count}), 200

# 获取文章的点赞用户(待改)
@alike_bp.route('/alike/list/<int:article_id>', methods=['GET'])
@jwt_required()
def get_likers():
    user_id = get_jwt_identity()

    if not article_id:
        return jsonify({"state": 0, "message": "Article ID is required"}), 400

    # 获取文章
    article = Article.query.filter_by(id=article_id).first()
    if not article:
        return jsonify({"state": 0, "message": "Article not found"}), 404

    # 仅允许文章作者查看
    if article.author_id != user_id:
        return jsonify({"state": 0, "message": "Permission denied"}), 403

    # 获取点赞者
    likes = Like.query.filter_by(article_id=article_id).all()
    likers_info = [{
        "nickname": like.user.nickname,
        "avatar": like.user.avatar
    } for like in likes]

    return jsonify({
        "state": 1,
        "message": "Liker list fetched successfully",
        "data": likers_info
    }), 200

