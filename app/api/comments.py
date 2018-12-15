# -*- coding: utf-8 -*-

from .auth import auth_required, is_admin
from flask import jsonify, request, url_for, current_app, g
from .. import db
from ..models import Comment, Post
from . import api
from exceptions import ValidationError


@api.route('/comments/')
@auth_required
def get_comments():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.filter_by(is_read=False).order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['YABLOG_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_comments', page=page-1)
    next = None
    if pagination.has_next:
        next = url_for('api.get_comments', page=page+1)
    return jsonify({
        'comments': [comment.to_json() for comment in comments],
        'prev': prev,
        'next': next,
        'count': pagination.total,
        'is_admin': True
    })


@api.route('/comments/<int:id>', methods=['PUT'])
@auth_required
def toggle_comment(id):
    comment = Comment.query.get_or_404(id)
    comment.is_read = True
    db.session.commit()
    return '', 200


@api.route('/posts/<int:id>/comments/')
def get_post_comments(id):
    post = Post.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.with_parent(post).order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['YABLOG_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_post_comments', id=id, page=page-1)
    next = None
    if pagination.has_next:
        next = url_for('api.get_post_comments', id=id, page=page+1)
    return jsonify({
        'comments': [comment.to_json() for comment in comments],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


@api.route('/comments/<int:id>')
def get_comment(id):
    comment = Comment.query.get_or_404(id)
    return jsonify(comment.to_json())


@api.route('/posts/<int:id>/comments/', methods=['POST'])
@is_admin
def new_post_comment(id):
    json_comment = request.json
    try:
        body = json_comment.get('body')
    except AttributeError:
        raise ValidationError('comment does not have a body')
    if body is None or body == '':
        raise ValidationError('comment does not have a body')
    comment = Comment(body=body)
    post = Post.query.get_or_404(id)
    comment.post = post
    comment.floor = len(post.comments)
    if g.current_user:
        comment.author = g.current_user.username
        comment.is_read = True
        comment.from_admin = True
    else:
        try:
            author = json_comment.get('author')
        except AttributeError:
            raise ValidationError('comment does not have a author')
        if author is None or author == '':
            raise ValidationError('comment does not have a author')
        comment.author = author
    db.session.add(comment)
    db.session.commit()
    response = jsonify(comment.to_json())
    response.status_code = 201
    response.headers['Location'] = url_for('api.get_post_comments', id=post.id, _external=True)
    return response


@api.route('/comments/<int:id>', methods=['DELETE'])
@auth_required
def delete_comment(id):
    comment = Comment.query.get(id)
    db.session.delete(comment)
    db.session.commit()
    return '', 204
