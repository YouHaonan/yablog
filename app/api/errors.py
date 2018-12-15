# -*- coding: utf-8 -*-


from flask import jsonify
from werkzeug.http import HTTP_STATUS_CODES
from . import api
from exceptions import ValidationError


def api_abort(code, message=None, **kwargs):
    if message is None:
        message = HTTP_STATUS_CODES.get(code, '')

    response = jsonify(code=code, message=message, **kwargs)
    response.status_code = code
    return response  # You can also just return (response, code) tuple


def invalid_token():
    response = api_abort(401, error='invalid_token', error_description='Either the token was expired or invalid.')
    response.headers['WWW-Authenticate'] = 'Bearer'
    return response


def token_missing():
    response = api_abort(401)
    response.headers['WWW-Authenticate'] = 'Bearer'
    return response


@api.errorhandler(ValidationError)
def validation_error(e):
    return api_abort(400, e.args[0])


@api.app_errorhandler(404)
def page_not_found(e):
    response = jsonify(code=404, message='The requested URL was not found on the server.')
    response.status_code = 404
    return response


@api.app_errorhandler(405)
def method_not_allowed(e):
    response = jsonify(code=405, message='The method is not allowed for the requested URL.')
    response.status_code = 405
    return response


@api.app_errorhandler(500)
def internal_server_error(e):
    response = jsonify(code=500, message='An internal server error occurred.')
    response.status_code = 500
    return response
