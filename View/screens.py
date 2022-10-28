# The screens dictionary contains the objects of the models and controllers
# of the screens of the application.
from Controller.comic_lists_base_screen import ComicListsBaseScreenController
from Model.comic_lists_base_screen import ComicListsBaseScreenModel
from Model.start_screen import StartScreenModel
from Controller.start_screen import StartScreenController
from Model.reading_list_screen import ReadingListScreenModel
from Controller.reading_list_screen import ReadingListScreenController
from Model.r_l_comic_books_screen import RLComicBooksScreenModel
from Controller.r_l_comic_books_screen import RLComicBooksScreenController
from Model.comic_book_screen import ComicBookScreenModel
from Controller.comic_book_screen import ComicBookScreenController
from Model.series_screen import SeriesScreenModel
from Controller.series_screen import SeriesScreenController
from Model.series_comics_screen import SeriesComicsScreenModel
from Controller.series_comics_screen import SeriesComicsScreenController
from Model.collections_screen import CollectionsScreenModel
from Controller.collections_screen import CollectionsScreenController
from Model.collection_comics_screen import CollectionComicsScreenModel
from Controller.collection_comics_screen import CollectionComicsScreenController
from Model.recommended_screen import RecommendedScreenModel
from Controller.recommended_screen import RecommendedScreenController


screens = {
    "start screen": {
        "model": StartScreenModel,
        "controller": StartScreenController,
    },
    "comic lists base screen": {
        "model": ComicListsBaseScreenModel,
        "controller": ComicListsBaseScreenController,
    },
    "reading list screen": {
        "model": ReadingListScreenModel,
        "controller": ReadingListScreenController,
    },

    "r l comic books screen": {
        "model": RLComicBooksScreenModel,
        "controller": RLComicBooksScreenController,
    },
    "series screen": {
        "model": SeriesScreenModel,
        "controller": SeriesScreenController,
    },

    "series comics screen": {
        "model": SeriesComicsScreenModel,
        "controller": SeriesComicsScreenController,
    },

    "collections screen": {
        "model": CollectionsScreenModel,
        "controller": CollectionsScreenController,
    },

    "collection comics screen": {
        "model": CollectionComicsScreenModel,
        "controller": CollectionComicsScreenController,
    },

    "recommended screen": {
        "model": RecommendedScreenModel,
        "controller": RecommendedScreenController,
    },
    "comic book screen": {
        "model": ComicBookScreenModel,
        "controller": ComicBookScreenController,
    },

}