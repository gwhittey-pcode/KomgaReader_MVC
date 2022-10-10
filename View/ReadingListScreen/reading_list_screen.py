import os
from functools import partial

from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import StringProperty, NumericProperty, ObjectProperty, DictProperty, BooleanProperty
from kivy.uix.label import Label
from kivy.utils import get_hex_from_color
from kivymd.app import MDApp
from kivy import Logger
from kivymd.material_resources import dp
from kivymd.uix.button import MDIconButton

from Utility.comic_functions import save_thumb
from Utility.db_functions import ReadingList
from Utility.server_conn import ComicServerConn
from Utility.myUrlrequest import UrlRequest as myUrlRequest
from View.Widgets.dialogs.dialogs import DialogLoadKvFiles
from View.Widgets.myimagelist import RLTileLabel
from View.base_screen import BaseScreenView
from kivymd.utils import asynckivy

import inspect

class ReadingListImage(RLTileLabel):
    rl_name = StringProperty()
    rl_book_count = NumericProperty()
    rl_id = StringProperty()
    my_clock = ObjectProperty()
    do_action = StringProperty()
    extra_headers = DictProperty()
    totalPages = NumericProperty()

    def __init__(self, rl_name=None, rl_book_count=0, **kwargs):
        super(ReadingListImage, self).__init__(**kwargs)
        extra_headers = kwargs.get('extra_headers')
        self.rl_book_count = rl_book_count
        list_menu_items = [
            "Open This Comic",
            "Mark as Read",
            "Mark as UnRead",
            # "Download Comic",
        ]

        self.menu_items = []
        for item in list_menu_items:
            a_menu_item = {
                "viewclass": "MDMenuItem",
                "text": f"[color=#000000]{item}[/color]",
                "callback": self.callback_for_menu_items,
            }
            self.menu_items.append(a_menu_item)
        self.app = MDApp.get_running_app()
        txt_color = get_hex_from_color((1, 1, 1, 1))
        str_txt = f"{rl_name}"
        # str_txt = f"{self.comic_obj.Series} #{self.comic_obj.Number}"
        if self.rl_id != "NOID":
            self.text = f"[color={txt_color}]{str_txt}[/color]"
            self.page_count_text = f"{str(rl_book_count)} Books"

    def callback_for_menu_items(self, *args):
        action = args[0].replace("[color=#000000]", "").replace("[/color]", "")
        if action == "Open This Reading List":
            self.open_readinglist()
        elif action == "Mark as Read":
            print('Mark as Read')
        elif action == "Mark as UnRead":
            print('Mark as UInRead')

    def on_press(self):
        callback = partial(self.menu)
        self.do_action = "read"
        Clock.schedule_once(callback, 0.25)
        self.my_clock = callback

    def menu(self, *args):
        print("menu")
        self.do_action = "menu"

    def on_release(self):
        if self.rl_id == "NOID":
            pass
        Clock.unschedule(self.my_clock)
        self.do_action = "menu"
        return super(ReadingListImage, self).on_press()

    def open_readinglist(self):
        if self.rl_id == "NOID":
            pass
        else:
            def __wait_for_open(dt):
                if server_readinglists_screen.loading_done is True:
                    self.app.manager_screens.current = "r l comic books screen"

            server_readinglists_screen = self.app.manager_screens.get_screen(
                "r l comic books screen"
            )
            server_readinglists_screen.setup_screen()
            server_readinglists_screen.page_number = 1
            readinglist_id = self.rl_id
            readinglist_name = self.rl_name
            server_readinglists_screen.list_loaded = False
            query = ReadingList.select().where(ReadingList.slug == readinglist_id)
            if query.exists():
                Logger.info(f"{readinglist_name} already in Database")
                set_mode = "From DataBase"
            else:
                Logger.info(
                    "{} not in Database getting info from server".format(
                        readinglist_name
                    )
                )
                set_mode = "From Server"
            #set_mode = 'From Server'
            Clock.schedule_once(
                lambda dt: server_readinglists_screen.collect_readinglist_data(
                    readinglist_name=readinglist_name,
                    readinglist_Id=readinglist_id,
                    mode=set_mode,
                    rl_book_count=self.rl_book_count
                )
            )
            self.app.manager_screens.current = "r l comic books screen"

    def open_comic_callback(self, *args):
        self.app.manager_screens.current = "r l comic books screen"


