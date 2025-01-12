from flask import Blueprint
from .export_routes import *
from .message_routes import *
from .archive_routes import *

# Blueprint 묶음 생성
def register_routes(app):
    app.register_blueprint(message_bp, url_prefix='/messages')
    app.register_blueprint(archive_bp, url_prefix='/archives')
    app.register_blueprint(export_bp, url_prefix='/export')