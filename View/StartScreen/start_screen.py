from kivymd.app import MDApp
import inspect

from kivy.clock import Clock
from kivy.core.window import Window
from kivy.logger import Logger
from kivy.metrics import dp
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from Utility.komga_server_conn import ComicServerConn
from Utility.myUrlrequest import UrlRequest as myUrlRequest
from View.base_screen import BaseScreenView
from .components import OneLineListItemWithSwitch,Header

class LoginPopupContent(BoxLayout):
    info_text = StringProperty()


class LoginPopup(Popup):
    def on_open(self):
        """ disable hotkeys while we do this"""
        Window.unbind(on_keyboard=MDApp.get_running_app().events_program)

    def on_dismiss(self):
        Window.bind(on_keyboard=MDApp.get_running_app().events_program)


class StartScreenView(BaseScreenView):

    def __init__(self, **kwargs):
        super(StartScreenView, self).__init__(**kwargs)
        self.app = MDApp.get_running_app()
        self.fetch_data = None
        self.Data = ""

        self.fetch_data = ComicServerConn()
        self.app.myLoginPop = LoginPopupContent()
        self.app.popup = LoginPopup(
            content=self.app.myLoginPop, size_hint=(.75, .75), size=(dp(500), dp(400))
        )
        self.password = self.app.password
        self.api_key = self.app.api_key
        self.username = self.app.username
        self.base_url = self.app.base_url
        self.open_last_comic_startup = self.app.open_last_comic_startup

    def on_pre_enter(self, *args):
        self.check_login()
        self.ids.top_bar.elevation = 0
    def check_login(self):
        # see if user has a api key stored from server
        if self.api_key == "":

            self.app.myLoginPop.ids.info.text = "[color=#FF0000]\
                    No API key stored login to get one\
                        [/color]"
            
    def validate_user(self):
        def got_api(self, *args):
            results = self.result
            app = MDApp.get_running_app()
            ary_cookie = self.resp_headers['Set-Cookie']
            for cookie in ary_cookie.split(';'):
                if "SESSION" in cookie:
                    str_key = cookie.split('=')
                    app.config.set("General", "api_key", str_key[1])
                    app.api_key = str_key[1]
                    app.config.write()

            app.myLoginPop.ids.info.text = "[color=#008000]\
                                                Login Test Sucessful\
                                                    [/color]"

            app.popup.dismiss()

        user = self.app.myLoginPop.ids.username_field.text
        self.app.config.set("General", "username", user)
        pwd = self.app.myLoginPop.ids.pwd_field.text
        self.app.config.set("General", "password", pwd)
        url = self.app.myLoginPop.ids.url_field.text
        self.base_url = url.strip()
        self.app.config.set("General", "base_url", self.base_url)
        self.app.base_url = self.base_url
        self.username = user
        self.password = pwd

        req_url = f"{self.base_url}/api/v1/login/set-cookie"
        head = {
            "Content-type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "X-Auth-Token": "",
        }
        self.request = myUrlRequest(
            req_url,
            req_headers=head,
            method="GET",
            on_success=got_api,
            on_error=self.got_error,
            on_redirect=self.got_redirect,
            on_failure=self.got_error,
            auth=(self.username, self.password)
        )

    def call_collect(
            self, set_mode, readinglists_screen, readinglist_name, readinglist_Id
    ):
        Clock.schedule_once(
            lambda dt: readinglists_screen.collect_readinglist_data(
                readinglist_name=readinglist_name,
                readinglist_Id=readinglist_Id,
                mode=set_mode,
            )
        )

    # def build_last_comic_section(  # noqa
    #         self, readinglist_name, readinglist_Id
    # ):
    #     def __got_readlist_data(results):
    #         async def __load_readinglist_scree(paginator_obj=None):
    #             if tmp_last_comic_type == "local_file":
    #                 x_readinglists_screen = self.app.manager_screens.get_screen(
    #                     "local_readinglists_screen"
    #                 )
    #             else:
    #                 x_readinglists_screen = self.app.manager_screens.get_screen(
    #                     "server_readinglists_screen"
    #                 )
    #             x_readinglists_screen.list_loaded = False
    #             x_readinglists_screen.setup_screen()
    #             x_readinglists_screen.page_number = tmp_last_pag_pagnum
    #             x_readinglists_screen.loading_done = False
    #             self.call_collect(
    #                 set_mode,
    #                 x_readinglists_screen,
    #                 readinglist_name,
    #                 readinglist_Id,
    #             )
    #
    #         tmp_last_comic_id = self.app.config.get("Saved", "last_comic_id")
    #         tmp_last_comic_type = self.app.config.get(
    #             "Saved", "last_comic_type"
    #         )
    #         tmp_last_pag_pagnum = int(
    #             self.app.config.get("Saved", "last_pag_pagnum")
    #         )
    #         if tmp_last_comic_id == "":
    #             return
    #         else:
    #             query = ReadingList.select().where(
    #                 ReadingList.slug == readinglist_Id
    #             )
    #             if query.exists():
    #                 Logger.info(f"{readinglist_name} already in Database")
    #                 set_mode = "From DataBase"
    #                 mode = ""
    #                 if tmp_last_comic_type == "local_file":
    #                     mode = "local_file"
    #                 self.new_readinglist = ComicList(
    #                     name=self.readinglist_name,
    #                     data="db_data",
    #                     slug=self.readinglist_Id,
    #                     mode=mode,
    #                 )
    #
    #                 # self.new_readinglist.comics_write()
    #                 max_item_per_page = int(
    #                     self.app.config.get("General", "max_item_per_page")
    #                 )
    #                 new_readinglist_reversed = self.new_readinglist.comics
    #                 paginator_obj = Paginator(
    #                     new_readinglist_reversed, max_item_per_page
    #                 )
    #                 for x in range(1, paginator_obj.num_pages()):
    #                     this_page = paginator_obj.page(x)
    #                     for comic in this_page.object_list:
    #                         if tmp_last_comic_id == comic.Id:
    #                             tmp_last_pag_pagnum = this_page.number
    #                 asynckivy.start(
    #                     __load_readinglist_scree(paginator_obj=paginator_obj)
    #                 )
    #                 if (
    #                         self.open_last_comic_startup == 1
    #                         and not self.app.app_started
    #                 ):
    #                     for comic in self.new_readinglist.comics:
    #                         if comic.slug == tmp_last_comic_id:
    #                             self.open_comic(
    #                                 tmp_last_comic_id=tmp_last_comic_id,
    #                                 tmp_last_comic_type=tmp_last_comic_type,
    #                                 paginator_obj=paginator_obj,
    #                                 comic=comic,
    #                                 tmp_last_pag_pagnum=tmp_last_pag_pagnum,
    #                             )
    #                 else:
    #                     grid = self.ids["main_grid"]
    #                     grid.cols = 1
    #                     grid.clear_widgets()
    #                     for comic in self.new_readinglist.comics:
    #                         if comic.slug == tmp_last_comic_id:
    #                             c = ReadingListComicImage(comic_obj=comic)
    #                             c.comiclist_obj = self.new_readinglist
    #                             c.paginator_obj = paginator_obj
    #                             x = self.app.comic_thumb_width
    #                             y = self.app.comic_thumb_height
    #                             if tmp_last_comic_type == "local_file":
    #                                 if comic.local_file == "":
    #                                     return
    #                                 import os
    #
    #                                 id_folder = os.path.join(
    #                                     self.app.sync_folder,
    #                                     self.new_readinglist.slug,
    #                                 )
    #                                 my_thumb_dir = os.path.join(
    #                                     id_folder, "thumb"
    #                                 )
    #                                 thumb_name = f"{comic.Id}.jpg"
    #                                 t_file = os.path.join(
    #                                     my_thumb_dir, thumb_name
    #                                 )
    #                                 c_image_source = t_file
    #                             else:
    #                                 round_y = round(dp(y))
    #                                 part_url = f"/Comics/{comic.Id}/Pages/0?"
    #                                 part_api = "&apiKey={}&height={}".format(
    #                                     self.api_key, round_y
    #                                 )

    def open_popup(self):
        self.app.popup.open()

    def close_popup(self):
        self.app.popup.dismiss()

    def got_error(self, req, results):
        Logger.critical("ERROR in %s %s" % (inspect.stack()[0][3], results))

    def got_time_out(self, req, results):
        Logger.critical("ERROR in %s %s" % (inspect.stack()[0][3], results))

    def got_failure(self, req, results):
        Logger.critical("ERROR in %s %s" % (inspect.stack()[0][3], results))

    def got_redirect(self, req, results):
        Logger.critical("ERROR in %s %s" % (inspect.stack()[0][3], results))

    def model_is_changed(self) -> None:
        """
        Called whenever any change has occurred in the data model.
        The view in this method tracks these changes and updates the UI
        according to these changes.
        """
