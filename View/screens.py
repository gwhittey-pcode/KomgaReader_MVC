# The screens dictionary contains the objects of the models and controllers
# of the screens of the application.
from Controller.collections_screen import CollectionsScreenController
# from Controller.object_list_screen import ObjectListScreenController
from Controller.comic_lists_base_screen import ComicListsBaseScreenController
from Controller.reading_list_screen import ReadingListScreenController
from Controller.series_screen import SeriesScreenController
from Model.collections_screen import CollectionsScreenModel
# from Model.object_list_screen import ObjectListScreenModel
from Model.comic_lists_base_screen import ComicListsBaseScreenModel
from Model.reading_list_screen import ReadingListScreenModel
from Model.series_screen import SeriesScreenModel
from Model.start_screen import StartScreenModel
from Controller.start_screen import StartScreenController
from Model.r_l_comic_books_screen import RLComicBooksScreenModel
from Controller.r_l_comic_books_screen import RLComicBooksScreenController
from Model.comic_book_screen import ComicBookScreenModel
from Controller.comic_book_screen import ComicBookScreenController
from Model.series_comics_screen import SeriesComicsScreenModel
from Controller.series_comics_screen import SeriesComicsScreenController
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
    "series screen": {
        "model": SeriesScreenModel,
        "controller": SeriesScreenController,
    },

    "reading list screen": {
        "model": ReadingListScreenModel,
        "controller": ReadingListScreenController,
    },

    "collections screen": {
        "model": CollectionsScreenModel,
        "controller": CollectionsScreenController,
    },
    # "object list screen": {
    #     "model": ObjectListScreenModel,
    #     "controller": ObjectListScreenController,
    # },
    "r l comic books screen": {
        "model": RLComicBooksScreenModel,
        "controller": RLComicBooksScreenController,
    },
    "series comics screen": {
        "model": SeriesComicsScreenModel,
        "controller": SeriesComicsScreenController,
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