
from View.SeriesScreen.series_screen import SeriesScreenView


class SeriesScreenController:
    """
    The `SeriesScreenController` class represents a controller implementation.
    Coordinates work of the view with the model.
    The controller implements the strategy pattern. The controller connects to
    the view to control its actions.
    """

    def __init__(self, model):
        self.model = model  # Model.series_screen.SeriesScreenModel
        self.view = SeriesScreenView(controller=self, model=self.model)

    def get_view(self) -> SeriesScreenView:
        return self.view
