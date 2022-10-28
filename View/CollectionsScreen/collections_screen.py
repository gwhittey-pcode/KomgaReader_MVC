from View.ComicListsBaseScreen import ComicListsBaseScreenView


class CollectionsScreenView(ComicListsBaseScreenView):
    def model_is_changed(self) -> None:
        """
        Called whenever any change has occurred in the data model.
        The view in this method tracks these changes and updates the UI
        according to these changes.
        """
