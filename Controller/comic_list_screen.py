
from View.ComicListScreen.comic_list_screen import ComicListScreenView


class ComicListScreenController:
    """
    The `ComicListScreenController` class represents a controller implementation.
    Coordinates work of the view with the model.
    The controller implements the strategy pattern. The controller connects to
    the view to control its actions.
    """

    def __init__(self, model):
        self.model = model  # Model.comic_list_screen.ComicListScreenModel
        self.view = ComicListScreenView(controller=self, model=self.model)

    def get_view(self) -> ComicListScreenView:
        return self.view
