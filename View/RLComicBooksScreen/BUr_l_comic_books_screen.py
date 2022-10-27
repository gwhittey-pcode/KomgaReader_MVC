import ntpath
import os
from pathlib import Path
from sqlite3 import ProgrammingError, OperationalError, DataError

from kivy import Logger
from kivy.properties import ObjectProperty, StringProperty, NumericProperty, BooleanProperty, DictProperty, ListProperty
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.utils import get_hex_from_color
from kivymd.app import MDApp
from kivymd.uix.button import MDIconButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.tooltip import MDTooltip
from kivymd.utils import asynckivy
from View.Widgets.comicthumb import ComicThumb
from Utility.comic_functions import save_thumb
from Utility.comic_json_to_class import ComicList, ComicBook
from Utility.komga_server_conn import ComicServerConn
from Utility.paginator import Paginator

from View.base_screen import BaseScreenView
import json
from functools import partial

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from Utility.myloader import Loader
from kivy.metrics import dp
from kivy.uix.popup import Popup
from kivy.logger import Logger
from kivymd.toast.kivytoast import toast
from View.Widgets.dialogs.dialogs import DialogLoadKvFiles
from Utility.komga_server_conn import ComicServerConn
from Utility.db_functions import Comic



class CustomMDFillRoundFlatIconButton(MDIconButton):
    pass


class SyncButtonIcon(MDIconButton, MDTooltip):
    icon_name = StringProperty("plus")

    my_clock = ObjectProperty()
    do_action = StringProperty()

    # def on_mouse_pos(self, *args):
    #     if not self.get_root_window():
    #         return
    #     pos = args[1]
    #     self.tooltip.text = self.tooltip_text
    #     self.tooltip.pos = pos
    #     # cancel scheduled event since I moved the cursor
    #     Clock.unschedule(self.display_tooltip)
    #     self.close_tooltip()  # close if it's opened
    #     if self.collide_point(*self.to_widget(*pos)):
    #         Clock.schedule_once(self.display_tooltip, 0.5)

    # def close_tooltip(self, *args):
    #     Window.remove_widget(self.tooltip)

    # def display_tooltip(self, *args):
    #     Window.add_widget(self.tooltip)

    def do_sync_rf(self, *args):
        MDApp.get_running_app().manager_screens.get_screen(
            "r l comic books screen"
        ).sync_readinglist()

    def do_options(self, *args):
        MDApp.get_running_app().manager_screens.get_screen(
            "r l comic books screen"
        ).open_sync_options()

    def do_data_refresh(self, *args):
        the_screen = MDApp.get_running_app().manager_screens.get_screen("r l comic books screen")
        the_screen.new_readinglist.do_db_refresh(screen=the_screen)

    def del_rl_files(self, *args):
        the_screen = MDApp.get_running_app().manager_screens.get_screen("r l comic books screen")
        import shutil
        id_folder = os.path.join(MDApp.get_running_app().sync_folder, the_screen.new_readinglist.slug)
        print("id:" + id_folder)
        shutil.rmtree(id_folder)

        print(the_screen.new_readinglist.slug)


class SynLimitButton(MDRaisedButton):
    def __init__(self, **kwargs):
        super(SynLimitButton, self).__init__(**kwargs)
        self.limit_menu_items = [
            {
                "viewclass": "MDMenuItem",
                "text": "[color=#000000]Books[/color]",
                "callback": self.callback_for_menu_items,
            },
            {
                "viewclass": "MDMenuItem",
                "text": "[color=#000000]GB[/color]",
                "callback": self.callback_for_menu_items,
            },
            {
                "viewclass": "MDMenuItem",
                "text": "[color=#000000]MB[/color]",
                "callback": self.callback_for_menu_items,
            },
        ]

    def callback_for_menu_items(self, *args):
        action = args[0].replace("[color=#000000]", "").replace("[/color]", "")
        if action == "Books":
            self.text = "Books"
        elif action == "GB":
            self.text = "GB"
        elif action == "MB":
            self.text = "MB"

    def open_menu(self):
        MDDropdownMenu(items=self.limit_menu_items, width_mult=3).open(self)


class Tooltip(Label):
    pass


