from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, List, Optional

from sqlalchemy import (ARRAY, BigInteger, Boolean, Column, DateTime, Enum,
                        Float, ForeignKey, ForeignKeyConstraint, Integer,
                        PrimaryKeyConstraint, String, Table, Text,
                        UniqueConstraint)
from sqlalchemy import text as _text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import registry, relationship

mapper_registry = registry()
metadata = mapper_registry.metadata


@mapper_registry.mapped
@dataclass
class Emojis:
    __tablename__ = 'emojis'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='PK_9adb96a675f555c6169bad7ba62'),
    )
    __sa_dataclass_metadata_key__ = 'sa'

    id: Any = field(metadata={'sa': Column(UUID)})
    name: str = field(metadata={'sa': Column(String, nullable=False)})
    bucket: str = field(metadata={'sa': Column(String, nullable=False, server_default=_text("'memehub-development'::character varying"))})
    bucket_folder: str = field(metadata={'sa': Column(String, nullable=False)})
    ext: str = field(metadata={'sa': Column(String, nullable=False)})
    is_dev: bool = field(metadata={'sa': Column(Boolean, nullable=False, server_default=_text('false'))})
    created_at: datetime = field(metadata={'sa': Column(DateTime(True), nullable=False, server_default=_text('now()'))})
    updated_at: Optional[datetime] = field(default=None, metadata={'sa': Column(DateTime(True), server_default=_text('now()'))})
    deleted_at: Optional[datetime] = field(default=None, metadata={'sa': Column(DateTime(True))})

    user_meme_emojis: List[UserMemeEmojis] = field(default_factory=list, metadata={'sa': relationship('UserMemeEmojis', back_populates='emoji')})


@mapper_registry.mapped
@dataclass
class Migrations:
    __tablename__ = 'migrations'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='PK_8c82d7f526340ab734260ea46be'),
    )
    __sa_dataclass_metadata_key__ = 'sa'

    id: int = field(init=False, metadata={'sa': Column(Integer)})
    timestamp: int = field(metadata={'sa': Column(BigInteger, nullable=False)})
    name: str = field(metadata={'sa': Column(String, nullable=False)})


@mapper_registry.mapped
@dataclass
class Redditors:
    __tablename__ = 'redditors'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='PK_061583869ba792c2095b65c671f'),
        UniqueConstraint('username', name='UQ_12ea821277fb068de87556497b0')
    )
    __sa_dataclass_metadata_key__ = 'sa'

    id: Any = field(metadata={'sa': Column(UUID)})
    username: str = field(metadata={'sa': Column(String(20), nullable=False)})

    reddit_memes: List[RedditMemes] = field(default_factory=list, metadata={'sa': relationship('RedditMemes', back_populates='redditor')})
    reddit_scores: List[RedditScores] = field(default_factory=list, metadata={'sa': relationship('RedditScores', back_populates='redditor')})


@mapper_registry.mapped
@dataclass
class Seasons:
    __tablename__ = 'seasons'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='PK_cb8ed53b5fe109dcd4a4449ec9d'),
    )
    __sa_dataclass_metadata_key__ = 'sa'

    id: int = field(init=False, metadata={'sa': Column(Integer)})

    good_boy_points: List[GoodBoyPoints] = field(default_factory=list, metadata={'sa': relationship('GoodBoyPoints', back_populates='season')})
    reddit_bets: List[RedditBets] = field(default_factory=list, metadata={'sa': relationship('RedditBets', back_populates='season')})


@mapper_registry.mapped
@dataclass
class Templates:
    __tablename__ = 'templates'
    __table_args__ = (
        PrimaryKeyConstraint('name', name='PK_5624219dd33b4644599d4d4b231'),
    )
    __sa_dataclass_metadata_key__ = 'sa'

    name: str = field(metadata={'sa': Column(String)})
    page: str = field(metadata={'sa': Column(String, nullable=False)})
    url: str = field(metadata={'sa': Column(String, nullable=False)})
    imgflip_name: str = field(metadata={'sa': Column(String, nullable=False)})
    num_images: Optional[int] = field(default=None, metadata={'sa': Column(Integer)})

    memes: List[Memes] = field(default_factory=list, metadata={'sa': relationship('Memes', back_populates='templates')})
    reddit_memes: List[RedditMemes] = field(default_factory=list, metadata={'sa': relationship('RedditMemes', back_populates='templates')})
    template_predictions: List[TemplatePredictions] = field(default_factory=list,
                                                            metadata={'sa': relationship('TemplatePredictions', back_populates='templates')})


