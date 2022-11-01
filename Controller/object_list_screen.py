
from View.ObjectListScreen.object_list_screen import ObjectListScreenView


class ObjectListScreenController:
    """
    The `ComicListScreenController` class represents a controller implementation.
    Coordinates work of the view with the model.
    The controller implements the strategy pattern. The controller connects to
    the view to control its actions.
    """

    def __init__(self, model):
        self.model = model  # Model.comic_list_screen.ComicListScreenModel
        self.view = ObjectListScreenView(controller=self, model=self.model)

    def get_view(self) -> ObjectListScreenView:
        return self.view
