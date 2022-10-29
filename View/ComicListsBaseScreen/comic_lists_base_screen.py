from kivy.properties import StringProperty

from View.base_screen import BaseScreenView


class ComicListsBaseScreenView(BaseScreenView):
    page_year = StringProperty("")
    page_title = StringProperty("")
    def model_is_changed(self) -> None:

        """
        Called whenever any change has occurred in the data model.
        The view in this method tracks these changes and updates the UI
        according to these changes.
        """