t_typeorm_metadata = Table(
    'typeorm_metadata', metadata,
    Column('type', String, nullable=False),
    Column('database', String),
    Column('schema', String),
    Column('table', String),
    Column('name', String),
    Column('value', Text)
)


@mapper_registry.mapped
@dataclass
class Users:
    __tablename__ = 'users'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='PK_a3ffb1c0c8416b9fc6f907b7433'),
        UniqueConstraint('email', name='UQ_97672ac88f789774dd47f7c8be3'),
        UniqueConstraint('username', name='UQ_fe0bb3f6520ee0469504521e710')
    )
    __sa_dataclass_metadata_key__ = 'sa'

    id: Any = field(metadata={'sa': Column(UUID)})
    roles: list = field(metadata={'sa': Column(ARRAY(Enum('Amin', 'Hive', 'Og', 'Mod', 'Auditor', name='users_roles_enum',
                        _create_events=False)), nullable=False, server_default=_text("'{}'::users_roles_enum[]"))})
    username: str = field(metadata={'sa': Column(String, nullable=False)})
    last_login: datetime = field(metadata={'sa': Column(DateTime, nullable=False, server_default=_text('now()'))})
    email_verified: bool = field(metadata={'sa': Column(Boolean, nullable=False, server_default=_text('false'))})
    paid_services: list = field(metadata={'sa': Column(ARRAY(Enum('Pro', name='users_paid_services_enum', _create_events=False)),
                                nullable=False, server_default=_text("'{}'::users_paid_services_enum[]"))})
    created_at: datetime = field(metadata={'sa': Column(DateTime(True), nullable=False, server_default=_text('now()'))})
    avatar: Optional[str] = field(default=None, metadata={'sa': Column(String)})
    email: Optional[str] = field(default=None, metadata={'sa': Column(String)})
    password: Optional[str] = field(default=None, metadata={'sa': Column(String)})
    updated_at: Optional[datetime] = field(default=None, metadata={'sa': Column(DateTime(True), server_default=_text('now()'))})
    deleted_at: Optional[datetime] = field(default=None, metadata={'sa': Column(DateTime(True))})

    good_boy_points: List[GoodBoyPoints] = field(default_factory=list, metadata={'sa': relationship('GoodBoyPoints', back_populates='user')})
    memes: List[Memes] = field(default_factory=list, metadata={'sa': relationship('Memes', back_populates='user')})
    notifications: List[Notifications] = field(default_factory=list, metadata={'sa': relationship('Notifications', back_populates='user')})
    comments: List[Comments] = field(default_factory=list, metadata={'sa': relationship('Comments', back_populates='user')})
    meme_votes: List[MemeVotes] = field(default_factory=list, metadata={'sa': relationship('MemeVotes', back_populates='user')})
    reddit_bets: List[RedditBets] = field(default_factory=list, metadata={'sa': relationship('RedditBets', back_populates='user')})
    user_meme_emojis: List[UserMemeEmojis] = field(default_factory=list, metadata={'sa': relationship('UserMemeEmojis', back_populates='user')})
    comment_votes: List[CommentVotes] = field(default_factory=list, metadata={'sa': relationship('CommentVotes', back_populates='user')})
    template_prediction_audits: List[TemplatePredictionAudits] = field(default_factory=list,
                                                                       metadata={'sa': relationship('TemplatePredictionAudits', back_populates='user')})


@mapper_registry.mapped
@dataclass
class GoodBoyPoints:
    __tablename__ = 'good_boy_points'
    __table_args__ = (
        ForeignKeyConstraint(['season_id'], ['seasons.id'], ondelete='CASCADE', name='FK_0f5e81e95ee95195c8fb180a7c7'),
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='FK_d2ed6d7a78b837259613213daee'),
        PrimaryKeyConstraint('season_id', 'user_id', name='PK_8cf5a90a6f26bb98214c4a4839a')
    )
    __sa_dataclass_metadata_key__ = 'sa'

    amount: int = field(metadata={'sa': Column(Integer, nullable=False, server_default=_text('100'))})
    season_id: int = field(metadata={'sa': Column(ForeignKey('seasons.id', ondelete='CASCADE'), nullable=False)})
    user_id: Any = field(metadata={'sa': Column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)})

    season: Optional[Seasons] = field(default=None, metadata={'sa': relationship('Seasons', back_populates='good_boy_points')})
    user: Optional[Users] = field(default=None, metadata={'sa': relationship('Users', back_populates='good_boy_points')})


