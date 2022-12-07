import os

from kivymd.app import MDApp
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class Comic(Base):
    __tablename__ = "comic"

    comic_id = Column(String, primary_key=True)
    number = Column(Integer, nullable=True)
    page_count = Column(Integer, nullable=True)
    title = Column(String, nullable=True)
    summary = Column(String, nullable=True)
    file_name = Column(String, nullable=True)
    name = Column(String, nullable=True)
    series_name = Column(String, nullable=True)
    readlist_name = Column(String, nullable=True)
    readinglists = relationship('ReadingList', secondary='readlist_comic', back_populates='comics')
    series = relationship('Series', secondary='series_comic', back_populates='comics')

    def __repr__(self):
        return f"Comic(comic_id={self.comic_id}, title={self.title}," \
               f"series_name={self.series_name} ,number={self.number},)"


class ReadingList(Base):
    __tablename__ = "reading_list"

    readlist_id = Column(String, primary_key=True)
    name = Column(String)
    booksCount = Column(Integer, nullable=True)
    comics = relationship('Comic', secondary='readlist_comic', back_populates='readinglists')

    def __repr__(self):
        return f"ReadingList(readlist_id={self.readlist_id}, name={self.name}, booksCount={self.booksCount}"


class Series(Base):
    __tablename__ = "series"

    series_id = Column(String, primary_key=True)
    name = Column(String)
    title = Column(String)
    booksCount = Column(Integer)
    library_id = Column(String)
    comics = relationship('Comic', secondary='series_comic', back_populates='series')


class SeriesComic(Base):
    __tablename__ = "series_comic"
    id = Column(Integer, primary_key=True)
    series_id = Column(String, ForeignKey('series.series_id'))
    comic_id = Column(String, ForeignKey('comic.comic_id'))


class ReadlistComic(Base):
    __tablename__ = "readlist_comic"
    id = Column(Integer, primary_key=True)
    readlist_id = Column(String, ForeignKey('reading_list.readlist_id'))
    comic_id = Column(String, ForeignKey('comic.comic_id'))


def get_session():
    app = MDApp.get_running_app()
    session = Session(app.db_engine)
    return session


def create_db():
    app = MDApp.get_running_app()
    db_folder = app.my_data_dir
    db_file = os.path.join(db_folder, "KomgaReader2.db")

    app.DB_ENGINE = create_engine(f"sqlite:///{db_file}", echo=False, future=True)
    app.DB_SES_MAKER = sessionmaker(bind=app.DB_ENGINE)
    Base.metadata.create_all(app.DB_ENGINE)


def get_db():
    app = MDApp.get_running_app()
    db = app.DB_SES_MAKER()
    try:
        yield db
    finally:
        db.close()


def get_or_create(session, model, **kwargs):
    """
    Creates an object or returns the object if exists
   """
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        created = False
        return instance, created

    else:
        instance = model(**kwargs)
        created = True
        session.add(instance)
        return instance, created
