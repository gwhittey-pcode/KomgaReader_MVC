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
    def __init__(self, **kwargs):
        super(ComicListsBaseScreenView, self).__init__(**kwargs)
        self.tcontent = None

    def on_pre_enter(self):
        self.app = MDApp.get_running_app()
        self.item_per_page = self.app.config.get("General", "max_item_per_page")
        self.base_url = self.app.base_url
        screen = MDApp.get_running_app().manager_screens.current_screen
        print(f"{screen.name =}")
        if screen.name == "series comics screen":
            self.filter_type = "Series Comics"
            self.show_filter = True
        elif screen.name == "collection comics screen":
            self.filter_type = "Collection Comics"
        elif screen.name == "r l comic books screen":
            self.filter_type = "ReadinList Comics"
        elif screen.name == "reading list screen":
            self.show_filter = False
        elif screen.name == "collections screen":
            self.show_filter = True
        elif screen.name == "series screen":
            self.show_filter = True
        # self.content = FilterPopupContent()
        # self.filter_popup =   filter_popup = FilterPopup(
        #     size_hint=(.5, .96),
        #     pos_hint={"right": 1, "top": .95},
        #     title="",
        #     content=self.content,
        #     separator_height=0
        # )
        item_per_menu_build()

        if self.filter_popup is None:
            self.build_filter_popup()


    def build_filter_popup(self):
        async def _build_filter_popup():
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
            # add readpgroess Filter
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

            self.filter_popup = FilterPopup(
                size_hint=(.5, .96),
                pos_hint={"right": 1, "top": .95},
                title="",
                content=self.tcontent,
                separator_height=0
            )
        asynckivy.start(_build_filter_popup())
    def model_is_changed(self) -> None:
        """
        Called whenever any change has occurred in the data model.
        The view in this method tracks these changes and updates the UI
        according to these changes.
        """
