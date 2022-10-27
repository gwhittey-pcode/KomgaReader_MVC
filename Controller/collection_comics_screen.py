
from View.CollectionComicsScreen.collection_comics_screen import CollectionComicsScreenView


class CollectionComicsScreenController:
    """
    The `CollectionComicsScreenController` class represents a controller implementation.
    Coordinates work of the view with the model.
    The controller implements the strategy pattern. The controller connects to
    the view to control its actions.
    """

    def __init__(self, model):
        self.model = model  # Model.collection_comics_screen.CollectionComicsScreenModel
        self.view = CollectionComicsScreenView(controller=self, model=self.model)

    def get_view(self) -> CollectionComicsScreenView:
        return self.view
