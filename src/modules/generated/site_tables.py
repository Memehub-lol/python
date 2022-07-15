from sqlalchemy import (ARRAY, BigInteger, Boolean, Column, DateTime, Enum,
                        Float, ForeignKey, ForeignKeyConstraint, Integer,
                        PrimaryKeyConstraint, String, Table, Text,
                        UniqueConstraint)
from sqlalchemy import text as _text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()
metadata = Base.metadata


class Emojis(Base):
    __tablename__ = 'emojis'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='PK_9adb96a675f555c6169bad7ba62'),
    )

    id = Column(UUID)
    name = Column(String, nullable=False)
    bucket = Column(String, nullable=False, server_default=_text("'memehub-development'::character varying"))
    bucket_folder = Column(String, nullable=False)
    ext = Column(String, nullable=False)
    is_dev = Column(Boolean, nullable=False, server_default=_text('false'))
    created_at = Column(DateTime(True), nullable=False, server_default=_text('now()'))
    updated_at = Column(DateTime(True), server_default=_text('now()'))
    deleted_at = Column(DateTime(True))

    user_meme_emojis = relationship('UserMemeEmojis', back_populates='emoji')


class Migrations(Base):
    __tablename__ = 'migrations'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='PK_8c82d7f526340ab734260ea46be'),
    )

    id = Column(Integer)
    timestamp = Column(BigInteger, nullable=False)
    name = Column(String, nullable=False)


class Redditors(Base):
    __tablename__ = 'redditors'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='PK_061583869ba792c2095b65c671f'),
        UniqueConstraint('username', name='UQ_12ea821277fb068de87556497b0')
    )

    id = Column(UUID)
    username = Column(String(20), nullable=False)

    reddit_memes = relationship('RedditMemes', back_populates='redditor')
    reddit_scores = relationship('RedditScores', back_populates='redditor')


class Seasons(Base):
    __tablename__ = 'seasons'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='PK_cb8ed53b5fe109dcd4a4449ec9d'),
    )

    id = Column(Integer)

    good_boy_points = relationship('GoodBoyPoints', back_populates='season')
    reddit_bets = relationship('RedditBets', back_populates='season')


class Templates(Base):
    __tablename__ = 'templates'
    __table_args__ = (
        PrimaryKeyConstraint('name', name='PK_5624219dd33b4644599d4d4b231'),
    )

    name = Column(String)
    page = Column(String, nullable=False)
    url = Column(String, nullable=False)
    imgflip_name = Column(String, nullable=False)
    num_images = Column(Integer)

    memes = relationship('Memes', back_populates='templates')
    reddit_memes = relationship('RedditMemes', back_populates='templates')
    template_predictions = relationship('TemplatePredictions', back_populates='templates')


t_typeorm_metadata = Table(
    'typeorm_metadata', metadata,
    Column('type', String, nullable=False),
    Column('database', String),
    Column('schema', String),
    Column('table', String),
    Column('name', String),
    Column('value', Text)
)


class Users(Base):
    __tablename__ = 'users'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='PK_a3ffb1c0c8416b9fc6f907b7433'),
        UniqueConstraint('email', name='UQ_97672ac88f789774dd47f7c8be3'),
        UniqueConstraint('username', name='UQ_fe0bb3f6520ee0469504521e710')
    )

    id = Column(UUID)
    roles = Column(ARRAY(Enum('Amin', 'Hive', 'Og', 'Mod', 'Auditor', name='users_roles_enum', _create_events=False)),
                   nullable=False, server_default=_text("'{}'::users_roles_enum[]"))
    username = Column(String, nullable=False)
    last_login = Column(DateTime, nullable=False, server_default=_text('now()'))
    email_verified = Column(Boolean, nullable=False, server_default=_text('false'))
    paid_services = Column(ARRAY(Enum('Pro', name='users_paid_services_enum', _create_events=False)),
                           nullable=False, server_default=_text("'{}'::users_paid_services_enum[]"))
    created_at = Column(DateTime(True), nullable=False, server_default=_text('now()'))
    avatar = Column(String)
    email = Column(String)
    password = Column(String)
    updated_at = Column(DateTime(True), server_default=_text('now()'))
    deleted_at = Column(DateTime(True))

    good_boy_points = relationship('GoodBoyPoints', back_populates='user')
    memes = relationship('Memes', back_populates='user')
    notifications = relationship('Notifications', back_populates='user')
    comments = relationship('Comments', back_populates='user')
    meme_votes = relationship('MemeVotes', back_populates='user')
    reddit_bets = relationship('RedditBets', back_populates='user')
    user_meme_emojis = relationship('UserMemeEmojis', back_populates='user')
    comment_votes = relationship('CommentVotes', back_populates='user')
    flags = relationship('Flags', foreign_keys='[Flags.flagger_id]', back_populates='flagger')
    flags_ = relationship('Flags', foreign_keys='[Flags.reviewer_id]', back_populates='reviewer')
    template_prediction_audits = relationship('TemplatePredictionAudits', back_populates='user')