@mapper_registry.mapped
@dataclass
class Memes:
    __tablename__ = 'memes'
    __table_args__ = (
        ForeignKeyConstraint(['template_name'], ['templates.name'], ondelete='CASCADE', name='FK_20b6d99f8f26e47f7a196b6194f'),
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='FK_c698d9cd6bae1726f90d1af4844'),
        PrimaryKeyConstraint('id', name='PK_12846fb6620e0a6a8ff699db4fa')
    )
    __sa_dataclass_metadata_key__ = 'sa'

    id: Any = field(metadata={'sa': Column(UUID)})
    idx: int = field(metadata={'sa': Column(Integer, nullable=False)})
    is_hive: bool = field(metadata={'sa': Column(Boolean, nullable=False, server_default=_text('false'))})
    bucket: str = field(metadata={'sa': Column(String, nullable=False, server_default=_text("'memehub-development'::character varying"))})
    bucket_folder: str = field(metadata={'sa': Column(String, nullable=False)})
    hash: str = field(metadata={'sa': Column(String, nullable=False)})
    ext: str = field(metadata={'sa': Column(String, nullable=False)})
    is_dev: bool = field(metadata={'sa': Column(Boolean, nullable=False, server_default=_text('false'))})
    num_comments: int = field(metadata={'sa': Column(Integer, nullable=False, server_default=_text('0'))})
    ups: int = field(metadata={'sa': Column(Integer, nullable=False, server_default=_text('0'))})
    downs: int = field(metadata={'sa': Column(Integer, nullable=False, server_default=_text('0'))})
    ratio: float = field(metadata={'sa': Column(Float(53), nullable=False, server_default=_text("'1'::double precision"))})
    user_id: Any = field(metadata={'sa': Column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)})
    created_at: datetime = field(metadata={'sa': Column(DateTime(True), nullable=False, server_default=_text('now()'))})
    title: Optional[str] = field(default=None, metadata={'sa': Column(String)})
    image_error: Optional[str] = field(default=None, metadata={'sa': Column(
        Enum('IsDeleted', 'Malformed', 'NoImage', 'Connection', 'Unidentified', 'Unknown', name='ImageError'))})
    template_name: Optional[str] = field(default=None, metadata={'sa': Column(ForeignKey('templates.name', ondelete='CASCADE'))})
    deleted_at: Optional[datetime] = field(default=None, metadata={'sa': Column(DateTime(True))})
    updated_at: Optional[datetime] = field(default=None, metadata={'sa': Column(DateTime(True), server_default=_text('now()'))})

    templates: Optional[Templates] = field(default=None, metadata={'sa': relationship('Templates', back_populates='memes')})
    user: Optional[Users] = field(default=None, metadata={'sa': relationship('Users', back_populates='memes')})
    comments: List[Comments] = field(default_factory=list, metadata={'sa': relationship('Comments', back_populates='meme')})
    meme_votes: List[MemeVotes] = field(default_factory=list, metadata={'sa': relationship('MemeVotes', back_populates='meme')})
    template_predictions: List[TemplatePredictions] = field(default_factory=list, metadata={'sa': relationship('TemplatePredictions', back_populates='meme')})
    user_meme_emojis: List[UserMemeEmojis] = field(default_factory=list, metadata={'sa': relationship('UserMemeEmojis', back_populates='meme')})


