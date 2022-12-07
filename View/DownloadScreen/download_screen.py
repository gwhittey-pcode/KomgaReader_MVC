import inspect
import os
from functools import partial
from pathlib import Path

from kivy import Logger
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.properties import ListProperty, StringProperty, ObjectProperty, BooleanProperty
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.progressbar import MDProgressBar
from kivymd.utils import asynckivy
from Utility.komga_server_conn import ComicServerConn
from View.DownloadScreen.components import MDDataTable as CustomMDDataTable
from View.base_screen import BaseScreenView
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.floatlayout import MDFloatLayout
from Utility.myUrlrequest import UrlRequest as myUrlRequest
from libs.database import Comic, Series, ReadingList, get_or_create, get_db


class Tab(MDFloatLayout, MDTabsBase):
    '''Class implementing content for a tab.'''


class MyMDLabel(MDLabel):
    id = StringProperty()

    def __init__(self, **kwargs):
        super(MyMDLabel, self).__init__(**kwargs)


class MyMDDataTable(CustomMDDataTable):
    name = StringProperty()

    def __init__(self, **kwargs):
        super(MyMDDataTable, self).__init__(**kwargs)


class MyMDProgressBar(MDProgressBar):
    id = StringProperty()

    def __init__(self, **kwargs):
        super(MyMDProgressBar, self).__init__(**kwargs)


