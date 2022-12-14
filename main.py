"""
Script for managing hot reloading of the project.
For more details see the documentation page -

https://kivymd.readthedocs.io/en/latest/api/kivymd/tools/patterns/create_project/

To run the application in hot boot mode, execute the command in the console:
DEBUG=1 python main.py
"""
import inspect
from collections import OrderedDict

import multitasking
from kivy import Logger
from kivy.core.window import Window, Keyboard
from kivy.properties import (
    ObjectProperty,
    StringProperty,
    NumericProperty,
    BooleanProperty, ListProperty
)
from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.utils import asynckivy
from Utility.myUrlrequest import UrlRequest as myUrlRequest
from View.screens import screens
import os
from pathlib import Path
from kivy.config import ConfigParser, Config

from libs.database import create_db
from mysettings.settingsjson import (
    settings_json_server,
    settings_json_dispaly,
    settings_json_screen_tap_control,
    settings_json_sync,
)
from kivy.factory import Factory
from mysettings.custom_settings import MySettings
from kivymd.uix.dialog import MDDialog


from View.Widgets.mytoolbar import MyToolBar
from string import ascii_lowercase as alc


class KomgaReader(MDApp):
    title = StringProperty
    store_dir = StringProperty()
    comic_db = ObjectProperty()
    username = StringProperty()
    password = StringProperty()
    api_key = StringProperty()
    max_item_per_page = StringProperty()
    open_last_comic_startup = NumericProperty()
    # how_to_open_comic = StringProperty()
    open_comic_screen = StringProperty()
    sync_is_running = BooleanProperty(False)
    rl_count = NumericProperty()
    full_screen = False
    filter_nav_drawer = ObjectProperty()
    first_screen = ObjectProperty()
    nav_layout = ObjectProperty()
    sort_filter = ListProperty()
    filter_string = StringProperty()
    filter_list = ListProperty()
    letter_count = ObjectProperty()
    ordered_letter_count = ObjectProperty()
    gen_publisher_list = ListProperty()
    gen_release_dates = ListProperty()
    stream_comic_pages = BooleanProperty()
    db_engine = ObjectProperty()
    DB_ENGINE = ObjectProperty()
    DB_SES_MAKER = ObjectProperty()
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.letter_count = None
        self.filter_nav_drawer = None
        self.load_all_kv_files(self.directory)
        self.base_url = ""
        self.password = ""
        self.username = ""
        self.comic_thumb_height = 300
        self.comic_thumb_width = 200
        self.item_per_page = 20
        self.title = ""
        self.settings_cls = MySettings
        # This is the screen manager that will contain all the screens of your
        # application.
        self.manager_screens = MDScreenManager()
        self.config = ConfigParser()
        self.filter_string = ""
        self.filter_list = []
        self.LIST_SCREENS = ['comic book screen'

                             ]
        register = Factory.register
        register("RLSmartTile", module="View.ReadingListScreen.components.rlimagelist")

    def build_config(self, config):
        """Creates an application settings file KomgaReader2.ini."""

        config.adddefaultsection("Language")
        config.adddefaultsection("Saved")
        config.setdefault("Language", "language", "en")

        config.setdefault("Saved", "last_comic_id", "")
        config.setdefault("Saved", "last_comic_type", "")
        config.setdefault("Saved", "last_reading_list_id", "")
        config.setdefault("Saved", "last_reading_list_name", "")
        config.setdefault("Saved", "last_pag_pagnum", "")

        config.setdefaults(
            "General",
            {
                "base_url": "http://",
                "storagedir": self.user_data_dir,
                "use_api_key": 0,
                "api_key": "",
                "username": "",
                "password": "",
                "open_last_comic_startup": 0,
                # "how_to_open_comic": "Open Local Copy",
                # 'use_pagination':   '1',
                "max_item_per_page": 25,
                "stream_comic_pages": 0
            },
        )
        config.setdefaults(
            "Sync", {"sync_folder": self.user_data_dir, "max_num_sync": 50}
        )
        config.setdefaults(
            "Display",
            {
                "mag_glass_size": 200,
                "right2left": 0,
                "dblpagesplit": "0",
                "stretch_image": "1",
                "keep_ratio": "0",
                "reading_list_icon_size": "Small",
                "max_comic_pages_limit": 50,
                "max_height": 1500,
            },
        )

        config.setdefaults(
            "Screen Tap Control",
            {
                "bottom_right": "Next Page",
                "bottom_left": "Prev Page",
                "bottom_center": "Open Page Nav",
                "top_right": "Return to Home Screen",
                "top_left": "Precodv Page",
                "top_center": "Open Collection Browser",
                "middle_right": "None",
                "middle_left": "None",
                "middle_center": "Open NavBar",
                "dbl_tap_time": 250,
            },
        )

        config.setdefaults(
            "Hotkeys",
            {
                "hk_next_page": ".",
                "hk_prev_page": ",",
                "hk_open_page_nav": "p",
                "hk_open_collection": "j",
                "hk_return_comic_list": "c",
                "hk_return_base_screen": "r",
                "hk_toggle_navbar": "n",
                "hk_toggle_fullscreen": "f",
            },
        )

    def set_value_from_config(self, *args):
        """Sets the values of variables from the settings
        file KomgaReader2.ini."""
        # self.config.read(os.path.join(self.directory, "komgareader.ini"))
        self.lang = self.config.get("Language", "language")
        self.sync_folder = self.config.get("Sync", "sync_folder")
        self.store_dir = os.path.join(
            self.config.get("General", "storagedir"), "store_dir"
        )
        if not Path(self.store_dir).is_dir():
            os.makedirs(self.store_dir)
        self.base_url = self.config.get("General", "base_url").rstrip("\\")
        self.api_key = self.config.get("General", "api_key")
        self.username = self.config.get("General", "username")
        self.password = self.config.get("General", "password")

        self.api_url = self.base_url + "/API"
        self.my_data_dir = os.path.join(self.store_dir, "comics_db")

        if not os.path.isdir(self.my_data_dir):
            os.makedirs(self.my_data_dir)

        self.max_item_per_page = self.config.get("General", "max_item_per_page")
        self.open_last_comic_startup = self.config.get(
            "General", "open_last_comic_startup"
        )
        # self.how_to_open_comic = self.config.get(
        #     "General", "how_to_open_comic"
        # )
        self.item_per_page = self.config.get("General", "max_item_per_page")
        self.stream_comic_pages = self.config.get("General", "stream_comic_pages")

    def config_callback(self, section, key, value):
        print(f"{key :}{value}")
        if key == "storagedir":
            def __callback_for_please_wait_dialog(*args):
                if args[0] == "Delete Database":
                    self.stop()
                elif args[0] == "Move Database":
                    db_folder = self.my_data_dir
                    old_dbfile = os.path.join(db_folder, "KomgaReader.db")
                    store_dir = os.path.join(value, "store_dir")
                    new_data_dir = os.path.join(store_dir, "comics_db")
                    new_dbfile = os.path.join(
                        new_data_dir, "KomgaReader.db"
                    )
                    if not os.path.isdir(store_dir):
                        os.makedirs(store_dir)
                    if not os.path.isdir(new_data_dir):
                        os.makedirs(new_data_dir)
                    from shutil import copyfile
                    copyfile(old_dbfile, new_dbfile)
                    self.stop()

            self.please_wait_dialog = MDDialog(
                title="Please Restart KomgaReader",
                size_hint=(0.8, 0.4),
                text_button_ok="Delete Database",
                text_button_cancel="Move Database",
                text=f"Storage/Databse dir changed Delete Data or Move it to new dir \nApp will Close please restart it for new setting to take effect?",
                events_callback=__callback_for_please_wait_dialog,
            )
            self.please_wait_dialog.open()
        else:
            config_items = {
                "base_url": "base_url",
                "api_key": "api_key",
                "password": "password",
                "username": "username",
                "max_item_per_page": "max_item_per_page",
                "sync_folder": "sync_folder",
                "stream_comic_pages": "stream_comic_pages"
            }
            item_list = list(config_items.keys())
            if key in item_list:
                item = config_items[key]
                setattr(self, item, value)
            # self.my_data_dir = os.path.join(self.store_dir, 'comics_db')

    def build(self) -> MDScreenManager:

        self.set_value_from_config()
        self.config.add_callback(self.config_callback)

        self.ordered_letter_count = []
        self.gen_publisher_list = []
        self.gen_release_dates = []
        path = os.path.dirname(__file__)
        icon_path = os.path.join(path, f"data{os.sep}")
        if self.api_key != "":
            self.get_letter_groups()
            self.get_gen_publishers()
            self.get_gen_release_dates()
        self.icon = os.path.join(icon_path, f"icon.png")
        self.theme_cls.primary_palette = "Cyan"
        self.theme_cls.theme_style = "Light"
        self.theme_cls.material_style = "M3"
        create_db()
        while self.ordered_letter_count:
            pass
        else:
            self.generate_application_screens()

            return self.manager_screens

    def generate_application_screens(self) -> None:
        """
        Creating and adding screens to the screen manager.
        You should not change this cycle unnecessarily. He is self-sufficient.

        If you need to add any screen, open the `View.screens.py` module and
        see how new screens are added according to the given application
        architecture.
        """

        for i, name_screen in enumerate(screens.keys()):
            model = screens[name_screen]["model"]()
            controller = screens[name_screen]["controller"](model)
            view = controller.get_view()
            view.manager_screens = self.manager_screens
            view.name = name_screen
            self.manager_screens.add_widget(view)



    def on_config_change(self, config, section, key, value):
        pass

    def build_settings(self, settings):
        # settings.add_json_panel(
        #     "Sync Settings", self.config, data=settings_json_sync
        # )
        settings.add_json_panel(
            "General Settings", self.config, data=settings_json_server
        )

        settings.add_json_panel(
            "Display Settings", self.config, data=settings_json_dispaly
        )
        settings.add_json_panel(
            "Screen Tap Control",
            self.config,
            data=settings_json_screen_tap_control,
        )
        # settings.add_json_panel(
        #     "Hotkeys", self.config, data=settings_json_hotkeys
        # )

    def hide_action_bar(self):
        self.manager_screens.ids.action_bar.opacity = 0
        self.manager_screens.ids.action_bar.disabled = True
        self.manager_screens.ids.action_bar.size_hint_y = None
        self.manager_screens.ids.action_bar.size = (0, 0)

    def show_action_bar(self):
        self.manager_screens.ids.action_bar.opacity = 1
        self.manager_screens.ids.action_bar.disabled = False
        self.manager_screens.ids.action_bar.size = (
            Window.width,
            self.theme_cls.standard_increment,
        )

    def events_program(self, instance, keyboard, keycode, text, modifiers):
        c = Keyboard()
        """Called when you press a Key"""
        app = MDApp.get_running_app()
        current_screen = app.manager_screens.current_screen
        hk_next_page = app.config.get("Hotkeys", "hk_next_page")
        hk_prev_page = app.config.get("Hotkeys", "hk_prev_page")
        hk_open_page_nav = app.config.get("Hotkeys", "hk_open_page_nav")
        hk_open_collection = app.config.get("Hotkeys", "hk_open_collection")
        hk_return_comic_list = app.config.get(
            "Hotkeys", "hk_return_comic_list"
        )
        hk_return_base_screen = app.config.get(
            "Hotkeys", "hk_return_base_screen"
        )
        hk_toggle_navbar = app.config.get("Hotkeys", "hk_toggle_navbar")

        hk_toggle_fullscreen = app.config.get(
            "Hotkeys", "hk_toggle_fullscreen"
        )
        Logger.debug(f"keyboard:{keyboard}")
        if current_screen.name in self.LIST_SCREENS:
            if keyboard in (c.string_to_keycode(hk_next_page), 275):
                current_screen.load_next_slide()
            elif keyboard in (c.string_to_keycode(hk_prev_page), 276):
                current_screen.load_prev_slide()
            elif keyboard == c.string_to_keycode(hk_open_page_nav):
                current_screen.page_nav_popup_open()
            elif keyboard == c.string_to_keycode(hk_open_collection):
                current_screen.comicscreen_open_collection_popup()
            elif keyboard == c.string_to_keycode(hk_toggle_navbar):
                current_screen.toggle_option_bar()
            elif keyboard == c.string_to_keycode(hk_return_comic_list):
                app.switch_readinglists_screen()
            elif keyboard == c.string_to_keycode(hk_return_base_screen):
                app.show_action_bar()
                app.manager.current = "base"
            elif keyboard == c.string_to_keycode(hk_toggle_fullscreen):
                self.toggle_full_screen()
        # else:
        # if keyboard in (282, 319):
        #     pass
        # elif keyboard == c.string_to_keycode(hk_toggle_fullscreen):
        #     self.toggle_full_screen()
        # elif keyboard == c.string_to_keycode(hk_return_comic_list):
        #     app.manager.current = "server_readinglists_screen"
        # elif keyboard == c.string_to_keycode(hk_return_base_screen):
        #     app.show_action_bar()
        #     app.switch_base_screen()
        return True

    def toggle_full_screen(self):
        if MDApp.get_running_app().full_screen is False:
            Window.fullscreen = True
            MDApp.get_running_app().full_screen = True
        else:
            MDApp.get_running_app().full_screen = False
            Window.fullscreen = False

    # def back_screen(self, event=None):
    #     """Screen manager Called when the Back Key is pressed."""
    #     # BackKey pressed.
    #     if event in (1001, 27):
    #         if self.manager.current == "base":
    #             self.dialog_exit()
    #             return
    #         try:
    #             self.manager.current = self.list_previous_screens.pop()
    #         except:  # noqa
    #             self.manager.current = "base"
    #         # self.screen.ids.action_bar.title = self.title

    def open_object_list_screen(self, object_type):
        screen = self.manager_screens.get_screen("object list screen")
        screen.setup_screen(object_type=object_type)
        self.manager_screens.current = "object list screen"

    @multitasking.task
    def get_gen_publishers(self):
        def __got_server_data(req, result):
            for publisher in result:
                self.gen_publisher_list.append(publisher)

        url_send = f"{self.base_url}/api/v1/publishers"
        str_cookie = "SESSION=" + self.config.get("General", "api_key")
        head = {
            "Content-type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "Cookie": str_cookie,
        }
        request = myUrlRequest(
            url_send,
            req_headers=head,
            on_success=__got_server_data,
            on_error=self.got_error,
            on_redirect=self.got_redirect,
            on_failure=self.got_error,
        )

    @multitasking.task
    def get_gen_release_dates(self):
        def __got_server_data(req, result):
            for publisher in result:
                self.gen_release_dates.append(publisher)

        url_send = f"{self.base_url}/api/v1/series/release-dates"
        str_cookie = "SESSION=" + self.config.get("General", "api_key")
        head = {
            "Content-type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "Cookie": str_cookie,
        }
        request = myUrlRequest(
            url_send,
            req_headers=head,
            on_success=__got_server_data,
            on_error=self.got_error,
            on_redirect=self.got_redirect,
            on_failure=self.got_error,
        )

    @multitasking.task
    def get_letter_groups(self):
        self.letter_count = {}

        def __got_server_data(req, result):
            num_count = 0
            series_count = 0
            for item in result:
                if item['group'] not in alc:
                    num_count = num_count + item['count']
                else:
                    self.letter_count[item['group'].capitalize()] = item['count']
                    series_count = series_count + item['count']
            self.series_count = series_count + num_count
            self.letter_count['#'] = num_count
            self.ordered_letter_count = OrderedDict(sorted(self.letter_count.items(), key=lambda t: t[0]))

        url_send = f"{self.base_url}/api/v1/series/alphabetical-groups"
        str_cookie = "SESSION=" + self.config.get("General", "api_key")
        head = {
            "Content-type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "Cookie": str_cookie,
        }
        request = myUrlRequest(
            url_send,
            req_headers=head,
            on_success=__got_server_data,
            on_error=self.got_error,
            on_redirect=self.got_redirect,
            on_failure=self.got_error,
        )

    def switch_stream(self, state):
        if state:
            self.config.set("General", "stream_comic_pages", '1')
            self.stream_comic_pages = '1'
        else:
            self.config.set("General", "stream_comic_pages", '0')
            self.stream_comic_pages = '0'
        self.config.write()

    def download_selected_comics(self):
        self.manager_screens.current = "download screen"

    def select_all_comics(self):
        dl_screen = self.manager_screens.get_screen("download screen")
        for item in dl_screen.comic_thumbs_list:
            print(f"{item.item_id =}")
            item.ids.download_select.icon = "download-circle"
            str_caption = f"  {item.comic_obj.Series} \n  #{item.comic_obj.Number}"
            item_dict = {
                "id": item.item_id,
                "name": str_caption,
                "title": item.comic_obj.Title,
                "page_count": item.comic_obj.PageCount
            }
            dl_screen.download_que.append(item_dict)
        print(dl_screen.download_que)

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


KomgaReader().run()
