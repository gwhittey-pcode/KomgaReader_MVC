import math
import ntpath
import os
from functools import partial
from pathlib import Path

from kivy.animation import Animation
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import StringProperty, NumericProperty, ObjectProperty, DictProperty, BooleanProperty, \
    ConfigParserProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.label import Label
from kivy.utils import get_hex_from_color
from kivymd.app import MDApp
from kivy import Logger
from kivymd.material_resources import dp
from kivymd.toast import toast
from kivymd.uix.behaviors import CommonElevationBehavior, CircularRippleBehavior, RectangularRippleBehavior
from kivymd.uix.button import MDIconButton, BaseButton
from kivymd.uix.button.button import ButtonElevationBehaviour, ButtonContentsText
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.list import OneLineAvatarIconListItem, IRightBodyTouch, ILeftBodyTouch
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.widget import MDWidget

from Utility.comic_functions import save_thumb
from Utility.db_functions import ReadingList
from Utility.komga_server_conn import ComicServerConn
from Utility.myUrlrequest import UrlRequest as myUrlRequest
from View.ComicListsBaseScreen import ComicListsBaseScreenView
from View.Widgets.dialogs.dialogs import DialogLoadKvFiles
from View.Widgets.custimagelist import RLTileLabel
from View.Widgets.paginationwidgets import MyMDRaisedButton, MyMDIconRaisedButton

from kivymd.utils import asynckivy
from View.Widgets.comicthumb import ComicThumb
from View.Widgets.paginationwidgets.pagination_widgets import build_pageination_nav


class CustomMDFillRoundFlatIconButton(MDIconButton):
    pass


class Tooltip(Label):
    pass

class MDRaisedIconButton(BaseButton, ButtonElevationBehaviour, ButtonContentsText):
    """
    A flat button with (by default) a primary color fill and matching
    color text.
    """

    # FIXME: Move the underlying attributes to the :class:`~BaseButton` class.
    #  This applies to all classes of buttons that have similar attributes.
    _default_md_bg_color = None
    _default_md_bg_color_disabled = None
    _default_theme_text_color = "Custom"
    _default_text_color = "PrimaryHue"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.shadow_softness = 8
        self.shadow_offset = (0, 2)
        self.shadow_radius = self._radius * 2
class ListItemWithCheckbox(OneLineAvatarIconListItem):
    """Custom list item."""
    icon = StringProperty("android")

    def on_checkbox_active(self, checkbox, value):
        if value:
            print('The checkbox', checkbox, 'is active', 'and', checkbox.state, 'state')
            print(self.text)
        else:
            print('The checkbox', checkbox, 'is inactive', 'and', checkbox.state, 'state')


class LeftCheckbox(ILeftBodyTouch, MDCheckbox):
    """Custom right container."""


class ReadingListScreenView(ComicListsBaseScreenView):
    dynamic_ids = DictProperty({})
    comic_thumb_width = NumericProperty()
    comic_thumb_height = NumericProperty()

    def __init__(self, **kwargs):
        super(ReadingListScreenView, self).__init__(**kwargs)
        self.item_per_menu = ConfigParserProperty("", "General", "max_item_per_page",  App.get_running_app().config)
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
        self.comic_thumb_height = 240
        self.comic_thumb_width = 156
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
        self.comic_thumb_height = 240
        self.comic_thumb_width = 156
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
                    "bg_color":background_color
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
        self.get_server_lists()

    def my_width_callback(self, obj, value):
        for key, val in self.ids.items():
            if key == "main_grid":
                c = val
                c.cols = math.floor((Window.width - dp(20)) // self.app.comic_thumb_width)

    def get_server_lists(self, new_page_num=0):
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
            fetch_data = ComicServerConn()
            url_send = f"{self.base_url}/api/v1/readlists?page={new_page_num}&size={self.item_per_page}"
            fetch_data.get_server_data_callback(
                url_send,
                callback=lambda url_send, results: __get_server_lists(self, results))

    def build_paginations(self):
        build_pageination_nav(screen_name="reading list screen")

    def ltgtbutton_press(self, i):
        if i.icon == "less-than":
            self.get_server_lists(new_page_num=int(self.current_page) - 1)
        elif i.icon == "greater-than":
            self.get_server_lists(new_page_num=int(self.current_page) + 1)
    def pag_num_press(self,i):
        self.get_server_lists(new_page_num=int(i.text)-1)
    def build_page(self):
        async def _build_page():
            grid = self.m_grid
            grid.clear_widgets()
            i = 1
            # add spacer so page forms right while imgs are dl
            first_item = self.rl_comics_json[0]['id']
            for item in self.rl_comics_json:
                await asynckivy.sleep(0)
                rl_id = item['id']
                rl_book_count = len( item['bookIds'])
                self.rl_book_count = rl_book_count
                c = ComicThumb(rl_book_count=rl_book_count, rl_name=item['name'], item_id=item['id'])
                c.str_caption = f"  {item['name']} \n\n  {rl_book_count} Books"
                # c.book_ids = book_ids
                #c.tooltip_text = f"  {item['name']} \n  {rl_book_count} Books"
                c.item_id = rl_id
                c.thumb_type = "ReadingList"
                c.text_size = dp(8)
                c.lines = 2
                c.totalPages = self.totalPages
                str_name = ""
                self.dialog_load_comic_data.name_kv_file = str_name
                self.dialog_load_comic_data.percent = str(
                    i * 100 // int(self.item_per_page)
                )
                y = self.comic_thumb_height
                thumb_filename = f"{rl_id}.jpg"
                id_folder = self.app.store_dir
                my_thumb_dir = os.path.join(id_folder, "comic_thumbs")
                t_file = os.path.join(my_thumb_dir, thumb_filename)
                if os.path.isfile(t_file):
                    c_image_source = t_file
                else:
                    c_image_source = f"{self.base_url}/api/v1/readlists/{rl_id}/thumbnail"
                    asynckivy.start(save_thumb(rl_id, c_image_source))
                c.source = c_image_source

                def loaded():
                    grid.add_widget(c)

                c.on_load = (loaded())
                grid.cols = math.floor((Window.width - dp(20)) // self.app.comic_thumb_width)
                self.dynamic_ids[id] = c
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