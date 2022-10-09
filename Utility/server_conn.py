from kivy import Logger
from kivymd.app import MDApp
from Utility.myUrlrequest import UrlRequest as myUrlRequest
from kivy.event import EventDispatcher
import inspect


class ComicServerConn(EventDispatcher):
    def __init__(self, **kwargs):
        self.app = MDApp.get_running_app()
        self.session_cookie = self.app.config.get("General", "api_key")

    def get_server_data(self, req_url, instance):
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
            req_url,
            req_headers=head,
            on_success=instance.got_json2,
            on_error=self.got_error,
            on_redirect=self.got_redirect,
            on_failure=self.got_error,
            # auth=(username,password)
        )

    def get_server_data_callback(self, req_url, callback):
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
            req_url,
            req_headers=head,
            on_success=callback,
            on_error=self.got_error,
            on_redirect=self.got_redirect,
            on_failure=self.got_error,
            # auth=(username,password)
        )

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

    def on_progress(self, request, current_size, total_size):
        print(f"current_size:{current_size}")
        print(f"total_size:{total_size}")
