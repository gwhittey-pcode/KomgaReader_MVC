import ntpath
import os
import pickle
from functools import partial
from pathlib import Path
from time import sleep
import peewee
from kivy.app import App
from kivy.clock import Clock
from kivy.event import EventDispatcher
from kivy.logger import Logger
from kivy.metrics import dp
from kivy.properties import (
    BooleanProperty,
    DictProperty,
    ListProperty,
    NumericProperty,
    ObjectProperty,
    StringProperty,
)
from kivymd.app import MDApp
from kivymd.toast.kivytoast.kivytoast import toast
from kivy.network.urlrequest import UrlRequest
from Utility.komga_server_conn import ComicServerConn
from Utility.db_functions import Comic, ComicIndex, ReadingList
from kivymd.uix.dialog import MDDialog

CHECKBOX_STATE_BOOL = {"normal": False, "down": True}
READINGLIST_DB_KEYS = [
    "name",
    "cb_limit_active",
    "limit_num",
    "cb_only_read_active",
    "cb_purge_active",
    "cb_optimize_size_active",
    "sw_syn_this_active",
    "end_last_sync_num",
    "totalCount",
    "data",
]

READINGLIST_SETTINGS_KEYS = [
    "cb_limit_active",
    "limit_num",
    "cb_only_read_active",
    "cb_purge_active",
    "cb_optimize_size_active",
    "sw_syn_this_active",
]
COMIC_DB_KEYS = [
    "Id",
    "Series",
    "Number",
    "Volume",
    "Year",
    "Month",
    "readProgress_page",
    "PageCount",
    "Title",
    "Summary",
    "FilePath",
    "local_file",
    "data",
    "is_sync",
    "Series_id",
    "rl_number",

]


def get_size(start_path="."):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)

    return total_size


class ComicBook(EventDispatcher):
    """
    class representing a single comic
    """

    Id = StringProperty()
    __str__ = StringProperty()
    slug = StringProperty()
    name = StringProperty()
    Number = StringProperty()
    Series = StringProperty()
    Series_id = StringProperty()
    date = StringProperty()
    Year = NumericProperty()
    Month = NumericProperty()
    readProgress_page = NumericProperty()
    PageCount = NumericProperty()
    Summary = StringProperty()
    Title = StringProperty()
    FilePath = StringProperty()
    Volume = StringProperty()
    readlist_obj = ObjectProperty()
    local_file = StringProperty("None")
    is_sync = BooleanProperty(False)
    data = DictProperty()
    order_index = NumericProperty()
    completed = BooleanProperty()
    def __init__(
        self,
        data=None,
        readlist_obj=None,
        comic_Id="",
        comic_index=0,
        mode="Server",
        *args,
        **kwargs,
    ):
        self.readlist_obj = readlist_obj
        if mode in ("Server", "FileOpen"):
            if comic_Id == "":
                comic_data = data
                self.data = comic_data
                self.Id = comic_data["id"]
                self.__str__ = "{} #{}".format(
                    comic_data["seriesTitle"], str(comic_data['metadata']['number'])
                )
                self.slug = str(comic_data["id"])
                self.name = f"{comic_data['seriesTitle']} #{str(comic_data['number'])}"
                self.Number = str(comic_data['metadata']['number'])
                self.Series = comic_data["seriesTitle"]
                self.Series_id = comic_data["seriesId"]
                self.date = f"{comic_data['metadata']['releaseDate']}"

                if comic_data['metadata']['releaseDate'] is not None:

                    self.Year = comic_data['metadata']['releaseDate'][0]
                    self.Month = comic_data['metadata']['releaseDate'][2]
                else:
                    self.Year = 2000
                    self.Month = 1
                if comic_data['readProgress']:
                    self.completed = comic_data['readProgress']['completed']
                    self.readProgress_page = comic_data['readProgress']['page']
                self.PageCount = comic_data['media']["pagesCount"]
                self.Title = comic_data['metadata']['title']
                if comic_data["metadata"]['summary'] is not None:
                    self.Summary = comic_data["metadata"]['summary']
                if comic_data["url"] is not None:
                    self.FilePath = comic_data["url"]
                self.Volume = 'None'
                app = App.get_running_app()
                self.comic_jsonstore = app.comic_db
                self.readlist_obj = readlist_obj
                self.comic_index = comic_index
                if data['number'] is not None:
                    self.rl_number = data['number']
                self.local_file = ""
                # if mode != "FileOpen":
                #     Clock.schedule_once(
                #         lambda dt: self.get_or_create_db_item())
        if mode == "db_data":
            self.Id = comic_Id
        # if mode != "FileOpen":
        #     # Clock.schedule_once(
        #     #    lambda dt: self.get_or_create_db_item())
        #     self.get_or_create_db_item()

    def get_or_create_db_item(self):
        tmp_defaults = {}
        for key in COMIC_DB_KEYS:
            if key == "comic_index":
                pass
            elif key == "data":
                new_dict = {k: self.data[k] for k in self.data.keys()}
                tmp_defaults["data"] = new_dict
            else:
                tmp_defaults[key] = getattr(self, key)

        db_item, created = Comic.get_or_create(
            Id=self.Id, defaults=tmp_defaults
        )
        if created is True:
            rl = self.readlist_obj
            db_item.comic_index.index = self.comic_index
            comic_index_db, created_index = ComicIndex.get_or_create(
                comic=db_item, readinglist=rl.db, index=self.comic_index
            )
            db_item.save()
            if rl.slug not in [item.slug for item in db_item.readinglists]:
                rl.db.comics.add(db_item)
        else:
            for key in COMIC_DB_KEYS:
                if key == "comic_index":
                    pass
                else:
                    setattr(self, key, getattr(db_item, key))
            self.__str__ = f"{db_item.Series} #{db_item.Number}"
            self.name = self.__str__
            self.date = f"{db_item.Month}/{db_item.Year}"
            self.slug = str(self.Id)

            self.comic_index = db_item.comic_index.select(
                ReadingList.slug == self.readlist_obj.slug
            )

    def update(self, key_list=()):
        for key, value in key_list:
            print(f"key:{key}\nval:{value}")

    def callback(self, store, key, result):
        pass

    def set_is_sync(self):
        try:
            db_item = ComicIndex.get(
                ComicIndex.comic == self.Id,
                ComicIndex.readinglist == self.readlist_obj.slug,
            )
            if db_item:
                if db_item.is_sync:
                    setattr(self, "is_sync", db_item.is_sync)
        except peewee.IntegrityError:
            Logger.error("Somthing went wrong")


