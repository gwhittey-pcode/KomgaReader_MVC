import urllib

from kivy.factory import Factory
from kivy.properties import StringProperty, ListProperty, ObjectProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.uix.stacklayout import StackLayout
from kivymd.app import MDApp
from kivymd.theming import ThemableBehavior
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.list import OneLineAvatarIconListItem, ILeftBodyTouch, IRightBodyTouch
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.utils import asynckivy

from View.Widgets.customexpansionpanel import CustomeMDExpansionPanel, CustomeMDExpansionPanelOneLine

register = Factory.register
register("FilterPopupContent", module="View.Widgets.filterpopup.filter_popup")


class FilterPopup(ThemableBehavior, Popup):
    canvas_color = ListProperty()
    callback = ObjectProperty(lambda x: None)
    tcontent = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.canvas_color = self.theme_cls.primary_color
        self.canvas_color[3] = 0.1

    # def make_popup(self):
    #     self.tcontent = FilterPopupContent()
    #
    #
    #     return filter_popup


class FilterPopupContent(StackLayout):
    info_text = StringProperty()
    show_filter_remove = BooleanProperty(True)
    show_pub_filter = BooleanProperty(True)
    show_sort_filter = BooleanProperty(True)

    @staticmethod
    def apply_filter():
        screen = MDApp.get_running_app().manager_screens.current_screen
        screen.filter_popup.dismiss()
        pub_list = MDApp.get_running_app().filter_list
        tmp_filter_list = ""
        for item in pub_list:
            for i, filter_type in enumerate(item.keys()):
                if filter_type == "sort":
                    a_filter_part = f"{item[filter_type]['value']},{item[filter_type]['dir']}"
                    a_filter_part = urllib.parse.quote(a_filter_part)
                    tmp_filter_list += f"&{filter_type}={a_filter_part}"
                else:
                    tmp_filter_list += f"&{filter_type}={urllib.parse.quote(item[filter_type]['value'])}"
        print(f"{tmp_filter_list = }")
        MDApp.get_running_app().filter_string = tmp_filter_list
        if screen.name == "r l comic books screen":
            screen.collect_readinglist_data(readinglist_name=screen.readinglist_name,
                                       readinglist_Id=screen.readinglist_Id, new_page_num=0)
        elif screen.name == "series comics screen":
            screen.collect_series_data(series_name=screen.series_name,
                                       series_Id=screen.series_Id, new_page_num=0)
        else:
            screen.get_server_lists(new_page_num=0)

    @staticmethod
    def clear_filters():
        app = MDApp.get_running_app()

        screen = MDApp.get_running_app().manager_screens.current_screen
        for item in screen.content_obj_list:
            for child in item.walk():
                if isinstance(child, ListItemWithCheckbox):
                    child.ids.the_checkbox.state = "normal"

        app.filter_string = ""
        app.filter_list.clear()
        print(f"{app.filter_list =}")
class MyMDExpansionPanel(CustomeMDExpansionPanel):
    pid = StringProperty("MDExpanis")

    def __init__(self, **kwargs):
        super(MyMDExpansionPanel, self).__init__(**kwargs)


class ReadProgressPanel(MDBoxLayout):
    def __init__(self, **kwargs):
        super(ReadProgressPanel, self).__init__(**kwargs)

    def build_list(self):
        async def __build_list():
            screen = MDApp.get_running_app().manager_screens.current_screen
            if screen.name in ["series screen", "collection comics screen"]:
                read_prgoress_menu_items = ['Unread', 'In Progress', 'Read', 'Complete']
            else:
                read_prgoress_menu_items = ['Unread', 'In Progress', 'Read']
            for i in read_prgoress_menu_items:
                asynckivy.sleep(0)
                self.ids.read_progress_list.add_widget(
                    ListItemWithCheckbox(text=f"{i}", check_box_value=f"{i}", pos_hint={"top": 1},
                                         filter_type="read_status"),

                )

        asynckivy.start(__build_list())


class PublisherPanel(MDBoxLayout):
    def __init__(self, **kwargs):
        super(PublisherPanel, self).__init__(**kwargs)

    def build_list(self):
        async def __build_list():
            screen = MDApp.get_running_app().manager_screens.current_screen
            filter_menu_items = []
            if screen.name == "collection comics screen":
                filter_menu_items = screen.collection_publisher_list
            else:
                filter_menu_items = MDApp.get_running_app().gen_publisher_list
            for i in filter_menu_items:
                asynckivy.sleep(0)
                self.ids.pub_list.add_widget(
                    ListItemWithCheckbox(text=f"{i}", check_box_value=f"{i}", filter_type="publisher")
                )

        asynckivy.start(__build_list())