@mapper_registry.mapped
@dataclass
class Notifications:
    __tablename__ = 'notifications'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='FK_9a8a82462cab47c73d25f49261f'),
        PrimaryKeyConstraint('id', name='PK_6a72c3c0f683f6462415e653c3a')
    )
    __sa_dataclass_metadata_key__ = 'sa'

    id: Any = field(metadata={'sa': Column(UUID)})
    topic: str = field(metadata={'sa': Column(Enum('MemeVote', 'CommentVote', 'Comment', name='notifications_topic_enum'), nullable=False)})
    metadata_: dict = field(metadata={'sa': Column('metadata', JSONB, nullable=False)})
    read: bool = field(metadata={'sa': Column(Boolean, nullable=False, server_default=_text('false'))})
    user_id: Any = field(metadata={'sa': Column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)})
    created_at: datetime = field(metadata={'sa': Column(DateTime(True), nullable=False, server_default=_text('now()'))})
    updated_at: Optional[datetime] = field(default=None, metadata={'sa': Column(DateTime(True), server_default=_text('now()'))})
    deleted_at: Optional[datetime] = field(default=None, metadata={'sa': Column(DateTime(True))})

    user: Optional[Users] = field(default=None, metadata={'sa': relationship('Users', back_populates='notifications')})


@mapper_registry.mapped
@dataclass
class RedditMemes:
    __tablename__ = 'reddit_memes'
    __table_args__ = (
        ForeignKeyConstraint(['redditor_id'], ['redditors.id'], ondelete='CASCADE', name='FK_a270a3212df747ae19cb09d1be9'),
        ForeignKeyConstraint(['template_name'], ['templates.name'], ondelete='CASCADE', name='FK_0634017e6f2351824f6db59ba4e'),
        PrimaryKeyConstraint('id', name='PK_1ae085193dc492081d372e0299c'),
        UniqueConstraint('url', name='UQ_80fc13a6facb2e40853bc5ce717')
    )
    __sa_dataclass_metadata_key__ = 'sa'

    id: Any = field(metadata={'sa': Column(UUID)})
    idx: int = field(metadata={'sa': Column(Integer, nullable=False)})
    username: str = field(metadata={'sa': Column(String, nullable=False)})
    reddit_id: str = field(metadata={'sa': Column(String, nullable=False)})
    subreddit: str = field(metadata={'sa': Column(String, nullable=False)})
    title: str = field(metadata={'sa': Column(String, nullable=False)})
    url: str = field(metadata={'sa': Column(String, nullable=False)})
    timestamp: int = field(metadata={'sa': Column(Integer, nullable=False)})
    upvote_ratio: float = field(metadata={'sa': Column(Float(53), nullable=False)})
    upvotes: int = field(metadata={'sa': Column(Integer, nullable=False)})
    downvotes: int = field(metadata={'sa': Column(Integer, nullable=False)})
    num_comments: int = field(metadata={'sa': Column(Integer, nullable=False)})
    created_at: datetime = field(metadata={'sa': Column(DateTime(True), nullable=False, server_default=_text('now()'))})
    meme_text: Optional[str] = field(default=None, metadata={'sa': Column(String)})
    percentile: Optional[float] = field(default=None, metadata={'sa': Column(Float(53))})
    image_error: Optional[str] = field(default=None, metadata={'sa': Column(
        Enum('IsDeleted', 'Malformed', 'NoImage', 'Connection', 'Unidentified', 'Unknown', name='ImageError'))})
    redditor_id: Optional[Any] = field(default=None, metadata={'sa': Column(ForeignKey('redditors.id', ondelete='CASCADE'))})
    template_name: Optional[str] = field(default=None, metadata={'sa': Column(ForeignKey('templates.name', ondelete='CASCADE'))})
    updated_at: Optional[datetime] = field(default=None, metadata={'sa': Column(DateTime(True), server_default=_text('now()'))})
    deleted_at: Optional[datetime] = field(default=None, metadata={'sa': Column(DateTime(True))})

    redditor: Optional[Redditors] = field(default=None, metadata={'sa': relationship('Redditors', back_populates='reddit_memes')})
    templates: Optional[Templates] = field(default=None, metadata={'sa': relationship('Templates', back_populates='reddit_memes')})
    reddit_bets: List[RedditBets] = field(default_factory=list, metadata={'sa': relationship('RedditBets', back_populates='reddit_meme')})
    template_predictions: List[TemplatePredictions] = field(default_factory=list,
                                                            metadata={'sa': relationship('TemplatePredictions', back_populates='reddit_meme')})


