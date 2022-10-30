from kivy.app import App
from kivy.logger import Logger
from kivy.network.urlrequest import UrlRequest
from Utility.myUrlrequest import UrlRequest as myUrlRequest
from kivy.event import EventDispatcher
import inspect


class ComicDataType:
    Arc = "arc"
    Issue = "issue"
    Publisher = "publisher"
    Series = "series"
    ReadingLists = "readinglists"


class ComicServerConn(EventDispatcher):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = App.get_running_app()

    def get_page_size_data(self, req_url, callback):
        str_cookie = 'SESSION=' + self.app.config.get("General", "api_key")
        head = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Cookie": str_cookie,
        }
        UrlRequest(
            req_url,
            req_headers=head,
            on_success=callback,
            on_error=self.got_error,
            on_redirect=self.got_redirect,
            on_failure=self.got_error,
        )

    def update_progress(self, req_url, index, completed, callback):
        data = {'page': index, 'completed': completed}
        import json
        data_json = json.dumps(data)
        str_cookie = 'SESSION=' + self.app.config.get("General", "api_key")
        head = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Cookie": str_cookie,
        }
        UrlRequest(
            req_url,
            method='PATCH',
            req_headers=head,
            req_body=data_json,
            on_success=callback,
            on_error=self.got_error,
            on_redirect=self.got_redirect,
            on_failure=self.got_error,
        )

    def get_server_data_callback(self, req_url: object, callback: object) -> object:
        str_cookie = "SESSION=" + self.app.config.get("General", "api_key")
        head = {
            "Content-type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "Cookie": str_cookie,
        }

        myUrlRequest(
            req_url,
            req_headers=head,
            on_success=callback,
            on_error=self.got_error,
            on_redirect=self.got_redirect,
            on_failure=self.got_error,
            # auth=(username,password)
        )

    def get_server_data(self, req_url, instance):
        str_cookie = "SESSION=" + self.app.config.get("General", "api_key")
        head = {
            "Content-type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "Cookie": str_cookie,
        }
        myUrlRequest(
            req_url,
            req_headers=head,
            on_success=instance.got_json2,
            on_error=self.got_error,
            on_redirect=self.got_redirect,
            on_failure=self.got_error,
            # auth=(username,password)
        )

    # def get_api_key(self, req_url, username, password, callback):
    #     head = {
    #         "Content-type": "application/x-www-form-urlencoded",
    #         "Accept": "application/json",
    #     }
    #     strbody = f"username={username}&password={password}&rememberMe=True"
    #     UrlRequest(
    #         req_url,
    #         req_headers=head,
    #         req_body=strbody,
    #         method="POST",
    #         on_success=callback,
    #         on_error=self.got_error,
    #         on_redirect=self.got_redirect,
    #         on_failure=self.got_error,
    #     )

    def get_server_file_download(self, req_url, callback, file_path):
        def update_progress(request, current_size, total_size):
            pass

        str_cookie = "SESSION=" + self.app.config.get("General", "api_key")
        head = {
            "Cookie": str_cookie,
        }
        req = myUrlRequest(
            req_url,
            req_headers=head,
            on_success=callback,
            on_error=self.got_error,
            on_redirect=self.got_redirect,
            on_failure=self.got_error,
            file_path=file_path,
            # auth=(username,password)
        )

    def got_json(self, req, result):
        return result["results"]

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


class JsonToObject:
    def __init__(self, json_object):
        self.json_object = json_object
        self.keys = json_object.keys()
        self.setup(json_object)

    def setup(self, d):
        for key, item in d.items():
            if isinstance(item, dict):
                new_object = JsonToObject(item)
                setattr(self, key, new_object)
            else:
                setattr(self, key, item)
