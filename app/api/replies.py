from .auth import auth_required, is_admin
from flask import jsonify, request, url_for, current_app, g
from .. import db
from ..models import Comment, Reply
from . import api
from exceptions import ValidationError


@api.route('/replies/')
@auth_required
def get_replies():
    page = request.args.get('page', 1, type=int)
    pagination = Reply.query.filter_by(is_read=False).order_by(Reply.timestamp.desc()).paginate(
        page, per_page=current_app.config['YABLOG_COMMENTS_PER_PAGE'],
        error_out=False)
    replies = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_replies', page=page-1)
    next = None
    if pagination.has_next:
        next = url_for('api.get_replies', page=page+1)
    return jsonify({
        'replies': [reply.to_json() for reply in replies],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


@api.route('/replies/<int:id>', methods=['PUT'])
@auth_required
def toggle_reply(id):
    reply = Reply.query.get_or_404(id)
    reply.is_read = True
    db.session.commit()
    return '', 200


@api.route('/comments/<int:id>/replies/')
def get_comment_replies(id):
    comment = Comment.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = Reply.query.with_parent(comment).order_by(Reply.timestamp.desc()).paginate(
        page, per_page=current_app.config['YABLOG_COMMENTS_PER_PAGE'],
        error_out=False)
    replies = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_comment_replies', id=id, page=page-1)
    next = None
    if pagination.has_next:
        next = url_for('api.get_comment_replies', id=id, page=page+1)
    return jsonify({
        'replies': [reply.to_json() for reply in replies],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


@api.route('/comments/<int:id>/replies/', methods=['POST'])
@is_admin
def new_comment_reply(id):
    json_reply = request.json
    try:
        body = json_reply.get('body')
        to = json_reply.get('to')
    except AttributeError:
        raise ValidationError('wrong format')
    if body is None or body == '':
        raise ValidationError('reply does not have a body or receiver')
    if to is None or to == '':
        raise ValidationError('reply does not have a receiver')
    reply = Reply(body=body)
    reply.to = to
    comment = Comment.query.get_or_404(id)
    reply.comment = comment
    if g.current_user:
        reply.author = g.current_user.username
        reply.from_admin = True
    else:
        try:
            author = json_reply.get('author')
        except AttributeError:
            raise ValidationError('reply does not have a author')
        if author is None or reply == '':
            raise ValidationError('reply does not have a author')
        reply.author = author
        to_admin = json_reply.get('to_admin', False)
        if to_admin:
            reply.is_read=False
    db.session.add(reply)
    db.session.commit()
    response = jsonify(reply.to_json())
    response.status_code = 201
    response.headers['Location'] = url_for('api.get_comment_replies', id=comment.id, _external=True)
    return response


@api.route('/replies/<int:id>', methods=['DELETE'])
@auth_required
def delete_reply(id):
    reply = Reply.query.get(id)
    db.session.delete(reply)
    db.session.commit()
    return '', 204
