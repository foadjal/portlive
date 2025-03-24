# app/__init__.py
from flask import Flask
from flask_socketio import SocketIO
from app.routes.home import home_bp
from app.routes.edit import edit_bp
from app.routes.dk import dk_bp
from app.routes.havre import havre_bp
from app.routes.home import home_bp
from app.routes.download import download_bp

socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')
    app.register_blueprint(dk_bp, url_prefix='/dk_port')
    app.register_blueprint(havre_bp, url_prefix='/havre_port')
    app.register_blueprint(home_bp)
    app.register_blueprint(edit_bp)
    app.register_blueprint(download_bp)

    return app
