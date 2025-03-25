# app/__init__.py
from flask import Flask
from flask_socketio import SocketIO
from app.routes.home import home_bp
from app.routes.edit import edit_bp
from app.routes.dk import dk_bp
from app.routes.havre import havre_bp
from app.routes.home import home_bp
from app.routes.download import download_bp
from flask_wtf import CSRFProtect
from flask_talisman import Talisman


csrf = CSRFProtect()
socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    Talisman(app,
             content_security_policy=None,
             force_https=False,)
    app.config.from_object('app.config.Config')
    csrf.init_app(app)

    @app.context_processor
    def inject_csrf():
        from flask_wtf.csrf import generate_csrf
        return dict(csrf_token=lambda: f'<input type="hidden" name="csrf_token" value="{generate_csrf()}">')

    app.register_blueprint(dk_bp, url_prefix='/dk_port')
    app.register_blueprint(havre_bp, url_prefix='/havre_port')
    app.register_blueprint(home_bp)
    app.register_blueprint(edit_bp)
    app.register_blueprint(download_bp)

    return app

