from contextlib import contextmanager
from typing import ClassVar, cast

import wandb
from src.modules.wnb.e_artifacts import EArtifact
from src.modules.wnb.enums.e_job_type import EJobType
from src.modules.wnb.interfaces.ModelConfig import ModelConfig
from src.modules.wnb.interfaces.SGDKwargs import SGDKwargs
from wandb.sdk.wandb_artifacts import Artifact
from wandb.sdk.wandb_run import Run

sgd_kwargs: SGDKwargs = {"lr": 0.000_1,
                         "momentum": 0.9,
                         "dampening": 0,
                         "weight_decay": 0.000_1,
                         "nesterov": True}


class MhClfWandb:
    run: ClassVar[Run] = wandb.run
    config: ClassVar[ModelConfig] = wandb.config

    project: ClassVar[str] = "meme-hub-project"
    entity: ClassVar[str] = "meme-clf"
    init_config: ClassVar[ModelConfig] = {"output_size": 0, "sgd_kwargs": sgd_kwargs}

    @contextmanager
    @classmethod
    def init(cls, job_type: EJobType):
        run = cast(Run, wandb.init(project=cls.project, entity=cls.entity, job_type=job_type.value, config=cls.init_config))
        yield run
        run.finish()

    @classmethod
    def use_artifact_direct(cls, artifact: Artifact) -> Artifact:
        return cls.run.use_artifact(artifact)

    @classmethod
    def use_artifact(cls, e_artifact: EArtifact, alias: str = "latest") -> Artifact:
        return cls.run.use_artifact(f"{e_artifact.value}:{alias}", type=e_artifact.get_type().value)
