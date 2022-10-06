import importlib

import View.ComicBookScreen.comic_book_screen

# We have to manually reload the view module in order to apply the
# changes made to the code on a subsequent hot reload.
# If you no longer need a hot reload, you can delete this instruction.
importlib.reload(View.ComicBookScreen.comic_book_screen)




class ComicBookScreenController:
    """
    The `ComicBookScreenController` class represents a controller implementation.
    Coordinates work of the view with the model.
    The controller implements the strategy pattern. The controller connects to
    the view to control its actions.
    """

    def __init__(self, model):
        self.model = model  # Model.comic_book_screen.ComicBookScreenModel
        self.view = View.ComicBookScreen.comic_book_screen.ComicBookScreenView(controller=self, model=self.model)

    def get_view(self) -> View.ComicBookScreen.comic_book_screen:
        return self.view
