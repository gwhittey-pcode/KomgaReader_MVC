import math

from View.ComicListsBaseScreen import ComicListsBaseScreenView

import os

from kivy.core.window import Window
from kivy.metrics import dp
from kivy.properties import StringProperty, NumericProperty, DictProperty, BooleanProperty, ObjectProperty, \
    ConfigParserProperty
from kivymd.app import MDApp
from kivymd.uix.menu import MDDropdownMenu
from kivymd.utils import asynckivy

from Utility.comic_functions import save_thumb
from Utility.comic_json_to_class import ComicList, ComicBook
from Utility.komga_server_conn import ComicServerConn
from View.Widgets.comicthumb import ComicThumb
from View.Widgets.dialogs.dialogs import DialogLoadKvFiles
from View.Widgets.paginationwidgets.pagination_widgets import build_pageination_nav


class CollectionComicsScreenView(ComicListsBaseScreenView):
    def __init__(self, **kwargs):
        super(CollectionComicsScreenView, self).__init__(**kwargs)
        self.collection_id = None
        self.item_per_menu = None
        self.app = MDApp.get_running_app()
        self.lists_loaded = BooleanProperty()
        self.lists_loaded = False
        self.base_url = self.app.base_url
        self.api_url = self.app.api_url
        self.session_cookie = self.app.config.get("General", "api_key")
        self.rl_page = 1
        self.fetch_data = None
        self.Data = ""
        self.fetch_data = ComicServerConn()
        self.dialog_load_readlist_data = None
        self.m_grid = ''
        self.bind(width=self.my_width_callback)
        self.dialog_load_comic_data = None
        self.item_per_page = self.app.config.get("General", "max_item_per_page")
        self.rl_book_count = 25
        self.totalPages = 0
        self.prev_button = ""
        self.next_button = ""
        self.last = False
        self.first = False
        self.current_page = 1
        self.loading_done = False
        self.item_per_menu_build()

        # self.filter_menu_build()

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
        self.get_server_lists(new_page_num=self.current_page)
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

    def callback_for_menu_items(self, *args):
        pass

    def on_pre_enter(self):
        self.m_grid = self.ids["main_grid"]

    def on_enter(self, *args):
        self.base_url = self.app.base_url
        self.api_url = self.app.api_url
        # self.prev_button = self.ids["prev_button"]
        # self.next_button = self.ids["next_button"]
        if self.loading_done is True:
            return
    def my_width_callback(self, obj, value):
        for key, val in self.ids.items():
            if key == "main_grid":
                c = val
                c.cols = math.floor((Window.width - dp(20)) // self.app.comic_thumb_width)

    def get_server_lists(self, new_page_num=0, collection_id=""):
        

        def __get_server_lists(self, results):
            self.rl_comics_json = results['content']
            self.rl_json = results
            self.totalPages = self.rl_json['totalPages']
            self.current_page = self.rl_json['pageable']['pageNumber']
            self.last = self.rl_json['last']
            self.first = self.rl_json['first']
            self.build_paginations()
            self.build_page()

        if self.lists_loaded is False:
            self.collection_id = collection_id
            fetch_data = ComicServerConn()
            url_send = f"{self.base_url}/api/v1/collections/{collection_id}/series" \
                       f"?page={new_page_num}&size={self.item_per_page}"
            fetch_data.get_server_data_callback(
                url_send,
                callback=lambda url_send, results: __get_server_lists(self, results))

    def build_paginations(self):
        build_pageination_nav(screen_name=self.name)

    def ltgtbutton_press(self, i):
        if i.icon == "less-than":
            self.get_server_lists(new_page_num=int(self.current_page) - 1,
                                  collection_id=self.collection_id
                                  )
        elif i.icon == "greater-than":
            self.get_server_lists(new_page_num=int(self.current_page) + 1,
                                  collection_id=self.collection_id
                                  )

    def pag_num_press(self, i):

        self.get_server_lists(new_page_num=int(i.text) - 1,
                              collection_id=self.collection_id
                              )

    def build_page(self):
        async def _build_page():
            grid = self.m_grid
            grid.clear_widgets()
            i = 1
            # add spacer so page forms right while imgs are dl
            c_spacer = ComicThumb(item_id="NOID")
            c_spacer.lines = 1
            c_spacer.padding = dp(10), dp(10)
            c_spacer.totalPages = self.totalPages
            src_thumb = "assets/spacer.jpg"
            c_spacer.source = src_thumb
            c_spacer.opacity = 0
            # grid.add_widget(c_spacer)
            first_item = self.rl_comics_json[0]['id']
            for item in self.rl_comics_json:
                await asynckivy.sleep(0)
                rl_id = item['id']
                rl_book_count = item['booksCount']
                self.rl_book_count = rl_book_count
                c = ComicThumb(rl_book_count=rl_book_count, rl_name=item['name'], item_id=item['id'])
                c.str_caption = f"  {item['name']} \n\n  {rl_book_count} Books"
                # c.book_ids = book_ids
                # c.tooltip_text = f"  {item['name']} \n  {rl_book_count} Books"
                c.item_id = rl_id
                c.thumb_type = "Series"
                c.text_size = dp(8)
                c.lines = 2
                c.totalPages = self.totalPages
                str_name = ""
                self.dialog_load_comic_data.name_kv_file = str_name
                self.dialog_load_comic_data.percent = str(
                    i * 100 // int(self.item_per_page)
                )
                y = self.app.comic_thumb_height
                thumb_filename = f"{rl_id}.jpg"
                id_folder = self.app.store_dir
                my_thumb_dir = os.path.join(id_folder, "comic_thumbs")
                t_file = os.path.join(my_thumb_dir, thumb_filename)
                if os.path.isfile(t_file):
                    c_image_source = t_file
                else:
                    c_image_source = f"{self.base_url}/api/v1/series/{rl_id}/thumbnail"
                    asynckivy.start(save_thumb(rl_id, c_image_source))
                c.source = c_image_source

                def loaded():
                    grid.add_widget(c)

                c.on_load = (loaded())
                grid.cols = math.floor((Window.width - dp(20)) // self.app.comic_thumb_width)
                i += 1
            self.loading_done = True
            self.dialog_load_comic_data.dismiss()
            scroll = self.ids.main_scroll
            for child in grid.children:
                if child.item_id == first_item:
                    scroll.scroll_to(child)

        self.dialog_load_comic_data = DialogLoadKvFiles()
        self.dialog_load_comic_data.open()
        asynckivy.start(_build_page())

    def get_page(self, instance):
        this_page = instance.page_num
        # if not self.rl_json['last']:
        #     self.next_button.opacity = 1
        #     self.next_button.disabled = False
        #     self.next_button.page_num = self.page_num + 1
        # else:
        #     self.next_button.opacity = 0
        #     self.next_button.disabled = True
        #     self.next_button.page_num = ""
        # if not self.rl_json['first']:
        #     self.prev_button.opacity = 1
        #     self.prev_button.disabled = False
        #     self.prev_button.page_num = self.page_num - 1
        # else:
        #     self.prev_button.opacity = 0
        #     self.prev_button.disabled = True
        #     self.prev_button.page_num = ""
        self.get_server_lists(new_page_num=this_page)

    def model_is_changed(self) -> None:
        """
        Called whenever any change has occurred in the data model.
        The view in this method tracks these changes and updates the UI
        according to these changes.
        """
