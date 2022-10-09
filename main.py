
"""
Script for managing hot reloading of the project.
For more details see the documentation page -

https://kivymd.readthedocs.io/en/latest/api/kivymd/tools/patterns/create_project/

To run the application in hot boot mode, execute the command in the console:
DEBUG=1 python main.py
"""
import inspect

# import importlib
# import os
#
# from kivy import Config
#
# from PIL import ImageGrab
#
# #
# resolution = ImageGrab.grab().size
#
# # Change the values of the application window size as you need.
# Config.set("graphics", "height", resolution[1]-100)
# Config.set("graphics", "width", "400")
#
# from kivy.core.window import Window
#
# # Place the application window on the right side of the computer screen.
# Window.top = 50
# Window.left = resolution[0] - Window.width
#
# from kivymd.tools.hotreload.app import MDApp
# from kivymd.uix.screenmanager import MDScreenManager
#
# class KomgaReader_MVC(MDApp):
#     KV_DIRS = [os.path.join(os.getcwd(), "View")]
#
#     def build_app(self) -> MDScreenManager:
#         """
#         In this method, you don't need to change anything other than the
#         application theme.
#         """
#
#         import View.screens
#         self.theme_cls.primary_palette = "Orange"
#         self.manager_screens = MDScreenManager()
#
#         Window.bind(on_key_down=self.on_keyboard_down)
#         importlib.reload(View.screens)
#         screens = View.screens.screens
#
#         for i, name_screen in enumerate(screens.keys()):
#             model = screens[name_screen]["model"]()
#             controller = screens[name_screen]["controller"](model)
#             view = controller.get_view()
#             view.manager_screens = self.manager_screens
#             view.name = name_screen
#             self.manager_screens.add_widget(view)
#
#         return self.manager_screens
#
#     def on_keyboard_down(self, window, keyboard, keycode, text, modifiers) -> None:
#         """
#         The method handles keyboard events.
#
#         By default, a forced restart of an application is tied to the
#         `CTRL+R` key on Windows OS and `COMMAND+R` on Mac OS.
#         """
#
#         if "meta" in modifiers or "ctrl" in modifiers and text == "r":
#             self.rebuild()
#
#
#
# KomgaReader_MVC().run()
#
#
#

# After you finish the project, remove the above code and uncomment the below
# code to test the application normally without hot reloading.

# """
# The entry point to the application.
# 
# The application uses the MVC template. Adhering to the principles of clean
# architecture means ensuring that your application is easy to test, maintain,
# and modernize.
# 
# You can read more about this template at the links below:
# 
# https://github.com/HeaTTheatR/LoginAppMVC
# https://en.wikipedia.org/wiki/Model–view–controller
# """
# 
from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from View.screens import screens
import os
from pathlib import Path
from kivy.config import ConfigParser
from mysettings.settingsjson import (
    settings_json_server,
    settings_json_dispaly,
    settings_json_screen_tap_control,
    settings_json_hotkeys,
    settings_json_sync,
)
from kivy.factory import Factory


#from mysettings.custom_settings import MySettings
from kivymd.uix.dialog import MDDialog
class KomgaReader(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.load_all_kv_files(self.directory)
        self.base_url = ""
        self.password = ""
        self.username = ""
        #self.settings_cls = MySettings
        # This is the screen manager that will contain all the screens of your
        # application.
        self.manager_screens = MDScreenManager()
        self.config = ConfigParser()
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
                "how_to_open_comic": "Open Local Copy",
                # 'use_pagination':   '1',
                "max_books_page": 25,
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
                "stretch_image": "0",
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
        self.config.read(os.path.join(self.directory, "komgareader.ini"))
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

        self.max_books_page = int(self.config.get("General", "max_books_page"))
        self.open_last_comic_startup = self.config.get(
            "General", "open_last_comic_startup"
        )
        self.how_to_open_comic = self.config.get(
            "General", "how_to_open_comic"
        )

    def config_callback(self, section, key, value):
        if key == "storagedir":
            def __callback_for_please_wait_dialog(*args):
                if args[0] == "Delete Database":
                    self.stop()
                elif args[0] == "Move Database":
                    print("move")
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
                "sync_folder": "sync_folder",
                "password": "password",
                "username": "username",
                "max_books_page": "max_books_page",
                "sync_folder": "sync_folder",
            }
            item_list = list(config_items.keys())
            if key in item_list:
                item = config_items[key]
                setattr(self, item, value)
            # self.my_data_dir = os.path.join(self.store_dir, 'comics_db')

    def build(self) -> MDScreenManager:
        self.set_value_from_config()
        self.config.add_callback(self.config_callback)
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
        settings.add_json_panel(
            "Sync Settings", self.config, data=settings_json_sync
        )
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
KomgaReader().run()
