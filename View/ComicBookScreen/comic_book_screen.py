import json
from functools import partial

from kivy import Logger
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.properties import (
    BooleanProperty,
    DictProperty,
    NumericProperty,
    ObjectProperty,
    StringProperty,
)
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivymd.app import MDApp
from kivymd.toast import toast
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.utils import asynckivy

from Utility.comic_functions import get_comic_page, get_file_page_size
from Utility.comic_json_to_class import ComicReadingList, ComicBook
from Utility.db_functions import Comic
from Utility.komga_server_conn import ComicServerConn
from Utility.myloader import Loader
from View.base_screen import BaseScreenView
from View.Widgets.comicbook_screen_widgets import ComicBookPageScatter, ComicBookPageImage, ThumbPopPageInnerGrid, \
    ComicBookPageThumb, ThumbPopPagebntlbl, CommonComicsScroll, CommonComicsOuterGrid, CommonComicsCoverInnerGrid, \
    CommonComicsCoverImage
from mysettings.settingsjson import settings_json_screen_tap_control
from View.Widgets.paginationwidgets.pagination_widgets import build_pageination_nav


class MyScrollView(ScrollView):
    id = StringProperty()


class TopBarContent(MDBoxLayout):
    pass


class TopBarPopup(Popup):
    def on_open(self):
        """ disable hotkeys while we do this"""
        Window.unbind(on_keyboard=MDApp.get_running_app().events_program)

    def on_dismiss(self):
        Window.bind(on_keyboard=MDApp.get_running_app().events_program)


class MyPopup(Popup):
    id = StringProperty()


class MyGridLayout(GridLayout):
    id = StringProperty()


class TopNavContent(MDBoxLayout):
    first = BooleanProperty(False)
    last = BooleanProperty(False)
    totalPages = NumericProperty()
    current_page = NumericProperty()
    item_per_page = NumericProperty
    readinglist_obj = ObjectProperty()

    def __init__(self, **kwargs):
        super(TopNavContent, self).__init__(**kwargs)
        self.app = MDApp.get_running_app().manager_screens.get_screen("comic book screen")

    def ltgtbutton_press(self, i):

        if i.icon == "less-than":
            self.app.collect_readinglist_data(
                new_page_num=int(self.current_page)-1,
                readinglist_id=self.readinglist_obj.slug,
                current_page_num=self.current_page-1,
            )
        elif i.icon == "greater-than":
            self.app.collect_readinglist_data(
                new_page_num=int(self.current_page)+1,
                readinglist_id=self.readinglist_obj.slug,
                current_page_num=self.current_page+1,
            )

    def pag_num_press(self, i):
        self.app.collect_readinglist_data(
            new_page_num=int(i.text) - 1,
            readinglist_id=self.readinglist_obj.slug,
            current_page_num=self.current_page - 1,
        )


class PaginationNavContent(MDBoxLayout):
    pass