class GoodBoyPoints(Base):
    __tablename__ = 'good_boy_points'
    __table_args__ = (
        ForeignKeyConstraint(['season_id'], ['seasons.id'], ondelete='CASCADE', name='FK_0f5e81e95ee95195c8fb180a7c7'),
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='FK_d2ed6d7a78b837259613213daee'),
        PrimaryKeyConstraint('season_id', 'user_id', name='PK_8cf5a90a6f26bb98214c4a4839a')
    )

    amount = Column(Integer, nullable=False, server_default=_text('100'))
    season_id = Column(ForeignKey('seasons.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    season = relationship('Seasons', back_populates='good_boy_points')
    user = relationship('Users', back_populates='good_boy_points')


class Memes(Base):
    __tablename__ = 'memes'
    __table_args__ = (
        ForeignKeyConstraint(['template_name'], ['templates.name'], ondelete='CASCADE', name='FK_20b6d99f8f26e47f7a196b6194f'),
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='FK_c698d9cd6bae1726f90d1af4844'),
        PrimaryKeyConstraint('id', name='PK_12846fb6620e0a6a8ff699db4fa')
    )

    id = Column(UUID)
    idx = Column(Integer, nullable=False)
    is_hive = Column(Boolean, nullable=False, server_default=_text('false'))
    bucket = Column(String, nullable=False, server_default=_text("'memehub-development'::character varying"))
    bucket_folder = Column(String, nullable=False)
    hash = Column(String, nullable=False)
    ext = Column(String, nullable=False)
    is_dev = Column(Boolean, nullable=False, server_default=_text('false'))
    num_comments = Column(Integer, nullable=False, server_default=_text('0'))
    ups = Column(Integer, nullable=False, server_default=_text('0'))
    downs = Column(Integer, nullable=False, server_default=_text('0'))
    ratio = Column(Float(53), nullable=False, server_default=_text("'1'::double precision"))
    user_id = Column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(DateTime(True), nullable=False, server_default=_text('now()'))
    title = Column(String)
    image_error = Column(Enum('IsDeleted', 'Malformed', 'NoImage', 'Connection', 'Unidentified', 'Unknown', name='ImageError'))
    template_name = Column(ForeignKey('templates.name', ondelete='CASCADE'))
    deleted_at = Column(DateTime(True))
    updated_at = Column(DateTime(True), server_default=_text('now()'))

    templates = relationship('Templates', back_populates='memes')
    user = relationship('Users', back_populates='memes')
    comments = relationship('Comments', back_populates='meme')
    meme_votes = relationship('MemeVotes', back_populates='meme')
    template_predictions = relationship('TemplatePredictions', back_populates='meme')
    user_meme_emojis = relationship('UserMemeEmojis', back_populates='meme')
    flags = relationship('Flags', back_populates='meme')


class Notifications(Base):
    __tablename__ = 'notifications'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='FK_9a8a82462cab47c73d25f49261f'),
        PrimaryKeyConstraint('id', name='PK_6a72c3c0f683f6462415e653c3a')
    )

    id = Column(UUID)
    topic = Column(Enum('MemeVote', 'CommentVote', 'Comment', name='notifications_topic_enum'), nullable=False)
    metadata_ = Column('metadata', JSONB, nullable=False)
    read = Column(Boolean, nullable=False, server_default=_text('false'))
    user_id = Column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(DateTime(True), nullable=False, server_default=_text('now()'))
    updated_at = Column(DateTime(True), server_default=_text('now()'))
    deleted_at = Column(DateTime(True))

    user = relationship('Users', back_populates='notifications')


