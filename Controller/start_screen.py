import importlib
from kivymd.app import MDApp
import View.StartScreen.start_screen
from kivy.metrics import dp

# We have to manually reload the view module in order to apply the
# changes made to the code on a subsequent hot reload.
# If you no longer need a hot reload, you can delete this instruction.
importlib.reload(View.StartScreen.start_screen)




class StartScreenController:
    """
    The `StartScreenController` class represents a controller implementation.
    Coordinates work of the view with the model.
    The controller implements the strategy pattern. The controller connects to
    the view to control its actions.
    """

    def __init__(self, model):
        self.model = model  # Model.start_screen.StartScreenModel
        self.view = View.StartScreen.start_screen.StartScreenView(controller=self, model=self.model)
        self.app = MDApp.get_running_app()

    def on_tap_button_reading_list(self):
        self.view.manager_screens.current = "reading list screen"

    def on_tap_button_login(self):
        self.view.manager_screens.current = "login screen"

    def get_view(self) -> View.StartScreen.start_screen:
        return self.view
