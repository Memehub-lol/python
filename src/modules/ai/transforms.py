from typing import Callable

import numpy as np
import torch
from torchvision.transforms import (ColorJitter, Compose, Normalize,
                                    RandomAffine, RandomHorizontalFlip,
                                    RandomVerticalFlip, ToTensor)
from torchvision.transforms.transforms import RandomCrop, RandomErasing, Resize

TensorFunc = Callable[..., torch.Tensor]


class Transformations:
    mean = np.asarray([0.485, 0.456, 0.406])
    std = np.asarray([0.229, 0.224, 0.225])
    toTensorOnly: TensorFunc = Compose([ToTensor()])
    toVGG16Input: TensorFunc = Compose([ToTensor(), Normalize(mean=mean, std=std)])
    unnormalize = Normalize((-mean / std).tolist(), (1.0 / std).tolist())

    @classmethod
    def get_transforms(cls,
                       hflip: bool = True,
                       rand_affine: bool = True,
                       color_jitter: bool = True,
                       erasing: bool = True,
                       crop: bool = True,
                       vflip: bool = False,
                       normalize: bool = True) -> TensorFunc:
        transforms_list: list[TensorFunc] = []
        if color_jitter:
            transforms_list.append(ColorJitter(brightness=0.1, contrast=0.1, saturation=0.1))
        if crop:
            transforms_list.extend([RandomCrop(200), Resize(224)])
        if rand_affine:
            transforms_list.append(RandomAffine(5, scale=(0.95, 1.05)))
        if hflip:
            transforms_list.append(RandomHorizontalFlip())
        if vflip:
            transforms_list.append(RandomVerticalFlip(0.3))
        transforms_list.append(ToTensor())
        if normalize:
            transforms_list.append(Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]))
        if erasing:
            transforms_list.append(RandomErasing(p=1))
        return Compose(transforms_list)
