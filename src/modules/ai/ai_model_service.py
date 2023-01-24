from PIL import Image as Img
from torch import Tensor

from src.enums.e_memeclf_version import EMemeClfVersion
from src.lib.image_url import ImageUrlUtils
from src.modules.ai.static_data import StaticData
from src.modules.ai.transforms import Transformations
from src.services.rai import Rai


class AiModelService:
    @classmethod
    def meme_clf_lts(cls,  images: Tensor) -> list[str]:
        static_data = StaticData.load(meme_version=EMemeClfVersion.get_version_by_lts(lts=True))
        return Rai.exec_meme_clf_dag(images, static_data)

    @classmethod
    def meme_clf(cls,  images: Tensor, static_data: StaticData) -> list[str]:
        return Rai.exec_meme_clf_dag(images, static_data)

    @classmethod
    def pred_single_by_image(cls, image: Tensor):
        return cls.meme_clf_lts(image.unsqueeze(0))[0]

    @classmethod
    def pred_from_path(cls, path: str):
        tensor = Transformations.toVGG16Input(Img.open(path))
        return cls.pred_single_by_image(tensor)

    @classmethod
    def pred_from_url(cls, url: str):
        tensor = Transformations.toVGG16Input(ImageUrlUtils.get_image(url))
        return cls.pred_single_by_image(tensor)
