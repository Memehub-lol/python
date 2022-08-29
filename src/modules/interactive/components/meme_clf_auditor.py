
from operator import itemgetter
from typing import cast

import matplotlib.pyplot as plt
import torch
from IPython.core.display import clear_output
from matplotlib.axes import Axes
from sqlalchemy import select
from src.lib import utils
from src.lib.environment import Environment
from src.lib.image_url import ImageUrlUtils
from src.services.database import (site_session_maker,
                                       training_session_maker)
from src.modules.ai.meme_clf.meme_clf_net import MemeClf
from src.modules.ai.model_runner.model_runner_dataset import (
    Entity, MemeClfPreditingDataset)
from src.modules.ai.static_data import StaticData
from src.modules.ai.transforms import Transformations
from src.modules.generated.site_tables import (RedditMemes,
                                               TemplatePredictions, Templates)
from src.modules.interactive.components.base import IPyProtocol
from src.modules.interactive.components.meme_clf_audit_stats import \
    display_audit_stats
from src.modules.interactive.inputs.get_version import get_meme_version
from src.modules.interactive.inputs.input_handler import options_input_handler
from src.modules.training_database.training_database_entities import \
    ValidationEntity
from src.modules.training_database.training_database_service import EDataPath
from torch import Tensor
from torchvision.transforms.transforms import ToPILImage


class IPyMemeClfAuditor(IPyProtocol):
    @classmethod
    def entry_point(cls):
        cls.meme_version = get_meme_version()
        filter_by = options_input_handler("Filter By:", ["All", "only_templates"])
        meme_clf = MemeClf.load(False, {}, 0, meme_version=cls.meme_version).eval()
        static_data = StaticData.load(meme_version=cls.meme_version)
        with site_session_maker() as session:
            cls.template_name_urls: dict[str,str] = {name: url for name, url in session.execute(select(Templates.name, Templates.url))}
        prevs: list[tuple[Tensor, str, str]] = []
        for tensors, ids in MemeClfPreditingDataset.data_loader(Entity.RedditMeme,
                                                                is_celery=False,
                                                                meme_version=cls.meme_version,
                                                                num_workers=1):
            with torch.no_grad():
                raw_dense = meme_clf.forward(tensors.to(Environment.device)).cpu().detach().numpy()
            int_names = list(map(str, raw_dense))
            names = itemgetter(*int_names)(static_data.get_num_name())
            for tensor, id, name in zip(tensors, ids, names):
                if filter_by == "only_templates" and name in ["not_template", "not_meme"]:
                    continue
                while keypress := cls.audit_meme(tensor, id, name):
                    if keypress == "is deleted":
                        raise NotImplementedError()
                    elif keypress == "skip":
                        break
                    elif keypress == "go back":
                        tensor, id, name = prevs.pop()
                        continue
                    else:
                        raise Exception("wtf")
                prevs.append((tensor, id, name))

    @classmethod
    def audit_meme(cls,tensor:Tensor, id:str, name:str):
        cls.display_audit_data(tensor, id, name)
        keypress = options_input_handler("Audit:", ["not_template",
                                                    "not_meme",
                                                    "correct",
                                                    "incorrect",
                                                    "is deleted",
                                                    "skip",
                                                    "go back"])
        if keypress in ["is deleted", "skip", "go back"]:
            return keypress
        is_correct = keypress in ["correct", name]
        is_not_meme = keypress == "not_meme" or (keypress == "correct" and name == "not_meme")
        is_not_template = keypress == "not_template" or (keypress == "correct" and name == "not_template")
        template_name = name if name not in ["not_meme", "not_template"] else None
        with site_session_maker() as session:
            reddit_meme = cast(RedditMemes, session.scalars(select(RedditMemes).filter_by(id=id)).first())
            url = cast(str, reddit_meme.url)
            path_name = keypress if keypress in ["not_meme","not_template"] else name
            path = EDataPath.get_reddit_path(path_name, url)
            if keypress != "incorrect" and not ImageUrlUtils.download_image(url, path, verbose=True):
                return
            reddit_meme.notMeme = is_not_meme
            reddit_meme.notTemplate = is_not_template
            reddit_meme.templateName = name if keypress == "correct" else None
            session.add(TemplatePredictions(version=cls.meme_version,
                                            not_meme=is_not_meme,
                                            not_template=is_not_template,
                                            reddit_meme_id=id,
                                            template_name=template_name,
                                            correct=is_correct))
            session.commit()
        with training_session_maker() as session:
            session.add(ValidationEntity(prediction=name,
                                        not_meme=is_not_meme,
                                        not_template=is_not_template,
                                        correct=is_correct,
                                        path=path,
                                        version=cls.meme_version,
                                        reddit_meme_id=id))
            session.commit()


    @classmethod
    def display_audit_data(cls,tensor:Tensor, id:str, name:str):
        clear_output()
        display_audit_stats(cls.meme_version)
        utils.display_dict_as_df(dict(prediction=name))
        plt.style.use('dark_background')
        fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(11, 4))
        fig.tight_layout()
        axes = cast(list[Axes], axes)
        axes[0].set_title("input")
        _ = axes[0].imshow(ToPILImage()(Transformations.unnormalize(tensor)))
        if name in cls.template_name_urls:
            axes[1].set_title("template")
            _ = axes[1].imshow(ImageUrlUtils.get_image(cls.template_name_urls[name]))
        plt.show()
        