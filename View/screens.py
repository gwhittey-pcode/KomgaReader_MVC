# The screens dictionary contains the objects of the models and controllers
# of the screens of the application.


from Model.start_screen import StartScreenModel
from Controller.start_screen import StartScreenController
from Model.reading_list_screen import ReadingListScreenModel
from Controller.reading_list_screen import ReadingListScreenController
from Model.r_l_comic_books_screen import RLComicBooksScreenModel
from Controller.r_l_comic_books_screen import RLComicBooksScreenController
from Model.comic_book_screen import ComicBookScreenModel
from Controller.comic_book_screen import ComicBookScreenController


screens = {
    "start screen": {
        "model": StartScreenModel,
        "controller": StartScreenController,
    },
    "reading list screen": {
        "model": ReadingListScreenModel,
        "controller": ReadingListScreenController,
    },

    "r l comic books screen": {
        "model": RLComicBooksScreenModel,
        "controller": RLComicBooksScreenController,
    },

    "comic book screen": {
        "model": ComicBookScreenModel,
        "controller": ComicBookScreenController,
    },
}