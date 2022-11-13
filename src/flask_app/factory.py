from apiflask import APIFlask
from flask_cors import CORS
from flask_httpauth import HTTPTokenAuth

from src.flask_app.routes.ai_blueprint import ai_blueprint
from src.flask_app.routes.reddit_blueprint import reddit_blueprint
from src.services.environment import Environment


def create_app():
    app = APIFlask(__name__, title="MemehubFlaskRestApi", version="0.0.1")
    _ = CORS(app, origins=Environment.ORIGIN_WHITELIST)
    auth = HTTPTokenAuth(scheme="ApiKey", header="X-Memehub-Flask-Key")
    app.security_schemes = {'ApiKeyAuth': {'type': 'apiKey', 'in': 'header', 'name': "X-Memehub-Flask-Key"}}
    app.config.from_object("src.flask_app.config")
    app.register_blueprint(ai_blueprint)
    app.register_blueprint(reddit_blueprint)
    return app
