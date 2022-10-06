import importlib

import View.RLComicBooksScreen.r_l_comic_books_screen

# We have to manually reload the view module in order to apply the
# changes made to the code on a subsequent hot reload.
# If you no longer need a hot reload, you can delete this instruction.
importlib.reload(View.RLComicBooksScreen.r_l_comic_books_screen)




class RLComicBooksScreenController:
    """
    The `RLComicBooksScreenController` class represents a controller implementation.
    Coordinates work of the view with the model.
    The controller implements the strategy pattern. The controller connects to
    the view to control its actions.
    """

    def __init__(self, model):
        self.model = model  # Model.r_l_comic_books_screen.RLComicBooksScreenModel
        self.view = View.RLComicBooksScreen.r_l_comic_books_screen.RLComicBooksScreenView(controller=self, model=self.model)

    def get_view(self) -> View.RLComicBooksScreen.r_l_comic_books_screen:
        return self.view
