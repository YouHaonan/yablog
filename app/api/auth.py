# -*- coding: utf-8 -*-

from functools import wraps
from flask import g, current_app, request
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired
from .errors import api_abort, invalid_token, token_missing
from app.models import Admin


def generate_token(user):
    expiration = 7200
    s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
    token = s.dumps({'id': user.id}).decode('ascii')
    return token, expiration


def validate_token(token):
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(token)
    except (BadSignature, SignatureExpired):
        return False
    user = Admin.query.get(data['id'])
    if user is None:
        return False
    g.current_user = user
    return True


def get_token():
    # Flask/Werkzeug do not recognize any authentication types
    # other than Basic or Digest, so here we parse the header by hand.
    if 'Authorization' in request.headers:
        try:
            token_type, token = request.headers['Authorization'].split(None, 1)
        except ValueError:
            # The Authorization header is either empty or has no token
            token_type = token = None
    else:
        token_type = token = None
    return token_type, token


def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token_type, token = get_token()
        if token_type is None or token_type.lower() != 'bearer':
            return api_abort(400, 'The token type must be bearer.')
        if token is None:
            return token_missing()
        if not validate_token(token):
            return invalid_token()
        return f(*args, **kwargs)

    return decorated


def is_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'Authorization' in request.headers:
            token_type, token = get_token()
            if token_type is None or token_type.lower() != 'bearer':
                return api_abort(400, 'The token type must be bearer.')
            if token is None:
                return token_missing()
            if not validate_token(token):
                return invalid_token()
        else:
            g.current_user = None
        return f(*args, **kwargs)

    return decorated
