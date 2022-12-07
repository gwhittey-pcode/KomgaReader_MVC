from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.menu.menu import MDMenu, MDDropdownMenu


def item_per_menu_build():
    item_per_menu_numbers = ("20", "50", "100", "200", "500")
    item_per_menu_items = []
    screen = MDApp.get_running_app().manager_screens.current_screen
    for nums in item_per_menu_numbers:
        if int(nums) == int(screen.item_per_page):
            background_color = screen.app.theme_cls.primary_color
        else:
            background_color = (1, 1, 1, 1)
        item_per_menu_items.append(
            {
                "text": f"{nums}",
                "viewclass": "OneLineListItem",
                "on_release": lambda x=f"{nums}": item_per_menu_callback(x),
                "bg_color": background_color
            }
        )
    screen = MDApp.get_running_app().manager_screens.current_screen
    screen.item_per_menu = MDDropdownMenu(
        caller=screen.ids.item_per_menu_button,
        items=item_per_menu_items,
        width_mult=1.6,
        radius=[24, 0, 24, 0],
        max_height=dp(240),
    )


def item_per_menu_callback(text_item):
    screen = MDApp.get_running_app().manager_screens.current_screen
    screen.item_per_menu.dismiss()
    new_item_per_page = text_item
    MDApp.get_running_app().item_per_page = new_item_per_page
    screen.item_per_page = new_item_per_page
    screen.app.config.set("General", "max_item_per_page", new_item_per_page)
    screen.app.config.write()
    if screen.name == "r l comic books screen":
        screen.collect_readinglist_data(
            new_page_num=int(screen.current_page) - 1,
            readinglist_Id=screen.readinglist_Id
        )
    elif screen.name =="series comics screen":
        screen.collect_series_data(
            series_name=screen.series_name,
            series_Id=screen.series_Id,
        )
    elif screen.name == "collection comics screen":
        screen.get_server_lists(new_page_num=screen.current_page,
                                collection_id=screen.collection_id,
                                collection_name=screen.page_title
                                )
    elif screen.name == "dlcomic group screen":
        screen.get_comicgroup_data(new_page_num=0,
                                 comic_group_id=screen.comic_group_id, group_type=screen.group_type,
                                 )
    else:
        screen.get_server_lists(new_page_num=screen.current_page)
    item_per_menu_build()
