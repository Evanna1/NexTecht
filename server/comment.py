from flask import jsonify, request, Blueprint
from config import Config
from __init__ import db
from db import User, Article, Manager, Comment, CommentLike
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
import functools
from collections import OrderedDict

comment_bp = Blueprint('comment', __name__)

def get_liked_status_for_comments(user_id, comment_ids):
    """查询某个用户是否点赞了给定的评论ID列表中的评论"""
    if not user_id or not comment_ids:
        return {}
    liked_comment_ids_query = db.session.query(CommentLike.comment_id)\
                                  .filter(CommentLike.user_id == user_id, CommentLike.comment_id.in_(comment_ids))
    try:
        liked_comment_ids = liked_comment_ids_query.scalars().all()
    except AttributeError:
        liked_comment_ids = [row[0] for row in liked_comment_ids_query.all()]
    return set(liked_comment_ids)

#用户创建评论，已经实现父评论功能
@comment_bp.route('/comment/<int:article_id>/create', methods=['POST'])
@jwt_required()
def create_comment(article_id):
    data = request.json
    content = data.get('content')
    parent_id = data.get('parent_id', None)

    if not content:
        return jsonify({"state": 0, "message": "Invalid input"}), 400

    if not isinstance(article_id, int) or article_id <= 0:
        return jsonify({"state": 0, "message": "Invalid article ID"}), 400

    article = Article.query.get_or_404(article_id)
    parent_comment = Comment.query.get(parent_id) if parent_id else None

    depth = 1 if not parent_comment else parent_comment.depth + 1

    # 从 JWT 中获取用户 ID
    user_id = get_jwt_identity()

    new_comment = Comment(
        content=content,
        user_id=user_id,  # 使用从 JWT 中获取的用户 ID
        article_id=article_id,
        parent_id=parent_id,
        depth=depth
    )
    db.session.add(new_comment)
    if parent_comment:
        parent_comment.reply_count += 1
        db.session.add(parent_comment)

        # 提交数据库会话
    db.session.commit()

    return jsonify({"state": 1, "message": "Comment created successfully", "comment_id": new_comment.id})

#用户更新自己的评论

@comment_bp.route('/comment/update/<int:comment_id>', methods=['PUT'])
@jwt_required()  # 使用 JWT 要求用户登录
def update_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)

    user_id = get_jwt_identity()
    user_id =int(user_id)
    if comment.user_id != user_id:
        return jsonify({"state": 0, "message": "Unauthorized","comment.user_id":comment.user_id,"user_id":user_id}), 403

    # 从请求中获取 JSON 数据
    data = request.json
    new_content = data.get('content')

    # 检查新内容是否为空
    if not new_content:
        return jsonify({"state": 0, "message": "Invalid input"}), 400

    # 更新评论内容
    comment.content = new_content
    db.session.commit()

    # 返回成功响应
    return jsonify({"state": 1, "message": "Comment updated successfully"})


# 用户删除自己的评论
@comment_bp.route('/comment/delete/<int:comment_id>', methods=['DELETE'])
@jwt_required()  # 使用 JWT 要求用户登录
def delete_comment(comment_id):
    # 获取评论对象，如果评论不存在则返回 404 错误
    comment = Comment.query.get_or_404(comment_id)

    # 从 JWT 中获取当前用户的 ID
    user_id = get_jwt_identity()
    user_id = int(user_id)  # 确保 user_id 是整数类型

    # 检查当前用户是否有权限删除该评论
    if comment.user_id != user_id:
        return jsonify({"state": 0, "message": "Unauthorized"}), 403

    # 如果该评论是子评论，更新父评论的回复数
    if comment.parent_id:
        parent_comment = Comment.query.get(comment.parent_id)
        if parent_comment:
            parent_comment.reply_count -= 1
            db.session.add(parent_comment)

    # 删除评论
    db.session.delete(comment)
    db.session.commit()

    # 返回成功响应
    return jsonify({"state": 1, "message": "Comment deleted successfully"})