class RLComicBooksScreenView(BaseScreenView):
    reading_list_title = StringProperty()
    page_number = NumericProperty()
    max_item_per_page = NumericProperty()
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
        # self.bind_to_resize()
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
        self.current_page = ObjectProperty()
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
        self.rl_book_count = NumericProperty()

    def callback_for_menu_items(self, *args):
        pass

    def setup_screen(self):
        self.session_cookie = self.app.config.get("General", "api_key")
        self.main_stack = self.ids["main_stack"]
        self.m_grid = self.ids["main_grid"]
        self.prev_button = self.ids["prev_button"]
        self.next_button = self.ids["next_button"]

    def on_pre_enter(self, *args):
        return super().on_pre_enter(*args)

    def my_width_callback(self, obj, value):
        for key, val in self.ids.items():
            if key == "main_grid":
                c = val
                c.cols = (Window.width - 10) // self.comic_thumb_width

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

    def file_sync_update(self, c_id, state):
        grid = self.m_grid
        for child in grid.children:
            if child.comic_obj:
                if child.comic_obj.Id == c_id:
                    child.has_localfile = state

    def collect_readinglist_data(
            self,
            readinglist_name="",
            readinglist_Id="",
            mode="From Server",
            current_page_num=1,
            rl_book_count=10,
            *largs,
    ):
        async def collect_readinglist_data():
            def __got_book_list_data(self, results):
                book_list_data = results['content']
                for book in book_list_data:
                    print(book['id'])

            self.readinglist_name = readinglist_name
            # self.app.set_screen(self.readinglist_name + " Page 1")
            self.reading_list_title = self.readinglist_name + " Page 1"
            self.readinglist_Id = readinglist_Id
            self.page_number = current_page_num
            self.mode = mode
            if self.mode == "From Server":
                fetch_data = ComicServerConn()
                url_send = f"{self.base_url}/api/v1/readlists/{self.readinglist_Id}/books?size={rl_book_count}"
                fetch_data.get_server_data(url_send, self)
                # fetch_data.get_server_data_callback(
                #         url_send,
                #         callback=lambda url_send, results: __got_book_list_data(self,results))
            elif self.mode == "From DataBase":
                self.got_db_data()

        asynckivy.start(collect_readinglist_data())

    def get_page(self, instance):
        page_num = instance.page_num
        # self.app.set_screen(self.readinglist_name + f" Page {page_num}")
        self.reading_list_title = self.readinglist_name + f" Page {page_num}"
        page = self.paginator_obj.page(page_num)
        self.current_page = page
        if page.has_next():
            self.next_button.opacity = 1
            self.next_button.disabled = False
            self.next_button.page_num = page.next_page_number()
        else:
            self.next_button.opacity = 0
            self.next_button.disabled = True
            self.next_button.page_num = ""
        if page.has_previous():
            self.prev_button.opacity = 1
            self.prev_button.disabled = False
            self.prev_button.page_num = page.previous_page_number()
        else:
            self.prev_button.opacity = 0
            self.prev_button.disabled = True
            self.prev_button.page_num = ""
        self.build_page(page.object_list)

    def build_page(self, object_lsit):
        async def _build_page():
            grid = self.m_grid
            grid.clear_widgets()
            # add spacer so page forms right while lmgs are dl
            c_spacer = ComicThumb(item_id="NOID")
            c_spacer.lines = 1
            c_spacer.padding = dp(60), dp(60)
            src_thumb = "assets/spacer.jpg"
            c_spacer.source = src_thumb
            grid.add_widget(c_spacer)
            c_spacer.opacity=0
            for comic in object_lsit:
                await asynckivy.sleep(0)
                str_cookie = 'SESSION=' + self.session_cookie
                c = ComicThumb(item_id=comic.Id, comic_obj=comic)
                c.lines = 2
                c.comiclist_obj = self.new_readinglist
                c.paginator_obj = self.paginator_obj
                c.str_caption = f"  {comic.Series } \n  #{comic.Number} - {comic.Title[:12]}... \n  {comic.PageCount} Pages"
                c.tooltip_text = f"{comic.Series }\n#{comic.Number} - {comic.Title}"
                c.thumb_type = "ComicBook"
                c.text_size = dp(8)
                y = self.comic_thumb_height
                thumb_filename = f"{comic.Id}.jpg"
                id_folder = self.app.store_dir
                my_thumb_dir = os.path.join(id_folder, "comic_thumbs")
                t_file = os.path.join(my_thumb_dir, thumb_filename)
                if os.path.isfile(t_file):
                    c_image_source = t_file
                else:
                    c_thumb_source = f"{self.base_url}/api/v1/books/{comic.Id}/thumbnail"
                    asynckivy.start(save_thumb(comic.Id, c_thumb_source))
                c_image_source = f"{self.base_url}/api/v1/books/{comic.Id}/thumbnail"
                c.source = c_image_source

                def loaded():
                    grid.add_widget(c)

                c.on_load = (loaded())
                c.PageCount = comic.PageCount
                c.pag_pagenum = self.current_page.number
                grid.cols = (Window.width - 10) // self.comic_thumb_width
                self.dynamic_ids[id] = c
            self.ids.page_count.text = "Page #\n{} of {}".format(
                self.current_page.number, self.paginator_obj.num_pages()
            )
            self.loading_done = True

        asynckivy.start(_build_page())

    def got_db_data(self):
        """
        used if rl data is already stored in db.
        """

        async def _do_readinglist():
            self.new_readinglist = ComicList(
                name=self.readinglist_name,
                data="db_data",
                slug=self.readinglist_Id,
            )
            await asynckivy.sleep(0)
            self.so = self.new_readinglist.sw_syn_this_active
            self.setup_options()
            new_readinglist_reversed = self.new_readinglist.comics
            self.paginator_obj = Paginator(
                new_readinglist_reversed, self.max_item_per_page
            )
            page = self.paginator_obj.page(self.page_number)
            self.current_page = page
            if page.has_next():
                self.next_button.opacity = 1
                self.next_button.disabled = False
                self.next_button.page_num = page.next_page_number()
            else:
                self.next_button.opacity = 0
                self.next_button.disabled = True
                self.next_button.page_num = ""
            if page.has_previous():
                self.prev_button.opacity = 1
                self.prev_button.disabled = False
                self.prev_button.page_num = page.previous_page_number()
            else:
                self.prev_button.opacity = 0
                self.prev_button.disabled = True
                self.prev_button.page_num = ""
            self.build_page(page.object_list)
            self.list_loaded = True

        asynckivy.start(_do_readinglist())

    def refresh_callback(self, *args):
        """A method that updates the state of reading list"""

        def __refresh_callback(interval):
            self.ids.main_grid.clear_widgets()
            self.collect_readinglist_data(
                self.readinglist_name,
                self.readinglist_Id,
                current_page_num=self.page_number,
                mode="From DataBase",
            )
            #            self.build_page(page.object_list)
            # self.ids.main_scroll.refresh_done()
            self.tick = 0

        Clock.schedule_once(__refresh_callback, 1)
    def got_json2(self, req, results):
        async def _got_json():
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
                self.new_readinglist.add_comic(new_comic)
                i += 1
            self.setup_options()
            new_readinglist_reversed = self.new_readinglist.comics[::-1]
            self.paginator_obj = Paginator(
                new_readinglist_reversed, self.max_item_per_page
            )
            page = self.paginator_obj.page(self.page_number)
            self.current_page = page
            if page.has_next():
                self.next_button.opacity = 1
                self.next_button.disabled = False
                self.next_button.page_num = page.next_page_number()
            else:
                self.next_button.opacity = 0
                self.next_button.disabled = True
                self.next_button.page_num = ""
            if page.has_previous():
                self.prev_button.opacity = 1
                self.prev_button.disabled = False
                self.prev_button.page_num = page.previous_page_number()
            else:
                self.prev_button.opacity = 0
                self.prev_button.disabled = True
                self.prev_button.page_num = ""
            self.build_page(page.object_list)
            self.list_loaded = True
            self.dialog_load_comic_data.dismiss()

        self.dialog_load_comic_data = DialogLoadKvFiles()
        self.dialog_load_comic_data.open()
        asynckivy.start(_got_json())

    def show_please_wait_dialog(self):
        def __callback_for_please_wait_dialog(*args):
            pass

        self.please_wait_dialog = MDDialog(
            title="No ReadingList loaded.",
            size_hint=(0.8, 0.4),
            text_button_ok="Ok",
            text=f"No ReadingList loaded.",
            events_callback=__callback_for_please_wait_dialog,
        )
        self.please_wait_dialog.open()

    def setup_options(self):

        self.sync_options = SyncOptionsPopup(
            size_hint=(0.76, 0.76),
            cb_limit_active=self.new_readinglist.cb_limit_active,
            limit_num_text=str(self.new_readinglist.limit_num),
            cb_only_read_active=self.new_readinglist.cb_only_read_active,
            cb_purge_active=self.new_readinglist.cb_purge_active,  # noqa
            # cb_optimize_size_active=self.new_readinglist.cb_optimize_size_active,  # noqa
            sw_syn_this_active=bool(self.new_readinglist.sw_syn_this_active),
        )
        self.sync_options.ids.limit_num.bind(
            on_text_validate=check_input,
            focus=check_input,
        )

        self.sync_options.title = self.new_readinglist.name

    def open_sync_options(self):
        if self.sync_options.ids.sw_syn_this.active is True:
            self.sync_options.ids.syn_on_off_label.text = f""
            self.sync_options.ids.syn_on_off_label.theme_text_color = "Primary"
        self.sync_options.open()

    def sync_readinglist(self):
        if self.sync_options.ids.sw_syn_this.active is False:
            self.sync_options.ids.syn_on_off_label.text = f"Sync Not Turned On"
            self.open_sync_options()
        elif self.sync_options.ids.sw_syn_this.active is True:
            toast(f"Starting sync of {self.new_readinglist.name}")
            self.new_readinglist.do_sync()


