
from View.RecommendedScreen.recommended_screen import RecommendedScreenView


class RecommendedScreenController:
    """
    The `RecommendedScreenController` class represents a controller implementation.
    Coordinates work of the view with the model.
    The controller implements the strategy pattern. The controller connects to
    the view to control its actions.
    """

    def __init__(self, model):
        self.model = model  # Model.recommended_screen.RecommendedScreenModel
        self.view = RecommendedScreenView(controller=self, model=self.model)

    def get_view(self) -> RecommendedScreenView:
        return self.view
