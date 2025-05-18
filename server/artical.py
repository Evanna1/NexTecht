import os
from flask import jsonify, request, Blueprint
from config import Config
from __init__ import db
from db import User, Article, Manager, UserBrowseRecord, Alike
from flask_jwt_extended import jwt_required, get_jwt_identity
import functools
from collections import OrderedDict
from werkzeug.utils import secure_filename
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import random
import logging
from sqlalchemy.exc import IntegrityError
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

artical_bp = Blueprint('artical', __name__)

# 管理员权限装饰器
def admin_required(f):
    @jwt_required()
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        current_user_id = get_jwt_identity()
        admin = Manager.query.filter_by(mng_id=current_user_id).first()
        if not admin:
            return jsonify({"error": "管理员身份验证失败"}), 403
        return f(*args, **kwargs)

    return decorated_function


def get_article_or_404(article_id):
    """获取文章对象,如果不存在则返回404"""
    article = Article.query.get_or_404(article_id)
    return article

def get_browses(user_id):
    records = UserBrowseRecord.query.filter_by(user_id=user_id).order_by(UserBrowseRecord.browse_time.desc()).all()
    article_ids = [record.article_id for record in records]
    return article_ids  # ✅ 返回纯数据列表


# 获取所有文章列表（管理员专用）
@artical_bp.route('/manager/article_list', methods=['GET'])
@admin_required
def get_all_articles():
    articles = Article.query.all()
    articles_list = [article.to_dict() for article in articles]
    return jsonify({
        "state": 1,
        "message": "List of articles",
        "articles": articles_list
    })


# 获取特定文章详情（管理员专用）
@artical_bp.route('/manager/article_detail/<int:article_id>', methods=['GET'])
@admin_required
def get_article_detail(article_id):
    article = get_article_or_404(article_id)
    return jsonify({"state": 1, "message": "detailss of article", "article": article.to_dict()})


# 修改文章状态（管理员专用）
@artical_bp.route('/article/manager/update/<int:article_id>/status', methods=['PATCH'])
@admin_required
def change_article_status_by_admin(article_id):
    article = get_article_or_404(article_id)
    new_status = request.json.get('status')
    if new_status not in [0, 1, 2]:
        return jsonify({"error": "无效的状态值"}), 400

    article.set_status(new_status)
    return jsonify({
        "state": 1,
        "message": "文章状态更新成功",
        "updated_status": new_status
    })


# 修改文章权限（管理员专用）
@artical_bp.route('/article/manager/update/<int:article_id>/permission', methods=['PATCH'])
@admin_required
def change_article_permission_by_admin(article_id):
    article = get_article_or_404(article_id)
    new_permission = request.json.get('permission')
    if new_permission not in [0, 1]:  # 文章权限位，0表示公开，1表示屏蔽
        return jsonify({"error": "无效的权限值"}), 400

    article.set_permission(new_permission)
    return jsonify({
        "state": 1,
        "message": "文章权限更新成功",
        "updated_status": new_permission
    })


# 物理删除文章（管理员专用）
@artical_bp.route('/article/manager/de1/<int:article_id>', methods=['DELETE'])
@admin_required
def delete_article_physically(article_id):
    article = get_article_or_404(article_id)
    try:
        db.session.delete(article)
        db.session.commit()
        return jsonify({"message": "文章已删除"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"删除文章时出错: {str(e)}"}), 500


#  软删除文章（管理员专用）
@artical_bp.route('/article/manager/de2/<int:article_id>', methods=['DELETE'])
@admin_required
def soft_delete_article(article_id):
    article = get_article_or_404(article_id)

    # 软删除：将状态标记为1（已删除）
    try:
        article.status = 1  # 假设1表示已删除
        db.session.commit()
        return jsonify({
            "message": "文章已软删除",
            "article_id": article.id,
            "status": article.status
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"软删除文章时出错: {str(e)}"}), 500

#上传图片
@artical_bp.route('/upload/image', methods=['POST'])
@jwt_required()  # 需要验证 JWT
def upload_image():
    # 获取上传的图片文件
    image_file = request.files.get('image')
    if not image_file:
        return jsonify({"state": 0, "message": "No image provided"}), 400

    # 生成安全的文件名
    image_filename = secure_filename(image_file.filename)

    # 获取当前文件（register模块）所在的目录
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # 拼接出 blog/public/img 的绝对路径
    save_path = os.path.abspath(os.path.join(current_dir, '..', '..', '..', 'blog', 'public', 'img'))
    os.makedirs(save_path, exist_ok=True)

    # 保存图片文件
    image_file.save(os.path.join(save_path, image_filename))

    # 返回图片的访问路径
    image_path = f'/img/{image_filename}'
    return jsonify({"state": 1, "message": "Image uploaded successfully", "image_path": image_path}), 201

