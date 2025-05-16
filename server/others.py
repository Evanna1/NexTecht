from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from __init__ import db
from db import Alike, Article
from collections import OrderedDict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

others_bp = Blueprint('others', __name__)

@others_bp.route('/others/recommend/articles', methods=['GET'])
@jwt_required()
def recommend_articles():
    user_id = get_jwt_identity()
    top_k = 3

    user_history_ids = get_user_history(user_id)
    if not user_history_ids:
        return jsonify({"state": 0, "message": "该用户暂无浏览历史，无法推荐"}), 200

    # 准备所有文章文本列表
    article_texts = [article.title + " " + article.content for article in articles]
    article_ids = [article.id for article in articles]

    # 计算所有文章的TF-IDF向量
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(article_texts)

    # 计算用户兴趣向量（历史文章向量均值）
    indices = [article_ids.index(aid) for aid in user_history_ids if aid in article_ids]
    if not indices:
        return jsonify({"state": 0, "message": "用户浏览历史文章不在库中"}), 200
    user_vector = tfidf_matrix[indices].mean(axis=0)

    # 计算所有文章与用户兴趣向量的余弦相似度
    sim_scores = cosine_similarity(tfidf_matrix, user_vector).flatten()

    # 排除用户已读文章，只推荐未读
    for idx in indices:
        sim_scores[idx] = -1  # 设为负值，排除推荐

    # 获取Top-k文章索引
    top_indices = sim_scores.argsort()[::-1][:top_k]

    # 构造返回结果
    rec_list = [
        OrderedDict([
            ("article_id", article_ids[i]),
            ("title", articles[i].title),
            ("score", round(sim_scores[i], 4))
        ])
        for i in top_indices if sim_scores[i] > 0
    ]

    return jsonify({"state": 1, "message": "推荐文章列表", "recommendations": rec_list})

