from kivy.core.window import Window
from kivymd.app import MDApp
from kivy import Logger
from Utility.server_conn import ComicServerConn
from Utility.myUrlrequest import UrlRequest as myUrlRequest
from View.base_screen import BaseScreenView
from kivymd.utils import asynckivy
from View.ReadingListScreen.components.reading_list_image import ReadingListImage
import inspect


class ReadingListScreenView(BaseScreenView):

    def __init__(self, **kwargs):
        super(ReadingListScreenView, self).__init__(**kwargs)
        self.session_cookie = self.app.config.get("General", "api_key")
        self.app = MDApp.get_running_app()
        self.lists_loaded = False
        self.comic_thumb_height = 300
        self.comic_thumb_width = 200

    def model_is_changed(self) -> None:
        """
        Called whenever any change has occurred in the data model.
        The view in this method tracks these changes and updates the UI
        according to these changes.
        """

    def on_enter(self, *args):
        self.get_comicrack_list()

    def get_comicrack_list(self, new_page_num=0):
        def __got_readlist_data(self, results):
            self.rl_comics_json = results['content']
            self.rl_json = results
            self.totalPages = self.rl_json['totalPages']
            self.page_num = self.rl_json['pageable']['pageNumber']
            print(results)
            # if self.rl_json['last'] == False :
            #     self.next_button.opacity = 1
            #     self.next_button.disabled = False
            #     self.next_button.page_num = self.page_num+1
            # else:
            #     self.next_button.opacity = 0
            #     self.next_button.disabled = True
            #     self.next_button.page_num = ""
            # if self.rl_json['first'] == False :
            #     self.prev_button.opacity = 1
            #     self.prev_button.disabled = False
            #     self.prev_button.page_num = self.page_num-1
            # else:
            #     self.prev_button.opacity = 0
            #     self.prev_button.disabled = True
            #     self.prev_button.page_num = ""
            # self.build_page()

        if self.lists_loaded is False:
            c = ReadingListImage()
            self.ids.main_grid.add_widget(c)
            self.ids.main_grid.cols = (Window.width - 30) // self.comic_thumb_width
            new_page_num = 0
            self.rl_count = 25
            fetch_data = ComicServerConn()
            url_send = f"{self.app.base_url}/api/v1/readlists?page={new_page_num}&size={self.rl_count}"
            str_cookie = "SESSION=" + self.session_cookie
            head = {
                "Content-type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
                "Cookie": str_cookie,
            }
            username = self.app.config.get("General", "username")
            password = self.app.config.get("General", "password")
            # api_key = self.app.config.get("General", "api_key")
            myUrlRequest(
                url_send,
                req_headers=head,
                on_success=__got_readlist_data,
                on_error=self.got_error,
                on_redirect=self.got_redirect,
                on_failure=self.got_error,
                # auth=(username,password)
            )

    def got_json2(self, results):
        print(results)

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
