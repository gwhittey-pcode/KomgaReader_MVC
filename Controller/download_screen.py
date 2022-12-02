
from View.DownloadScreen.download_screen import DownloadScreenView


class DownloadScreenController:
    """
    The `DownloadScreenController` class represents a controller implementation.
    Coordinates work of the view with the model.
    The controller implements the strategy pattern. The controller connects to
    the view to control its actions.
    """

    def __init__(self, model):
        self.model = model  # Model.download_screen.DownloadScreenModel
        self.view = DownloadScreenView(controller=self, model=self.model)

    def get_view(self) -> DownloadScreenView:
        return self.view
