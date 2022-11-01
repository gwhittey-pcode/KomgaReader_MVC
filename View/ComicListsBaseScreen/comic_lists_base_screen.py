from kivy.properties import StringProperty, NumericProperty, ObjectProperty
from kivymd.app import MDApp

from Utility.items_per_page_menu import item_per_menu_build
from View.base_screen import BaseScreenView


class ComicListsBaseScreenView(BaseScreenView):
    page_year = StringProperty("")
    page_title = StringProperty("")
    item_per_page = StringProperty()
    base_url = StringProperty()
    app = ObjectProperty()

    def on_pre_enter(self):
        self.app = MDApp.get_running_app()
        self.item_per_page = self.app.config.get("General", "max_item_per_page")
        self.base_url = self.app.base_url
        item_per_menu_build()
        self.app.filter_nav_drawer.filter_menu_build()
    def model_is_changed(self) -> None:
        """
        Called whenever any change has occurred in the data model.
        The view in this method tracks these changes and updates the UI
        according to these changes.
        """
