import math
import os

from kivy.core.window import Window
from kivy.metrics import dp
from kivy.properties import StringProperty, NumericProperty, DictProperty, BooleanProperty, ObjectProperty
from kivymd.app import MDApp
from kivymd.uix.menu import MDDropdownMenu
from kivymd.utils import asynckivy

from Utility.comic_functions import save_thumb
from Utility.comic_json_to_class import ComicList, ComicBook
from Utility.items_per_page_menu import item_per_menu_build
from Utility.komga_server_conn import ComicServerConn
from View.ComicListsBaseScreen import ComicListsBaseScreenView
from View.Widgets.comicthumb import ComicThumb
from View.Widgets.dialogs.dialogs import DialogLoadKvFiles
from View.Widgets.paginationwidgets.pagination_widgets import build_pageination_nav


class RLComicBooksScreenView(ComicListsBaseScreenView):
    reading_list_title = StringProperty()
    page_number = NumericProperty()
    max_item_per_page = StringProperty()
    dynamic_ids = DictProperty({})  # declare class attribute, dynamic_ids
    sync_bool = BooleanProperty(False)
    so = BooleanProperty()
    new_readinglist = ObjectProperty()
    comic_thumb_height = NumericProperty()
    comic_thumb_width = NumericProperty()

    def __init__(self, **kwargs):
        super(RLComicBooksScreenView, self).__init__(**kwargs)
        self.sync_options = None
        self.app = MDApp.get_running_app()
        self.fetch_data = None
        self.readinglist_Id = StringProperty()
        self.readinglist_name = ""
        self.bind(width=self.my_width_callback)
        self.m_grid = ""
        self.main_stack = ""
        self.prev_button = ""
        self.next_button = ""
        self.base_url = self.app.base_url
        self.api_url = self.app.api_url
        self.session_cookie = self.app.config.get("General", "api_key")
        self.list_count = ""
        self.paginator_obj = ObjectProperty()
        self.current_page = NumericProperty(1)
        self.list_loaded = BooleanProperty()
        self.page_number = 1
        self.list_loaded = False
        self.comic_thumb_height = 240
        self.comic_thumb_width = 156
        self.file_download = True
        self.num_file_done = 0
        self.max_item_per_page = self.app.max_item_per_page
        self.please_wait_dialog = None
        self.dialog_load_comic_data = None
        self.item_per_page = self.app.config.get("General", "max_item_per_page")
        self.item_per_menu = None

        # self.filter_menu_build()
        self.rl_comics_json = ""
        self.next_readinglist = ObjectProperty()
        self.prev_readinglist = ObjectProperty()

    def setup_screen(self):
        self.session_cookie = self.app.config.get("General", "api_key")
        self.main_stack = self.ids["main_stack"]
        self.m_grid = self.ids["main_grid"]

    def collect_readinglist_data(
            self,
            readinglist_name="",
            readinglist_Id="",
            mode="From Server",
            current_page_num=1,
            rl_book_count=10,
            new_page_num=0,

            *largs,
    ):
        """Collect Reaing List Date From Server """

        async def collect_readinglist_data():
            self.readinglist_name = readinglist_name
            # self.app.set_screen(self.readinglist_name + " Page 1")
            self.reading_list_title = self.readinglist_name + " Page 1"
            self.page_title = self.readinglist_name
            self.toolbar_tittle = self.page_title
            self.readinglist_Id = readinglist_Id
            self.page_number = current_page_num
            self.new_page_num = new_page_num
            fetch_data = ComicServerConn()
            url_send_current = f"{self.base_url}/api/v1/readlists/{self.readinglist_Id}/books?page={new_page_num}&size={self.item_per_page}"
            fetch_data.get_server_data(url_send_current, self)

        asynckivy.start(collect_readinglist_data())

    def got_json2(self, req, results):
        async def _got_json():
            self.rl_comics_json = results['content']
            self.rl_json = results
            self.totalPages = self.rl_json['totalPages']
            self.current_page = self.rl_json['pageable']['pageNumber']
            self.last = self.rl_json['last']
            self.first = self.rl_json['first']
            self.build_paginations()
            self.new_readinglist = ComicList(
                name=self.readinglist_name,
                data=results,
                slug=self.readinglist_Id,
            )
            total_count = self.new_readinglist.totalCount
            i = 1
            for item in self.new_readinglist.comic_json:
                await asynckivy.sleep(0)
                str_name = "{} #{}".format(item["seriesTitle"], item["number"])
                self.dialog_load_comic_data.name_kv_file = str_name
                self.dialog_load_comic_data.percent = str(
                    i * 100 // int(total_count)
                )
                comic_index = self.new_readinglist.comic_json.index(item)
                new_comic = ComicBook(
                    item,
                    readlist_obj=self.new_readinglist,
                    comic_index=comic_index,
                )
                if new_comic not in self.new_readinglist.comics:
                    self.new_readinglist.add_comic(new_comic)
                i += 1
            new_readinglist_reversed = self.new_readinglist.comics[::-1]

            self.build_page(new_readinglist_reversed)
            self.list_loaded = True
            self.dialog_load_comic_data.dismiss()

        self.dialog_load_comic_data = DialogLoadKvFiles()
        self.dialog_load_comic_data.open()
        asynckivy.start(_got_json())

    def build_paginations(self):
        build_pageination_nav(screen_name="r l comic books screen")

    def build_page(self, comiclist_obj):
        async def _build_page():
            grid = self.m_grid
            grid.clear_widgets()
            for comic in comiclist_obj:
                await asynckivy.sleep(0)
                c = ComicThumb(item_id=comic.Id, comic_obj=comic)
                c.lines = 2
                c.comiclist_obj = self.new_readinglist
                c.next_readinglist = self.next_readinglist
                c.prev_readinglist = c.prev_readinglist
                c.paginator_obj = self.paginator_obj
                c.str_caption = f"  {comic.Series} \n  #{comic.Number} - {comic.Title[:12]}... \n  {comic.PageCount} Pages"
                c.thumb_type = "ComicBook"
                c.comic_list_type = "reading_list_comic_books"
                c.text_size = dp(8)
                c.current_page = self.current_page
                c.first = self.first
                c.last = self.last
                c.totalPages = self.totalPages
                thumb_filename = f"{comic.Id}.jpg"
                id_folder = self.app.store_dir
                my_thumb_dir = os.path.join(id_folder, "comic_thumbs")
                t_file = os.path.join(my_thumb_dir, thumb_filename)
                if os.path.isfile(t_file):
                    c_image_source = t_file
                else:
                    c_image_source = f"{self.base_url}/api/v1/books/{comic.Id}/thumbnail"
                    asynckivy.start(save_thumb(comic.Id, c_image_source))
                c.source = c_image_source

                def loaded():
                    grid.add_widget(c)

                c.on_load = (loaded())
                c.PageCount = comic.PageCount
                c.pag_pagenum = self.current_page
                grid.cols = math.floor((Window.width - dp(20)) // self.app.comic_thumb_width)
                self.dynamic_ids[id] = c

            self.loading_done = True

        asynckivy.start(_build_page())

    def ltgtbutton_press(self, i):
        if i.icon == "less-than":
            self.collect_readinglist_data(new_page_num=int(self.current_page) - 1,
                                          readinglist_Id=self.readinglist_Id)
        elif i.icon == "greater-than":
            self.collect_readinglist_data(new_page_num=int(self.current_page) + 1, readinglist_Id=self.readinglist_Id)

    def pag_num_press(self, i):
        self.collect_readinglist_data(new_page_num=int(i.text) - 1, readinglist_Id=self.readinglist_Id)

    def page_turn(self, c_id, new_user_last_page_read):
        grid = self.m_grid
        for child in grid.children:
            try:
                if child.comic_obj:
                    if child.comic_obj.Id == c_id:
                        if new_user_last_page_read == 0:
                            child.percent_read = 0
                        else:
                            child.percent_read = round(
                                new_user_last_page_read
                                / (child.comic_obj.PageCount - 1)
                                * 100
                            )
                        child.page_count_text = f"{child.percent_read}%"
            except:
                print(child)

    def my_width_callback(self, obj, value):
        for key, val in self.ids.items():
            if key == "main_grid":
                c = val
                c.cols = math.floor((Window.width - dp(20)) // self.app.comic_thumb_width)


    def model_is_changed(self) -> None:
        """
        Called whenever any change has occurred in the data model.
        The view in this method tracks these changes and updates the UI
        according to these changes.
        """