'''
#用户点赞评论   (这部分要等点赞表写完)
@comment_bp.route('/comment/like/<int:comment_id>', methods=['POST'])
@jwt_required()  # 使用 JWT 要求用户登录
def like_comment(comment_id):
    # 获取评论对象，如果评论不存在则返回 404 错误
    comment = Comment.query.get_or_404(comment_id)

    # 从 JWT 中获取当前用户的 ID
    user_id = get_jwt_identity()
    user_id = int(user_id)  # 确保 user_id 是整数类型

    # 检查用户是否已经点赞过该评论
    if comment in current_user.liked_comments:
        return jsonify({"state": 0, "message": "You have already liked this comment"}), 400

    # 用户点赞评论
    comment.like_count += 1
    db.session.add(comment)

    # 将点赞记录添加到用户点赞列表（假设有一个中间表记录用户点赞的评论）
    current_user.liked_comments.append(comment)
    db.session.add(current_user)

    # 提交数据库会话
    db.session.commit()

    # 返回成功响应
    return jsonify({"state": 1, "message": "Comment liked successfully"})
'''

#用户举报评论(目前只有置位举报，没有记录其他信息)
@comment_bp.route('/comment/report/<int:comment_id>', methods=['POST'])
@jwt_required()
def report_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    comment.report_comment()
    return jsonify({"state": 1, "message": "Comment reported successfully"})



#用户获取自己发布的所有评论
@comment_bp.route('/comment/listall', methods=['GET'])
@jwt_required()  # 使用 JWT 要求用户登录
def get_user_comments():
    # 从 JWT 中获取当前用户的 ID
    user_id = get_jwt_identity()
    user_id = int(user_id)  # 确保 user_id 是整数类型

    # 获取当前用户发布的所有评论
    comments = Comment.query.filter_by(user_id=user_id).all()

    # 将评论转换为字典列表
    comments_list = [
        OrderedDict([
            ("id", comment.id),
            ("content", comment.content),
            ("article_id", comment.article_id),
            ("create_time", comment.create_time.isoformat() if comment.create_time else None),
            ("update_time", comment.update_time.isoformat() if comment.update_time else None),
            ("status", comment.status),
            ("is_approved", comment.is_approved),
            ("like_count", comment.like_count),
            ("reply_count", comment.reply_count),
            ("depth", comment.depth),
            ("parent_id", comment.parent_id)
        ])
        for comment in comments
    ]

    # 返回成功响应
    return jsonify({"state": 1, "message": "User comments", "comments": comments_list})

'''
#用户获取自己点赞的所有评论
@comment_bp.route('/user/<int:user_id>/liked_comments', methods=['GET'])
@login_required
def get_user_liked_comments(user_id):
    if user_id != current_user.id:
        return jsonify({"state": 0, "message": "Unauthorized"}), 403

    # 假设有一个中间表来记录用户点赞的评论
    liked_comments = current_user.liked_comments.all()
    comments_list = [
        OrderedDict([
            ("id", comment.id),
            ("content", comment.content),
            ("article_id", comment.article_id),
            ("create_time", comment.create_time.isoformat() if comment.create_time else None),
            ("update_time", comment.update_time.isoformat() if comment.update_time else None),
            ("status", comment.status),
            ("is_approved", comment.is_approved),
            ("like_count", comment.like_count),
            ("reply_count", comment.reply_count),
            ("depth", comment.depth),
            ("parent_id", comment.parent_id)
        ])
        for comment in liked_comments
    ]

    return jsonify({"state": 1, "message": "User liked comments", "comments": comments_list})

#用户取消点赞评论
@comment_bp.route('/comment/<int:comment_id>/unlike', methods=['POST'])
@login_required
def unlike_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if comment.like_count > 0:
        comment.like_count -= 1
        db.session.commit()
        return jsonify({"state": 1, "message": "Comment unliked successfully"})
    else:
        return jsonify({"state": 0, "message": "Comment is not liked"}), 400
'''

#用户获取自己所有被举报的评论