class ComicBookScreenView(BaseScreenView):
    scroller = ObjectProperty()
    top_pop = ObjectProperty()
    section = StringProperty()
    sort_by = StringProperty()
    last_load = NumericProperty()
    str_page_count = StringProperty()
    full_screen = BooleanProperty()
    next_nav_comic_thumb = ObjectProperty()
    prev_nav_comic_thumb = ObjectProperty()
    pag_pagenum = NumericProperty()
    view_mode = StringProperty()
    dynamic_ids = DictProperty({})  # declare class attribute, dynamic_ids
    paginator_obj = ObjectProperty()
    comic_obj = ObjectProperty()
    id = StringProperty()

    def __init__(self, **kwargs):
        super(ComicBookScreenView, self).__init__(**kwargs)
        self.reload_top_nav = False
        self.fetch_data = None
        self.app = MDApp.get_running_app()
        self.base_url = self.app.base_url
        #        self.api_url = self.app.base_url
        self.current_page = None
        self.fetch_data = ComicServerConn()
        self.api_key = self.app.config.get("General", "api_key")

        self.popup_bkcolor = (0.5, 0.5, 0.5, 0.87)
        self.full_screen = False
        self.option_isopen = False
        self.next_dialog_open = False
        self.prev_dialog_open = False
        self.scroller = None
        config_app = MDApp.get_running_app()
        settings_data = json.loads(settings_json_screen_tap_control)
        # Window.bind(on_keyboard=self.events_program)
        for setting in settings_data:
            if setting["type"] == "options":
                tap_config = config_app.config.get(
                    setting["section"], setting["key"]
                )
                if tap_config == "Disabled":
                    self.ids[setting["key"]].disabled = True
        self.my_topbar_content = TopBarContent()
        self.popup = TopBarPopup(
            content=self.my_topbar_content,
            pos_hint={"top": 1},
            size_hint=(1, None),
            height=round(dp(60))
        )
        self.topbar_state = False

    def setup_screen(
            self,
            readinglist_obj=None,
            comic_obj=None,  # noqa
            view_mode="Server",
            paginator_obj=None,
            pag_pagenum=1,
            last_load=0,
            current_page=0,
            first=False,
            last=False,
            totalPages=1,
            item_per_page=20,

            **kwargs,
    ):
        self.current_page = current_page
        self.first = first
        self.last = last
        self.totalPages = totalPages
        self.item_per_page = item_per_page
        self.pag_pagenum = 0
        self.last_load = 0
        self.readinglist_obj = readinglist_obj
        self.comic_obj = comic_obj
        self.paginator_obj = paginator_obj
        self.view_mode = view_mode
        self.app.config.write()
        self.pag_pagenum = pag_pagenum
        self.last_load = last_load
        self.app.open_comic_screen = "None"

        self.session_cookie = self.app.config.get("General", "api_key")
        last_comic_type = "Server"
        self.app.config.set("Saved", "last_comic_id", self.comic_obj.Id)
        self.app.config.set("Saved", "last_comic_type", last_comic_type)
        self.app.config.set(
            "Saved", "last_reading_list_id", self.readinglist_obj.slug
        )
        self.app.config.set(
            "Saved", "last_reading_list_name", self.readinglist_obj.name
        )
        if int(self.pag_pagenum):
            self.app.config.set(
                "Saved", "last_pag_pagnum", self.pag_pagenum
            )

        self.app.config.write()
        comic_book_carousel = self.ids.comic_book_carousel
        comic_book_carousel.clear_widgets()
        if self.scroller:
            self.scroller.clear_widgets()
        if self.top_pop:
            self.top_pop.clear_widgets()
        number_pages = int(comic_obj.PageCount)
        max_comic_pages_limit = int(
            MDApp.get_running_app().config.get(
                "Display", "max_comic_pages_limit"
            )
        )
        if number_pages <= max_comic_pages_limit:
            x_title = "Pages 1 to %s of %s " % (number_pages, number_pages)
        else:
            if self.last_load == 0:
                x_title = "Pages 1 to %s of %s " % (
                    max_comic_pages_limit,
                    number_pages,
                )
            else:
                x_title = "Pages %s to %s of %s " % (
                    max_comic_pages_limit,
                    (self.last_load + max_comic_pages_limit),
                    number_pages,
                )
        self.str_page_count = x_title
        x_title = f"{self.comic_obj.__str__} {x_title}"
        scroll = MyScrollView(
            size_hint=(.4, 1),
            do_scroll_x=True,
            do_scroll_y=False,
            id="page_thumb_scroll",
            scroll_type=["bars", "content"],
            pos_hint={'center_x': 0.5, 'top': 1}
        )
        self.dynamic_ids["page_thumb_scroll"] = scroll
        self.page_nav_popup = MyPopup(
            id="page_nav_popup",
            title=x_title,
            pos_hint={"y": 0},
            size_hint=(1, None),
            height=round(dp(340)),
        )
        self.dynamic_ids["page_nav_popup"] = self.page_nav_popup
        self.page_nav_popup.add_widget(scroll)
        self.scroller = scroll
        outer_grid = MyGridLayout(
            rows=1,
            size_hint=(None, 1),
            spacing=(5, 0),
            padding=(5, 1),
            id="outtergrd",
        )
        outer_grid.bind(minimum_width=outer_grid.setter("width"))
        scroll.add_widget(outer_grid)
        i = 0
        self.use_sections = False
        if number_pages <= max_comic_pages_limit:
            self.use_sections = False
            for i in range(0, number_pages):
                self.add_pages(comic_book_carousel, outer_grid, comic_obj, i)
        else:
            self.use_sections = True
            if self.last_load == 0:
                z = max_comic_pages_limit
                for i in range(0, number_pages)[0:z]:
                    self.add_pages(
                        comic_book_carousel, outer_grid, comic_obj, i
                    )
                self.last_load = max_comic_pages_limit
                self.last_section = 0
            else:
                z = self.last_load + max_comic_pages_limit
                for i in range(0, number_pages)[self.last_load: z]:
                    self.add_pages(
                        comic_book_carousel, outer_grid, comic_obj, i
                    )
                if (self.last_load - max_comic_pages_limit) >= 0:
                    self.last_section = self.last_load - max_comic_pages_limit
                self.last_load = self.last_load + max_comic_pages_limit
            if self.use_sections:
                if i + 1 >= number_pages:
                    self.use_sections = False
                    self.section = "Last"
                elif i + 1 == max_comic_pages_limit:
                    self.section = "First"
                else:
                    self.section = "Section"

        self.close_next_dialog()
        self.close_prev_dialog()
        self.collect_readinglist_data(readinglist_id=self.readinglist_obj.slug,
                                      current_page_num=self.current_page,
                                      new_page_num=self.current_page )
        # self.next_comic = self.get_next_comic()
        # self.prev_comic = self.get_prev_comic()
        # self.build_next_comic_dialog()
        # self.build_prev_comic_dialog()
        self.app.open_comic_screen = self.comic_obj.Id

    def add_pages(self, comic_book_carousel, outer_grid, comic_obj, i):
        def got_page_size(results):
            Logger.debug(results)
            this_page_data = results[i]
            width = int(this_page_data["width"])
            height = int(this_page_data["height"])
            if width > height:
                Logger.debug("Size thing Triggered")
                strCookie = 'SESSION=' + self.session_cookie
                comic_page_image.proxyImage = Loader.image(
                    comic_page_source, nocache=True,
                    extra_headers={"Cookie": strCookie, }
                )
                if comic_page_image.proxyImage.loaded:
                    comic_page_image._new_image_downloaded(
                        comic_page_scatter,
                        outer_grid,
                        comic_obj,
                        i,
                        comic_page_source,
                        comic_page_image.proxyImage,
                    )
                else:
                    comic_page_image.proxyImage.bind(
                        on_load=partial(
                            comic_page_image._new_image_downloaded,
                            comic_page_scatter,
                            outer_grid,
                            comic_obj,
                            i,
                            comic_page_source
                        )
                    )

        strech_image = MDApp.get_running_app().config.get(
            "Display", "stretch_image"
        )

        max_height = MDApp.get_running_app().config.get("Display", "max_height")
        comic_page_scatter = ComicBookPageScatter(
            id="comic_scatter" + str(i),
            comic_page=i,
            do_rotation=False,
            do_translation=False,
            size_hint=(1, 1),
            auto_bring_to_front=True,
            scale_min=1,
        )
        if strech_image == "1":
            s_allow_stretch = True
            s_keep_ratio = False
        else:
            s_allow_stretch = False
            s_keep_ratio = True
        max_height = "Use Original Size"
        if max_height == "Use Original Size":
            s_url_part = f"/api/v1/books/{comic_obj.Id}/pages/{i}?zero_based=true"
        if self.view_mode == "FileOpen" or self.comic_obj.is_sync:
            comic_page_source = get_comic_page(comic_obj, i)
        else:
            comic_page_source = f"{self.app.base_url}{s_url_part}"
        self.strCookie = 'SESSION=' + self.session_cookie
        comic_page_image = ComicBookPageImage(
            comic_slug=comic_obj.slug,
            id="pi_" + str(i),
            allow_stretch=s_allow_stretch,
            keep_ratio=s_keep_ratio,
            comic_page=i,
            source=comic_page_source,
            extra_headers={"Cookie": self.strCookie}
        )
        comic_page_scatter.add_widget(comic_page_image)
        comic_book_carousel.add_widget(comic_page_scatter)
        # Let's make the thumbs for popup
        s_height = round(dp(240))

        s_url_part = f"/api/v1/books/{comic_obj.Id}/pages/{i + 1}/thumbnail"
        if self.view_mode == "FileOpen" or comic_obj.is_sync:
            src_img = get_comic_page(comic_obj, i)
        else:
            src_img = f"{self.app.base_url}{s_url_part}"
        inner_grid = ThumbPopPageInnerGrid(
            id="inner_grid" + str(i), spacing=(0, 0),

        )
        page_thumb = ComicBookPageThumb(
            comic_slug=comic_obj.slug,
            id="page_thumb" + str(i),
            comic_page=i,
            source=src_img,
            allow_stretch=False,
            extra_headers={"Cookie": self.strCookie}
        )

        page_thumb.size_hint_y = None
        page_thumb.height = dp(240)
        inner_grid.add_widget(page_thumb)
        page_thumb.bind(on_release=page_thumb.click)
        smbutton = ThumbPopPagebntlbl(
            text="P%s" % str(i + 1),
            padding=(0, 0),
            id=f"page_thumb_lbl{i}",
            comic_slug=comic_obj.slug,
            comic_page=i,
            text_color=(0, 0, 0, 1),
        )
        inner_grid.add_widget(smbutton)
        smbutton.bind(on_release=smbutton.click)
        outer_grid.add_widget(inner_grid)
        if comic_obj.PageCount - 1 == i:
            self.load_user_current_page()
        s_url_part = f"/api/v1/books/{comic_obj.Id}/pages"
        get_size_url = f"{self.app.base_url}{s_url_part}"
        if self.view_mode == "FileOpen" or self.comic_obj.is_sync:
            width, height = get_file_page_size(comic_page_source)
            data = {"width": width, "height": height}
            got_page_size(data)
        else:
            self.fetch_data.get_page_size_data(
                get_size_url,
                callback=lambda req, results: got_page_size(results),
            )

    def slide_changed(self, index):  # noqa
        if self.app.open_comic_screen == "None":
            return

        def __update_page(key_val=None):
            # db_item = Comic.get(Comic.Id == self.comic_obj.Id)
            for key, value in key_val.items():
                # setattr(db_item, key, value)
                setattr(self.comic_obj, key, value)
                if key == "UserLastPageRead":
                    if self.view_mode == "FileOpen" or (
                            self.view_mode == "Sync" and self.comic_obj.is_sync
                    ):
                        local_readinglists_screen = self.app.manager_screens.get_screen(
                            "local_readinglists_screen"
                        )
                        local_readinglists_screen.page_turn(
                            self.comic_obj.Id, value
                        )
                    else:
                        server_readinglists_screen = self.app.manager_screens.get_screen(
                            "r l comic books screen"
                        )
                        server_readinglists_screen.page_turn(
                            self.comic_obj.Id, value
                        )
            # db_item.save()

        if self.view_mode == "FileOpen" or (
                self.view_mode == "Sync" and self.comic_obj.is_sync
        ):

            if index is not None:

                comic_book_carousel = self.ids.comic_book_carousel
                current_page = comic_book_carousel.current_slide.comic_page
                comic_obj = self.comic_obj
                comic_Id = comic_obj.Id
                if self.comic_obj.is_sync:
                    if current_page + 1 > self.comic_obj.UserLastPageRead:
                        key_val = {
                            "UserLastPageRead": current_page + 1,
                            "UserCurrentPage": current_page + 1,
                        }
                    else:
                        key_val = {"UserCurrentPage": current_page + 1}
                    Clock.schedule_once(
                        lambda dt, key_value={}: __update_page(key_val=key_val)
                    )
        else:

            def updated_progress(results):
                pass

            if index is not None:
                comic_book_carousel = self.ids.comic_book_carousel
                current_page = comic_book_carousel.current_slide.comic_page + 1
                comic_obj = self.comic_obj
                if current_page >= comic_obj.PageCount:
                    completed = 'true'
                else:
                    completed = 'false'
                comic_Id = comic_obj.Id
                update_url = f"{self.app.base_url}/api/v1/books/{comic_Id}/read-progress"
                if current_page > self.comic_obj.UserLastPageRead:
                    key_val = {
                        "UserLastPageRead": current_page,
                        "UserCurrentPage": current_page,
                    }
                else:
                    key_val = {"UserCurrentPage": current_page}
                Clock.schedule_once(
                    lambda dt, key_value={}: __update_page(key_val=key_val)
                )
                self.fetch_data.update_progress(
                    update_url,
                    current_page,
                    completed=completed,
                    callback=lambda req, results: updated_progress(results),
                )
                server_readinglists_screen = self.app.manager_screens.get_screen(
                    "r l comic books screen"
                )
                server_readinglists_screen.page_turn(
                    self.comic_obj.Id, current_page
                )
                for slide in comic_book_carousel.slides:
                    for child in slide.walk():
                        try:
                            if child.id is not None:
                                if "comic_scatter" in child.id:
                                    if child.zoom_state == "zoomed":
                                        child.do_zoom(False)
                        except AttributeError:
                            pass

    def load_user_current_page(self):
        for slide in self.ids.comic_book_carousel.slides:
            if slide.comic_page + 1 == self.comic_obj.UserCurrentPage:
                self.ids.comic_book_carousel.load_slide(slide)

    def page_nav_popup_open(self):
        self.page_nav_popup.open()
        comic_book_carousel = self.ids.comic_book_carousel
        current_slide = comic_book_carousel.current_slide
        for child in self.walk():
            try:
                if child.id == current_slide.id:
                    current_page = child
                    comic_page = current_page.comic_page
            except AttributeError:
                pass
        for child in self.page_nav_popup.walk():
            try:
                if child.id == "page_thumb_scroll":
                    scroller = child
                    for grandchild in scroller.walk():
                        c_page_thumb = f"page_thumb{comic_page}"
                        if grandchild.id == c_page_thumb:
                            target_thumb = grandchild
                            self.scroller.scroll_to(
                                target_thumb, padding=10, animate=True
                            )
            except AttributeError:
                pass

    def load_next_slide(self):
        comic_book_carousel = self.ids.comic_book_carousel
        comic_scatter = comic_book_carousel.current_slide
        if self.use_sections:
            if comic_book_carousel.next_slide is None:
                if self.next_dialog_open is False:
                    self.open_next_dialog()
                    self.next_dialog_open = True
                else:
                    x = self.next_nav_comic_thumb
                    if x.action_do == "load_next_page_comic":
                        self.load_next_page_comic(self.next_nav_comic_thumb)
                    else:
                        self.next_nav_comic_thumb.do_action()
                    self.close_next_dialog()
                return
            else:
                comic_book_carousel.load_next()
                return
        else:
            if (
                    self.comic_obj.PageCount - 1 == comic_scatter.comic_page
                    and comic_book_carousel.next_slide is None
            ):
                if self.next_dialog_open is False:
                    self.open_next_dialog()
                    self.next_dialog_open = True
                else:
                    x = self.next_nav_comic_thumb
                    if x.action_do == "load_next_page_comic":
                        self.load_next_page_comic(self.next_nav_comic_thumb)
                    else:
                        self.next_nav_comic_thumb.do_action()
                    self.close_next_dialog()
                return
            else:
                comic_book_carousel.load_next()

    def load_prev_slide(self):
        comic_book_carousel = self.ids.comic_book_carousel
        comic_scatter = comic_book_carousel.current_slide
        if self.use_sections:
            if comic_book_carousel.previous_slide is None:
                if self.prev_dialog_open is False:
                    self.open_prev_dialog()
                    self.prev_dialog_open = True
                else:
                    x = self.next_nav_comic_thumb
                    if x.action_do == "load_prev_page_comic":
                        self.load_prev_page_comic(self.prev_nav_comic_thumb)
                    else:
                        self.prev_nav_comic_thumb.do_action()
                    self.close_prev_dialog()
                return
            else:
                comic_book_carousel.load_previous()
                return
        else:
            if (
                    comic_scatter.comic_page == 0
                    and comic_book_carousel.previous_slide is None
            ):
                if self.prev_dialog_open is False:
                    self.open_prev_dialog()
                    self.prev_dialog_open = True
                else:
                    x = self.next_nav_comic_thumb
                    if x.action_do == "load_prev_page_comic":
                        self.load_prev_page_comic(self.prev_nav_comic_thumb)
                    else:
                        self.prev_nav_comic_thumb.do_action()
                    self.close_prev_dialog()
                return
            else:
                comic_book_carousel.load_previous()
                return
                ######

    def toggle_option_bar(self):
        if self.topbar_state == True:
            self.popup.dismiss()
            self.topbar_state = False
        else:
            self.popup.open()
            self.topbar_state = True

    def open_top_bar(self):
        self.popup.open()

    def close_top_bar(self):
        self.popup.dismiss()

    def collect_readinglist_data(self, readinglist_id="", current_page_num=1, new_page_num=0, ):
        print(f'readinglist_id:{readinglist_id}')
        """Collect Reaing List Date From Server """
        print("collect_readinglist_data")
        self.readinglist_Id = readinglist_id
        self.page_number = current_page_num
        self.new_page_num = new_page_num
        t_newpage = new_page_num
        fetch_data = ComicServerConn()
        url_send = f"{self.base_url}/api/v1/readlists/{self.readinglist_Id}/books?page={new_page_num}&size={self.item_per_page}"
        print(url_send)
        fetch_data.get_server_data(url_send, self)

    def got_json2(self, req, results):
        self.rl_comics_json = results['content']
        self.rl_json = results
        self.totalPages = self.rl_json['totalPages']
        self.current_page = self.rl_json['pageable']['pageNumber']
        self.last = self.rl_json['last']
        self.first = self.rl_json['first']
        self.new_readinglist = ComicReadingList(
            name=self.readinglist_obj.name,
            data=results,
            slug=self.readinglist_Id,
        )
        for item in self.new_readinglist.comic_json:
            comic_index = self.new_readinglist.comic_json.index(item)
            new_comic = ComicBook(
                item,
                readlist_obj=self.new_readinglist,
                comic_index=comic_index,
            )
            if new_comic not in self.new_readinglist.comics:
                self.new_readinglist.add_comic(new_comic)
            else:
                print("in")
        new_readinglist_reversed = self.new_readinglist.comics[::-1]
        self.readinglist_obj = self.new_readinglist
        print(f"self.readinglist_obj: {self.readinglist_obj}")
        for comic in new_readinglist_reversed:
            print(comic.Id)
        self.build_top_nav()

    def build_top_nav(self):
        print("build_top_nav")
        """
        Build the top popup that contains the readnglist comics
        and links via cover image to open
        them
        """
        if self.top_pop:
            self.reload_top_nav = True
            self.top_pop.dismiss()
        top_nav_content = TopNavContent()
        scroll = top_nav_content.ids.page_thumb_scroll
        self.top_pop = MyPopup(
            id="page_pop",
            title="Comics in List",
            title_align="center",
            content=top_nav_content,
            pos_hint={"top": 1},
            size_hint=(1, None),
            height=round(dp(420)),
        )

        print(f"self.totalPages {self.totalPages}")
        top_nav_content.first = self.first
        top_nav_content.last = self.last
        top_nav_content.current_page = self.new_page_num
        print(f"top_nav_content.current_page:{top_nav_content.current_page}")
        top_nav_content.item_per_page = self.item_per_page
        top_nav_content.totalPages = self.totalPages
        top_nav_content.readinglist_obj = self.readinglist_obj
        grid = CommonComicsOuterGrid(
            id="outtergrd",
            size_hint=(None, None),
            spacing=5,
            padding=(5, 5, 5, 5),
        )
        for child in grid.children:
            print("grid")
            print(child)
            grid.remove_widget(child)
        grid.bind(minimum_width=grid.setter("width"))

        c_readinglist_name = self.readinglist_obj.name
        group_str = f" - Page# {self.new_page_num} of {self.readinglist_obj.totalCount}"
        c_title = f"{c_readinglist_name}{group_str}"
        self.top_pop.title = c_title
        comics_list = self.readinglist_obj.comics[::-1]
        page_num_grid = top_nav_content.ids.page_num_grid
        build_pageination_nav(widget=top_nav_content)
        for comic in comics_list:
            if (
                    comic.is_sync
                    or (self.view_mode != "Sync" and comic.is_sync is False)
                    or self.view_mode == "FileOpen"
            ):
                comic_name = str(comic.__str__)
                s_url_part = f"/api/v1/books/{comic.Id}/pages/1/thumbnail"  # noqa
                if self.view_mode == "FileOpen" or (
                        self.view_mode == "Sync" and comic.is_sync
                ):
                    src_thumb = get_comic_page(comic, 0)
                else:
                    src_thumb = f"{self.app.base_url}{s_url_part}"
                inner_grid = CommonComicsCoverInnerGrid(
                    id="inner_grid" + str(comic.Id), padding=(0, 0, 0, 0)
                )

                comic_thumb = CommonComicsCoverImage(
                    source=src_thumb, id=str(comic.Id), comic_obj=comic,
                    extra_headers={"Cookie": self.strCookie, }
                )
                if self.view_mode == "FileOpen":
                    comic_thumb.mode = "FileOpen"
                elif self.view_mode == "Sync":
                    comic_thumb.mode = "Sync"
                comic_thumb.readinglist_obj = self.readinglist_obj
                comic_thumb.paginator_obj = self.paginator_obj
                comic_thumb.new_page_num = self.current_page
                comic_thumb.current_page = self.current_page
                comic_thumb.comic_obj = comic
                inner_grid.add_widget(comic_thumb)
                comic_thumb.bind(on_release=self.top_pop.dismiss)
                comic_thumb.bind(on_release=comic_thumb.open_collection)
                # smbutton = CommonComicsCoverLabel(text=comic_name)
                smbutton = ThumbPopPagebntlbl(
                    text=comic_name,

                    padding=(1, 1),
                    id=f"comic_lbl{comic.Id}",
                    comic_slug=comic.slug,
                    font_size=10.5,
                    text_color=(0, 0, 0, 1),
                )
                inner_grid.add_widget(smbutton)
                smbutton.bind(on_release=self.top_pop.dismiss)
                smbutton.bind(on_release=comic_thumb.open_collection)
                grid.add_widget(inner_grid)
        scroll.add_widget(grid)
        if self.reload_top_nav:
            self.top_pop.open()

    def model_is_changed(self) -> None:
        """
            Called whenever any change has occurred in the data model.
            The view in this method tracks these changes and updates the UI
            according to these changes.
            """

    def open_next_dialog(self):
        toast("At last page open next comic")
        self.next_dialog.open()

    def next_dialog_closed(self, *args):
        self.next_dialog_open = False

    def close_next_dialog(self, *args):
        try:
            self.next_dialog.dismiss()
            self.next_dialog_open = False
        except Exception:
            pass

    def open_prev_dialog(self):
        toast("At first page open prev comic")
        self.prev_dialog.open()

    def prev_dialog_closed(self, *args):
        self.next_dialog_open = False

    def close_prev_dialog(self, *args):
        try:
            self.prev_dialog.dismiss()
            self.prev_dialog_open = False
        except Exception:
            pass

    def comicscreen_open_collection_popup(self):
        self.top_pop.open()
        # self.pagination_nav_popup.open()
