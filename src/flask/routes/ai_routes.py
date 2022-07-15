from typing import Any, Dict, Optional, cast

from flask.blueprints import Blueprint
from flask.globals import request
from src.modules.ai.ai_model_service import AiModelService
from src.lib.versioning import Versioner

ai_routes = Blueprint('ai_routes', __name__, url_prefix="/ai")


@ai_routes.route("/version", methods=["GET"])
def version():
    return {"version": Versioner.meme_clf(lts=True)}


@ai_routes.route("/meme_clf", methods=["POST"])
def meme_clf() -> Dict[str, Any]:
    assert isinstance(json := cast(Optional[Dict[str, str]], request.get_json()), dict)
    assert (url := json.get("url")) is not None
    return AiModelService.pred_from_url(url)