#创建文章(图片和tag可选)
@artical_bp.route('/article/create', methods=['POST'])
@jwt_required()
def create_article():
    current_user_id = get_jwt_identity()
    data = request.form
    title = data.get('title')
    content = data.get('content')
    image_path = data.get('image_path')  # 如果你是用 URL 的话，否则从文件字段拿
    permission = int(data.get('permission', 0))  # 默认为公开（0）
    tag = data.get('tag')  # 获取分类标签，如果没有提供，则为 None

    if not title or not content:
        return jsonify({"state": 0, "message": "Title and content are required"}), 400

    new_article = Article(
        title=title,
        content=content,
        user_id=current_user_id,
        image_path=image_path if image_path else None,  # 如果没有图片路径，则设置为 None
        tag=tag if tag else None,  # 如果没有提供 tag，则设置为 None
        permission=permission  # 0: 公开，1: 私密
    )

    db.session.add(new_article)
    db.session.commit()

    return jsonify({"state": 1, "message": "Article created successfully", "article_id": new_article.id}), 201

#根据tag获取文章
@artical_bp.route('/articles/by_tag/<string:tag>', methods=['GET'])
def get_articles_by_tag(tag):
    articles = Article.query.filter_by(tag=tag).all()
    return jsonify([article.to_dict() for article in articles])


# 获取特定用户文章列表（管理员和用户均可）
@artical_bp.route('/article/list', methods=['GET'])
@jwt_required()
def get_articles():
    current_user_id = get_jwt_identity()

    # 获取查询参数中的用户ID（可选）
    user_id = request.args.get('user_id', type=int)

    if user_id:
        #  管理员查看指定用户的文章
        current_manager = Manager.query.get(current_user_id)
        if not current_manager:
            return jsonify({"state": 0, "message": "权限不足，无法查看其他用户的文章"}), 403

        articles = Article.query.filter_by(user_id=user_id).all()
    else:
        # 普通用户查看自己的文章
        articles = Article.query.filter_by(user_id=current_user_id).all()

    return jsonify([article.to_dict() for article in articles])


#更新文章，加上了图片更新和tag功能
@artical_bp.route('/article/update/<int:article_id>', methods=['PUT'])
@jwt_required()
def update_article_by_user(article_id):
    article = Article.query.get(article_id)
    if not article:
        return jsonify({'error': 'Article not found'}), 404

    current_user_id = get_jwt_identity()
    current_user_id = int(current_user_id)  # 将字符串转换为整数
    if article.user_id != current_user_id:
        return jsonify({'error': 'Permission denied', "article.user_id": article.user_id,
                        "current_user_id": current_user_id}), 403  # 403: 禁止访问

    data = request.json
    new_title = data.get('title')
    new_content = data.get('content')
    new_image_path = data.get('image_path')  # 获取新的图片路径
    new_tag = data.get('tag')  # 获取新的分类标签
    if not new_title and not new_content and new_tag is None and new_image_path is None:
        return jsonify({"error": "至少需要提供新的标题、内容、分类标签或图片"}), 400

    # 更新文章
    article.update_article(new_title, new_content, new_tag=new_tag, new_image_path=new_image_path)

    return jsonify(article.to_dict())


# 删除文章（用户）
@artical_bp.route('/article/delete/<int:article_id>', methods=['DELETE'])
@jwt_required()
def delete_article_by_user(article_id):
    article = Article.query.get(article_id)
    current_user_id = get_jwt_identity()

    if article.user_id != current_user_id:
        return jsonify({'error': 'Permission denied'}), 403  # 403: 禁止访问

    if not article:
        return jsonify({'error': 'Article not found'}), 404

    try:
        article.delete_article()
        return jsonify({'message': 'Article deleted successfully'})
    except Exception as e:
        return jsonify({"error": f"删除文章时出错: {str(e)}"}), 500

# 获取特定文章详情（用户专用）
@artical_bp.route('/user/article_content/<int:article_id>', methods=['GET'])
@jwt_required()
def get_article_content(article_id):
    current_user_id = get_jwt_identity()
    article = get_article_or_404(article_id)
    if not article:
        return jsonify({"state": 0, "message": "Article not found"}), 404
    # 更新阅读量
    article.read_count = article.read_count + 1
    new_record = UserBrowseRecord(
        user_id=current_user_id,
        article_id=article_id,
        browse_time=datetime.utcnow()
    )
    db.session.add(new_record)
    db.session.commit()
    return jsonify({"state": 1, "message": "details of article", "article": article.to_dict()})



# 获取自己的历史浏览记录（用户专用）
@artical_bp.route('/article/browses', methods=['GET'])
@jwt_required()
def get_user_browses():
    current_user_id = get_jwt_identity()
    user_id = int(current_user_id)

    records = UserBrowseRecord.query.filter_by(user_id=user_id).order_by(UserBrowseRecord.browse_time.desc()).all()

    result = [
        {
            "article_id": r.article.id,
            "title": r.article.title,
            "content": r.article.content,
            "browse_time": r.browse_time.isoformat()
        }
        for r in records
    ]

    return jsonify({"state": 1, "message": "Browse records retrieved successfully", "browses": result})

