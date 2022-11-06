import math
import os
import urllib.parse

from kivy.app import App
from kivy.core.window import Window
from kivy.properties import StringProperty, NumericProperty, ObjectProperty, DictProperty, BooleanProperty, \
    ConfigParserProperty
from kivy.uix.label import Label
from kivymd.app import MDApp
from kivymd.material_resources import dp
from kivymd.uix.button import MDIconButton, BaseButton
from kivymd.uix.button.button import ButtonElevationBehaviour, ButtonContentsText
from kivymd.uix.list import OneLineAvatarIconListItem, IRightBodyTouch, ILeftBodyTouch
from kivymd.uix.selectioncontrol import MDCheckbox
from Utility.comic_functions import save_thumb
from Utility.komga_server_conn import ComicServerConn
from View.Widgets.dialogs.dialogs import DialogLoadKvFiles
from kivymd.utils import asynckivy
from View.Widgets.comicthumb import ComicThumb
from View.Widgets.paginationwidgets.pagination_widgets import build_pageination_nav
from View.ComicListsBaseScreen import ComicListsBaseScreenView


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





class ObjectListScreenView(ComicListsBaseScreenView):
    dynamic_ids = DictProperty({})
    comic_thumb_width = NumericProperty()
    comic_thumb_height = NumericProperty()
    page_year = StringProperty("")
    page_title = StringProperty("")
    item_per_page = StringProperty()
    base_url = StringProperty()
    app = ObjectProperty()
    def __init__(self, **kwargs):
        super(ObjectListScreenView, self).__init__(**kwargs)
        self.object_type = None


        self.app = MDApp.get_running_app()
        self.item_per_menu = self.app.config.get("General", "max_item_per_page")
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
        self.page_year=""


    def callback_for_menu_items(self, *args):
        pass

    def on_enter(self):
        self.m_grid = self.ids["main_grid"]
        if self.loading_done is True:
            return
        self.app = MDApp.get_running_app()
        self.item_per_page = self.app.config.get("General", "max_item_per_page")
        self.base_url = self.app.base_url




    def setup_screen(self,object_type="Reading List"):
        self.session_cookie = self.app.config.get("General", "api_key")
        self.main_stack = self.ids["main_stack"]
        self.m_grid = self.ids["main_grid"]
        self.object_type = object_type
        self.get_server_lists()

    def my_width_callback(self, obj, value):
        for key, val in self.ids.items():
            if key == "main_grid":
                c = val
                c.cols = math.floor((Window.width - dp(20)) // self.app.comic_thumb_width)

    def get_server_lists(self, new_page_num=0):
        def __get_server_lists(results):
            self.rl_comics_json = results['content']
            self.rl_json = results
            self.totalPages = self.rl_json['totalPages']
            self.current_page = self.rl_json['pageable']['pageNumber']
            self.last = self.rl_json['last']
            self.first = self.rl_json['first']
            self.build_paginations()
            self.build_page()

        if self.object_type == "Reading List":
            self.page_title = "Reading Lists"
            url_send = f"{self.base_url}/api/v1/readlists?page={new_page_num}&size={str(self.item_per_page)}"
        elif self.object_type == "Series List":
            self.page_title = "Series Lists"
            url_send = f"{self.base_url}/api/v1/series?page={new_page_num}" \
                       f"&size={str(self.item_per_page)}"
            if len(self.app.filter_string)!=0:
                add_filter_string =""
                for publisher in self.app.filter_string:
                    s_pb = f"{publisher}"
                    add_filter_string += f"&publisher={urllib.parse.quote(s_pb)}"
                url_send = f"{url_send}{add_filter_string}"
        elif self.object_type == "Collection List":
            self.page_title = "Collection Lists"
            url_send = f"{self.base_url}/api/v1/collections?page={new_page_num}&size={str(self.item_per_page)}"
        if self.lists_loaded is False:
            fetch_data = ComicServerConn()
            fetch_data.get_server_data_callback(
                url_send,
                callback=lambda url_send, results: __get_server_lists(results))

    def build_paginations(self):
        build_pageination_nav(screen_name="object list screen")

    def ltgtbutton_press(self, i):
        if i.icon == "less-than":
            self.get_server_lists(new_page_num=int(self.current_page) - 1)
        elif i.icon == "greater-than":
            self.get_server_lists(new_page_num=int(self.current_page) + 1)

    def pag_num_press(self, i):
        self.get_server_lists(new_page_num=int(i.text) - 1)

    def build_page(self):
        async def _build_page():
            grid = self.m_grid
            grid.clear_widgets()
            i = 1
            # add spacer so page forms right while imgs are dl
            first_item = self.rl_comics_json[0]['id']
            for item in self.rl_comics_json:
                await asynckivy.sleep(0)

                c = ComicThumb(rl_name=item['name'], item_id=item['id'])
                rl_book_count = 0
                rl_id = item['id']
                if self.object_type == "Reading List":
                    rl_book_count = len(item['bookIds'])
                    c.str_caption = f"  {item['name']} \n\n  {rl_book_count} Books"
                elif self.object_type == "Series List":
                    rl_book_count = int(item['booksCount'])
                    c.str_caption = f"  {item['name']} \n\n  {rl_book_count} Books"
                elif self.object_type == "Collection List":
                    rl_book_count = len(item['seriesIds'])
                    c.str_caption = f"  {item['name']} \n\n  {rl_book_count} Series"
                self.rl_book_count = rl_book_count
                c.rl_book_count = rl_book_count
                c.current_page = self.current_page
                # c.book_ids = book_ids
                # c.tooltip_text = f"  {item['name']} \n  {rl_book_count} Books"
                c.item_id = rl_id
                c.thumb_type = self.object_type
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
                    if self.object_type == "Reading List":
                        url_image = f"{self.base_url}/api/v1/readlists/{rl_id}/thumbnail"
                    elif self.object_type == "Series List":
                        url_image = f"{self.base_url}/api/v1/series/{rl_id}/thumbnail"
                    elif self.object_type == "Collection List":
                        url_image = f"{self.base_url}/api/v1/collections/{rl_id}/thumbnail"
                    c_image_source = url_image
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