class RedditMemes(Base):
    __tablename__ = 'reddit_memes'
    __table_args__ = (
        ForeignKeyConstraint(['redditor_id'], ['redditors.id'], ondelete='CASCADE', name='FK_a270a3212df747ae19cb09d1be9'),
        ForeignKeyConstraint(['template_name'], ['templates.name'], ondelete='CASCADE', name='FK_0634017e6f2351824f6db59ba4e'),
        PrimaryKeyConstraint('id', name='PK_1ae085193dc492081d372e0299c'),
        UniqueConstraint('url', name='UQ_80fc13a6facb2e40853bc5ce717')
    )

    id = Column(UUID)
    idx = Column(Integer, nullable=False)
    username = Column(String, nullable=False)
    reddit_id = Column(String, nullable=False)
    subreddit = Column(String, nullable=False)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    timestamp = Column(Integer, nullable=False)
    upvote_ratio = Column(Float(53), nullable=False)
    upvotes = Column(Integer, nullable=False)
    downvotes = Column(Integer, nullable=False)
    num_comments = Column(Integer, nullable=False)
    created_at = Column(DateTime(True), nullable=False, server_default=_text('now()'))
    meme_text = Column(String)
    percentile = Column(Float(53))
    image_error = Column(Enum('IsDeleted', 'Malformed', 'NoImage', 'Connection', 'Unidentified', 'Unknown', name='ImageError'))
    redditor_id = Column(ForeignKey('redditors.id', ondelete='CASCADE'))
    template_name = Column(ForeignKey('templates.name', ondelete='CASCADE'))
    updated_at = Column(DateTime(True), server_default=_text('now()'))
    deleted_at = Column(DateTime(True))

    redditor = relationship('Redditors', back_populates='reddit_memes')
    templates = relationship('Templates', back_populates='reddit_memes')
    reddit_bets = relationship('RedditBets', back_populates='reddit_meme')
    template_predictions = relationship('TemplatePredictions', back_populates='reddit_meme')


class RedditScores(Base):
    __tablename__ = 'reddit_scores'
    __table_args__ = (
        ForeignKeyConstraint(['redditor_id'], ['redditors.id'], ondelete='CASCADE', name='FK_adcc81afcb5f0b2c57e6ca18a10'),
        PrimaryKeyConstraint('id', name='PK_6ee18c3e5f54447fff6721e5b91')
    )

    id = Column(UUID)
    username = Column(String(20), nullable=False)
    subreddit = Column(String(50), nullable=False)
    time_delta = Column(Integer, nullable=False)
    timestamp = Column(Integer, nullable=False)
    datetime = Column(DateTime, nullable=False)
    final_score = Column(Float(53), nullable=False)
    raw_score = Column(Float(53), nullable=False)
    num_in_bottom = Column(Integer, nullable=False)
    num_in_top = Column(Integer, nullable=False)
    shitposter_index = Column(Float(53), nullable=False)
    highest_upvotes = Column(Integer, nullable=False)
    hu_score = Column(Float(53), nullable=False)
    lowest_ratio = Column(Float(53), nullable=False)
    redditor_id = Column(ForeignKey('redditors.id', ondelete='CASCADE'))

    redditor = relationship('Redditors', back_populates='reddit_scores')


class Comments(Base):
    __tablename__ = 'comments'
    __table_args__ = (
        ForeignKeyConstraint(['meme_id'], ['memes.id'], ondelete='CASCADE', name='FK_8f3a6a35e7aa671c66636cca35f'),
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='FK_4c675567d2a58f0b07cef09c13d'),
        PrimaryKeyConstraint('id', name='PK_8bf68bc960f2b69e818bdb90dcb')
    )

    id = Column(UUID)
    text = Column(String, nullable=False)
    is_hive = Column(Boolean, nullable=False, server_default=_text('false'))
    user_id = Column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    meme_id = Column(ForeignKey('memes.id', ondelete='CASCADE'), nullable=False)
    ups = Column(Integer, nullable=False, server_default=_text('0'))
    downs = Column(Integer, nullable=False, server_default=_text('0'))
    ratio = Column(Float(53), nullable=False, server_default=_text("'1'::double precision"))
    created_at = Column(DateTime(True), nullable=False, server_default=_text('now()'))
    permlink = Column(String)
    deleted_at = Column(DateTime(True))
    updated_at = Column(DateTime(True), server_default=_text('now()'))

    meme = relationship('Memes', back_populates='comments')
    user = relationship('Users', back_populates='comments')
    comment_votes = relationship('CommentVotes', back_populates='comment')
    flags = relationship('Flags', back_populates='comment')


