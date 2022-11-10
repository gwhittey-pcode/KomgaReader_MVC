import importlib

import View.ReadingListScreen.reading_list_screen

# We have to manually reload the view module in order to apply the
# changes made to the code on a subsequent hot reload.
# If you no longer need a hot reload, you can delete this instruction.
importlib.reload(View.ReadingListScreen.reading_list_screen)




class ReadingListScreenController:
    """
    The `ReadingListScreenController` class represents a controller implementation.
    Coordinates work of the view with the model.
    The controller implements the strategy pattern. The controller connects to
    the view to control its actions.
    """

    def __init__(self, model):
        self.model = model  # Model.reading_list_screen.ReadingListScreenModel
        self.view = View.ReadingListScreen.reading_list_screen.ReadingListScreenView(controller=self, model=self.model)

    def get_view(self) -> View.ReadingListScreen.reading_list_screen:
        return self.view
