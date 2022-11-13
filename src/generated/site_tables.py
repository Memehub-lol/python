from sqlalchemy import Boolean, Column, DateTime, Enum, Float, ForeignKeyConstraint, Integer, PrimaryKeyConstraint, String, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class ImgflipTemplates(Base):
    __tablename__ = 'imgflip_templates'
    __table_args__ = (
        PrimaryKeyConstraint('imgflip_name', name='PK_00960a2c151692800a35316a6cc'),
    )

    created_at = Column(DateTime(True), nullable=False, server_default=text('now()'))
    name = Column(String, nullable=False)
    page = Column(String, nullable=False)
    url = Column(String, nullable=False)
    imgflip_name = Column(String)
    deleted_at = Column(DateTime(True))
    num_images = Column(Integer)

    reddit_memes = relationship('RedditMemes', back_populates='imgflip_templates')


class Redditors(Base):
    __tablename__ = 'redditors'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='PK_061583869ba792c2095b65c671f'),
        UniqueConstraint('username', name='UQ_12ea821277fb068de87556497b0')
    )

    id = Column(UUID, server_default=text('uuid_generate_v4()'))
    created_at = Column(DateTime(True), nullable=False, server_default=text('now()'))
    username = Column(String(20), nullable=False)
    deleted_at = Column(DateTime(True))

    reddit_memes = relationship('RedditMemes', back_populates='redditor')
    reddit_scores = relationship('RedditScores', back_populates='redditor')


class RedditMemes(Base):
    __tablename__ = 'reddit_memes'
    __table_args__ = (
        ForeignKeyConstraint(['redditor_id'], ['redditors.id'], ondelete='CASCADE', name='FK_a270a3212df747ae19cb09d1be9'),
        ForeignKeyConstraint(['template_name'], ['imgflip_templates.imgflip_name'], ondelete='CASCADE', name='FK_0634017e6f2351824f6db59ba4e'),
        PrimaryKeyConstraint('id', name='PK_1ae085193dc492081d372e0299c'),
        UniqueConstraint('url', name='UQ_80fc13a6facb2e40853bc5ce717')
    )

    id = Column(UUID, server_default=text('uuid_generate_v4()'))
    created_at = Column(DateTime(True), nullable=False, server_default=text('now()'))
    idx = Column(Integer, nullable=False)
    reddit_id = Column(String, nullable=False)
    subreddit = Column(String, nullable=False)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    upvote_ratio = Column(Float(53), nullable=False)
    upvotes = Column(Integer, nullable=False)
    downvotes = Column(Integer, nullable=False)
    num_comments = Column(Integer, nullable=False)
    redditor_id = Column(UUID, nullable=False)
    deleted_at = Column(DateTime(True))
    image_error = Column(Enum('IsDeleted', 'Malformed', 'NoImage', 'Connection', 'Unidentified', 'Unknown', name='ImageError'))
    percentile = Column(Float(53))
    not_meme = Column(Boolean)
    not_template = Column(Boolean)
    meme_text = Column(String)
    template_name = Column(String)

    redditor = relationship('Redditors', back_populates='reddit_memes')
    imgflip_templates = relationship('ImgflipTemplates', back_populates='reddit_memes')


class RedditScores(Base):
    __tablename__ = 'reddit_scores'
    __table_args__ = (
        ForeignKeyConstraint(['redditor_id'], ['redditors.id'], ondelete='CASCADE', name='FK_adcc81afcb5f0b2c57e6ca18a10'),
        PrimaryKeyConstraint('id', name='PK_6ee18c3e5f54447fff6721e5b91')
    )

    id = Column(UUID, server_default=text('uuid_generate_v4()'))
    created_at = Column(DateTime(True), nullable=False, server_default=text('now()'))
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
    deleted_at = Column(DateTime(True))
    redditor_id = Column(UUID)

    redditor = relationship('Redditors', back_populates='reddit_scores')
