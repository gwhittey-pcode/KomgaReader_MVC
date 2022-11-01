from kivy.properties import StringProperty
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.expansionpanel import MDExpansionPanel, MDExpansionPanelThreeLine
from kivymd.uix.list import OneLineListItem, OneLineAvatarIconListItem, ILeftBodyTouch, IRightBodyTouch
from kivymd.uix.navigationdrawer import MDNavigationDrawer
from kivymd.uix.selectioncontrol import MDCheckbox

from Utility.komga_server_conn import ComicServerConn


class PublisherPanel(MDBoxLayout):
    def __init__(self, **kwargs):
        super(PublisherPanel, self).__init__(**kwargs)

        def __got_publisher_data(results):
            filter_menu_items = results
            for i in filter_menu_items:
                self.ids.pub_list.add_widget(
                    ListItemWithCheckbox(text=f"{i}", check_box_value=f"{i}")
                )

        fetch_data = ComicServerConn()
        url_send = f"{MDApp.get_running_app().base_url}/api/v1/publishers"
        fetch_data.get_server_data_callback(
            url_send,
            callback=lambda url_send, results: __got_publisher_data(results))


class MyMDNavigationDrawer(MDNavigationDrawer):
    def __init__(self, **kwargs):
        super(MyMDNavigationDrawer, self).__init__(**kwargs)

    def filter_menu_build(self):
        top_list = MDExpansionPanel(
            # icon=f"{images_path}kivymd.png",
            content=PublisherPanel(),
            panel_cls=MDExpansionPanelThreeLine(
                text="Text",
                secondary_text="Secondary text",
                tertiary_text="Tertiary text",
            ),
        )
        self.ids.filter_nav_draw.add_widget(top_list)
        for zid in self.ids.filter_nav_draw.ids:
            print(f"{zid =}")


class ListItemWithCheckbox(OneLineAvatarIconListItem):
    """Custom list item."""
    icon = StringProperty("")
    check_box_value = StringProperty()

    def check_box_active(self, check_box_value):
        MDApp.get_running_app().filter_string.append(check_box_value)
        print(MDApp.get_running_app().filter_string)


class LeftCheckbox(ILeftBodyTouch, MDCheckbox):
    """Custom right container."""


class RightCheckbox(IRightBodyTouch, MDCheckbox):
    '''Custom right container.'''
