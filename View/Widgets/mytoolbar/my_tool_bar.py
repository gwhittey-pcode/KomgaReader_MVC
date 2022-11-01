import os

from kivy.lang import Builder
from kivy.properties import StringProperty
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.app import MDApp
from kivy.factory import Factory

register = Factory.register
register("MyToolBar", module="View.Widgets.mytoolbar.my_tool_bar")


class MyToolBar(MDTopAppBar):
    title_text = StringProperty("Komga Reader")

    def __init__(self, **kwargs):
        super(MyToolBar, self).__init__(**kwargs)

        app = MDApp.get_running_app()
        specific_text_color =  MDApp.get_running_app().theme_cls.accent_color
        self.left_action_items = [

            ["home", lambda x: self.switch_base_screen(), "Home"],
            ["cog-outline", lambda x: app.open_settings(), "Settings"],

            # ["fullscreen",lambda x: app.toggle_full_screen(), "Full Screen"]
        ]
        self.right_action_items = [
            [
                "format-list-group-plus",
                lambda x: self.switch_readinglists_screen(),
                "Reading Lists"
            ],
            [
                "format-list-numbered",
                lambda x: self.switch_r_l_comic_books_screen(),
                "Reading List Comics"
            ],
            [
                "bookshelf",
                lambda x: self.switch_series_screen(),
                "Series"
            ],

            [
                "book-open-page-variant",
                lambda x: self.switch_comic_reader(),
                "Open Comic Book"
            ],
            ["close-box-outline", lambda x: app.stop(), "Exit App"],
        ]

    def switch_base_screen(self):
        MDApp.get_running_app().manager_screens.current = "start screen"

    def switch_r_l_comic_books_screen(self):
        MDApp.get_running_app().manager_screens.current = "r l comic books screen"

    def switch_readinglists_screen(self):
        MDApp.get_running_app().manager_screens.current = "reading list screen"

    def switch_series_screen(self):
        MDApp.get_running_app().manager_screens.current = "series screen"

    def switch_comic_reader(self):
        MDApp.get_running_app().manager_screens.current = "comic book screen"