@mapper_registry.mapped
@dataclass
class RedditScores:
    __tablename__ = 'reddit_scores'
    __table_args__ = (
        ForeignKeyConstraint(['redditor_id'], ['redditors.id'], ondelete='CASCADE', name='FK_adcc81afcb5f0b2c57e6ca18a10'),
        PrimaryKeyConstraint('id', name='PK_6ee18c3e5f54447fff6721e5b91')
    )
    __sa_dataclass_metadata_key__ = 'sa'

    id: Any = field(metadata={'sa': Column(UUID)})
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
    redditor_id: Optional[Any] = field(default=None, metadata={'sa': Column(ForeignKey('redditors.id', ondelete='CASCADE'))})

    redditor: Optional[Redditors] = field(default=None, metadata={'sa': relationship('Redditors', back_populates='reddit_scores')})


@mapper_registry.mapped
@dataclass
class Comments:
    __tablename__ = 'comments'
    __table_args__ = (
        ForeignKeyConstraint(['meme_id'], ['memes.id'], ondelete='CASCADE', name='FK_8f3a6a35e7aa671c66636cca35f'),
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='FK_4c675567d2a58f0b07cef09c13d'),
        PrimaryKeyConstraint('id', name='PK_8bf68bc960f2b69e818bdb90dcb')
    )
    __sa_dataclass_metadata_key__ = 'sa'

    id: Any = field(metadata={'sa': Column(UUID)})
    text: str = field(metadata={'sa': Column(String, nullable=False)})
    is_hive: bool = field(metadata={'sa': Column(Boolean, nullable=False, server_default=_text('false'))})
    user_id: Any = field(metadata={'sa': Column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)})
    meme_id: Any = field(metadata={'sa': Column(ForeignKey('memes.id', ondelete='CASCADE'), nullable=False)})
    ups: int = field(metadata={'sa': Column(Integer, nullable=False, server_default=_text('0'))})
    downs: int = field(metadata={'sa': Column(Integer, nullable=False, server_default=_text('0'))})
    ratio: float = field(metadata={'sa': Column(Float(53), nullable=False, server_default=_text("'1'::double precision"))})
    created_at: datetime = field(metadata={'sa': Column(DateTime(True), nullable=False, server_default=_text('now()'))})
    permlink: Optional[str] = field(default=None, metadata={'sa': Column(String)})
    deleted_at: Optional[datetime] = field(default=None, metadata={'sa': Column(DateTime(True))})
    updated_at: Optional[datetime] = field(default=None, metadata={'sa': Column(DateTime(True), server_default=_text('now()'))})

    meme: Optional[Memes] = field(default=None, metadata={'sa': relationship('Memes', back_populates='comments')})
    user: Optional[Users] = field(default=None, metadata={'sa': relationship('Users', back_populates='comments')})
    comment_votes: List[CommentVotes] = field(default_factory=list, metadata={'sa': relationship('CommentVotes', back_populates='comment')})


@mapper_registry.mapped
@dataclass
class MemeVotes:
    __tablename__ = 'meme_votes'
    __table_args__ = (
        ForeignKeyConstraint(['meme_id'], ['memes.id'], ondelete='CASCADE', name='FK_1c753aeebeef161406fa54dd9f8'),
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='FK_e189c768c54d5c6149cc11d4a7f'),
        PrimaryKeyConstraint('meme_id', 'user_id', name='PK_12153b440464555c8b47fd8d979')
    )
    __sa_dataclass_metadata_key__ = 'sa'

    meme_id: Any = field(metadata={'sa': Column(ForeignKey('memes.id', ondelete='CASCADE'), nullable=False)})
    user_id: Any = field(metadata={'sa': Column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)})
    upvote: bool = field(metadata={'sa': Column(Boolean, nullable=False)})
    created_at: datetime = field(metadata={'sa': Column(DateTime(True), nullable=False, server_default=_text('now()'))})

    meme: Optional[Memes] = field(default=None, metadata={'sa': relationship('Memes', back_populates='meme_votes')})
    user: Optional[Users] = field(default=None, metadata={'sa': relationship('Users', back_populates='meme_votes')})


