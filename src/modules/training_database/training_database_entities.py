from typing import Any, Union

from sqlalchemy import DateTime
from sqlalchemy import text as _text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import Boolean, Integer, String

training_base: Any = declarative_base()
training_metadata = training_base.metadata  # type: ignore


class NotMemeEntity(training_base):
    __tablename__ = "not_meme"

    id = Column(Integer, primary_key=True)
    path = Column(String(400), nullable=False)
    is_test_set = Column(Boolean(), nullable=False)


class NotTemplateEntity(training_base):
    __tablename__ = "not_template"

    id = Column(Integer, primary_key=True)
    path = Column(String(400), nullable=False)
    is_test_set = Column(Boolean(), nullable=False)


class TemplateEntity(training_base):
    __tablename__ = "meme_template"

    id = Column(Integer, primary_key=True)
    name = Column(String(400), nullable=False)
    path = Column(String(400), nullable=False)
    is_test_set = Column(Boolean(), nullable=False)


class ValidationEntity(training_base):
    __tablename__ = "validation"

    id = Column(Integer, primary_key=True)
    prediction = Column(String(400), nullable=False)
    path = Column(String(400), nullable=True)
    reddit_meme_id = Column(UUID, nullable=False)
    version = Column(String(400), nullable=False)
    correct = Column(Boolean, nullable=False)
    not_meme = Column(Boolean, nullable=False)
    not_template = Column(Boolean, nullable=False)
    created_at = Column(DateTime(True), nullable=False, server_default=_text('now()'))


TTrainingEntity = Union[NotMemeEntity, NotTemplateEntity, TemplateEntity]
training_entities: list[TTrainingEntity] = [NotMemeEntity, NotTemplateEntity, TemplateEntity]
