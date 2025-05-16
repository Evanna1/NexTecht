import os
from flask import jsonify, request, Blueprint
from config import Config
from __init__ import db
from db import User, Article, Manager
from flask_jwt_extended import jwt_required, get_jwt_identity
import functools
from collections import OrderedDict
from werkzeug.utils import secure_filename

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
def get_article_content(article_id):
    article = get_article_or_404(article_id)
    # 更新阅读量
    article.read_count = article.read_count + 1
    db.session.commit()  
    return jsonify({"state": 1, "message": "details of article", "article": article.to_dict()})











