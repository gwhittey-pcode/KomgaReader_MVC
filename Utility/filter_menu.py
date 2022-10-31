from kivymd.app import MDApp
from kivymd.uix.menu import MDDropdownMenu
from Utility.komga_server_conn import ComicServerConn


def filter_menu_build():
    screen = MDApp.get_running_app().manager_screens.current_screen
    item_per_menu_items = []
    def __got_publisher_data(results):

        filter_menu_items = results
        for item in filter_menu_items:
            item_per_menu_items.append(
                {
                    "text": f"{item}",
                    "viewclass": "ListItemWithCheckbox",
                    "on_release": lambda x=f"{item}": screen.filter_menu_callback(x),
                }
            )
        screen.filter_menu = MDDropdownMenu(
            caller=screen.ids.filter_menu_button,
            items=item_per_menu_items,
            width_mult=5,
            # max_height=dp(240)
        )

    fetch_data = ComicServerConn()
    url_send = f"{screen.base_url}/api/v1/publishers"
    fetch_data.get_server_data_callback(
        url_send,
        callback=lambda url_send, results: __got_publisher_data(results))

    def filter_menu_callback(self, text_item):
        self.filter_menu.dismiss()
