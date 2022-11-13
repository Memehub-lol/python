from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Boolean, Column, DateTime, Enum, Float, ForeignKeyConstraint, Integer, PrimaryKeyConstraint, String, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import registry, relationship

mapper_registry = registry()


@mapper_registry.mapped
@dataclass
class ImgflipTemplates:
    __tablename__ = 'imgflip_templates'
    __table_args__ = (
        PrimaryKeyConstraint('imgflip_name', name='PK_00960a2c151692800a35316a6cc'),
    )
    __sa_dataclass_metadata_key__ = 'sa'

    created_at: datetime = field(metadata={'sa': Column(DateTime(True), nullable=False, server_default=text('now()'))})
    name: str = field(metadata={'sa': Column(String, nullable=False)})
    page: str = field(metadata={'sa': Column(String, nullable=False)})
    url: str = field(metadata={'sa': Column(String, nullable=False)})
    imgflip_name: str = field(metadata={'sa': Column(String)})
    deleted_at: Optional[datetime] = field(default=None, metadata={'sa': Column(DateTime(True))})
    num_images: Optional[int] = field(default=None, metadata={'sa': Column(Integer)})

    reddit_memes: List[RedditMemes] = field(default_factory=list, metadata={'sa': relationship('RedditMemes', back_populates='imgflip_templates')})


@mapper_registry.mapped
@dataclass
class Redditors:
    __tablename__ = 'redditors'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='PK_061583869ba792c2095b65c671f'),
        UniqueConstraint('username', name='UQ_12ea821277fb068de87556497b0')
    )
    __sa_dataclass_metadata_key__ = 'sa'

    id: str = field(metadata={'sa': Column(UUID, server_default=text('uuid_generate_v4()'))})
    created_at: datetime = field(metadata={'sa': Column(DateTime(True), nullable=False, server_default=text('now()'))})
    username: str = field(metadata={'sa': Column(String(20), nullable=False)})
    deleted_at: Optional[datetime] = field(default=None, metadata={'sa': Column(DateTime(True))})

    reddit_memes: List[RedditMemes] = field(default_factory=list, metadata={'sa': relationship('RedditMemes', back_populates='redditor')})
    reddit_scores: List[RedditScores] = field(default_factory=list, metadata={'sa': relationship('RedditScores', back_populates='redditor')})


@mapper_registry.mapped
@dataclass
class RedditMemes:
    __tablename__ = 'reddit_memes'
    __table_args__ = (
        ForeignKeyConstraint(['redditor_id'], ['redditors.id'], ondelete='CASCADE', name='FK_a270a3212df747ae19cb09d1be9'),
        ForeignKeyConstraint(['template_name'], ['imgflip_templates.imgflip_name'], ondelete='CASCADE', name='FK_0634017e6f2351824f6db59ba4e'),
        PrimaryKeyConstraint('id', name='PK_1ae085193dc492081d372e0299c'),
        UniqueConstraint('url', name='UQ_80fc13a6facb2e40853bc5ce717')
    )
    __sa_dataclass_metadata_key__ = 'sa'

    id: str = field(metadata={'sa': Column(UUID, server_default=text('uuid_generate_v4()'))})
    created_at: datetime = field(metadata={'sa': Column(DateTime(True), nullable=False, server_default=text('now()'))})
    idx: int = field(metadata={'sa': Column(Integer, nullable=False)})
    reddit_id: str = field(metadata={'sa': Column(String, nullable=False)})
    subreddit: str = field(metadata={'sa': Column(String, nullable=False)})
    title: str = field(metadata={'sa': Column(String, nullable=False)})
    url: str = field(metadata={'sa': Column(String, nullable=False)})
    upvote_ratio: float = field(metadata={'sa': Column(Float(53), nullable=False)})
    upvotes: int = field(metadata={'sa': Column(Integer, nullable=False)})
    downvotes: int = field(metadata={'sa': Column(Integer, nullable=False)})
    num_comments: int = field(metadata={'sa': Column(Integer, nullable=False)})
    redditor_id: str = field(metadata={'sa': Column(UUID, nullable=False)})
    deleted_at: Optional[datetime] = field(default=None, metadata={'sa': Column(DateTime(True))})
    image_error: Optional[str] = field(default=None, metadata={'sa': Column(Enum('IsDeleted', 'Malformed', 'NoImage', 'Connection', 'Unidentified', 'Unknown', name='ImageError'))})
    percentile: Optional[float] = field(default=None, metadata={'sa': Column(Float(53))})
    not_meme: Optional[bool] = field(default=None, metadata={'sa': Column(Boolean)})
    not_template: Optional[bool] = field(default=None, metadata={'sa': Column(Boolean)})
    meme_text: Optional[str] = field(default=None, metadata={'sa': Column(String)})
    template_name: Optional[str] = field(default=None, metadata={'sa': Column(String)})

    redditor: Optional[Redditors] = field(default=None, metadata={'sa': relationship('Redditors', back_populates='reddit_memes')})
    imgflip_templates: Optional[ImgflipTemplates] = field(default=None, metadata={'sa': relationship('ImgflipTemplates', back_populates='reddit_memes')})


@mapper_registry.mapped
@dataclass
class RedditScores:
    __tablename__ = 'reddit_scores'
    __table_args__ = (
        ForeignKeyConstraint(['redditor_id'], ['redditors.id'], ondelete='CASCADE', name='FK_adcc81afcb5f0b2c57e6ca18a10'),
        PrimaryKeyConstraint('id', name='PK_6ee18c3e5f54447fff6721e5b91')
    )
    __sa_dataclass_metadata_key__ = 'sa'

    id: str = field(metadata={'sa': Column(UUID, server_default=text('uuid_generate_v4()'))})
    created_at: datetime = field(metadata={'sa': Column(DateTime(True), nullable=False, server_default=text('now()'))})
    username: str = field(metadata={'sa': Column(String(20), nullable=False)})
    subreddit: str = field(metadata={'sa': Column(String(50), nullable=False)})
    time_delta: int = field(metadata={'sa': Column(Integer, nullable=False)})
    timestamp: int = field(metadata={'sa': Column(Integer, nullable=False)})
    datetime_: datetime = field(metadata={'sa': Column('datetime', DateTime, nullable=False)})
    final_score: float = field(metadata={'sa': Column(Float(53), nullable=False)})
    raw_score: float = field(metadata={'sa': Column(Float(53), nullable=False)})
    num_in_bottom: int = field(metadata={'sa': Column(Integer, nullable=False)})
    num_in_top: int = field(metadata={'sa': Column(Integer, nullable=False)})
    shitposter_index: float = field(metadata={'sa': Column(Float(53), nullable=False)})
    highest_upvotes: int = field(metadata={'sa': Column(Integer, nullable=False)})
    hu_score: float = field(metadata={'sa': Column(Float(53), nullable=False)})
    lowest_ratio: float = field(metadata={'sa': Column(Float(53), nullable=False)})
    deleted_at: Optional[datetime] = field(default=None, metadata={'sa': Column(DateTime(True))})
    redditor_id: Optional[str] = field(default=None, metadata={'sa': Column(UUID)})

    redditor: Optional[Redditors] = field(default=None, metadata={'sa': relationship('Redditors', back_populates='reddit_scores')})
