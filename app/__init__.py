#  -*- coding: utf-8 -*-

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.config import config
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from flask_whooshee import Whooshee
from flask_migrate import Migrate

db = SQLAlchemy()
photos = UploadSet('photos', IMAGES)
whooshee = Whooshee()
migrate = Migrate(db=db)


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    db.init_app(app)
    configure_uploads(app, photos)
    whooshee.init_app(app)
    migrate.init_app(app)
    patch_request_class(app, 2 * 1024 * 1024)

    from .api import api
    app.register_blueprint(api, url_prefix='/api')

    from .main import main
    app.register_blueprint(main)

    return app