@mapper_registry.mapped
@dataclass
class RedditBets:
    __tablename__ = 'reddit_bets'
    __table_args__ = (
        ForeignKeyConstraint(['reddit_meme_id'], ['reddit_memes.id'], ondelete='CASCADE', name='FK_26a6a9ec8b2c14a1c39d472d995'),
        ForeignKeyConstraint(['season_id'], ['seasons.id'], ondelete='CASCADE', name='FK_729ff002c468787d968de7261c1'),
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='FK_e2cfb2caed31fce82673b5c7bc7'),
        PrimaryKeyConstraint('id', name='PK_18a00df96371cfa8c88d0e1fff0')
    )
    __sa_dataclass_metadata_key__ = 'sa'

    id: Any = field(metadata={'sa': Column(UUID)})
    reddit_meme_id: Any = field(metadata={'sa': Column(ForeignKey('reddit_memes.id', ondelete='CASCADE'), nullable=False)})
    side: str = field(metadata={'sa': Column(Enum('Buy', 'Sell', name='reddit_bets_side_enum'), nullable=False)})
    bet_size: int = field(metadata={'sa': Column(Integer, nullable=False)})
    percentile: float = field(metadata={'sa': Column(Float(53), nullable=False)})
    profit_loss: int = field(metadata={'sa': Column(Integer, nullable=False)})
    is_yolo: bool = field(metadata={'sa': Column(Boolean, nullable=False)})
    user_id: Any = field(metadata={'sa': Column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)})
    season_id: int = field(metadata={'sa': Column(ForeignKey('seasons.id', ondelete='CASCADE'), nullable=False)})
    created_at: datetime = field(metadata={'sa': Column(DateTime(True), nullable=False, server_default=_text('now()'))})
    target: Optional[float] = field(default=None, metadata={'sa': Column(Float(53))})
    updated_at: Optional[datetime] = field(default=None, metadata={'sa': Column(DateTime(True), server_default=_text('now()'))})
    deleted_at: Optional[datetime] = field(default=None, metadata={'sa': Column(DateTime(True))})

    reddit_meme: Optional[RedditMemes] = field(default=None, metadata={'sa': relationship('RedditMemes', back_populates='reddit_bets')})
    season: Optional[Seasons] = field(default=None, metadata={'sa': relationship('Seasons', back_populates='reddit_bets')})
    user: Optional[Users] = field(default=None, metadata={'sa': relationship('Users', back_populates='reddit_bets')})


@mapper_registry.mapped
@dataclass
class TemplatePredictions:
    __tablename__ = 'template_predictions'
    __table_args__ = (
        ForeignKeyConstraint(['meme_id'], ['memes.id'], ondelete='CASCADE', name='FK_388aaeb9309f64e660e60076c60'),
        ForeignKeyConstraint(['reddit_meme_id'], ['reddit_memes.id'], ondelete='CASCADE', name='FK_4532ed3262f878d1a7d704fd9d7'),
        ForeignKeyConstraint(['template_name'], ['templates.name'], ondelete='CASCADE', name='FK_05d8cde523861e5a62a50e8dca6'),
        PrimaryKeyConstraint('id', name='PK_fcb34b1c845aaf6ca6f54f6e138')
    )
    __sa_dataclass_metadata_key__ = 'sa'

    id: int = field(init=False, metadata={'sa': Column(Integer)})
    version: str = field(metadata={'sa': Column(String, nullable=False)})
    not_meme: bool = field(metadata={'sa': Column(Boolean, nullable=False, server_default=_text('false'))})
    not_template: bool = field(metadata={'sa': Column(Boolean, nullable=False, server_default=_text('false'))})
    meme_id: Optional[Any] = field(default=None, metadata={'sa': Column(ForeignKey('memes.id', ondelete='CASCADE'))})
    reddit_meme_id: Optional[Any] = field(default=None, metadata={'sa': Column(ForeignKey('reddit_memes.id', ondelete='CASCADE'))})
    template_name: Optional[str] = field(default=None, metadata={'sa': Column(ForeignKey('templates.name', ondelete='CASCADE'))})
    correct: Optional[bool] = field(default=None, metadata={'sa': Column(Boolean)})

    meme: Optional[Memes] = field(default=None, metadata={'sa': relationship('Memes', back_populates='template_predictions')})
    reddit_meme: Optional[RedditMemes] = field(default=None, metadata={'sa': relationship('RedditMemes', back_populates='template_predictions')})
    templates: Optional[Templates] = field(default=None, metadata={'sa': relationship('Templates', back_populates='template_predictions')})
    template_prediction_audits: List[TemplatePredictionAudits] = field(
        default_factory=list, metadata={'sa': relationship('TemplatePredictionAudits', back_populates='template_prediction')})


