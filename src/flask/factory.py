import json
from functools import partial

import inflection
from flask_cors import CORS
from src.flask.routes.ai_routes import ai_routes
from src.lib import logger
from src.lib.environment import Environment
from src.lib.utils import convert_keys
from werkzeug.exceptions import HTTPException

from flask.app import Flask
from flask.globals import request
from flask.json import jsonify
from flask.wrappers import Response


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    _ = CORS(app, origins=Environment.whitelist)
    app.config.from_object("config.flask")
    app.register_blueprint(ai_routes)

    @app.before_request
    def incoming_camel_to_snake():
        if request.method !="GET":
            convert_keys(request.json, converter=inflection.underscore)

    @app.after_request
    def outgoing_snake_to_camel(response: Response):
        json_str = response.get_data(as_text=True)
        try:
            resp_json = json.loads(json_str)
        except:
            return response
        if not isinstance(resp_json, dict) and not isinstance(resp_json, list):
            return response
        converter = partial(inflection.camelize, uppercase_first_letter=False)
        json_str_converted = json.dumps(convert_keys(resp_json, converter=converter))
        response.set_data(json_str_converted)
        return response

    @app.errorhandler(HTTPException)
    def handle_exception(e: HTTPException):
        logger.error(e)
        return jsonify({"code": e.code,
                        "name": e.name,
                        "description": e.description})

    return app
