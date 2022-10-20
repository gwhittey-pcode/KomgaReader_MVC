from kivy import Logger
from kivy.clock import Clock
from kivy.properties import StringProperty, NumericProperty, DictProperty, ObjectProperty
from kivymd.app import MDApp
from kivymd.uix.behaviors import CommonElevationBehavior, TouchBehavior, HoverBehavior
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFillRoundFlatIconButton
from kivy.uix.modalview import ModalView
from kivymd.uix.tooltip import MDTooltip

from Utility.db_functions import ReadingList
from ..myimagelist.myimagelist import MyMDSmartTile


class ComicThumbOverlay(MDFillRoundFlatIconButton):
    pass


class ComicThumb(MDBoxLayout, TouchBehavior, ):
    source = StringProperty()
    str_caption = StringProperty()
    read_progress = NumericProperty()
    percent_read = NumericProperty()
    extra_headers = DictProperty()
    tooltip_text = StringProperty()
    item_id = StringProperty()
    thumb_type = StringProperty()
    rl_book_count = NumericProperty()
    rl_name = StringProperty()
    view_mode = StringProperty("Server")
    comic_obj = ObjectProperty(rebind=True)

    def __init__(self, comic_obj=None, **kwargs):
        super(ComicThumb, self).__init__(**kwargs)
        self.source = ""
        self.item_id = kwargs.get('item_id')
        if comic_obj is None:
            pass
        else:
            self.comic_obj = comic_obj
            UserLastPageRead = self.comic_obj.UserLastPageRead
            PageCount = comic_obj.PageCount

            self.percent_read = round(
                UserLastPageRead
                / PageCount
                * 100
            )

    def on_short_touch(self):
        if self.thumb_type == "ReadingList":
            self.open_readinglist()
        elif self.thumb_type == "ComicBook":
            self.open_comic()
        else:
            print("No Item")

    def on_long_touch(self, touch, *args):
        """Called when the widget is pressed for a long time."""

    def on_double_tap(self, touch, *args):
        """Called by double clicking on the widget."""

    def on_triple_tap(self, touch, *args):
        """Called by triple clicking on the widget."""

    def open_readinglist(self):
        app = MDApp.get_running_app()
        if self.item_id == "NOID":
            pass
        else:
            def __wait_for_open(dt):
                if server_readinglists_screen.loading_done is True:
                    app.manager_screens.current = "r l comic books screen"

            server_readinglists_screen = app.manager_screens.get_screen(
                "r l comic books screen"
            )
            server_readinglists_screen.setup_screen()
            server_readinglists_screen.page_number = 1
            readinglist_id = self.item_id
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
            # set_mode = 'From Server'
            Clock.schedule_once(
                lambda dt: server_readinglists_screen.collect_readinglist_data(
                    readinglist_name=readinglist_name,
                    readinglist_Id=readinglist_id,
                    mode=set_mode,
                    rl_book_count=self.rl_book_count
                )
            )
            self.ids.top_box.remove_tooltip()
            app.manager_screens.current = "r l comic books screen"

    def open_comic(self):
        app = MDApp.get_running_app()
        if self.comic_obj is not None:
            screen = app.manager_screens.get_screen("comic book screen")
            screen.setup_screen(
                readinglist_obj=self.readinglist_obj,
                comic_obj=self.comic_obj,
                paginator_obj=self.paginator_obj,
                pag_pagenum=self.pag_pagenum,
                last_load=0,
                view_mode=self.view_mode,
            )
            Clock.schedule_once(lambda dt: self.open_comic_callback(), 0.1)
        else:
            pass

    def open_comic_callback(self, *args):
        self.ids.top_box.remove_tooltip()
        app = MDApp.get_running_app()
        app.manager_screens.current = "comic book screen"