# -*- coding: utf-8 -*-


from .auth import auth_required
from flask import jsonify, request, url_for
from . import api
from .. import photos
import os
from flask import current_app
from exceptions import ValidationError


@api.route('/photos/', methods=['POST'])
@auth_required
def upload_photos():
    if 'photo' in request.files:
        filename = photos.save(request.files['photo'])
        file_url = photos.url(filename)
        json_photo ={
            'photo_name': filename,
            'url': file_url
        }
        response = jsonify(json_photo)
        response.status_code = 201
        return response
    else:
        raise ValidationError('photos can not be empty')


@api.route('/photos/<name>', methods=['DELETE'])
@auth_required
def delete_photos(name):
    path = os.path.join(current_app.config['UPLOADED_PHOTOS_DEST'], name)
    try:
        os.remove(path)
    except FileNotFoundError:
        pass
    return '', 204