class CustomMDFillRoundFlatIconButton(MDIconButton):
    pass


class Tooltip(Label):
    pass


class ReadingListScreenView(BaseScreenView):
    dynamic_ids = DictProperty({})
    comic_thumb_width = NumericProperty()
    comic_thumb_height = NumericProperty()
    def __init__(self, **kwargs):
        super(ReadingListScreenView, self).__init__(**kwargs)
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
        self.rl_count = 50
        self.rl_book_count = 25
        self.totalPages = 0
        self.prev_button = ""
        self.next_button = ""
        self.comic_thumb_height = 240
        self.comic_thumb_width = 156
    def callback_for_menu_items(self, *args):
        pass

    def on_pre_enter(self):
        self.m_grid = self.ids["main_grid"]

    def on_enter(self, *args):
        self.base_url = self.app.base_url
        self.api_url = self.app.api_url
        self.prev_button = self.ids["prev_button"]
        self.next_button = self.ids["next_button"]
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
            self.page_num = self.rl_json['pageable']['pageNumber']
            if self.rl_json['last'] == False:
                self.next_button.opacity = 1
                self.next_button.disabled = False
                self.next_button.page_num = self.page_num + 1
            else:
                self.next_button.opacity = 0
                self.next_button.disabled = True
                self.next_button.page_num = ""
            if self.rl_json['first'] == False:
                self.prev_button.opacity = 1
                self.prev_button.disabled = False
                self.prev_button.page_num = self.page_num - 1
            else:
                self.prev_button.opacity = 0
                self.prev_button.disabled = True
                self.prev_button.page_num = ""
            self.build_page()

        if self.lists_loaded is False:
            fetch_data = ComicServerConn()
            url_send = f"{self.base_url}/api/v1/readlists?page={new_page_num}&size={self.rl_count}"
            fetch_data.get_server_data_callback(
                url_send,
                callback=lambda url_send, results: __got_readlist_data(self, results))

    def build_page(self):
        async def _build_page():
            grid = self.m_grid
            grid.clear_widgets()
            i = 1
            # add spacer so page forms right while imgs are dl
            c_spacer = ReadingListImage(rl_name="",
                                        rl_book_count=0,
                                        rl_id="NOID",

                                        )
            c_spacer.lines = 1
            c_spacer.padding = dp(60), dp(60)
            c_spacer.totalPages = self.totalPages
            src_thumb = "assets/spacer.jpg"
            c_spacer.source = src_thumb
            grid.add_widget(c_spacer)
            for item in self.rl_comics_json:
                await asynckivy.sleep(0)
                rl_id = item['id']
                x = 0
                for bookID in item['bookIds']:
                    x += 1
                rl_book_count = x
                self.rl_book_count = rl_book_count
                strCookie = 'SESSION=' + self.session_cookie
                c = ReadingListImage(rl_name=item['name'],
                                     rl_book_count=rl_book_count,
                                     rl_id=rl_id,
                                     extra_headers={"Cookie": strCookie, },
                                     )

                c_spacer.lines = 1
                c_spacer.padding = dp(60), dp(60)
                c_spacer.totalPages = self.totalPages
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
            str_text = f"Page #\n {self.page_num} of {self.totalPages}"
            self.ids.page_count.text = str_text
            self.loading_done = True
            self.dialog_load_comic_data.dismiss()

        self.dialog_load_comic_data = DialogLoadKvFiles()
        self.dialog_load_comic_data.open()
        asynckivy.start(_build_page())

    def get_page(self, instance):
        this_page = instance.page_num
        print(this_page)
        if not self.rl_json['last']:
            self.next_button.opacity = 1
            self.next_button.disabled = False
            self.next_button.page_num = self.page_num + 1
        else:
            self.next_button.opacity = 0
            self.next_button.disabled = True
            self.next_button.page_num = ""
        if not self.rl_json['first']:
            self.prev_button.opacity = 1
            self.prev_button.disabled = False
            self.prev_button.page_num = self.page_num - 1
        else:
            self.prev_button.opacity = 0
            self.prev_button.disabled = True
            self.prev_button.page_num = ""
        self.get_comicrack_list(new_page_num=this_page)


    def model_is_changed(self) -> None:
        """
        Called whenever any change has occurred in the data model.
        The view in this method tracks these changes and updates the UI
        according to these changes.
        """

