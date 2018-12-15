# -*- coding: utf-8 -*-

import os
from .auth import auth_required, is_admin
from flask import jsonify, request, url_for, current_app, g
from .. import db
from ..models import Post, Tag, Photo
from . import api
from exceptions import ValidationError
import re


@api.route('/posts/') 
@is_admin
def get_posts():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['YABLOG_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_posts', page=page-1)
    next = None
    if pagination.has_next:
        next = url_for('api.get_posts', page=page+1)
    is_admin = False
    if g.current_user:
        is_admin = True
    return jsonify({
        'posts': [Post.to_json(post) for post in posts],
        'prev': prev,
        'next': next,
        'count': pagination.total,
        'is_admin': is_admin
    })


@api.route('/posts/<int:id>')
def get_post(id):
    post = Post.query.get_or_404(id)
    return jsonify(Post.to_json(post))


@api.route('/posts/', methods=['POST'])
@auth_required
def new_post():
    json_post = request.json
    title = json_post.get('title')
    body = json_post.get('body')
    tags = json_post.get('tags')
    photos=json_post.get('nameList')
    if body is None or body == '':
        raise ValidationError('post does not have a body')
    if title is None or title == '':
        raise ValidationError('post does not have a title')
    post = Post(title=title, body=body)
    if tags:
        for name in re.split('[,，]', tags):
            tag = Tag.query.filter_by(name=name).first()
            if tag is None:
                tag = Tag(name=name)
                db.session.add(tag)
                db.session.commit()
            post.tags.append(tag)
    if photos:
        for name in photos:
            photo = Photo(name=name)
            db.session.add(photo)
            db.session.commit()
            post.photos.append(photo)
    db.session.add(post)
    db.session.commit()
    response = jsonify(Post.to_json(post))
    response.status_code = 201
    response.headers['Location'] = url_for('api.get_post', id=post.id, _external=True)
    return response


@api.route('/posts/<int:id>', methods=['PUT'])
@auth_required
def edit_post(id):
    post = Post.query.get_or_404(id)
    post.body = request.json.get('body', post.body)
    post.title = request.json.get('title', post.title)
    photos = request.json.get('nameList')
    tags = request.json.get('tags')
    for i in post.tags:
        if i.name not in re.split(r'[,，]', tags) and not i.posts:
            db.session.delete(i)
            db.session.commit()
    if tags:
        post.tags.clear()
        for name in re.split(r'[,，]', tags):
            tag = Tag.query.filter_by(name=name).first()
            if tag is None:
                tag = Tag(name=name)
                db.session.add(tag)
                db.session.commit()
            post.tags.append(tag)
    if photos:
        print(photos)
        for name in photos:
            photo = Photo(name=name)
            db.session.add(photo)
            db.session.commit()
            post.photos.append(photo)
    db.session.commit()
    return jsonify(Post.to_json(post))


@api.route('/tags/<int:id>/posts/')
def get_tag_posts(id):
    tag = Tag.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.with_parent(tag).paginate(
        page, per_page=current_app.config['YABLOG_COMMENTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_post_comments', id=id, page=page-1)
    next = None
    if pagination.has_next:
        next = url_for('api.get_post_comments', id=id, page=page+1)
    return jsonify({
        'posts': [Post.to_json(post) for post in posts],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


@api.route('/posts/<int:id>', methods=['DELETE'])
@auth_required
def delete_post(id):
    post = Post.query.get(id)
    tags = post.tags
    photos = post.photos
    db.session.delete(post)
    for i in tags:
        if not i.posts:
            db.session.delete(i)
    print(photos)
    for j in photos:
        path = os.path.join(current_app.config['UPLOADED_PHOTOS_DEST'] , j.name)
        try:
            os.remove(path)
        except FileNotFoundError:
            pass
    db.session.commit()
    return '', 204