class MemeVotes(Base):
    __tablename__ = 'meme_votes'
    __table_args__ = (
        ForeignKeyConstraint(['meme_id'], ['memes.id'], ondelete='CASCADE', name='FK_1c753aeebeef161406fa54dd9f8'),
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='FK_e189c768c54d5c6149cc11d4a7f'),
        PrimaryKeyConstraint('meme_id', 'user_id', name='PK_12153b440464555c8b47fd8d979')
    )

    meme_id = Column(ForeignKey('memes.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    upvote = Column(Boolean, nullable=False)
    created_at = Column(DateTime(True), nullable=False, server_default=_text('now()'))

    meme = relationship('Memes', back_populates='meme_votes')
    user = relationship('Users', back_populates='meme_votes')


class RedditBets(Base):
    __tablename__ = 'reddit_bets'
    __table_args__ = (
        ForeignKeyConstraint(['reddit_meme_id'], ['reddit_memes.id'], ondelete='CASCADE', name='FK_26a6a9ec8b2c14a1c39d472d995'),
        ForeignKeyConstraint(['season_id'], ['seasons.id'], ondelete='CASCADE', name='FK_729ff002c468787d968de7261c1'),
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='FK_e2cfb2caed31fce82673b5c7bc7'),
        PrimaryKeyConstraint('id', name='PK_18a00df96371cfa8c88d0e1fff0')
    )

    id = Column(UUID)
    reddit_meme_id = Column(ForeignKey('reddit_memes.id', ondelete='CASCADE'), nullable=False)
    side = Column(Enum('Buy', 'Sell', name='reddit_bets_side_enum'), nullable=False)
    bet_size = Column(Integer, nullable=False)
    percentile = Column(Float(53), nullable=False)
    profit_loss = Column(Integer, nullable=False)
    is_yolo = Column(Boolean, nullable=False)
    user_id = Column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    season_id = Column(ForeignKey('seasons.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(DateTime(True), nullable=False, server_default=_text('now()'))
    target = Column(Float(53))
    updated_at = Column(DateTime(True), server_default=_text('now()'))
    deleted_at = Column(DateTime(True))

    reddit_meme = relationship('RedditMemes', back_populates='reddit_bets')
    season = relationship('Seasons', back_populates='reddit_bets')
    user = relationship('Users', back_populates='reddit_bets')


class TemplatePredictions(Base):
    __tablename__ = 'template_predictions'
    __table_args__ = (
        ForeignKeyConstraint(['meme_id'], ['memes.id'], ondelete='CASCADE', name='FK_388aaeb9309f64e660e60076c60'),
        ForeignKeyConstraint(['reddit_meme_id'], ['reddit_memes.id'], ondelete='CASCADE', name='FK_4532ed3262f878d1a7d704fd9d7'),
        ForeignKeyConstraint(['template_name'], ['templates.name'], ondelete='CASCADE', name='FK_05d8cde523861e5a62a50e8dca6'),
        PrimaryKeyConstraint('id', name='PK_fcb34b1c845aaf6ca6f54f6e138')
    )

    id = Column(Integer)
    version = Column(String, nullable=False)
    not_meme = Column(Boolean, nullable=False, server_default=_text('false'))
    not_template = Column(Boolean, nullable=False, server_default=_text('false'))
    meme_id = Column(ForeignKey('memes.id', ondelete='CASCADE'))
    reddit_meme_id = Column(ForeignKey('reddit_memes.id', ondelete='CASCADE'))
    template_name = Column(ForeignKey('templates.name', ondelete='CASCADE'))
    correct = Column(Boolean)

    meme = relationship('Memes', back_populates='template_predictions')
    reddit_meme = relationship('RedditMemes', back_populates='template_predictions')
    templates = relationship('Templates', back_populates='template_predictions')
    template_prediction_audits = relationship('TemplatePredictionAudits', back_populates='template_prediction')


class UserMemeEmojis(Base):
    __tablename__ = 'user_meme_emojis'
    __table_args__ = (
        ForeignKeyConstraint(['emoji_id'], ['emojis.id'], ondelete='CASCADE', name='FK_c4ef77d699a823062a410780944'),
        ForeignKeyConstraint(['meme_id'], ['memes.id'], ondelete='CASCADE', name='FK_50008851d377026989d01b961ab'),
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='FK_266ed5f9d84f42ad99059ec9662'),
        PrimaryKeyConstraint('id', name='PK_315c0b261bcdfb77d1386c51f45')
    )

    id = Column(UUID)
    user_id = Column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    meme_id = Column(ForeignKey('memes.id', ondelete='CASCADE'), nullable=False)
    emoji_id = Column(ForeignKey('emojis.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(DateTime(True), nullable=False, server_default=_text('now()'))
    updated_at = Column(DateTime(True), server_default=_text('now()'))
    deleted_at = Column(DateTime(True))

    emoji = relationship('Emojis', back_populates='user_meme_emojis')
    meme = relationship('Memes', back_populates='user_meme_emojis')
    user = relationship('Users', back_populates='user_meme_emojis')


class CommentVotes(Base):
    __tablename__ = 'comment_votes'
    __table_args__ = (
        ForeignKeyConstraint(['comment_id'], ['comments.id'], ondelete='CASCADE', name='FK_1b41b98c56a06654513bffc1274'),
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='FK_bc20ac5a0c8715d3e99e5dc6793'),
        PrimaryKeyConstraint('user_id', 'comment_id', name='PK_134f68c8e62163194eb6cd95632')
    )

    user_id = Column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    comment_id = Column(ForeignKey('comments.id', ondelete='CASCADE'), nullable=False)
    upvote = Column(Boolean, nullable=False)
    created_at = Column(DateTime(True), nullable=False, server_default=_text('now()'))

    comment = relationship('Comments', back_populates='comment_votes')
    user = relationship('Users', back_populates='comment_votes')


class Flags(Base):
    __tablename__ = 'flags'
    __table_args__ = (
        ForeignKeyConstraint(['comment_id'], ['comments.id'], ondelete='CASCADE', name='FK_bb192feedb10393d7500f087af6'),
        ForeignKeyConstraint(['flagger_id'], ['users.id'], ondelete='CASCADE', name='FK_de975295f26e5588844615b0ca7'),
        ForeignKeyConstraint(['meme_id'], ['memes.id'], ondelete='CASCADE', name='FK_9bdb838c855bb52623c30cb23a8'),
        ForeignKeyConstraint(['reviewer_id'], ['users.id'], ondelete='CASCADE', name='FK_582ce2deca7af40717204251ced'),
        PrimaryKeyConstraint('id', name='PK_ea7e333c92a55de9e9b8d0b9afd')
    )

    id = Column(UUID)
    type = Column(Enum('Nsfw', 'Spam', 'Abuse', 'Repost', name='flags_type_enum'), nullable=False)
    flagger_id = Column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(DateTime(True), nullable=False, server_default=_text('now()'))
    flagger_comment = Column(String)
    status = Column(Enum('Reviewed', 'Confirmed', 'Ignored', 'Flagged', name='flags_status_enum'))
    reviewer_id = Column(ForeignKey('users.id', ondelete='CASCADE'))
    meme_id = Column(ForeignKey('memes.id', ondelete='CASCADE'))
    comment_id = Column(ForeignKey('comments.id', ondelete='CASCADE'))
    updated_at = Column(DateTime(True), server_default=_text('now()'))
    deleted_at = Column(DateTime(True))

    comment = relationship('Comments', back_populates='flags')
    flagger = relationship('Users', foreign_keys=[flagger_id], back_populates='flags')
    meme = relationship('Memes', back_populates='flags')
    reviewer = relationship('Users', foreign_keys=[reviewer_id], back_populates='flags_')


class TemplatePredictionAudits(Base):
    __tablename__ = 'template_prediction_audits'
    __table_args__ = (
        ForeignKeyConstraint(['template_prediction_id'], ['template_predictions.id'], ondelete='CASCADE', name='FK_e9d11ed35d8d34811e27098db4e'),
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='FK_cc591ea6494a5b5c1d1a1513433'),
        PrimaryKeyConstraint('id', name='PK_5eeaa1c988a3a9b220aa986e6a2')
    )

    id = Column(Integer)
    template_prediction_id = Column(ForeignKey('template_predictions.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    meme_clf_correct = Column(Boolean)
    audit_error = Column(Enum('IsDeleted', name='template_prediction_audits_audit_error_enum'))

    template_prediction = relationship('TemplatePredictions', back_populates='template_prediction_audits')
    user = relationship('Users', back_populates='template_prediction_audits')