@mapper_registry.mapped
@dataclass
class UserMemeEmojis:
    __tablename__ = 'user_meme_emojis'
    __table_args__ = (
        ForeignKeyConstraint(['emoji_id'], ['emojis.id'], ondelete='CASCADE', name='FK_c4ef77d699a823062a410780944'),
        ForeignKeyConstraint(['meme_id'], ['memes.id'], ondelete='CASCADE', name='FK_50008851d377026989d01b961ab'),
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='FK_266ed5f9d84f42ad99059ec9662'),
        PrimaryKeyConstraint('id', name='PK_315c0b261bcdfb77d1386c51f45')
    )
    __sa_dataclass_metadata_key__ = 'sa'

    id: Any = field(metadata={'sa': Column(UUID)})
    user_id: Any = field(metadata={'sa': Column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)})
    meme_id: Any = field(metadata={'sa': Column(ForeignKey('memes.id', ondelete='CASCADE'), nullable=False)})
    emoji_id: Any = field(metadata={'sa': Column(ForeignKey('emojis.id', ondelete='CASCADE'), nullable=False)})
    created_at: datetime = field(metadata={'sa': Column(DateTime(True), nullable=False, server_default=_text('now()'))})
    updated_at: Optional[datetime] = field(default=None, metadata={'sa': Column(DateTime(True), server_default=_text('now()'))})
    deleted_at: Optional[datetime] = field(default=None, metadata={'sa': Column(DateTime(True))})

    emoji: Optional[Emojis] = field(default=None, metadata={'sa': relationship('Emojis', back_populates='user_meme_emojis')})
    meme: Optional[Memes] = field(default=None, metadata={'sa': relationship('Memes', back_populates='user_meme_emojis')})
    user: Optional[Users] = field(default=None, metadata={'sa': relationship('Users', back_populates='user_meme_emojis')})


@mapper_registry.mapped
@dataclass
class CommentVotes:
    __tablename__ = 'comment_votes'
    __table_args__ = (
        ForeignKeyConstraint(['comment_id'], ['comments.id'], ondelete='CASCADE', name='FK_1b41b98c56a06654513bffc1274'),
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='FK_bc20ac5a0c8715d3e99e5dc6793'),
        PrimaryKeyConstraint('user_id', 'comment_id', name='PK_134f68c8e62163194eb6cd95632')
    )
    __sa_dataclass_metadata_key__ = 'sa'

    user_id: Any = field(metadata={'sa': Column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)})
    comment_id: Any = field(metadata={'sa': Column(ForeignKey('comments.id', ondelete='CASCADE'), nullable=False)})
    upvote: bool = field(metadata={'sa': Column(Boolean, nullable=False)})
    created_at: datetime = field(metadata={'sa': Column(DateTime(True), nullable=False, server_default=_text('now()'))})

    comment: Optional[Comments] = field(default=None, metadata={'sa': relationship('Comments', back_populates='comment_votes')})
    user: Optional[Users] = field(default=None, metadata={'sa': relationship('Users', back_populates='comment_votes')})



@mapper_registry.mapped
@dataclass
class TemplatePredictionAudits:
    __tablename__ = 'template_prediction_audits'
    __table_args__ = (
        ForeignKeyConstraint(['template_prediction_id'], ['template_predictions.id'], ondelete='CASCADE', name='FK_e9d11ed35d8d34811e27098db4e'),
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='FK_cc591ea6494a5b5c1d1a1513433'),
        PrimaryKeyConstraint('id', name='PK_5eeaa1c988a3a9b220aa986e6a2')
    )
    __sa_dataclass_metadata_key__ = 'sa'

    id: int = field(init=False, metadata={'sa': Column(Integer)})
    template_prediction_id: int = field(metadata={'sa': Column(ForeignKey('template_predictions.id', ondelete='CASCADE'), nullable=False)})
    user_id: Any = field(metadata={'sa': Column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)})
    meme_clf_correct: Optional[bool] = field(default=None, metadata={'sa': Column(Boolean)})
    audit_error: Optional[str] = field(default=None, metadata={'sa': Column(Enum('IsDeleted', name='template_prediction_audits_audit_error_enum'))})

    template_prediction: Optional[TemplatePredictions] = field(default=None,
                                                               metadata={'sa': relationship('TemplatePredictions', back_populates='template_prediction_audits')})
    user: Optional[Users] = field(default=None, metadata={'sa': relationship('Users', back_populates='template_prediction_audits')})
