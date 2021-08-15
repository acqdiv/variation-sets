""" Quick backend for randomized data from NAL """

from sqlalchemy import create_engine, Text, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


def db_connect(path):
    """ Performs database connection.

    path : str

    Returns:
        SQLAlchemy engine instance
    """
    return create_engine(path, echo=False)


def create_tables(engine):
    """ Drops all databases before creating them.

        Args:
            engine: a sqlalchemy database engine
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(engine)


class Result(Base):
    __tablename__ = 'randomized'
    session_id_fk = Column(Integer, primary_key=True)
    utterance_id_fk_rand = Column(Integer, nullable=True, unique=False)
    word = Column(Text, nullable=False, unique=False)
    pos_word_stem = Column(Text, nullable=False, unique=False)
    morpheme = Column(Text, nullable=False, unique=False)
    pos = Column(Text, nullable=False, unique=False)
