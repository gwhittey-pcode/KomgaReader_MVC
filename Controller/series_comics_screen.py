
from View.SeriesComicsScreen.series_comics_screen import SeriesComicsScreenView


class SeriesComicsScreenController:
    """
    The `SeriesComicsScreenController` class represents a controller implementation.
    Coordinates work of the view with the model.
    The controller implements the strategy pattern. The controller connects to
    the view to control its actions.
    """

    def __init__(self, model):
        self.model = model  # Model.series_comics_screen.SeriesComicsScreenModel
        self.view = SeriesComicsScreenView(controller=self, model=self.model)

    def get_view(self) -> SeriesComicsScreenView:
        return self.view
