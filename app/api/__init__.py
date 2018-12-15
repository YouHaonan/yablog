# -*- coding: utf-8 -*-

from flask import Blueprint
from flask_cors import CORS

api = Blueprint('api', __name__)
CORS(api)

from . import comments, errors, posts, token, tags, photos, search, replies


