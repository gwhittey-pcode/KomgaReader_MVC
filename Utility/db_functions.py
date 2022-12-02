from peewee import (
    SqliteDatabase,
    CharField,
    IntegerField,
    ForeignKeyField,
    TextField,
    Model,
    ManyToManyField,
    DeferredThroughModel,
    DatabaseProxy,
    BooleanField,
)

from kivy.app import App
import os

database_proxy = DatabaseProxy()
from playhouse.fields import PickleField  # noqa


def start_db():
    app = App.get_running_app()
    db_folder = app.my_data_dir
    db_file = os.path.join(db_folder, "KomgaReader.db")
    database_proxy.initialize(SqliteDatabase(db_file))
    database_proxy.create_tables(
        [
            ReadingList,
            Comic,
            Series,
            ComicSeries,
            ComicIndex,
            ReadingList.comics.get_through_model(),
            Series.comics.get_through_model(),

        ]
    )


class BaseModel(Model):
    class Meta:
        # This model uses the "KomgaReader.db" database.
        database = database_proxy


class Comic(BaseModel):
    id = CharField(primary_key=True)
    number = CharField(null=True)
    year = IntegerField(null=True)
    month = IntegerField(null=True)
    page_count = IntegerField(null=True)
    title = TextField(null=True)
    summary = TextField(null=True)
    file_path = CharField(null=True)
    name = CharField(null=True)
    series_name = CharField(null=True)
    readlist_name = CharField(null=True)
    # Volume = CharField(null=True)
    # data = PickleField(null=True)
    # local_file = CharField(null=True)
    # is_sync = BooleanField(default=False)
    # been_sync = BooleanField(default=False)


ComicIndexDeferred = DeferredThroughModel()
ComicSeriesDeferred = DeferredThroughModel()


class ReadingList(BaseModel):
    name = CharField(null=True)
    readlist_id = CharField(primary_key=True)
    booksCount = IntegerField(null=True)
    comics = ManyToManyField(
        Comic, backref="readinglists", through_model=ComicIndexDeferred
    )

    # cb_limit_active = BooleanField(null=True)
    # limit_num = IntegerField(null=True)
    # cb_only_read_active = BooleanField(null=True)
    # cb_purge_active = BooleanField(null=True)
    # cb_optimize_size_active = BooleanField(null=True)
    # sw_syn_this_active = BooleanField(null=True)
    # end_last_sync_num = IntegerField(default=0)
    # totalCount = IntegerField()


class Series(BaseModel):
    series_id = CharField(primary_key=True)
    name = CharField(null=True)
    title = CharField(null=True)
    booksCount = IntegerField(default=0)
    libraryId = CharField(null=True)
    comics = ManyToManyField(
        Comic, backref="series", through_model=ComicSeriesDeferred
    )


class ComicSeries(BaseModel):
    comic = ForeignKeyField(Comic, backref="comic_index")
    series = ForeignKeyField(Series, backref="Indexes")


ComicSeriesDeferred.set_model(ComicSeries)


class ComicIndex(BaseModel):
    comic = ForeignKeyField(Comic, backref="comic_index")
    readinglist = ForeignKeyField(ReadingList, backref="Indexes")

ComicIndexDeferred.set_model(ComicIndex)
