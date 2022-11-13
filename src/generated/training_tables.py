from sqlalchemy import Boolean, Column, DateTime, Integer, PrimaryKeyConstraint, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class MemeTemplate(Base):
    __tablename__ = 'meme_template'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='meme_template_pkey'),
    )

    id = Column(Integer)
    name = Column(String(400), nullable=False)
    path = Column(String(400), nullable=False)
    is_test_set = Column(Boolean, nullable=False)


class NotMeme(Base):
    __tablename__ = 'not_meme'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='not_meme_pkey'),
    )

    id = Column(Integer)
    path = Column(String(400), nullable=False)
    is_test_set = Column(Boolean, nullable=False)


class NotTemplate(Base):
    __tablename__ = 'not_template'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='not_template_pkey'),
    )

    id = Column(Integer)
    path = Column(String(400), nullable=False)
    is_test_set = Column(Boolean, nullable=False)


class Validation(Base):
    __tablename__ = 'validation'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='validation_pkey'),
    )

    id = Column(Integer)
    prediction = Column(String(400), nullable=False)
    reddit_meme_id = Column(UUID, nullable=False)
    version = Column(String(400), nullable=False)
    correct = Column(Boolean, nullable=False)
    not_meme = Column(Boolean, nullable=False)
    not_template = Column(Boolean, nullable=False)
    created_at = Column(DateTime(True), nullable=False, server_default=text('now()'))
    path = Column(String(400))
