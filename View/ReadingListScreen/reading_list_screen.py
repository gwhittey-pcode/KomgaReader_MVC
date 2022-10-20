import ntpath
import os
from functools import partial
from pathlib import Path

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import StringProperty, NumericProperty, ObjectProperty, DictProperty, BooleanProperty
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
from View.Widgets.dialogs.dialogs import DialogLoadKvFiles
from View.Widgets.custimagelist import RLTileLabel
from View.Widgets.paginationwidgets import MyMDRaisedButton, MyMDIconRaisedButton
from View.base_screen import BaseScreenView
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


class ReadingListScreenView(BaseScreenView):
    dynamic_ids = DictProperty({})
    comic_thumb_width = NumericProperty()
    comic_thumb_height = NumericProperty()

    def __init__(self, **kwargs):
        super(ReadingListScreenView, self).__init__(**kwargs)
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
        self.comic_thumb_height = 240
        self.comic_thumb_width = 156
        self.m_grid = ''
        self.bind(width=self.my_width_callback)
        self.dialog_load_comic_data = None
        self.rl_count = 20
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
        self.filter_menu_build()


    def item_per_menu_build(self):
        item_per_menu_numbers = ("20", "50", "100", "200", "500")
        item_per_menu_items = [
            {
                "text": f"{nums}",
                "viewclass": "OneLineListItem",
                "on_release": lambda x=f"{nums}": self.item_per_menu_callback(x),
            } for nums in item_per_menu_numbers
        ]
        self.item_per_menu = MDDropdownMenu(
            caller=self.ids.item_per_menu_button,
            items=item_per_menu_items,
            width_mult=1.6,
            radius=[24, 0, 24, 0],
            max_height=dp(240)
        )

    def item_per_menu_callback(self, text_item):
        self.item_per_menu.dismiss()
        self.rl_count = int(text_item)
        self.get_comicrack_list(new_page_num=1)

    def filter_menu_build(self):
        def __got_publisher_data(results):
            filter_menu_items = results
            item_per_menu_items = [
                {
                    "text": f"{item}",
                    "viewclass": "ListItemWithCheckbox",
                    "on_release": lambda x=f"{item}": self.filter_menu_callback(x),
                } for item in filter_menu_items
            ]
            self.filter_menu = MDDropdownMenu(
                caller=self.ids.filter_menu_button,
                items=item_per_menu_items,
                width_mult=5,
                # max_height=dp(240)
            )

        fetch_data = ComicServerConn()
        url_send = f"{self.base_url}/api/v1/publishers"
        fetch_data.get_server_data_callback(
            url_send,
            callback=lambda url_send, results: __got_publisher_data(results))

    def filter_menu_callback(self, text_item):
        self.filter_menu.dismiss()
        print(text_item)



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
        self.get_comicrack_list()

    def my_width_callback(self, obj, value):
        for key, val in self.ids.items():
            if key == "main_grid":
                c = val
                c.cols = (Window.width - 10) // self.comic_thumb_width

    def get_comicrack_list(self, new_page_num=0):
        def __got_readlist_data(self, results):
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
            url_send = f"{self.base_url}/api/v1/readlists?page={new_page_num}&size={self.rl_count}"
            print(url_send)
            fetch_data.get_server_data_callback(
                url_send,
                callback=lambda url_send, results: __got_readlist_data(self, results))

    def build_paginations(self):
        build_pageination_nav()

    def ltgtbutton_press(self, i):
        if i.icon == "less-than":
            self.get_comicrack_list(new_page_num=int(self.current_page) - 1)
        elif i.icon == "greater-than":
            self.get_comicrack_list(new_page_num=int(self.current_page) + 1)
    def pag_num_press(self,i):
        self.get_comicrack_list(new_page_num=int(i.text)-1)
    def build_page(self):
        async def _build_page():
            grid = self.m_grid
            grid.clear_widgets()
            i = 1
            # add spacer so page forms right while imgs are dl
            c_spacer = ComicThumb(item_id="NOID")
            c_spacer.lines = 1
            c_spacer.padding = dp(60), dp(60)
            c_spacer.totalPages = self.totalPages
            src_thumb = "assets/spacer.jpg"
            c_spacer.source = src_thumb
            c_spacer.opacity = 0
            grid.add_widget(c_spacer)
            first_item = self.rl_comics_json[0]['id']
            for item in self.rl_comics_json:
                await asynckivy.sleep(0)
                rl_id = item['id']
                x = 0
                for bookID in item['bookIds']:
                    x += 1
                rl_book_count = x
                self.rl_book_count = rl_book_count
                strCookie = 'SESSION=' + self.session_cookie
                c = ComicThumb(rl_book_count=rl_book_count, rl_name=item['name'], item_id=item['id'])
                c.str_caption = f"  {item['name']} \n\n  {rl_book_count} Books"
                #c.tooltip_text = f"  {item['name']} \n  {rl_book_count} Books"
                c.item_id = rl_id
                c.thumb_type = "ReadingList"
                c.text_size = dp(8)
                c_spacer.lines = 1
                c_spacer.padding = dp(20), dp(20)
                c.totalPages = self.totalPages
                # c.extra_headers = {"X-Auth-Token":"fbdd4f69-274d-4fd4-ad58-0932d20e37f6",}
                # c.readinglist_obj = self.new_readinglist
                str_name = ""
                self.dialog_load_comic_data.name_kv_file = str_name
                self.dialog_load_comic_data.percent = str(
                    i * 100 // int(self.rl_count)
                )
                y = self.comic_thumb_height
                thumb_filename = f"{rl_id}.jpg"
                id_folder = self.app.store_dir
                my_thumb_dir = os.path.join(id_folder, "comic_thumbs")
                t_file = os.path.join(my_thumb_dir, thumb_filename)
                if os.path.isfile(t_file):
                    c_image_source = t_file
                else:
                    part_url = f"/api/v1/readlists/{rl_id}/thumbnail"
                    c_image_source = f"{self.base_url}{part_url}"
                    asynckivy.start(save_thumb(rl_id, c_image_source))
                c.source = c_image_source

                def loaded():
                    grid.add_widget(c)

                c.on_load = (loaded())
                grid.cols = (Window.width - 30) // self.comic_thumb_width
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
        print(this_page)
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
        self.get_comicrack_list(new_page_num=this_page)

    def model_is_changed(self) -> None:
        """
        Called whenever any change has occurred in the data model.
        The view in this method tracks these changes and updates the UI
        according to these changes.
        """
