from sqlalchemy import Column, ForeignKey, Integer, BigInteger, Enum, Boolean, DateTime, Float
from sqlalchemy.types import TypeDecorator, Unicode
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

import datetime

Base = declarative_base()


class CoerceUTF8(TypeDecorator):
    """Safely coerce Python bytestrings to Unicode
    before passing off to the database."""

    impl = Unicode

    def process_bind_param(self, value, dialect):
        if isinstance(value, str):
            value = value.decode('utf-8')
        return value


class Post(Base):
    '''This class represents a post that has had a vote request against it'''
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True, unique=True)
    post_type_id = Column(Integer, ForeignKey('posttypes.id'), nullable=False, index=True)
    post_type = relationship('PostType', backref='posts')
    answer_id = Column(Integer, nullable=True)
    accepted_answer_id = Column(Integer, nullable=True)
    body = Column(CoerceUTF8(65000, convert_unicode=True), nullable=False)  # At the time this was created, max post
                                                                            # size in data was was 54,000.
    close_votes = Column(Integer, nullable=False, default=0)
    closed_date = Column(DateTime, nullable=True)
    closed_reason = Column(CoerceUTF8(2000, convert_unicode=True), nullable=True)
    comment_count = Column(Integer, nullable=False, default=0)
    creation_date = Column(DateTime, nullable=False)
    delete_vote_count = Column(Integer, nullable=False, default=0)
    down_vote_count = Column(Integer, nullable=False, default=0)
    favorite_count = Column(Integer, nullable=False, default=0)
    is_accepted = Column(Boolean, nullable=True, default=None)
    last_activity_date = Column(DateTime, nullable=False)
    last_edit_date = Column(DateTime, nullable=True)
    last_editor_id = Column(BigInteger, ForeignKey('users.id'), nullable=True)
    last_editor = relationship('User', backref='editor', foreign_keys=[last_editor_id])
    link = Column(CoerceUTF8(500, convert_unicode=True), nullable=False)
    locked_date = Column(DateTime, nullable=True)
    owner_id = Column(BigInteger, ForeignKey('users.id'), nullable=False, index=True)
    owner = relationship('User', backref='owner', foreign_keys=[owner_id])
    question_id = Column(Integer, nullable=False, index=True)
    reopen_vote_count = Column(Integer, nullable=False, default=0)
    score = Column(Integer, nullable=False, default=0)
    tags = Column(CoerceUTF8(300, convert_unicode=True), nullable=True)
    title = Column(CoerceUTF8(500, convert_unicode=True), nullable=True)
    up_vote_count = Column(Integer, nullable=False, default=0)
    view_count = Column(Integer, nullable=False, default=0)
    request_from_room_num = Column(Integer, nullable=False, index=True)
    request_from_room_site = Column(CoerceUTF8(100, convert_unicode=True), nullable=False, index=True)
    request_time = Column(DateTime, nullable=False, default=datetime.datetime.now())
    request_type_id = Column(Integer, ForeignKey('requesttypes.id'), nullable=False, index=True)
    request_type = relationship('RequestType', backref='posts')
    last_check = Column(DateTime, nullable=True)

    def __repr__(self):
        return "<Post(id={}, Type={}, link={})>".format(self.id, self.post_type, self.link)


class User(Base):
    '''This represents a user on the site'''
    __tablename__ = 'users'
    id = Column(BigInteger, primary_key=True, unique=True)
    name = Column(CoerceUTF8(100, convert_unicode=True), nullable=False)
    reputation = Column(BigInteger, nullable=False)
    link = Column(CoerceUTF8(500, convert_unicode=True), nullable=False)
    type = Column(CoerceUTF8(50, convert_unicode=True), nullable=False)

    def __repr__(self):
        return "<User(id={}, Type={}, link={})>".format(self.id, self.post_type_id, self.link)


class RequestType(Base):
    '''Type of vote requests that received'''
    __tablename__ = 'requesttypes'
    id = Column(Integer, primary_key=True, unique=True)
    name = Column(CoerceUTF8(500, convert_unicode=True), nullable=False, unique=True)

    def __repr__(self):
        return "<RequestType(id={}, name={})>".format(self.id, self.name)

    @classmethod
    def all_request_types(cls, session):
        types_dict = {}
        for r in session.query(cls).all():
            types_dict[r.name] = r.__dict__
        return types_dict

    @classmethod
    def by_type(cls, session, name):
        return session.query(cls.id).filter(cls.name == name).scalar()



class PostType(Base):
    '''This represents the type of posts'''
    __tablename__ = 'posttypes'
    id = Column(Integer, primary_key=True, unique=True)
    name = Column(CoerceUTF8(50, convert_unicode=True), nullable=False)

    def __repr__(self):
        return "<PostType(id={}, name={})>".format(self.id, self.name)

    @classmethod
    def all_post_types(cls, session):
        types_dict = {}
        for r in session.query(cls).all():
            types_dict[r.name] = r.__dict__
        return types_dict


def create_all_tables(engine):
    Base.metadata.create_all(engine)