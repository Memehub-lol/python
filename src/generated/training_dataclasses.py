from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Integer, PrimaryKeyConstraint, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import registry

mapper_registry = registry()


@mapper_registry.mapped
@dataclass
class MemeTemplate:
    __tablename__ = 'meme_template'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='meme_template_pkey'),
    )
    __sa_dataclass_metadata_key__ = 'sa'

    id: int = field(init=False, metadata={'sa': Column(Integer)})
    name: str = field(metadata={'sa': Column(String(400), nullable=False)})
    path: str = field(metadata={'sa': Column(String(400), nullable=False)})
    is_test_set: bool = field(metadata={'sa': Column(Boolean, nullable=False)})


@mapper_registry.mapped
@dataclass
class NotMeme:
    __tablename__ = 'not_meme'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='not_meme_pkey'),
    )
    __sa_dataclass_metadata_key__ = 'sa'

    id: int = field(init=False, metadata={'sa': Column(Integer)})
    path: str = field(metadata={'sa': Column(String(400), nullable=False)})
    is_test_set: bool = field(metadata={'sa': Column(Boolean, nullable=False)})


@mapper_registry.mapped
@dataclass
class NotTemplate:
    __tablename__ = 'not_template'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='not_template_pkey'),
    )
    __sa_dataclass_metadata_key__ = 'sa'

    id: int = field(init=False, metadata={'sa': Column(Integer)})
    path: str = field(metadata={'sa': Column(String(400), nullable=False)})
    is_test_set: bool = field(metadata={'sa': Column(Boolean, nullable=False)})


@mapper_registry.mapped
@dataclass
class Validation:
    __tablename__ = 'validation'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='validation_pkey'),
    )
    __sa_dataclass_metadata_key__ = 'sa'

    id: int = field(init=False, metadata={'sa': Column(Integer)})
    prediction: str = field(metadata={'sa': Column(String(400), nullable=False)})
    reddit_meme_id: str = field(metadata={'sa': Column(UUID, nullable=False)})
    version: str = field(metadata={'sa': Column(String(400), nullable=False)})
    correct: bool = field(metadata={'sa': Column(Boolean, nullable=False)})
    not_meme: bool = field(metadata={'sa': Column(Boolean, nullable=False)})
    not_template: bool = field(metadata={'sa': Column(Boolean, nullable=False)})
    created_at: datetime = field(metadata={'sa': Column(DateTime(True), nullable=False, server_default=text('now()'))})
    path: Optional[str] = field(default=None, metadata={'sa': Column(String(400))})
