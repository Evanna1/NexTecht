from flask import jsonify, request, Blueprint
from config import Config
from __init__ import db
from db import User, Article, Manager
from flask_jwt_extended import jwt_required, get_jwt_identity
import functools
from collections import OrderedDict

artical_bp = Blueprint('artical', __name__)


# 修改的地方：
# 1、文章创建函数，增加用户状态和用户权限检查
# 但是其他函数的用户状态和用户权限检查还没有加入
# 2、获取文章列表函数

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


# 获取所有文章列表（管理员专用）
@artical_bp.route('/manager/article_list', methods=['GET'])
@admin_required
def get_all_articles():
    articles = Article.query.all()
    articles_list = [
        OrderedDict([
            ("id", article.id),
            ("title", article.title),
            ("user_id", article.user_id),
            ("create_time", article.create_time.isoformat() if article.create_time else None),
            ("status", article.status),
            ("permission", article.permission)
        ])
        for article in articles
    ]

    return jsonify({"state": 1, "message": "List of articles", "articles": articles_list})


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


# 创建文章（用户）
@artical_bp.route('/article/create', methods=['POST'])
@jwt_required()
def create_article():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    # 检查用户状态和发布权限(我新增的)
    if user.u_status != 0:  # 0表示正常状态,1表示禁止被关注
        return jsonify({"error": "用户状态异常，禁止发布文章"}), 403
    if user.is_publish != 1:
        return jsonify({"error": "当前用户没有发布文章的权限"}), 403

    data = request.json
    title = data.get('title')
    content = data.get('content')

    if not title or not content:
        return jsonify({"error": "标题和内容不能为空"}), 400

    new_article = Article(title=title, content=content, user_id=user_id)
    try:
        db.session.add(new_article)
        db.session.commit()
        return jsonify(new_article.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"创建文章时出错: {str(e)}"}), 500


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


# 更新文章（用户）
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

    if not new_title and not new_content:
        return jsonify({"error": "至少需要提供新的标题或内容"}), 400

    article.update_article(new_title, new_content)
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
#
# @artical_bp.route('/article/browsesList/<int:user_id>', methods=['GET'])
# @jwt_required()
# def get_user_browses(user_id):
#     current_user_id = get_jwt_identity()
#     current_user_id = int(current_user_id)
#
#     if current_user_id != user_id:
#         return jsonify({"state": 0, "message": "Unauthorized"}), 403
#
#     browse_records = UserBrowseRecord.query.filter_by(user_id=user_id).order_by(UserBrowseRecord.browse_time.desc()).all()
#
#     browsed_articles = [
#         {
#             "id": record.article.id,
#             "title": record.article.title,
#             "browse_time": record.browse_time.isoformat()
#         }
#         for record in browse_records
#     ]
#
#     return jsonify({"state": 1, "message": "Browse records retrieved successfully", "browses": browsed_articles})
#
# @artical_bp.route('/article/browsesArtical', methods=['POST'])
# @jwt_required()
# def add_browse_record():
#     current_user_id = get_jwt_identity()
#     data = request.get_json()
#
#     article_id = data.get('article_id')
#     if not article_id:
#         return jsonify({"state": 0, "message": "article_id is required"}), 400
#
#     new_record = UserBrowseRecord(user_id=current_user_id, article_id=article_id)
#     db.session.add(new_record)
#     db.session.commit()
#
#     return jsonify({"state": 1, "message": "Browse record saved successfully"})











