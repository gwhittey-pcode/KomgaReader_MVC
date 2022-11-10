
from View.CollectionsScreen.collections_screen import CollectionsScreenView


class CollectionsScreenController:
    """
    The `CollectionsScreenController` class represents a controller implementation.
    Coordinates work of the view with the model.
    The controller implements the strategy pattern. The controller connects to
    the view to control its actions.
    """

    def __init__(self, model):
        self.model = model  # Model.collections_screen.CollectionsScreenModel
        self.view = CollectionsScreenView(controller=self, model=self.model)

    def get_view(self) -> CollectionsScreenView:
        return self.view
