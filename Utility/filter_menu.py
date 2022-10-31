from kivymd.app import MDApp
from kivymd.uix.menu import MDDropdownMenu

from Utility.komga_server_conn import ComicServerConn


def filter_menu_build():
    screen = MDApp.get_running_app().manager_screens.current_screen
    publisher_menu = MDDropdownMenu()

    def __got_publisher_data(results):
        filter_menu_items = results
        publisher_menu_items = []
        screen.filter_menu = MDDropdownMenu()
        for item in filter_menu_items:
            publisher_menu_items.append(
                {
                    "text": f"{item}",
                    "viewclass": "MDDropdownMenu",
                    "on_release": lambda x="Publisher": filter_menu_callback(x),
                }
            )

            publisher_menu.caller = screen.filter_menu
            publisher_menu.items = publisher_menu_items
            publisher_menu.width_mult = 5
            # max_height=dp(240)

        item_per_menu_items = [{
            "text": f"Publisher",
            "viewclass": publisher_menu,
            "on_release": lambda x="Publisher": filter_menu_callback(x),
        }]

        screen.filter_menu.caller=screen.ids.filter_menu_button
        screen.filter_menu.items=item_per_menu_items
        screen.filter_menu.width_mult=5
        # max_height=dp(240)


    fetch_data = ComicServerConn()
    url_send = f"{screen.base_url}/api/v1/publishers"
    fetch_data.get_server_data_callback(
        url_send,
        callback=lambda url_send, results: __got_publisher_data(results))

    def filter_menu_callback(text_item):
        publisher_menu.open()
        screen.filter_menu.dismiss()
