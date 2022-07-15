from operator import itemgetter
from typing import cast

import torch
from sqlalchemy import select
from src.lib.environment import Environment
from src.lib.services.database import (site_session_maker,
                                       training_session_maker)
from src.modules.ai.meme_clf.meme_clf_net import MemeClf
from src.modules.ai.static_data import StaticData
from src.modules.generated.site_tables import TemplatePredictions
from src.modules.interactive.components.base import IPyProtocol
from src.modules.interactive.components.bootstrap.prediction_bootstrapper_dataset import \
    PredictionBootstrapperDataset
from src.modules.interactive.components.meme_clf_audit_stats import \
    display_audit_stats
from src.modules.interactive.inputs.get_version import get_meme_version
from src.modules.training_database.training_database_entities import \
    ValidationEntity
from src.modules.training_database.training_database_service import EDataPath
from tqdm import tqdm


class PredictionBootstrapper(IPyProtocol):
    @classmethod
    def entry_point(cls):
        cls.meme_version = get_meme_version()
        meme_clf = MemeClf.load(False, {}, 0, meme_version=cls.meme_version).eval()
        static_data = StaticData.load(meme_version=cls.meme_version)
        count, loader = PredictionBootstrapperDataset.data_loader(meme_version=cls.meme_version)
        with (site_session_maker() as site_session,
              training_session_maker() as training_session,
              tqdm(total=count) as pbar):
            for meme_ids, val_ids, urls, tensors in loader:
                with torch.no_grad():
                    raw_dense = meme_clf.forward(tensors.to(Environment.device)).cpu().detach().numpy()
                int_names = list(map(str, raw_dense))
                names = itemgetter(*int_names)(static_data.get_num_name())
                for meme_id, val_id, url, name in zip(meme_ids, val_ids.numpy(), urls, names):
                    val = cast(ValidationEntity, training_session.scalar(select(ValidationEntity).filter_by(id=int(val_id))))
                    is_not_meme = name == "not_meme"
                    is_not_template = name == "not_template"
                    if val.not_meme and is_not_meme:
                        correct = True
                    elif val.not_template and is_not_template:
                        correct = True
                    elif val.prediction == name:
                        correct = True
                    else:
                        correct = False
                    site_session.add(TemplatePredictions(not_meme=is_not_meme,
                                                         not_template=is_not_template,
                                                         template_name=name if name not in ["not_meme", "not_template"] else None,
                                                         version=cls.meme_version,
                                                         reddit_meme_id=meme_id,
                                                         correct=correct))
                    site_session.commit()
                    training_session.add(ValidationEntity(prediction=name,
                                                          not_meme=is_not_meme,
                                                          not_template=is_not_template,
                                                          correct=correct,
                                                          path=EDataPath.get_reddit_path(name, url),
                                                          version=cls.meme_version,
                                                          reddit_meme_id=meme_id))
                    training_session.commit()
                    _ = pbar.update(1)
        display_audit_stats(cls.meme_version)
