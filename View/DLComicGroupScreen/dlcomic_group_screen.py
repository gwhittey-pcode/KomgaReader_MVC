import math
import os
from pathlib import Path

from kivy.core.window import Window
from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.utils import asynckivy

from View.ComicListsBaseScreen import ComicListsBaseScreenView
from View.Widgets.comicthumb import ComicThumb
from View.Widgets.dialogs.dialogs import DialogLoadKvFiles
from View.Widgets.paginationwidgets.pagination_widgets import build_pageination_nav
from View.base_screen import BaseScreenView
from libs.database import Series, ReadingList, Comic, get_db


class DLComicGroupScreenView(ComicListsBaseScreenView):

    def __init__(self, **kwargs):
        super(DLComicGroupScreenView, self).__init__(**kwargs)
        self.session = None
        self.dialog_load_comic_data = None
        self.last = None
        self.first = False
        self.comic_group_id = None
        self.group_type = None
        self.totalPages = None
        self.comic_thumb_height = None
        self.current_page = 0
        self.group_type = 'series'

    def get_comicgroup_data(self, comic_group_id, group_type, new_page_num=0):
        self.ids.main_scroll.scroll_y = 1
        self.current_page = new_page_num
        app = MDApp.get_running_app()

        self.comic_group_id = comic_group_id
        self.group_type = group_type
        self.session = next(get_db())
        if group_type == "readlist":
            comic_group = self.session.query(ReadingList).filter(ReadingList.readlist_id == comic_group_id).first()
        else:
            comic_group = self.session.query(Series).filter(Series.series_id == comic_group_id).first()
        self.totalPages = (len(comic_group.comics) + int(self.item_per_page) - 1) // int(self.item_per_page)
        self.page_title = comic_group.name
        if self.current_page == 0:
            self.first = True
        else:
            self.first = False
        if self.current_page == self.totalPages:
            self.last = True
        else:
            self.last = False
        build_pageination_nav(screen_name="dlcomic group screen")
        self.build_page(comic_group=comic_group)

    def pag_num_press(self, i):
        self.get_comicgroup_data(new_page_num=int(i.text) - 1,
                                 comic_group_id=self.comic_group_id, group_type=self.group_type,
                                 )

    def ltgtbutton_press(self, i):
        if i.icon == "less-than":
            self.collect_readinglist_data(new_page_num=int(self.current_page) - 1,
                                          comic_group_id=self.comic_group_id,
                                          group_type=self.group_type
                                          )
        elif i.icon == "greater-than":
            self.get_comicgroup_data(new_page_num=int(self.current_page) + 1,
                                     comic_group_id=self.comic_group_id,
                                     group_type=self.group_type
                                     )

    def build_page(self, comic_group=None):
        async def _build_page():
            self.m_grid = self.ids["main_grid"]
            grid = self.m_grid
            grid.clear_widgets()
            self.comic_thumb_height = 240
            current_slice = self.current_page * self.item_per_page
            start_slice = int(self.current_page) * int(self.item_per_page)
            end_slice = int(int(self.current_page) + 1) * int(self.item_per_page)
            i = 1
            for comic in comic_group.comics[start_slice:end_slice]:
                c = ComicThumb(item_id=comic.comic_id, comic_obj=comic, thumb_type="download_group")
                c.lines = 2
                if self.group_type == "readlist":
                    c.comiclist_obj = comic.readinglists[0]
                else:
                    c.comiclist_obj = comic.series[0]
                c.str_caption = f"  {comic.series_name} \n  #{comic.number} - " \
                                f"{comic.title[:12]}... \n  {comic.page_count} Pages"
                # c.tooltip_text = f"{comic.Series}\n#{comic.Number} - {comic.Title}"

                c.comic_list_type = "series"
                c.text_size = dp(8)
                c.current_page = self.current_page
                c.first = self.first
                c.last = self.last
                c.totalPages = self.totalPages
                c.item_per_page = self.item_per_page
                y = self.comic_thumb_height
                thumb_filename = f"{comic.comic_id}.jpg"
                id_folder = self.app.store_dir
                my_download_folder = Path(os.path.join(id_folder, "download_comic_files"))
                my_thumb_dir = Path(os.path.join(my_download_folder, "comic_thumbs"))
                t_file = os.path.join(my_thumb_dir, thumb_filename)
                c_image_source = t_file
                c.source = c_image_source
                grid.add_widget(c)
                self.comic_thumbs_list.append(c)
                str_name = "{} #{}".format(comic.series_name, comic.number)
                self.dialog_load_comic_data.name_kv_file = str_name
                self.dialog_load_comic_data.percent = str(
                    i * 100 // int(self.item_per_page)
                )
                i += 1
            grid.cols = math.floor((Window.width - dp(20)) // self.app.comic_thumb_width)
            self.dialog_load_comic_data.dismiss()
            self.session.close()
            
        self.dialog_load_comic_data = DialogLoadKvFiles()
        self.dialog_load_comic_data.str_text = "Loading Data From DB"
        self.dialog_load_comic_data.open()
        asynckivy.start(_build_page())
