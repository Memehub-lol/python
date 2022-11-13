from enum import Enum


class EArtifactType(Enum):
    Dataset = "dataset"
    Model = "model"


class EArtifact(Enum):
    Imgflip = "imgflip"
    Reddit = "reddit"
    MemeClf = "meme_clf"

    def get_type(self) -> EArtifactType:
        if self is EArtifact.Imgflip:
            return EArtifactType.Dataset
        elif self is EArtifact.Reddit:
            return EArtifactType.Dataset
        elif self is EArtifact.MemeClf:
            return EArtifactType.Model
        raise Exception("enum exhausted")
