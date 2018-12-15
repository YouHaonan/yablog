# -*- coding: utf-8 -*-

from flask import jsonify, request, url_for, current_app
from ..models import Tag, Post
from . import api
from sqlalchemy.sql.expression import func


@api.route('/tags/')
def get_tags():
    page = request.args.get('page', 1, type=int)
    pagination = Tag.query.join(Tag.posts).group_by(Tag.id).order_by(func.count(Post.id).desc()).paginate(
        page, per_page=current_app.config['YABLOG_TAGS_PER_PAGE'],
        error_out=False)
    tags = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_tags', page=page-1)
    next = None
    if pagination.has_next:
        next = url_for('api.get_tags', page=page+1)
    return jsonify({
        'tags': [tag.to_json() for tag in tags],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


@api.route('/tags/<int:id>')
def get_tag(id):
    tag = Tag.query.filter_by(reviewed=True).get_or_404(id)
    return jsonify(tag.to_json())


# @api.route('/tags/<int:post_id>/<int:tag_id>', methods=['DELETE'])
# @auth_required
# def delete_tag(post_id, tag_id):
#     tag = Tag.query.get_or_404(tag_id)
#     post = Post.query.get_or_404(post_id)
#     post.tags.remove(tag)
#     db.session.commit()
#
#     if not tag.posts:
#         db.session.delete(tag)
#         db.session.commit()
#     return '', 204


@api.route('/posts/<int:id>/tags/')
def get_post_tags(id):
    post = Post.query.get_or_404(id)
    tags = post.tags
    return jsonify({
        'tags': [tag.to_json() for tag in tags],
        'count': len(tags)
    })

