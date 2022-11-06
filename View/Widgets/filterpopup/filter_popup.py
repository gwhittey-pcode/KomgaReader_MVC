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

    def clear_filters(self):
        if self.show_pub_filter:
            self.show_pub_filter = False
        elif not self.show_pub_filter:
            self.show_pub_filter = True


class MyMDExpansionPanel(CustomeMDExpansionPanel):
    pid = StringProperty("MDExpanis")

    def __init__(self, **kwargs):
        super(MyMDExpansionPanel, self).__init__(**kwargs)


class ReadProgressPanel(MDBoxLayout):
    def __init__(self, **kwargs):
        super(ReadProgressPanel, self).__init__(**kwargs)

    def build_list(self):
        async def __build_list():
            read_prgoress_menu_items = ['Unread', 'In Progress', 'Read', 'Complete']
            for i in read_prgoress_menu_items:
                asynckivy.sleep(0)
                self.ids.read_progress_list.add_widget(
                    ListItemWithCheckbox(text=f"{i}", check_box_value=f"{i}", pos_hint={"top": 1}),
                )

        asynckivy.start(__build_list())


class PublisherPanel(MDBoxLayout):
    def __init__(self, **kwargs):
        super(PublisherPanel, self).__init__(**kwargs)

    def build_list(self):
        async def __build_list():
            filter_menu_items = ['Antarctic Press', 'Archaia', 'Cartoon Books', 'Crusade', 'Dark Horse Comics',
                                 'DC Comics',
                                 'Dynamite Entertainment', 'Eaglemoss Publications', 'Ediciones Zinco',
                                 'Editorial Televisa', 'Fantagraphics', 'Heroic Publishing', 'IDW Publishing', 'Image',
                                 'Jet City Comics', 'London Night Studios', 'Marvel', 'Marvel Comics', 'Maximum Press',
                                 'Oni Press', 'Scholastic Book Services', 'Star Reach Publications', 'Timely',
                                 'Titan Comics', 'Top Cow']
            for i in filter_menu_items:
                asynckivy.sleep(0)
                self.ids.pub_list.add_widget(
                    ListItemWithCheckbox(text=f"{i}", check_box_value=f"{i}")
                )

        asynckivy.start(__build_list())


class ReleaseDatePanel(MDBoxLayout):
    def __init__(self, **kwargs):
        super(ReleaseDatePanel, self).__init__(**kwargs)

    def build_list(self):
        async def __build_list():
            release_dates = ["2020", "2019", "2018", "2017", "2016", "2015", "2014", "2013", "2012", "2011", "2010",
                             "2009", "2008", "2007", "2006", "2005", "2004", "2003", "2002", "2001", "2000", "1999",
                             "1998", "1997", "1996", "1995", "1994", "1993", "1992", "1991", "1990", "1989", "1988",
                             "1987", "1986", "1985", "1984", "1983", "1982", "1981", "1980", "1979", "1978", "1977",
                             "1976", "1975", "1974", "1972", "1971", "1970", "1968", "1967", "1966", "1964", "1963",
                             "1962", "1961", "1960", "1959", "1954", "1946", "1941", "1940", "1938", "1937"
                             ]
            for i in release_dates:
                await asynckivy.sleep(0)
                self.ids.release_dates_add.add_widget(
                    ListItemWithCheckbox(text=f"{i}", check_box_value=f"{i}")
                )

        asynckivy.start(__build_list())


class SortPanel(MDBoxLayout):
    def __init__(self, **kwargs):
        super(SortPanel, self).__init__(**kwargs)

    def build_list(self):
        async def __build_list():
            screen = MDApp.get_running_app().manager_screens.current_screen
            filter_menu_items = []
            if screen.name == "series comics screen":
                filter_menu_items = ["Number", "Date added", "Dare updated", "Release date", "Folder Name",
                                     "Books Count"]
            elif screen.name == "object list screen":
                filter_menu_items = ["Number", "Date added", "Release date", "File size", "Filename"]
            app = MDApp.get_running_app().manager_screens.current_screen
            app.sort_filter_list = filter_menu_items
            print(f"{app.sort_filter_list =}")
            for i in filter_menu_items:
                asynckivy.sleep(0)
                self.ids.sort_list.add_widget(
                    SortTypeList(text=f"{i}", icon="", id=f"{i}")
                )

        asynckivy.start(__build_list())


class ListItemWithCheckbox(OneLineAvatarIconListItem):
    """Custom list item."""
    icon = StringProperty("")
    check_box_value = StringProperty()

    def check_box_active(self, check_box_value):
        if check_box_value in MDApp.get_running_app().filter_publisher_list:
            MDApp.get_running_app().filter_publisher_list.remove(check_box_value)
        else:
            MDApp.get_running_app().filter_publisher_list.append(check_box_value)
        print(MDApp.get_running_app().filter_publisher_list)


class LeftCheckbox(ILeftBodyTouch, MDCheckbox):
    """Custom right container."""


class RightCheckbox(IRightBodyTouch, MDCheckbox):
    '''Custom right container.'''


class SortTypeList(OneLineAvatarIconListItem):
    def __init__(self, **kwargs):
        super(SortTypeList, self).__init__(**kwargs)

    id = StringProperty()
    what_chevron = StringProperty()
    icon = StringProperty()

    def set_sort(self):
        if self.what_chevron == "down":
            self.what_chevron = "up"
        else:
            self.what_chevron = "down"
        for child in self.parent.children:
            if child.id != self.id:
                child.what_chevron = ""
