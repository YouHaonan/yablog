# -*- coding: utf-8 -*-


from flask import jsonify, request
from .auth import generate_token
from .errors import api_abort
from ..models import Admin
from . import api


@api.route('/oauth/token/', methods=['POST'])
def generate():
    grant_type = request.json.get('grant_type')
    username = request.json.get('username')
    password = request.json.get('password')

    if grant_type is None or grant_type.lower() != 'password':
        return api_abort(code=400, message='The grant type must be password.')

    user = Admin.query.filter_by(username=username).first()
    if user is None or not user.validate_password(password):
        return api_abort(code=400, message='Either the username or password was invalid.')

    token, expiration = generate_token(user)

    response = jsonify({
        'access_token': token,
        'token_type': 'Bearer',
        'expires_in': expiration
    })
    response.headers['Cache-Control'] = 'no-store'
    response.headers['Pragma'] = 'no-cache'
    return response
