import math

from View.ComicListsBaseScreen import ComicListsBaseScreenView

import os

from kivy.core.window import Window
from kivy.metrics import dp
from kivy.properties import StringProperty, NumericProperty, DictProperty, BooleanProperty, ObjectProperty
from kivymd.app import MDApp
from kivymd.uix.menu import MDDropdownMenu
from kivymd.utils import asynckivy

from Utility.comic_functions import save_thumb
from Utility.comic_json_to_class import ComicList, ComicBook
from Utility.komga_server_conn import ComicServerConn
from View.Widgets.comicthumb import ComicThumb
from View.Widgets.dialogs.dialogs import DialogLoadKvFiles
from View.Widgets.paginationwidgets.pagination_widgets import build_pageination_nav


class SeriesComicsScreenView(ComicListsBaseScreenView):
    reading_list_title = StringProperty()
    page_number = NumericProperty()
    max_item_per_page = NumericProperty()
    dynamic_ids = DictProperty({})  # declare class attribute, dynamic_ids
    sync_bool = BooleanProperty(False)
    so = BooleanProperty()
    new_series = ObjectProperty()
    comic_thumb_height = NumericProperty()
    comic_thumb_width = NumericProperty()

    def __init__(self, **kwargs):
        super(SeriesComicsScreenView, self).__init__(**kwargs)
        self.sync_options = None
        self.app = MDApp.get_running_app()
        self.fetch_data = None
        self.series_Id = StringProperty()
        self.series_name = ""
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
        self.item_per_menu_build()
        # self.filter_menu_build()
        self.rl_comics_json = ""
        self.next_series = ObjectProperty()
        self.prev_series = ObjectProperty()

    def setup_screen(self):
        self.session_cookie = self.app.config.get("General", "api_key")
        self.main_stack = self.ids["main_stack"]
        self.m_grid = self.ids["main_grid"]

    def collect_series_data(
            self,
            series_name="",
            series_Id="",
            mode="From Server",
            current_page_num=1,
            rl_book_count=10,
            new_page_num=0,

            *largs,
    ):
        """Collect Reaing List Date From Server """

        async def collect_series_data():
            self.series_name = series_name
            # self.app.set_screen(self.series_name + " Page 1")
            self.reading_list_title = self.series_name + " Page 1"
            self.series_Id = series_Id
            self.page_number = current_page_num
            self.new_page_num = new_page_num
            fetch_data = ComicServerConn()
            url_send_current = f"{self.base_url}/api/v1/series/{self.series_Id}/books?page={new_page_num}&size={self.item_per_page}"
            print(f"{url_send_current}")
            fetch_data.get_server_data(url_send_current, self)

        asynckivy.start(collect_series_data())

    def got_json2(self, req, results):
        async def _got_json():
            self.rl_comics_json = results['content']
            self.rl_json = results
            self.totalPages = self.rl_json['totalPages']
            self.current_page = self.rl_json['pageable']['pageNumber']
            self.last = self.rl_json['last']
            self.first = self.rl_json['first']
            self.build_paginations()
            if not self.first:
                self.get_prev_reading_list_page()
            if not self.last:
                self.get_next_reading_list_page()
            self.new_series = ComicList(
                name=self.series_name,
                data=results,
                slug=self.series_Id,
            )
            total_count = self.new_series.totalCount
            i = 1
            for item in self.new_series.comic_json:
                await asynckivy.sleep(0)
                str_name = "{} #{}".format(item["seriesTitle"], item["number"])
                self.dialog_load_comic_data.name_kv_file = str_name
                self.dialog_load_comic_data.percent = str(
                    i * 100 // int(total_count)
                )
                comic_index = self.new_series.comic_json.index(item)
                new_comic = ComicBook(
                    item,
                    readlist_obj=self.new_series,
                    comic_index=comic_index,
                )
                if new_comic not in self.new_series.comics:
                    self.new_series.add_comic(new_comic)
                i += 1
            new_series_reversed = self.new_series.comics[::-1]

            self.build_page(new_series_reversed)
            self.list_loaded = True
            self.dialog_load_comic_data.dismiss()

        self.dialog_load_comic_data = DialogLoadKvFiles()
        self.dialog_load_comic_data.open()
        asynckivy.start(_got_json())

    def get_next_reading_list_page(self):
        def __get_next_reading_list_page(self, results):
            next_rl_comics_json = results['content']
            next_series = ComicList(
                name=self.series_name,
                data=results,
                slug=self.series_Id,
            )
            total_count = self.new_series.totalCount
            i = 1
            for item in next_rl_comics_json:
                str_name = "{} #{}".format(item["seriesTitle"], item["number"])
                self.dialog_load_comic_data.name_kv_file = str_name
                self.dialog_load_comic_data.percent = str(
                    i * 100 // int(total_count)
                )
                comic_index = next_series.comic_json.index(item)
                new_comic = ComicBook(
                    item,
                    readlist_obj=next_series,
                    comic_index=comic_index,
                )
                if new_comic not in next_series.comics:
                    next_series.add_comic(new_comic)
                i += 1
            self.next_series = next_series

        fetch_data = ComicServerConn()
        url_send_next = f"{self.base_url}/api/v1/series/{self.series_Id}/books?page={self.new_page_num + 1}&size={self.item_per_page}"
        fetch_data.get_server_data_callback(
            url_send_next,
            callback=lambda url_send, results: __get_next_reading_list_page(self, results))

    def get_prev_reading_list_page(self):
        def __get_prev_reading_list_page(self, results):
            prev_rl_comics_json = results['content']
            prev_series = ComicList(
                name=self.series_name,
                data=results,
                slug=self.series_Id,
            )
            total_count = self.new_series.totalCount
            i = 1
            for item in prev_rl_comics_json:
                str_name = "{} #{}".format(item["seriesTitle"], item["number"])
                self.dialog_load_comic_data.name_kv_file = str_name
                self.dialog_load_comic_data.percent = str(
                    i * 100 // int(total_count)
                )
                comic_index = prev_series.comic_json.index(item)
                new_comic = ComicBook(
                    item,
                    readlist_obj=prev_series,
                    comic_index=comic_index,
                )
                if new_comic not in prev_series.comics:
                    prev_series.add_comic(new_comic)
                i += 1
            self.prev_series = prev_series

        fetch_data = ComicServerConn()
        url_send_next = f"{self.base_url}/api/v1/series/{self.series_Id}/books?page={self.new_page_num - 1}&size={self.item_per_page}"
        fetch_data.get_server_data_callback(
            url_send_next,
            callback=lambda url_send, results: __get_prev_reading_list_page(self, results))

    def build_paginations(self):
        build_pageination_nav(screen_name=self.name)

    def build_page(self, comiclist_obj):
        async def _build_page():
            grid = self.m_grid
            grid.clear_widgets()
            # add spacer so page forms right while lmgs are dl
            c_spacer = ComicThumb(item_id="NOID")
            c_spacer.lines = 1
            c_spacer.padding = dp(10), dp(10)
            src_thumb = "assets/spacer.jpg"
            c_spacer.source = src_thumb
            grid.add_widget(c_spacer)
            c_spacer.opacity = 0
            for comic in comiclist_obj:
                await asynckivy.sleep(0)
                str_cookie = 'SESSION=' + self.session_cookie
                c = ComicThumb(item_id=comic.Id, comic_obj=comic)
                c.lines = 2
                c.comiclist_obj = self.new_series
                c.paginator_obj = self.paginator_obj
                c.str_caption = f"  {comic.Series} \n  #{comic.Number} - {comic.Title[:12]}... \n  {comic.PageCount} Pages"
                # c.tooltip_text = f"{comic.Series}\n#{comic.Number} - {comic.Title}"
                c.thumb_type = "ComicBook"
                c.comic_list_type = "series"
                c.text_size = dp(8)
                c.current_page = self.current_page
                c.first = self.first
                c.last = self.last
                c.totalPages = self.totalPages
                c.item_per_page = self.item_per_page
                y = self.comic_thumb_height
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
            self.collect_series_data(new_page_num=int(self.current_page) - 1, series_Id=self.series_Id)
        elif i.icon == "greater-than":
            self.collect_series_data(new_page_num=int(self.current_page) + 1, series_Id=self.series_Id)

    def pag_num_press(self, i):
        self.collect_series_data(new_page_num=int(i.text) - 1, series_Id=self.series_Id)

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

    def item_per_menu_build(self):
        item_per_menu_numbers = ("20", "50", "100", "200", "500")
        item_per_menu_items = []
        for nums in item_per_menu_numbers:
            if int(nums) == int(self.item_per_page):
                background_color = self.app.theme_cls.primary_color
            else:
                background_color = (1, 1, 1, 1)
            item_per_menu_items.append(
                {
                    "text": f"{nums}",
                    "viewclass": "OneLineListItem",
                    "on_release": lambda x=f"{nums}": self.item_per_menu_callback(x),
                    "bg_color": background_color
                }
            )

        self.item_per_menu = MDDropdownMenu(
            caller=self.ids.item_per_menu_button,
            items=item_per_menu_items,
            width_mult=1.6,
            radius=[24, 0, 24, 0],
            max_height=dp(240),
        )

    def item_per_menu_callback(self, text_item):
        self.item_per_menu.dismiss()
        self.item_per_page = int(text_item)
        self.app.config.set("General", "max_item_per_page", self.item_per_page)
        self.app.config.write()
        self.collect_series_data(current_page_num=self.current_page, series_Id=self.series_Id)
        self.item_per_menu_build()

    # def filter_menu_build(self):
    #     def __got_publisher_data(results):
    #         filter_menu_items = results
    #         item_per_menu_items = [
    #             {
    #                 "text": f"{item}",
    #                 "viewclass": "ListItemWithCheckbox",
    #                 "on_release": lambda x=f"{item}": self.filter_menu_callback(x),
    #             } for item in filter_menu_items
    #         ]
    #         self.filter_menu = MDDropdownMenu(
    #             caller=self.ids.filter_menu_button,
    #             items=item_per_menu_items,
    #             width_mult=5,
    #             # max_height=dp(240)
    #         )
    #
    #     fetch_data = ComicServerConn()
    #     url_send = f"{self.base_url}/api/v1/publishers"
    #     fetch_data.get_server_data_callback(
    #         url_send,
    #         callback=lambda url_send, results: __got_publisher_data(results))

    def filter_menu_callback(self, text_item):
        self.filter_menu.dismiss()

    def model_is_changed(self) -> None:
        """
        Called whenever any change has occurred in the data model.
        The view in this method tracks these changes and updates the UI
        according to these changes.
        """
