
from View.ComicListsBaseScreen.comic_lists_base_screen import ComicListsBaseScreenView


class ComicListsBaseScreenController:
    """
    The `ComicListsBaseScreenController` class represents a controller implementation.
    Coordinates work of the view with the model.
    The controller implements the strategy pattern. The controller connects to
    the view to control its actions.
    """

    def __init__(self, model):
        self.model = model  # Model.comic_lists_base_screen.ComicListsBaseScreenModel
        self.view = ComicListsBaseScreenView(controller=self, model=self.model)

    def get_view(self) -> ComicListsBaseScreenView:
        return self.view
