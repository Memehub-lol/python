from operator import itemgetter
from typing import Any, Optional, cast

import numpy as np
from PIL import Image as Img
from src.lib.image_url import ImageUrlUtils
from src.lib.services.rai import Rai
from src.lib.versioning import Versioner
from src.modules.ai.static_data import StaticData
from src.modules.ai.transforms import Transformations
from torch import Tensor
from torchvision.transforms.transforms import ToTensor


class AiModelService:
    @classmethod
    def meme_clf(cls,  images: Tensor, static_data: Optional[StaticData] = None) -> list[str]:
        redisai = Rai.get_client()
        if static_data is None:
            meme_version = Versioner.meme_clf(lts=True)
            static_data = StaticData.load(meme_version=meme_version)
        try:
            dag = redisai.dag(routing=cast(Any, None))
            dag.tensorset("images", tensor=images.numpy())
            dag.modelrun("features", inputs="images", outputs="features")
            dag.modelrun("dense", inputs="features", outputs="dense")
            dag.tensorget("dense")
            raw_dense = cast(np.ndarray, dag.execute()[-1])
            int_names = list(map(str, np.argmax(raw_dense, axis=1)))
            names = itemgetter(*int_names)(static_data.get_num_name())
            return [names] if len(int_names) == 1 else names
        except Exception as e:
            print(redisai.modelget("features", meta_only=True))
            print(redisai.modelget("dense", meta_only=True))
            raise e

    @classmethod
    def pred_from_url(cls, url: str):
        tensor = Transformations.toVGG16Input(ImageUrlUtils.get_image(url))
        return cls.pred_single_by_image(tensor)

    @classmethod
    def pred_from_path(cls, path: str):
        tensor = Transformations.toVGG16Input(Img.open(path))
        return cls.pred_single_by_image(tensor)

    @classmethod
    def pred_single_by_image(cls, image: Tensor):
        name = cls.meme_clf(image.unsqueeze(0))[0]
        return {"meme_clf_pred": name}
