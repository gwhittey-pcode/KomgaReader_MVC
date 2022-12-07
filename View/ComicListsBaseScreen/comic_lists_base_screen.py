from collections import OrderedDict

import multitasking
from kivy.clock import Clock
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty, ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivymd.app import MDApp
from kivymd.theming import ThemableBehavior
from kivymd.utils import asynckivy

from Utility.items_per_page_menu import item_per_menu_build
from View.Widgets.customexpansionpanel import CustomeMDExpansionPanelOneLine
from View.Widgets.filterpopup import FilterPopup
from View.Widgets.filterpopup.filter_popup import FilterPopupContent, MyMDExpansionPanel, SortPanel, ReleaseDatePanel, \
    PublisherPanel, ReadProgressPanel
from View.Widgets.paginationwidgets.pagination_widgets import build_pageination_nav
from View.base_screen import BaseScreenView
from string import ascii_lowercase as alc
from Utility.myUrlrequest import UrlRequest as myUrlRequest

class ComicListsBaseScreenView(BaseScreenView):
    page_year = StringProperty("")
    page_title = StringProperty("")
    item_per_page = StringProperty()
    base_url = StringProperty()
    app = ObjectProperty()
    show_filter = BooleanProperty(False)
    filter_type = StringProperty("None")
    filter_popup = ObjectProperty(None)
    read_progress_content = ObjectProperty()
    pub_content = ObjectProperty()
    sort_content = ObjectProperty()
    release_date_content = ObjectProperty()
    content_obj_list = ListProperty()
    filter_letter = StringProperty("All")
    is_comic_single = BooleanProperty(False)
    comic_thumbs_list = ListProperty()
    show_download_icon = BooleanProperty(False)
    batch_download = BooleanProperty(False)
    dl_type = StringProperty()
    download_text = StringProperty("")
    def __init__(self, **kwargs):
        super(ComicListsBaseScreenView, self).__init__(**kwargs)
        self.tcontent = None
        app = MDApp.get_running_app()
        # @multitasking.task
        # def get_letter_groups():
        #     self.letter_count = {}
        #
        #     def __got_server_data(req, result):
        #         num_count = 0
        #         series_count = 0
        #         for item in result:
        #             if item['group'] not in alc:
        #                 num_count = num_count + item['count']
        #             else:
        #                 self.letter_count[item['group'].capitalize()] = item['count']
        #                 series_count = series_count + item['count']
        #         app.series_count = series_count + num_count
        #         app.letter_count['#'] = num_count
        #         app.ordered_letter_count = OrderedDict(sorted(app.letter_count.items(), key=lambda t: t[0]))
        #
        #     url_send = f"{self.base_url}/api/v1/series/alphabetical-groups"
        #     str_cookie = "SESSION=" + self.config.get("General", "api_key")
        #     head = {
        #         "Content-type": "application/x-www-form-urlencoded",
        #         "Accept": "application/json",
        #         "Cookie": str_cookie,
        #     }
        #     request = myUrlRequest(
        #         url_send,
        #         req_headers=head,
        #         on_success=__got_server_data,
        #         on_error=app.got_error,
        #         on_redirect=app.got_redirect,
        #         on_failure=app.got_error,
        #     )
    def on_pre_enter(self):
        self.ids.top_bar.elevation = 0
        self.show_filter = False
        self.app = MDApp.get_running_app()
        self.item_per_page = self.app.config.get("General", "max_item_per_page")
        self.base_url = self.app.base_url
        screen = MDApp.get_running_app().manager_screens.current_screen
        self.comic_thumbs_list = []
        if screen.name == "series comics screen":
            self.filter_type = "Series Comics"
            self.show_filter = True
            self.is_comic_single = True
            self.show_download_icon = True
        elif screen.name == "collection comics screen":
            self.show_filter = True
            self.filter_type = "Collection Comics"
            self.show_download_icon = False
        elif screen.name == "r l comic books screen":
            self.show_filter = True
            self.filter_type = "ReadinList Comics"
            self.is_comic_single = True
            self.show_download_icon = True
        elif screen.name == "reading list screen":
            self.show_filter = False
            self.show_download_icon = True
            self.dl_type = "reading list"
        elif screen.name == "collections screen":
            self.show_filter = False
        elif screen.name == "series screen":
            self.show_filter = True
            self.show_download_icon = True
            self.batch_download = True
            self.dl_type = "series"
        elif screen.name == "dlcomic group screen":
            self.show_filter = False
            self.show_download_icon = False
            self.batch_download = True
        # self.content = FilterPopupContent()
        # self.filter_popup =   filter_popup = FilterPopup(
        #     size_hint=(.5, .96),
        #     pos_hint={"right": 1, "top": .95},
        #     title="",
        #     content=self.content,
        #     separator_height=0
        # )
        item_per_menu_build()
        if self.show_filter:
            if self.filter_popup is None:
                self.build_filter_popup()

    def build_filter_popup(self):
        print("1")

        async def _build_filter_popup():
            print("2")
            self.tcontent = FilterPopupContent()
            # Add Publisher filter
            self.read_progress_content = ReadProgressPanel()
            self.content_obj_list.append(self.read_progress_content)
            self.read_progress_content.build_list()
            read_progress_obj = MyMDExpansionPanel(
                id="read_status",
                content=self.read_progress_content,
                panel_cls=CustomeMDExpansionPanelOneLine(
                    text="  Read Progress",

                ),
            )
            self.tcontent.ids.read_progress_filter.add_widget(read_progress_obj)
            if screen.name in ["series screen", "collection comics screen"]:
                self.build_publisher_panel()
            else:
                screen.tcontent.ids.pub_filter_add.opacity = 0
                screen.tcontent.ids.pub_filter_add.disabled = 1
                screen.tcontent.ids.pub_filter_add.size = (1, 1)
            if screen.name in ["series screen", "collection comics screen"]:
                self.build_release_date_panel()
            else:
                print("ok")
                screen.tcontent.ids.release_dates_filter_add.opacity = 0
                screen.tcontent.ids.release_dates_filter_add.disabled = 1
                screen.tcontent.ids.release_dates_filter_add.size = (1, 1)
            if screen.name not in ["r l comic books screen", "collection comics screen"]:
                self.build_sort_panel()
            else:
                screen.tcontent.ids.sort_filter_add.opacity = 0
                screen.tcontent.ids.sort_filter_add.disabled = 1
                screen.tcontent.ids.sort_filter_add.size = (1, 1)
            self.filter_popup = FilterPopup(
                size_hint=(.5, .96),
                pos_hint={"right": 1, "top": .95},
                title="",
                content=self.tcontent,
                separator_height=0
            )

        screen = MDApp.get_running_app().manager_screens.current_screen
        if screen.name not in ["collections screen", "reading list screen"]:
            asynckivy.start(_build_filter_popup())

    def build_publisher_panel(self):
        self.pub_content = PublisherPanel()
        self.content_obj_list.append(self.pub_content)
        self.pub_content.build_list()
        pub_obj = MyMDExpansionPanel(
            id="publisher",
            content=self.pub_content,
            panel_cls=CustomeMDExpansionPanelOneLine(
                text="  Publisher",

            ),
        )
        self.tcontent.ids.pub_filter_add.add_widget(pub_obj)

    def build_release_date_panel(self):
        self.release_date_content = ReleaseDatePanel()
        self.content_obj_list.append(self.release_date_content)
        self.release_date_content.build_list()
        pub_obj = MyMDExpansionPanel(
            id="release_year",
            content=self.release_date_content,
            panel_cls=CustomeMDExpansionPanelOneLine(
                text="  Release Dates",

            ),
        )
        self.tcontent.ids.release_dates_filter_add.add_widget(pub_obj)

    def build_sort_panel(self):
        # add read progress Filter
        self.sort_content = SortPanel()
        self.sort_content.build_list()
        sort_obj = MyMDExpansionPanel(
            id="sort",
            content=self.sort_content,
            panel_cls=CustomeMDExpansionPanelOneLine(
                text="  Sort",

            ),
        )
        self.tcontent.ids.sort_filter_add.add_widget(sort_obj)

    def model_is_changed(self) -> None:
        """
        Called whenever any change has occurred in the data model.
        The view in this method tracks these changes and updates the UI
        according to these changes.
        """