class ComicList(EventDispatcher):

    # ids = DictProperty({})
    name = StringProperty()
    comics = ListProperty()
    data = DictProperty()
    slug = StringProperty()
    comic_db = ObjectProperty()
    comic_json = ListProperty()
    cb_only_read_active = BooleanProperty(False)
    cb_only_read_active = BooleanProperty(False)
    cb_purge_active = BooleanProperty(False)
    cb_optimize_size_active = BooleanProperty(False)
    cb_limit_active = BooleanProperty(False)
    limit_num = NumericProperty(25)
    sw_syn_this_active = BooleanProperty(False)
    comic_db_in = BooleanProperty(False)
    db = ObjectProperty()
    comics_loaded = ObjectProperty(False)
    last_comic_read = NumericProperty()
    start_last_sync_num = NumericProperty(0)
    end_last_sync_num = NumericProperty(0)
    totalCount = NumericProperty()
    pickled_data = ObjectProperty()
    sync_list = ListProperty()
    def __init__(self, name="", data=None, slug="", mode="Server"):
        self.slug = slug
        self.name = name
        self.event = None

        if data != "db_data":
            self.pickled_data = pickle.dumps(data, -1)
            self.data = pickle.loads(self.pickled_data)
            self.comic_json = self.data['content']
            if mode != "FileOpen":
                if name == "Single_FileLoad":
                    self.totalCount = 0
                else:
                    self.totalCount = self.data["totalElements"]
        # if mode != "FileOpen":
        #     self.get_or_create_db_item(mode=mode)

    def add_comic(self, comic, index=0):
        """
            Add Single comic book to this colection
        """
        self.comics.insert(0, comic)

    def get_or_create_db_item(self, mode):
        tmp_defaults = {}
        try:
            for key in READINGLIST_DB_KEYS:
                if key == "data":
                    new_dict = {k: self.data[k] for k in self.data.keys()}
                    tmp_defaults["data"] = new_dict
                else:
                    tmp_defaults[key] = getattr(self, key)
            db_item, created = ReadingList.get_or_create(
                slug=self.slug, defaults=tmp_defaults
            )
            self.db = db_item
            if db_item:
                for key in READINGLIST_DB_KEYS:
                    setattr(self, key, getattr(db_item, key))
                if created is True:
                    len_dbcomics = len(db_item.comics)
                    if (
                        len_dbcomics == len(self.comic_json)
                        and len(self.comic_json) != 0
                    ):
                        self.comic_db_in = True
                        self.comics = self.db.comics.order_by(
                            -Comic.comic_index.index
                        )
                else:
                    self.comic_db_in = True
                    comicindex_db = ComicIndex.get(
                        ComicIndex.readinglist == self.slug
                    )
                    if mode == "local_file":
                        list_comics = self.db.comics.where(
                            Comic.is_sync == True, Comic.local_file != ""
                        ).order_by(  # noqa
                            comicindex_db.index
                        )
                    else:
                        list_comics = self.db.comics.order_by(
                            comicindex_db.index
                        )
                    for comic in list_comics:
                        new_comic = ComicBook(
                            comic_Id=comic.Id,
                            readlist_obj=self,
                            mode="db_data",
                        )
                        self.comics.append(new_comic)
                    self.comics_loaded = True
        except peewee.OperationalError:
            Logger.critical(
                "Somthing happened in get_or_create of readinglist"
            )

    def save_settings(self, *args, **kwargs):
        try:
            rl = ReadingList.get(ReadingList.slug == self.slug)
            for key in READINGLIST_SETTINGS_KEYS:
                setattr(rl, key, kwargs[key])
                setattr(self, key, kwargs[key])
            rl.save()
        except peewee.OperationalError:
            pass

    def get_server_file_download(self, req_url, callback, file_path):
        def is_finished(dt):
            if req.is_finished is True:
                app = App.get_running_app()
                screen = app.manager_screens.get_screen("r l comic books screen")
                screen.ids.sync_button.enabled = True
                Clock.schedule_once(self.download_file)
            else:
                Clock.schedule_once(is_finished, 0.25)

        app = MDApp.get_running_app()
        session_cookie = app.config.get("General", "api_key")
        str_cookie = "SESSION=" + session_cookie
        head = {
            "Cookie": str_cookie,
        }

        req = UrlRequest(
            req_url, req_headers=head, on_success=callback, file_path=file_path
        )
        app = App.get_running_app()
        screen = app.manager_screens.get_screen("r l comic books screen")
        if len(self.sync_list) != 0:
            screen.ids.sync_status_lbl.text = (
                f"Sync is Running Left in Que: {len(self.sync_list)}"
            )
            Clock.schedule_once(is_finished, 0.25)
        else:
            toast("Reading List has been Synced, Refreshing Screen")
            screen.ids.sync_status_lbl.text = ""
            screen.ids.sync_button.enabled = True
            app.sync_is_running = False
            # screen.refresh_callback()

    def got_file(self, comic_obj, comic_file="", *args, **kwargs):
        def file_finished_toast(dt):
            toast(f"{os.path.basename(comic_file)} Synced")
        self.num_file_done += 1
        Clock.schedule_once(file_finished_toast)
        self.file_download = True
        db_comic = Comic.get(Comic.Id == comic_obj.Id)
        db_comic.is_sync = True
        db_comic.save()
        db_comic = Comic.get(Comic.Id == comic_obj.Id)
        db_comic.local_file = comic_file
        db_comic.been_sync = True
        db_comic.save()
        rl_db = ReadingList.get(ReadingList.slug == self.slug)
        rl_db.end_last_sync_num += 1
        rl_db.save()
        app = App.get_running_app()
        server_readinglists_screen = app.manager_screens.get_screen(
            "r l comic books screen"
        )
        server_readinglists_screen.file_sync_update(comic_obj.Id, True)

    def download_file(self, dt):
        def got_thumb(results):
            pass

        app = MDApp.get_running_app()
        screen = app.manager_screens.get_screen("r l comic books screen")
        screen.ids.sync_button.enabled = False
        if len(self.sync_list) == 0:
            toast("Reading List has been Synced, Refreshing Screen")
            app = App.get_running_app()
            screen = app.manager_screens.get_screen("r l comic books screen")
            screen.ids.sync_status_lbl.text = ""
            screen.ids.sync_button.enabled = True
            app.sync_is_running = False
            # screen.refresh_callback()
            return
        app = MDApp.get_running_app()
        comic = self.sync_list.pop(0)
        self.file_download = False
        file_name = ntpath.basename(comic.FilePath)
        part_url = f'/api/v1/books/{comic.Id}/thumbnail'
        thumb_url = f"{app.base_url}{part_url}"
        sync_url = f'{app.base_url}/api/v1/books/{comic.Id}/file'
        id_folder = os.path.join(app.sync_folder, self.slug)
        my_comic_dir = Path(os.path.join(id_folder, "comics"))
        my_thumb_dir = Path(os.path.join(id_folder, "thumb"))
        if not self.my_comic_dir.is_dir():
            os.makedirs(my_comic_dir)
        if not self.my_thumb_dir.is_dir():
            os.makedirs(my_thumb_dir)
        t_file = os.path.join(my_comic_dir, file_name)
        self.get_server_file_download(
            sync_url,
            callback=self.got_file(comic, comic_file=t_file),
            file_path=t_file,
        )
        thumb_name = f"{comic.Id}.jpg"
        self.fetch_data.get_server_file_download(
            thumb_url,
            callback=lambda req, results: got_thumb(results),
            file_path=os.path.join(my_thumb_dir, thumb_name),
        )

    def _finish_sync(self, comic_list, *largs):
        def __finish_toast(dt):
            toast("Reading List has been Synced, Refreshing Screen")
            # app = App.get_running_app()
            # screen = app.manager_screens.get_screen("r l comic books screen")
            # screen.refresh_callback()

        list_comics = comic_list
        num_comic = len(list_comics)
        if self.num_file_done == num_comic:
            Clock.schedule_once(__finish_toast, 3)
            self.event.cancel()
            self.event = None

    def sync_readinglist(self, comic_list=[]):

        self.sync_list = comic_list
        app = MDApp.get_running_app()
        screen = app.manager_screens.get_screen("r l comic books screen")
        screen.ids.sync_status_lbl.text = (
            f"Sync is Running Comics to Sync: {len(self.sync_list)}"
        )
        app.sync_is_running = True
        screen.ids.sync_button.enabled = False
        Clock.schedule_once(self.download_file)
        # app.delayed_work(
        #    self.download_file, list_comics, delay=.5)
        # self.event = Clock.schedule_interval(
        #     partial(self._finish_sync, comic_list), 0.5
        # )
