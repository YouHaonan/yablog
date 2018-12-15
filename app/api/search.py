# -*- coding: utf-8 -*-


from flask import jsonify, request
from ..models import Post, Tag
from . import api
from exceptions import ValidationError


@api.route('/search/', methods=['POST'])
def search():
    q = request.json.get('q', '')
    if q == '':
        raise ValidationError('key words can not be empty')
    posts = Post.query.whooshee_search(q)
    tags = Tag.query.whooshee_search(q)
    post_list = []
    for post in posts:
        post_list.append(post)
    if tags:
        for tag in tags:
            post_list = post_list + tag.posts
    new_list = list(set(post_list))
    response = jsonify({
        'posts': [Post.to_json(post) for post in new_list]}
    )
    return response

