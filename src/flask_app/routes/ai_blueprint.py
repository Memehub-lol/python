

from dataclasses import dataclass, field

from apiflask import APIBlueprint
from apiflask.validators import URL
from marshmallow_dataclass import class_schema

from src.enums.e_memeclf_version import EMemeClfVersion
from src.modules.ai.ai_model_service import AiModelService

ai_blueprint = APIBlueprint('ai_blueprint', __name__, url_prefix="/ai")


@dataclass
class VersionOut:
    version: str


@ai_blueprint.get("/version")
@ai_blueprint.output(class_schema(VersionOut)())
def version():
    return {"version": EMemeClfVersion.get_version_by_lts(lts=True)}


@dataclass
class MemeClfIn:
    url: str = field(metadata={'required': True, 'validate': URL()})


@dataclass
class MemeClfOut:
    meme_clf_pred: str


@ai_blueprint.post("/meme_clf")
@ai_blueprint.input(class_schema(MemeClfIn)(), location='json')
@ai_blueprint.output(class_schema(MemeClfOut)())
def meme_clf(meme_clf_in: MemeClfIn):
    return {"meme_clf_pred": AiModelService.pred_from_url(meme_clf_in.url)}
