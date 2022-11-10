import inspect
import math
import urllib

from kivy import Logger
from kivymd.toast import toast

from Utility.items_per_page_menu import item_per_menu_build
from View.ComicListsBaseScreen import ComicListsBaseScreenView
import os
from kivy.app import App
from kivy.core.window import Window
from kivy.properties import \
    StringProperty, NumericProperty, ObjectProperty, DictProperty, \
    BooleanProperty, ConfigParserProperty
from kivymd.app import MDApp
from kivymd.material_resources import dp
from kivymd.uix.menu import MDDropdownMenu
from Utility.comic_functions import save_thumb
from Utility.komga_server_conn import ComicServerConn
from View.Widgets.dialogs.dialogs import DialogLoadKvFiles
from kivymd.utils import asynckivy
from View.Widgets.comicthumb import ComicThumb
from View.Widgets.paginationwidgets.pagination_widgets import build_pageination_nav
from Utility.myUrlrequest import UrlRequest as myUrlRequest

class SeriesScreenView(ComicListsBaseScreenView):
    dynamic_ids = DictProperty({})
    comic_thumb_width = NumericProperty()
    comic_thumb_height = NumericProperty()

    def __init__(self, **kwargs):
        super(SeriesScreenView, self).__init__(**kwargs)
        self.app = MDApp.get_running_app()
        self.lists_loaded = BooleanProperty()
        self.lists_loaded = False
        self.rl_page = 1
        self.Data = ""
        self.fetch_data = ComicServerConn()
        self.dialog_load_readlist_data = None
        self.m_grid = ''
        self.bind(width=self.my_width_callback)
        self.dialog_load_comic_data = None
        self.totalPages = 0
        self.last = False
        self.first = False
        self.current_page = 1
        self.loading_done = False
        self.page_title = "Series"
        self.page_year = ""

    def filter_menu_callback(self, text_item):
        self.filter_menu.dismiss()

    def callback_for_menu_items(self, *args):
        pass

    def on_enter(self, *args):
        self.m_grid = self.ids["main_grid"]
        if self.loading_done is True:
            return
        self.app = MDApp.get_running_app()
        self.item_per_page = self.app.config.get("General", "max_item_per_page")
        self.base_url = self.app.base_url
        print(self.app.letter_count["#"])

        self.get_server_lists()

    def my_width_callback(self, obj, value):
        for key, val in self.ids.items():
            if key == "main_grid":
                c = val
                c.cols = math.floor((Window.width - dp(20)) // self.app.comic_thumb_width)

    def get_server_lists(self, new_page_num=0):
        def __get_server_lists(req,results):
            t_rl_comics_json = ""
            t_rl_comics_json = results['content']
            print(f"{t_rl_comics_json =}")
            if not t_rl_comics_json:
                toast("No Items Found with Filter Settings")
                return
            self.rl_comics_json = results['content']
            self.rl_json = results
            self.totalPages = self.rl_json['totalPages']
            self.current_page = self.rl_json['pageable']['pageNumber']
            self.last = self.rl_json['last']
            self.first = self.rl_json['first']
            self.build_paginations()
            t_rl_comics_json = ""
            self.tmp_fetch = ""
            asynckivy.start(self.build_page())

        if self.lists_loaded is False:
            fetch_data = ComicServerConn()
            url_send = f"{self.base_url}/api/v1/series?page={new_page_num}&size={self.item_per_page}"
            if len(self.app.filter_string) != 0:
                url_send = f"{url_send}{self.app.filter_string}"
            if self.filter_letter != "All":
                if self.filter_letter == "#":
                    search_regex = "&search_regex=%5E%28%5B0-9%5D%29%2CTITLE"
                else:
                    part_rex = f"^{self.filter_letter},TITLE"
                    search_regex = f"&search_regex={urllib.parse.quote(part_rex)}"
                url_send = f"{url_send}{search_regex}"
                url_send = url_send.replace(" ", "")
            print(f"{url_send =}")
            str_cookie = "SESSION=" + self.app.config.get("General", "api_key")
            head = {
                "Content-type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
                "Cookie": str_cookie,
            }

            myUrlRequest(
                url_send,
                req_headers=head,
                on_success=__get_server_lists,
                on_error=self.got_error,
                on_redirect=self.got_redirect,
                on_failure=self.got_error,
                # auth=(username,password)
            )

    def build_paginations(self):
        build_pageination_nav(screen_name=self.name)

    def ltgtbutton_press(self, i):
        if i.icon == "less-than":
            self.get_server_lists(new_page_num=int(self.current_page) - 1)
        elif i.icon == "greater-than":
            self.get_server_lists(new_page_num=int(self.current_page) + 1)

    def pag_num_press(self, i):
        self.get_server_lists(new_page_num=int(i.text) - 1)

    async def build_page(self):
        self.dialog_load_comic_data = DialogLoadKvFiles()
        self.dialog_load_comic_data.open()
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
            self.dynamic_ids[id] = c
            i += 1
        self.loading_done = True
        self.dialog_load_comic_data.dismiss()
        scroll = self.ids.main_scroll
        for child in grid.children:
            if child.item_id == first_item:
                scroll.scroll_to(child)

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

    def model_is_changed(self) -> None:
        """
        Called whenever any change has occurred in the data model.
        The view in this method tracks these changes and updates the UI
        according to these changes.
        """