def check_input(*args: object) -> object:
    text_field = args[0]
    if text_field.text.isnumeric():
        text_field.error = False
        return True
    else:
        text_field.error = True
        return False


class SyncOptionsPopup(Popup):
    background = "assets/cPop_bkg.png"
    text = StringProperty("")
    cb_limit_active = BooleanProperty(False)
    limit_num_text = BooleanProperty(False)
    cb_only_read_active = BooleanProperty(False)
    cb_purge_active = BooleanProperty(False)
    cb_optimize_size_active = BooleanProperty(False)
    sw_syn_this_active = BooleanProperty(False)
    ok_text = StringProperty("OK")
    cancel_text = StringProperty("Cancel")

    __events__ = ("on_ok", "on_cancel")

    def __init__(self, **kwargs):
        super(SyncOptionsPopup, self).__init__(**kwargs)
        app = MDApp.get_running_app()
        server_readinglists_screen = app.manager_screens.get_screen(
            "r l comic books screen"
        )
        self.current_screen = server_readinglists_screen

    def on_open(self):
        # self.sw_syn_this.active=bool(self.current_screen.new_readinglist.sw_syn_this_active)
        """ disable hotkeys while we do this"""
        Window.unbind(on_keyboard=MDApp.get_running_app().events_program)

    def on_dismiss(self):
        Window.bind(on_keyboard=MDApp.get_running_app().events_program)

    def on_ok(self):
        chk_input = check_input(self.ids.limit_num)
        if chk_input is True:
            if self.ids.sw_syn_this.active:
                self.current_screen.sync_bool = True
            else:
                self.current_screen.sync_bool = False
            self.current_screen.new_readinglist.save_settings(
                cb_limit_active=self.ids.cb_limit.active,
                limit_num=int(self.ids.limit_num.text),
                cb_only_read_active=self.ids.cb_only_read.active,
                cb_purge_active=self.ids.cb_purge.active,
                cb_optimize_size_active=False,
                sw_syn_this_active=self.ids.sw_syn_this.active,
            )
            self.dismiss()
        else:
            self.ids.limit_num.focus = True
            return

    def on_cancel(self):
        self.ids.cb_limit.active = (
            self.current_screen.new_readinglist.cb_limit_active
        )  # noqa
        self.ids.limit_num.text = str(
            self.current_screen.new_readinglist.limit_num
        )
        self.ids.cb_only_read.active = (
            self.current_screen.new_readinglist.cb_only_read_active
        )  # noqa
        self.ids.cb_purge.active = (
            self.current_screen.new_readinglist.cb_purge_active
        )  # noqa
        # self.ids.cb_optimize_size.active = (
        #     self.current_screen.new_readinglist.cb_optimize_size_active
        # )  # noqa
        self.ids.sw_syn_this.active = bool(
            self.current_screen.new_readinglist.sw_syn_this_active
        )
        self.ids.limit_num.error = False
        self.dismiss()

    def model_is_changed(self) -> None:
        """
        Called whenever any change has occurred in the data model.
        The view in this method tracks these changes and updates the UI
        according to these changes.
        """
