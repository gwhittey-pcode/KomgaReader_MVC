import inspect
import os
import zipfile
from functools import partial
from pathlib import Path

from kivy import Logger
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.properties import ListProperty, StringProperty, ObjectProperty
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.progressbar import MDProgressBar
from View.DownloadScreen.components import MDDataTable as CustomMDDataTable
from View.base_screen import BaseScreenView
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.floatlayout import MDFloatLayout
from Utility.myUrlrequest import UrlRequest as myUrlRequest
from Utility.db_functions import Series, Comic, ReadingList
import multitasking

multitasking.set_max_threads(10)


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

    def __init__(self, **kwargs):
        super(DownloadScreenView, self).__init__(**kwargs)
        self.series_book_id = []
        self.dl_que_bars = []
        self.download_que = []
        Clock.schedule_once(self.build_tables, 0)

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
            ]
        )
        self.downloaded_series_tabel.bind(on_row_press=self.on_row_press)
        dl_series_box = self.ids.dl_series_box
        dl_series_box.add_widget(self.downloaded_series_tabel)
        Clock.schedule_once(self.populate_tables, 0)

    def populate_tables(self, *args):
        query = Series.select()

        for series in query:
            self.downloaded_series_tabel.row_data.append(
                [series.series_id, series.name, "Series"]
            )

        readlist_query = ReadingList.select()
        for readlist in readlist_query:
            self.downloaded_series_tabel.row_data.append(
                [readlist.readlist_id, readlist.name, "readlist"]
            )
        comic_query = Comic.select()
        for comic in comic_query:
            self.downloaded_files_tabel.row_data.append(
                [comic.id, comic.name, comic.series_name, comic.readlist_name]
            )

    def download_items(self, item_id="", dl_type=""):
        screen = self.manager_screens.current_screen
        for item in screen.comic_thumbs_list:
            if item.item_id == item_id:
                item.ids.download_select.icon = "download-circle"
        print(f"{dl_type =}")
        self.download_series(item_id=item_id, dl_type=dl_type)

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
        print(f"{instance_table.row_data[the_index] =}")

    @multitasking.task
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

    def unzip_content(self, req, result):
        # threading.Thread(target=self.unzip_thread).start()
        self.unzip_thread()

    @multitasking.task
    def unzip_thread(self, file_path="", series_id=""):
        app = MDApp.get_running_app()
        print("Unzipping file")
        fh = open(file_path, 'rb')
        z = zipfile.ZipFile(fh)
        for name in z.namelist():
            print('%s' % (name))

        id_folder = app.store_dir
        my_download_folder = Path(os.path.join(id_folder, "comic_files"))
        series_folder = Path(os.path.join(my_download_folder, series_id))
        if not series_folder.is_dir():
            os.makedirs(series_folder)
        ZIP_EXTRACT_FOLDER = series_folder
        if not os.path.exists(ZIP_EXTRACT_FOLDER):
            os.makedirs(ZIP_EXTRACT_FOLDER)
        z.extractall(ZIP_EXTRACT_FOLDER)
        fh.close()
        os.remove(file_path)
        print("Done")

    def got_file(self, req, *args, **kwargs):
        if len(self.table_que.row_data) != 0:
            self.table_que.remove_row(self.table_que.row_data[0])
        if len(self.download_que) != 0:
            self.do_download_books(item_id=kwargs['item_id'])
        comic_db = Comic.get(Comic.id == kwargs['book_id'])
        comic_db.file_path = kwargs['file_path']
        comic_db.save()
        in_data = False
        for item in self.downloaded_files_tabel.row_data:
            if item[0] == comic_db.id:
                in_data = True

        if not in_data:
            self.downloaded_files_tabel.row_data.append(
                [comic_db.id, comic_db.name, comic_db.series_name, comic_db.readlist_name]
            )

    @multitasking.task
    def do_download_books(self, item_id=''):
        app = MDApp.get_running_app()
        str_cookie = "SESSION=" + app.config.get("General", "api_key")
        head = {
            "Cookie": str_cookie,
        }
        id_folder = app.store_dir
        my_download_folder = Path(os.path.join(id_folder, "comic_files"))
        series_folder = Path(os.path.join(my_download_folder, item_id))
        if not series_folder.is_dir():
            os.makedirs(series_folder)
        if len(self.download_que) != 0:
            book_id = self.download_que[0]['id']
        t_file = self.download_que[0]['file_name']
        file_path = os.path.join(series_folder, t_file)
        url_send = f"{app.base_url}/api/v1/books/{book_id}/file"
        myUrlRequest(
            url_send,
            req_headers=head,
            on_success=partial(self.got_file, item_id=item_id, file_path=file_path, book_id=book_id),
            chunk_size=28192,
            on_error=self.got_error,
            on_redirect=self.got_redirect,
            on_failure=self.got_error,
            # on_progress=partial(self.on_progress, book_id=book_id),
            file_path=file_path,
            # auth=(username,password)
        )
        if len(self.download_que) != 0:
            self.download_que.pop(0)

    @multitasking.task
    def download_series(self, item_id="", dl_type=""):
        def __got_series_book_data(req, results, **kwargs):
            print(f"__got_series_book_data")
            i = 0
            series_db = kwargs['series_db']
            for item in results['content']:
                comic_db, comic_created = Comic.get_or_create(
                    id=item['id'],
                )
                if comic_created:
                    comic_db.number=item['number']
                    comic_db.page_count=item['media']['pagesCount']
                    comic_db.title=item['metadata']['title']
                    comic_db.summary=item['metadata']['summary']
                    comic_db.name=item['name']
                    comic_db.series_name=item['seriesTitle']
                if dl_type == "series":
                    if not comic_db.series:
                        comic_db.series.add(series_db)
                elif dl_type == "reading list":
                    if not comic_db.readinglists:
                        comic_db.readinglists.add(series_db)
                    comic_db.readlist_name = series_db.name
                comic_db.save()
                server_path = item['url']
                file_name = server_path.split("/")[-1]
                str_append = [f"{i}",
                              item['name'],
                              item['seriesTitle'],
                              file_name,
                              ]
                self.download_que.append(
                    {
                        "id": item['id'],
                        "file_name": file_name,
                    }
                )
                i += 1
                self.table_que.row_data.append(str_append)
            app.manager_screens.current = "download screen"
            self.do_download_books(item_id=item_id)

        def __got_series_data(req, results):
            if dl_type == "series":
                the_book_count = results['booksCount']
                db_series, created = Series.get_or_create(
                    series_id=item_id,
                )
                if created:
                    db_series.name = results['name']
                    db_series.title = results['metadata']['title']
                    db_series.booksCount = the_book_count
                    db_series. libraryId = results['libraryId']
                    db_series.save()
                    self.downloaded_series_tabel.row_data.append(
                        [results['id'], results['name'], "Series"]
                    )
                url_series_book_data = f"{app.base_url}/api/v1/series/{item_id}/books?size={the_book_count}"
            elif dl_type == "reading list":
                the_book_count = len(results['bookIds'])+1
                db_series, created = ReadingList.get_or_create(
                    readlist_id=item_id,
                )
                if created:
                    db_series.name = results['name']
                    db_series.booksCount = the_book_count
                    db_series.save()
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