@comment_bp.route('/comment/reported_comments', methods=['GET'])
@jwt_required()  # 使用 JWT 要求用户登录
def get_user_reported_comments():
    # 从 JWT 中获取当前用户的 ID
    user_id = get_jwt_identity()
    user_id = int(user_id)  # 确保 user_id 是整数类型

    # 获取当前用户发布的所有被举报的评论
    reported_comments = Comment.query.filter_by(user_id=user_id, status=3).all()

    # 将评论转换为字典列表
    comments_list = [
        OrderedDict([
            ("id", comment.id),
            ("content", comment.content),
            ("article_id", comment.article_id),
            ("create_time", comment.create_time.isoformat() if comment.create_time else None),
            ("update_time", comment.update_time.isoformat() if comment.update_time else None),
            ("status", comment.status),
            ("is_approved", comment.is_approved),
            ("like_count", comment.like_count),
            ("reply_count", comment.reply_count),
            ("depth", comment.depth),
            ("parent_id", comment.parent_id)
        ])
        for comment in reported_comments
    ]

    # 返回成功响应
    return jsonify({"state": 1, "message": "User reported comments", "comments": comments_list})


# 获取特定文章的顶级评论列表（分页）
@comment_bp.route('/article/<int:article_id>/comments', methods=['GET'])
# 使用 verify_jwt_in_request 让接口可选登录，如果登录则获取 user_id 用于判断 is_liked
def get_article_comments(article_id):
    current_user_id = None
    try:
        verify_jwt_in_request(optional=True)
        jwt_identity = get_jwt_identity()
        if jwt_identity is not None:
             current_user_id = int(jwt_identity)
    except Exception:
        pass # 用户未登录或 token 无效

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int) # 每页10条评论

    # 查询属于该文章的顶级评论 (depth = 1)，过滤状态为正常 (status=0)，按创建时间倒序排列
    pagination = Comment.query.filter_by(article_id=article_id, depth=1, status=0)\
                               .order_by(Comment.create_time.desc())\
                               .paginate(page=page, per_page=per_page, error_out=False)

    comments = pagination.items
    total_pages = pagination.pages
    total_items = pagination.total

    # 获取当前页面评论的 ID 列表
    comment_ids = [comment.id for comment in comments]

    # 高效查询当前用户是否点赞了这些评论
    liked_comment_ids_by_current_user = get_liked_status_for_comments(current_user_id, comment_ids)

    comments_list = []
    for comment in comments:
         comment_dict = comment.to_dict() # 使用 Comment 模型的 to_dict()
         # 添加 is_liked 状态
         comment_dict['is_liked'] = comment.id in liked_comment_ids_by_current_user
         comments_list.append(comment_dict)

    return jsonify({
        "state": 1,
        "message": "Comments fetched successfully",
        "comments": comments_list,
        "total_pages": total_pages,
        "total_items": total_items,
        "current_page": page,
        "per_page": per_page
    })

# 获取特定评论的子评论列表 (depth = 2)
@comment_bp.route('/comment/<int:parent_id>/replies', methods=['GET'])
# 使用 verify_jwt_in_request 让接口可选登录
def get_comment_replies(parent_id):
    current_user_id = None
    try:
        verify_jwt_in_request(optional=True)
        jwt_identity = get_jwt_identity()
        if jwt_identity is not None:
             current_user_id = int(jwt_identity)
    except Exception:
        pass # 用户未登录

    # 查询属于该父评论的子评论 (depth = 2)，过滤状态为正常 (status=0)，按创建时间正序排列
    # 通常子评论数量不会特别多，可以一次性获取
    replies = Comment.query.filter_by(parent_id=parent_id, depth=2, status=0)\
                           .order_by(Comment.create_time.asc())\
                           .all()

    # 获取子评论的 ID 列表
    reply_ids = [reply.id for reply in replies]

    # 高效查询当前用户是否点赞了这些子评论
    liked_reply_ids_by_current_user = get_liked_status_for_comments(current_user_id, reply_ids)


    replies_list = []
    for reply in replies:
         reply_dict = reply.to_dict() # 使用 Comment 模型的 to_dict()
         # 添加 is_liked 状态
         reply_dict['is_liked'] = reply.id in liked_reply_ids_by_current_user
         replies_list.append(reply_dict)

    return jsonify({
        "state": 1,
        "message": "Replies fetched successfully",
        "replies": replies_list
    })