class DownloadScreenView(BaseScreenView):
    series_book_id = ListProperty()
    dl_que_bars = ListProperty()
    download_que = ListProperty()
    table_que = ObjectProperty()
    downloaded_files_tabel = ObjectProperty()
    downloaded_series_tabel = ObjectProperty()
    download_active = BooleanProperty(False)
    download_running = BooleanProperty(False)

    def __init__(self, **kwargs):
        super(DownloadScreenView, self).__init__(**kwargs)
        self.downloading_file = False
        self.dialog_load_comic_data = None
        self.series_book_id = []
        self.dl_que_bars = []
        self.download_que = []
        # Clock.schedule_once(self.build_tables, 0)
        Clock.schedule_interval(self.check_download_toggle, .2)
    def on_pre_enter(self, *args):
        self.ids.top_bar.elevation = 0
    def build_tables(self, *args):
        self.table_que = MyMDDataTable(
            rows_num=10,
            name="table_que",
            size_hint=(1, 1),
            use_pagination=True,
            column_data=[
                ("Que #", dp(30)),
                ("Comic Name", dp(60)),
                ("Series/RL", dp(60)),
                ("File Path", dp(60)),
                # ("Download %", dp(30)),
            ],

        )
        self.table_que.row_data = []
        self.table_que.bind(on_row_press=self.on_row_press)
        que_box = self.ids.que_box
        que_box.add_widget(self.table_que)
        self.downloaded_files_tabel = MyMDDataTable(
            rows_num=10,
            name="files_table",
            size_hint=(1, 1),
            use_pagination=True,
            column_data=[
                ("id", dp(60)),
                ("Comic Name", dp(60)),
                ("Series", dp(60)),
                ("Read List", dp(60)),
            ]
        )
        self.downloaded_files_tabel.bind(on_row_press=self.on_row_press)
        dl_file_box = self.ids.dl_file_box
        dl_file_box.add_widget(self.downloaded_files_tabel)
        self.downloaded_series_tabel = MyMDDataTable(
            rows_num=10,
            check=True,
            name="series_table",
            size_hint=(1, 1),
            use_pagination=True,
            column_data=[
                ("id", dp(60)),
                ("Series/RL Name", dp(60)),
                ("Series/RL", dp(60)),
                ("# Books", dp(60)),
            ]
        )
        self.downloaded_series_tabel.bind(on_row_press=self.on_row_press)
        dl_series_box = self.ids.dl_series_box
        dl_series_box.add_widget(self.downloaded_series_tabel)
        # Clock.schedule_once(self.populate_tables, 0)

    def populate_tables(self, *args):
        app = MDApp.get_running_app()
        session = next(get_db())
        query = session.query(Series).all()

        for series in query:
            self.downloaded_series_tabel.row_data.append(
                [series.series_id, series.title, "Series", series.booksCount]
            )

        readlist_query = session.query(ReadingList).all()
        for readlist in readlist_query:
            self.downloaded_series_tabel.row_data.append(
                [readlist.readlist_id, readlist.name, "readlist", readlist.booksCount]
            )
        comic_query = session.query(Comic).all()
        for comic in comic_query:
            self.downloaded_files_tabel.row_data.append(
                [comic.comic_id, comic.name, comic.series_name, comic.readlist_name]
            )
        session.close()


    def on_row_press(self, instance_table, instance_row):
        index = instance_row.index
        cols_num = len(instance_table.column_data)
        row_num = int(index / cols_num)
        col_num = index % cols_num
        full_pages = len(instance_table.row_data) // instance_table.rows_num
        cell_row = instance_table.table_data.view_adapter.get_visible_view(row_num * cols_num)
        page_num = instance_table.table_data.current_page
        t_rows_per_page = instance_table.rows_num
        the_index = t_rows_per_page * page_num + row_num
        group_id = instance_table.row_data[the_index][0]
        group_type = "series"
        if instance_table.row_data[the_index][2] == "series_table":
            group_type = "series"
        elif instance_table.row_data[the_index][2] == "readlist":
            group_type = "readlist"
        app = MDApp.get_running_app()
        screen = app.manager_screens.get_screen('dlcomic group screen')
        Clock.schedule_once(lambda dt: screen.get_comicgroup_data(group_id, group_type))
        app.manager_screens.current = 'dlcomic group screen'

    def on_progress(self, req, current_size, total_size, *args, **kwargs):
        str_progress = int(current_size) / int(total_size) * 100
        the_row = self.table_que.row_data[0]
        self.table_que.update_row(
            the_row,
            [the_row[0],
             the_row[1],
             the_row[2],
             the_row[3],
             f"{str_progress}%"
             ]

        )

    def check_download_toggle(self, dt, *args):
        if self.download_active and len(self.download_que) != 0 and not self.download_running:
            self.download_running = True
            for que_item in self.download_que:
                Clock.schedule_once(partial(self.do_download_books, que_item=que_item), .01)

    def toggle_download(self, *args):
        print(f"{self.download_active =}")
        if self.download_active:
            self.download_active = False
            self.ids.download_toggle_btn.text = "Start Download"
            self.download_running = False
        else:
            self.download_active = True
            self.ids.download_toggle_btn.text = "Pause Download"

    def download_items(self, item_id="", dl_type=""):
        screen = self.manager_screens.current_screen
        for item in screen.comic_thumbs_list:
            if item.item_id == item_id:
                item.ids.download_select.icon = "download-circle"
        if dl_type in ["series", "reading list"]:
            self.download_group(item_id=item_id, dl_type=dl_type)
        elif dl_type == "reading list":
            pass

    def got_file(self, req, *args, **kwargs):
        print("Got File")
        if len(self.download_que) != 0:
            self.download_que.remove(kwargs['que_item'])

        def __got_thumb(*args):
            pass

        if len(self.table_que.row_data) != 0:
            for row in self.table_que.row_data:
                if row[3] == kwargs['que_item']['file_name']:
                    print(f"{row =}")
                    self.table_que.remove_row(row)
        app = MDApp.get_running_app()
        session = next(get_db())
        comic_db = session.query(Comic).filter(Comic.comic_id == kwargs['book_id']).one()
        comic_db.file_name = kwargs['file_name']
        screen = MDApp.get_running_app().manager_screens.current_screen
        screen.ids.download_text.text = f"Downloaded {comic_db.file_name}"
        thumb_filename = f"{comic_db.comic_id}.jpg"
        id_folder = app.store_dir
        my_download_folder = Path(os.path.join(id_folder, "download_comic_files"))
        my_thumb_dir = Path(os.path.join(my_download_folder, "comic_thumbs"))
        t_file = os.path.join(my_thumb_dir, thumb_filename)
        if not my_thumb_dir.is_dir():
            os.makedirs(my_thumb_dir)
        if os.path.isfile(t_file):
            pass
        else:
            c_image_source = f"{app.base_url}/api/v1/books/{comic_db.comic_id}/thumbnail"
            fetch_data = ComicServerConn()
            fetch_data.get_server_file_download(
                c_image_source,
                callback=__got_thumb,
                file_path=t_file,
            )
        in_data = False
        for item in self.downloaded_files_tabel.row_data:
            if item[0] == comic_db.comic_id:
                in_data = True
        if not in_data:
            self.downloaded_files_tabel.row_data.append(
                [comic_db.comic_id, comic_db.name, comic_db.series_name, comic_db.readlist_name]
            )
        session.commit()
        session.close()
        if len(self.download_que) == 0:
            self.ids.download_toggle_btn.text = "Start Download"
            self.download_running = True
        else:
            self.downloading_file = False

    def do_download_books(self, *args, que_item=None):
        if len(self.download_que) != 0:
            que_item = que_item
            book_id = que_item['id']
            group_item_id = que_item['group_item_id']
            app = MDApp.get_running_app()
            str_cookie = "SESSION=" + app.config.get("General", "api_key")
            head = {
                "Cookie": str_cookie,
            }
            id_folder = app.store_dir
            my_download_folder = Path(os.path.join(id_folder, "download_comic_files", "comic_files"))
            if not my_download_folder.is_dir():
                os.makedirs(my_download_folder)
            t_file = que_item['file_name']
            file_path = os.path.join(my_download_folder, t_file)
            url_send = f"{app.base_url}/api/v1/books/{book_id}/file"
            self.downloading_file = True
            myUrlRequest(
                url_send,
                req_headers=head,
                on_success=partial(self.got_file,
                                   group_item_id=group_item_id,
                                   file_name=t_file,
                                   book_id=book_id,
                                   que_item=que_item
                                   ),
                chunk_size=28192,
                on_error=self.got_error,
                on_redirect=self.got_redirect,
                on_failure=self.got_error,
                # on_progress=partial(self.on_progress, book_id=book_id),
                file_path=file_path,
            )

    def download_group(self, item_id="", dl_type=""):
        async def __download_group():
            def __got_series_book_data(req, results, **kwargs):
                i = 0
                series_db = kwargs['series_db']
                for comicbook in results['content']:
                    session = next(get_db())
                    comic_db, comic_created = get_or_create(session, Comic, comic_id=comicbook['id'])
                    if comic_created:
                        comic_db.number = comicbook['number']
                        comic_db.page_count = comicbook['media']['pagesCount']
                        comic_db.title = comicbook['metadata']['title']
                        comic_db.summary = comicbook['metadata']['summary']
                        comic_db.name = comicbook['name']
                        comic_db.series_name = comicbook['seriesTitle']
                    if dl_type == "series":
                        if not comic_db.series:
                            comic_db.series.append(series_db)
                    elif dl_type == "reading list":
                        if not comic_db.readinglists:
                            comic_db.readinglists.append(series_db)
                        comic_db.readlist_name = series_db.name
                    session.add(comic_db)
                    session.commit()
                    session.close()
                    server_path = comicbook['url']
                    file_name = server_path.split("/")[-1]
                    str_append = [f"{i}",
                                  comicbook['name'],
                                  comicbook['seriesTitle'],
                                  file_name,
                                  ]
                    self.download_que.append(
                        {
                            "id": comicbook['id'],
                            "file_name": file_name,
                            "group_item_id": item_id,
                        }
                    )
                    i += 1
                    self.table_que.row_data.append(str_append)

            def __got_series_data(req, results):
                session = next(get_db())
                url_series_book_data = ""
                if dl_type == "series":
                    the_book_count = results['booksCount']
                    url_series_book_data = ""
                    db_series, created = get_or_create(session, Series, series_id=item_id)
                    if created:
                        db_series.name = results['name']
                        db_series.title = results['metadata']['title']
                        db_series.booksCount = the_book_count
                        db_series.libraryId = results['libraryId']
                        session.add(db_series)
                        session.commit()
                        self.downloaded_series_tabel.row_data.append(
                            [results['id'], results['name'], "Series"]
                        )
                    url_series_book_data = f"{app.base_url}/api/v1/series/{item_id}/books?size={the_book_count}"
                elif dl_type == "reading list":
                    the_book_count = len(results['bookIds']) + 1
                    db_series, created = get_or_create(session, ReadingList, readlist_id=item_id)
                    if created:
                        db_series.name = results['name']
                        db_series.booksCount = the_book_count
                        session.add(db_series)
                        session.commit()
                        session.close()
                        self.downloaded_series_tabel.row_data.append(
                            [results['id'], results['name'], "Readlist"]
                        )
                    url_series_book_data = f"{app.base_url}/api/v1/readlists/{item_id}/books?size={the_book_count}"

                req = myUrlRequest(
                    url_series_book_data,
                    req_headers=head,
                    on_success=partial(__got_series_book_data, series_db=db_series),
                    on_error=self.got_error,
                    on_redirect=self.got_redirect,
                    on_failure=self.got_error,
                )

            app = MDApp.get_running_app()
            if dl_type == "series":
                url_series_data = f"{app.base_url}/api/v1/series/{item_id}"
            elif dl_type == "reading list":
                url_series_data = f"{app.base_url}/api/v1/readlists/{item_id}"
            str_cookie = "SESSION=" + app.config.get("General", "api_key")
            head = {
                "Content-type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
                "Cookie": str_cookie,
            }
            myUrlRequest(
                url_series_data,
                req_headers=head,
                on_success=__got_series_data,
                on_error=self.got_error,
                on_redirect=self.got_redirect,
                on_failure=self.got_error,
            )

        asynckivy.start(__download_group())

    def got_error(self, req, results):
        Logger.critical("----got_error--")
        Logger.critical("ERROR in %s %s" % (inspect.stack()[0][3], results))

    def got_time_out(self, req, results):
        Logger.critical("----got_time_out--")
        Logger.critical("ERROR in %s %s" % (inspect.stack()[0][3], results))

    def got_failure(self, req, results):
        Logger.critical("----got_failure--")
        Logger.critical("ERROR in %s %s" % (inspect.stack()[0][3], results))

    def got_redirect(self, req, results):
        Logger.critical("----got_redirect--")
        Logger.critical("ERROR in %s %s" % (inspect.stack()[0][3], results))

    def on_tab_switch(
            self, instance_tabs, instance_tab, instance_tab_label, tab_text
    ):
        '''
        Called when switching tabs.

        :type instance_tabs: <kivymd.uix.tab.MDTabs object>;
        :param instance_tab: <__main__.Tab object>;
        :param instance_tab_label: <kivymd.uix.tab.MDTabsLabel object>;
        :param tab_text: text or name icon of tab;
        '''

        count_icon = instance_tab.icon  # get the tab icon
        print(f"Welcome to {count_icon}' tab'")

    def model_is_changed(self) -> None:
        """
        Called whenever any change has occurred in the data model.
        The view in this method tracks these changes and updates the UI
        according to these changes.
        """
