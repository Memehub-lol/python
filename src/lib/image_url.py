from pathlib import Path

import numpy as np
import requests
from PIL import Image
from PIL.Image import Image as ImageType
from src.lib import logger
from src.lib.image_exceptions import ImageExceptions

IMG_HEIGHT = 224
IMG_WIDTH = 224
IMG_CHANNEL = 3
IMG_H_W = (IMG_HEIGHT, IMG_WIDTH)
IMG_SHAPE = (*IMG_H_W, IMG_CHANNEL)


class ImageUrlUtils:
    @classmethod
    def check_is_deleted_image(cls, image: ImageType):
        for deleted_image in deleted_images:
            if (np.array_equal(np.asarray(deleted_image), np.asarray(image))):
                raise ImageExceptions.IsDeleted

    @classmethod
    def get_image(cls, url: str, check_is_deleted: bool = False):
        raw = requests.get(url, stream=True).raw
        image = Image.open(raw).resize(IMG_H_W).convert("RGB")
        if check_is_deleted:
            cls.check_is_deleted_image(image)
        image_arr = np.asarray(image)
        if not image_arr.shape == IMG_SHAPE:
            raise ImageExceptions.MalformedImage
        elif not image_arr.any():
            raise ImageExceptions.NoImage
        return image

    @classmethod
    def download_image(cls, url: str, path: str, verbose: bool = False) -> bool:
        try:
            if Path(path).is_file():
                return True
            cls.get_image(url).save(path)
            return True
        except Exception as e:
            if verbose:
                logger.error("url: %s", url)
                logger.error(e)
            return False


reddit_deleted_images = ["https://i.redd.it/ga6x8tx90v381.jpg"]
deleted_images = [ImageUrlUtils.get_image(deleted_image) for deleted_image in reddit_deleted_images]
