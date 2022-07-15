from sqlalchemy import case, func, select
from src.lib.services.database import training_session_maker
from src.lib.utils import display_dict_as_df
from src.modules.training_database.training_database_entities import \
    ValidationEntity


def display_audit_stats(version: str):
    with training_session_maker() as session:
        total = session.scalar(select(func.count(ValidationEntity.id)).filter_by(version=version))
        total_correct = session.scalar(select(func.count(case((ValidationEntity.correct == True, 1)))).filter_by(version=version))
        total_incorrect = session.scalar(select(func.count(case((ValidationEntity.correct == False, 1)))).filter_by(version=version))
        total_template = session.scalar(select(func.count(ValidationEntity.id)).filter_by(version=version).filter(
            ValidationEntity.not_meme.is_(False)).filter(ValidationEntity.not_template.is_(False)))
        template_correct = session.scalar(select(func.count(case((ValidationEntity.correct == True, 1)))).filter_by(version=version).filter(
            ValidationEntity.not_meme.is_(False)).filter(ValidationEntity.not_template.is_(False)))
        template_incorrect = session.scalar(select(func.count(case((ValidationEntity.correct == False, 1)))).filter_by(
            version=version).filter(ValidationEntity.not_meme.is_(False)).filter(ValidationEntity.not_template.is_(False)))
        not_meme = session.scalar(select(func.count(case((ValidationEntity.not_meme == True, 1)))).filter_by(version=version))
        not_template = session.scalar(select(func.count(case((ValidationEntity.not_template == True, 1)))).filter_by(version=version))
    total_ratio = round(total_correct/total if total else 0, 2)
    total_template_ratio = round(template_correct/total_template if total_template else 0, 2)
    display_dict_as_df(dict(total=total,
                            not_meme=not_meme,
                            not_template=not_template,
                            total_template=total_template,
                            total_correct=total_correct,
                            total_incorrect=total_incorrect,
                            total_ratio=total_ratio,
                            template_correct=template_correct,
                            template_incorrect=template_incorrect,
                            total_template_ratio=total_template_ratio))