class ReleaseDatePanel(MDBoxLayout):
    def __init__(self, **kwargs):
        super(ReleaseDatePanel, self).__init__(**kwargs)

    def build_list(self):
        async def __build_list():
            release_dates = []
            screen = MDApp.get_running_app().manager_screens.current_screen
            if screen.name == "collection comics screen":
                release_dates = screen.collection_release_dates
            else:
                release_dates = MDApp.get_running_app().gen_release_dates

            for i in release_dates:
                await asynckivy.sleep(0)
                self.ids.release_dates_add.add_widget(
                    ListItemWithCheckbox(text=f"{i}", check_box_value=f"{i}", filter_type="release_year")
                )

        asynckivy.start(__build_list())


class SortPanel(MDBoxLayout):
    def __init__(self, **kwargs):
        super(SortPanel, self).__init__(**kwargs)

    def build_list(self):
        async def __build_list():
            screen = MDApp.get_running_app().manager_screens.current_screen
            filter_menu_items = []
            if screen.name in ("reading list screen", "series screen", "collections screen"):
                filter_menu_items = [
                    {"Name": "metadata.titleSort"}, {"Date added": "createdDate"},
                    {"Date updated": "lastModifiedDate"}, {"Release date": "booksMetadata.releaseDate"},
                    {"Folder Name": "name"}, {"Books Count": "booksCount"}
                ]
            elif screen.name == "series comics screen":
                filter_menu_items = [
                    {"Number": "metadata.numberSort"}, {"Date added": "createdDate"},
                    {"Release date": "metadata.releaseDate"}, {"File Size": "size"}, {"Filename": "name"}]
            # app = MDApp.get_running_app().manager_screens.current_screen
            # app.sort_filter_list = filter_menu_items
            for dict_item in filter_menu_items:
                asynckivy.sleep(0)
                for name, value in dict_item.items():
                    self.ids.sort_list.add_widget(
                        SortTypeList(text=f"{name}", icon="", id=f"{value}", filter_type="sort")
                    )

        asynckivy.start(__build_list())


class ListItemWithCheckbox(OneLineAvatarIconListItem):
    """Custom list item."""
    icon = StringProperty("")
    check_box_value = StringProperty()
    filter_type = StringProperty()

    def __str__(self):
        return f"{self.check_box_value}({self.filter_type})"

    def check_box_active(self, check_box_value):
        chk_value = ""
        if self.filter_type == 'read_status':
            chk_value = check_box_value.replace(" ", "_").upper()
        else:
            chk_value = check_box_value
        filter_item = {self.filter_type: {"value": chk_value, "dir": ""}}
        if filter_item in MDApp.get_running_app().filter_list:
            MDApp.get_running_app().filter_list.remove(filter_item)
        else:
            MDApp.get_running_app().filter_list.append(filter_item)


class LeftCheckbox(ILeftBodyTouch, MDCheckbox):
    id = StringProperty()

    def __init__(self, **kwargs):
        super(LeftCheckbox, self).__init__(**kwargs)

    def __str__(self):
        return f"{self.id} : {self.state}"

    """Custom right container."""


class RightCheckbox(IRightBodyTouch, MDCheckbox):
    '''Custom right container.'''


class SortTypeList(OneLineAvatarIconListItem):
    def __init__(self, **kwargs):
        super(SortTypeList, self).__init__(**kwargs)

    id = StringProperty()
    what_chevron = StringProperty()
    icon = StringProperty()
    filter_type = StringProperty()

    def __str__(self):
        return f"{self.id}({self.filter_type})"

    def set_sort(self):
        print(f"{self.id =}")
        if self.what_chevron == "down":
            self.what_chevron = "up"
            sort_dir = "asc"
        else:
            sort_dir = "desc"
            self.what_chevron = "down"

        filter_item = {self.filter_type: {"value": self.id, "dir": sort_dir}}
        the_item = None
        action = ""

        i = 0
        for item in MDApp.get_running_app().filter_list:
            print(f"{item = }")
            for x, filter_type in enumerate(item.keys()):
                if filter_type == "sort":
                    action = "remove"
                    the_item = i
            i += 1
        if action == "remove":
            MDApp.get_running_app().filter_list.pop(the_item)
            MDApp.get_running_app().filter_list.append(filter_item)
        else:
            MDApp.get_running_app().filter_list.append(filter_item)
        for child in self.parent.children:
            if child.id != self.id:
                child.what_chevron = ""
        print(f"{MDApp.get_running_app().filter_list =}")