# 推荐算法
@artical_bp.route('/article/recommend', methods=['GET'])
@jwt_required()
def recommend_articles():
    user_id = get_jwt_identity()
    top_k = 10

    count = 0
    user_history_ids = get_browses(user_id)
    articles = Article.query.all()
    article_texts = [article.title + " " + article.content for article in articles]
    article_ids = [article.id for article in articles]
    rec_list = []

    if not user_history_ids:
        remaining = [a for a in articles]
        random.shuffle(remaining)  # 或可按创建时间倒序等方式排序
        for article in remaining:
            rec_list.append(OrderedDict([
                ("article_id", article.id),
                ("title", article.title),
                ("score", 0)  # 无相似度，打分为 0
            ]))
            count += 1
            if count >= top_k:
                break
        return jsonify({"state": 1, "message": "推荐文章列表", "recommendations": rec_list})

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(article_texts)

    indices = [article_ids.index(aid) for aid in user_history_ids if aid in article_ids]
    if not indices:
        return jsonify({"state": 0, "message": "用户浏览历史文章不在库中"}), 200

    user_vector = tfidf_matrix[indices].mean(axis=0).A1
    sim_scores = cosine_similarity(tfidf_matrix, user_vector.reshape(1, -1)).flatten()

    # 排除已读文章
    for idx in indices:
        sim_scores[idx] = -1

    # 获取 Top-K 推荐索引
    top_indices = sim_scores.argsort()[::-1]

    used_ids = set(user_history_ids)

    for i in top_indices:
        if sim_scores[i] <= 0:
            continue
        rec_list.append(OrderedDict([
            ("article_id", article_ids[i]),
            ("title", articles[i].title),
            ("score", round(sim_scores[i], 4))
        ]))
        used_ids.add(article_ids[i])
        count += 1
        if count >= top_k:
            break

    # 补足推荐不足的情况
    if count < top_k:
        remaining = [a for a in articles if a.id not in used_ids]
        random.shuffle(remaining)  # 或可按创建时间倒序等方式排序
        for article in remaining:
            rec_list.append(OrderedDict([
                ("article_id", article.id),
                ("title", article.title),
                ("score", 0)  # 无相似度，打分为 0
            ]))
            count += 1
            if count >= top_k:
                break

    return jsonify({"state": 1, "message": "推荐文章列表", "recommendations": rec_list})

# 热度算法
@artical_bp.route('/article/hot', methods=['GET'])
def hot_articles():
    top_k = 10  # 返回前10个热度最高的文章
    a, b = 3, 1  # 点赞权重3，阅读权重1

    articles = Article.query.all()
    if not articles:
        return jsonify({"state": 0, "message": "暂无文章数据"}), 200

    # 计算热度分数
    articles_with_scores = []
    for article in articles:
        article_id = getattr(article, 'id', 0)
        like_num = Alike.query.filter_by(article_id=article_id).count()
        read_num = getattr(article, 'read_count', 0) or 0
        score = a * like_num + b * read_num
        articles_with_scores.append((article, score))

    # 按热度降序排序
    articles_with_scores.sort(key=lambda x: x[1], reverse=True)

    # 取 top_k
    top_articles = articles_with_scores[:top_k]

    # 构造返回结果
    result = [
        OrderedDict([
            ("article_id", art.id),
            ("title", art.title),
            ("hot_score", score)
        ])
        for art, score in top_articles
    ]

    return jsonify({"state": 1, "message": "热门文章列表", "articles": result}), 200

# 定义获取指定用户文章列表的路由
@artical_bp.route('/article/list/by-user/<int:user_id>', methods=['GET'])
# 使用 optional=True，表示这个接口可以带 JWT 访问，也可以不带
@jwt_required(optional=True)
def get_user_articles(user_id):
    # 获取当前登录用户的 ID，如果未登录则为 None
    current_user_id = get_jwt_identity()

    # 基础查询：获取属于该用户的文章
    query = Article.query.filter_by(user_id=user_id)

    # 根据访问者的身份应用权限过滤
    # 注意：Python 的身份比较用 'is' 或 '==' 都可以，这里用 == 更通用
    if current_user_id is None or current_user_id != user_id:
        # 如果当前用户未登录，或者当前用户不是文章作者
        # 只能看到 permission 为 0 的文章（公开文章）
        query = query.filter_by(permission=0)
    # 否则 (else)，说明 current_user_id == user_id，即访问者是作者本人
    # 作者本人可以看到自己的所有文章，不需要额外的 permission 过滤

    # 对文章按创建时间倒序排序（通常是这样）
    articles = query.order_by(Article.create_time.desc()).all()

    # 准备返回的文章列表数据
    articles_list = []
    for article in articles:
        articles_list.append({
            "id": article.id,
            "title": article.title,
            "content": article.content,
            "tag": article.tag,
            "permission": article.permission, # 可以返回 permission，前端知道这是公开还是私密
            "create_at": article.create_time.strftime('%Y-%m-%d %H:%M:%S') if article.create_time else None,
            # 如果需要作者信息，也可以在这里加入，但通常在用户主页接口中获取更合适
            # "author_id": article.author_id,
        })
    print(f"Debug: User ID: {user_id}, Current User ID: {current_user_id}")
    print(f"Debug: Final articles_list count: {len(articles_list)}")
    print(f"Debug: Final articles_list content: {articles_list}")  # 打印列表内容看是否为空或包含预期文章
    return jsonify({"data": articles_list}), 200




