""" ORM declarations, database table definitions for ACQDIV-DB """

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


class Session(Base):
    """ Each row in the Sessions table represents an input file.

        Note:
            - session_id field is the input filename
            - source_id field is the id given in the session file
    """
    __tablename__ = 'sessions'

    id = Column(Integer, primary_key=True)
    source_id = Column(Text, nullable=False, unique=False)
    corpus = Column(Text, nullable=False, unique=False)
    language = Column(Text, nullable=False, unique=False)
    date = Column(Text, nullable=True, unique=False)
    target_child_fk = Column(Integer, ForeignKey('uniquespeakers.id'))
    # SQLAlchemy relationship definitions:
    speakers = relationship('Speaker', backref='Session')
    utterances = relationship('Utterance', backref='Session')
    words = relationship('Word', backref='Session')
    morphemes = relationship('Morpheme', backref='Session')


class Speaker(Base):
    """ Speaker table includes a row for each speaker in a session. Speakers may appear in > 1 session.
    """
    __tablename__ = 'speakers'

    id = Column(Integer, primary_key=True)
    session_id_fk = Column(Integer, ForeignKey('sessions.id'))
    uniquespeaker_id_fk = Column(Integer, ForeignKey('uniquespeakers.id'))
    corpus = Column(Text, nullable=False, unique=False)
    language = Column(Text, nullable=False, unique=False)
    speaker_label = Column(Text, nullable=True, unique=False) 
    name = Column(Text, nullable=True, unique=False)
    age_raw = Column(Text, nullable=True, unique=False)
    age = Column(Text, nullable=True, unique=False)
    age_in_days = Column(Integer, nullable=True, unique=False)
    gender_raw = Column(Text, nullable=True, unique=False)
    gender = Column(Text, nullable=True, unique=False)
    role_raw = Column(Text, nullable=True, unique=False)
    role = Column(Text, nullable=True, unique=False)
    macrorole = Column(Text, nullable=True, unique=False)
    languages_spoken = Column(Text, nullable=True, unique=False)
    birthdate = Column(Text, nullable=True, unique=False)

    def __repr__(self):
        return "Speaker(%s), Label(%s), Birthdate(%s)" % (self.name, self.speaker_label, self.birthdate)


class UniqueSpeaker(Base):
    """ Unique speakers across all corpora.
    """
    __tablename__ = 'uniquespeakers'

    id = Column(Integer, primary_key=True)
    speaker_label = Column(Text, nullable=True, unique=False)
    name = Column(Text, nullable=True, unique=False)
    birthdate = Column(Text, nullable=True, unique=False)
    gender = Column(Text, nullable=True, unique=False)
    corpus = Column(Text, nullable=True, unique=False)


class Utterance(Base):
    """ Utterances in all sessions.

        Note:
            - source_id is the id in the original files and is not unique across corpora, e.g. u1, u1, u1
            - addressee field is not present in all corpora (see corpus manual for more info)
            - x_raw vs x is distinction between original input and cleaned/manipulated output
    """
    __tablename__ = 'utterances'

    id = Column(Integer, primary_key=True)
    session_id_fk = Column(Integer, ForeignKey('sessions.id'))
    source_id = Column(Text, nullable=True, unique=False)
    corpus = Column(Text, nullable=False, unique=False)
    language = Column(Text, nullable=False, unique=False)
    speaker_id_fk = Column(Text, nullable=False, unique=False)
    speaker_label = Column(Text, nullable=True, unique=False)
    addressee = Column(Text, nullable=True, unique=False)
    utterance_raw = Column(Text, nullable=True, unique=False)
    utterance = Column(Text, nullable=True, unique=False)
    translation = Column(Text, nullable=True, unique=False)
    morpheme = Column(Text, nullable=True, unique=False)
    gloss_raw = Column(Text, nullable=True, unique=False)
    pos_raw = Column(Text, nullable=True, unique=False)
    sentence_type = Column(Text, nullable=True, unique=False)
    start = Column(Text, nullable=True, unique=False)
    end = Column(Text, nullable=True, unique=False)
    start_raw = Column(Text, nullable=True, unique=False)
    end_raw = Column(Text, nullable=True, unique=False)
    comment = Column(Text, nullable=True, unique=False)
    warning = Column(Text, nullable=True, unique=False)
    # SQLAlchemy relationship definitions:
    words = relationship('Word', backref='Utterance')
    morphemes = relationship('Morpheme', backref='Utterance')


class Word(Base):
    """ Words table.

    TODO: get unique words and assign ids in the postprocessor
    """
    __tablename__ = 'words'

    id = Column(Integer, primary_key=True)
    session_id_fk = Column(Integer, ForeignKey('sessions.id'))
    utterance_id_fk = Column(Integer, ForeignKey('utterances.id'))
    corpus = Column(Text, nullable=False, unique=False)
    language = Column(Text, nullable=False, unique=False)
    word = Column(Text, nullable=True, unique=False)
    pos = Column(Text, nullable=True, unique=False)
    word_actual = Column(Text, nullable=True, unique=False)
    word_target = Column(Text, nullable=True, unique=False)
    warning = Column(Text, nullable=True, unique=False)
    # SQLAlchemy relationship definitions:
    morphemes = relationship('Morpheme', backref='Word')


class Morpheme(Base):
    """ Morphemes table
    """
    __tablename__ = 'morphemes'

    id = Column(Integer, primary_key=True)
    session_id_fk = Column(Integer, ForeignKey('sessions.id'))
    utterance_id_fk = Column(Integer, ForeignKey('utterances.id'))
    word_id_fk = Column(Integer, ForeignKey('words.id'))
    corpus = Column(Text, nullable=True, unique=False)
    language = Column(Text, nullable=True, unique=False)
    type = Column(Text, nullable=True, unique=False)
    morpheme = Column(Text, nullable=True, unique=False)
    gloss_raw = Column(Text, nullable=True, unique=False)
    gloss = Column(Text, nullable=True, unique=False)
    pos_raw = Column(Text, nullable=True, unique=False)
    pos = Column(Text, nullable=True, unique=False)
    warning = Column(Text, nullable=True, unique=False)
