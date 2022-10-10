import json
from functools import partial

from kivy import Logger
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import StringProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivymd.app import  MDApp
from kivymd.toast import toast
from kivymd.uix.boxlayout import MDBoxLayout

from Utility.comic_functions import get_comic_page, get_file_page_size
from Utility.db_functions import Comic
from Utility.komga_server_conn import ComicServerConn
from Utility.myloader import Loader
from View.Widgets.comicbook_screen_widgets import ComicBookPageScatter, ComicBookPageImage, ThumbPopPageInnerGrid, \
    ComicBookPageThumb, ThumbPopPagebntlbl, CommonComicsScroll, CommonComicsOuterGrid, CommonComicsCoverInnerGrid, \
    CommonComicsCoverImage
from View.Widgets.mytoolbar import MDToolbarTooltips
from View.base_screen import BaseScreenView
from kivy.metrics import dp
from kivy.properties import (
    BooleanProperty,
    DictProperty,
    NumericProperty,
    ObjectProperty,
    StringProperty,
)

from mysettings.settingsjson import settings_json_screen_tap_control


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
            **kwargs,
    ):

        self.current_page = None
        self.readinglist_obj = None
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
        self.strCookie = 'SESSION=' + self.session_cookie
        if self.view_mode == "FileOpen":
            pass
        else:
            if self.view_mode == "Sync":
                last_comic_type = "local_file"
            else:
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
        for slide in comic_book_carousel.slides:
            print(slide)
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
        self.build_top_nav()
        self.next_comic = self.get_next_comic()
        self.prev_comic = self.get_prev_comic()
        self.build_next_comic_dialog()
        self.build_prev_comic_dialog()
        self.app.open_comic_screen = self.comic_obj.Id

    def toggle_full_screen(self):
        if self.full_screen is False:
            Window.fullscreen = True
            self.full_screen is True
        else:
            Window.fullscreen = False

    def open_mag_glass(self):
        comic_book_carousel = self.ids.comic_book_carousel
        current_slide = comic_book_carousel.current_slide
        current_slide.open_mag_glass()

    def on_pre_leave(self, *args):
        self.top_pop.dismiss()
        self.popup.dismiss()
        self.page_nav_popup.dismiss()
        # self.option_pop.dismiss()

    def load_user_current_page(self):
        for slide in self.ids.comic_book_carousel.slides:
            if slide.comic_page == self.comic_obj.UserCurrentPage:
                self.ids.comic_book_carousel.load_slide(slide)

    def refresh_callback(self, *args):
        """A method that updates the state of your application
        while the spinner remains on the screen."""

        def refresh_callback(interval):
            pass
            # self.screen.ids.box.clear_widgets()
            # if self.x == 0:
            #     self.x, self.y = 15, 30
            # else:
            #     self.x, self.y = 0, 15
            # self.set_list()
            # self.screen.ids.refresh_layout.refresh_done()
            # self.tick = 0

        Clock.schedule_once(refresh_callback, 1)

    def slide_changed(self, index):  # noqa
        if self.app.open_comic_screen == "None":
            return

        def __update_page(key_val=None):
            db_item = Comic.get(Comic.Id == self.comic_obj.Id)
            for key, value in key_val.items():
                setattr(db_item, key, value)
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
                            self.comic_obj.Id, value - 1
                        )
            db_item.save()

        if self.view_mode == "FileOpen" or (
                self.view_mode == "Sync" and self.comic_obj.is_sync
        ):

            if index is not None:

                comic_book_carousel = self.ids.comic_book_carousel
                current_page = comic_book_carousel.current_slide.comic_page
                comic_obj = self.comic_obj
                comic_Id = comic_obj.Id
                if self.comic_obj.is_sync:
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
                # for slide in comic_book_carousel.slides:
                #     for child in slide.walk():
                #         if child.id is not None:
                #             if "comic_scatter" in child.id:
                #                 if child.zoom_state == "zoomed":
                #                     child.do_zoom(False)
        else:

            def updated_progress(results):
                pass

            if index is not None:
                comic_book_carousel = self.ids.comic_book_carousel
                current_page = comic_book_carousel.current_slide.comic_page
                comic_obj = self.comic_obj
                if current_page >= comic_obj.PageCount:
                    completed = 'true'
                else:
                    completed = 'false'
                comic_Id = comic_obj.Id
                update_url = f"{self.app.base_url}/api/v1/books/{comic_Id}/read-progress"
                if current_page > self.comic_obj.UserLastPageRead:
                    key_val = {
                        "UserLastPageRead": current_page + 1,
                        "UserCurrentPage": current_page + 1,
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

    def add_pages(self, comic_book_carousel, outer_grid, comic_obj, i):
        t_api_key = self.app.config.get("General", "api_key")

        # fire off dblpage split if server replies size of image is
        # width>height

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
        # elif max_height == "Use Window Size":
        #     h = round(dp(Window.height))
        #     # w = round(dp(Window.height))
        #     s_url_part = f"/Comics/{comic_obj.Id}/Pages/{i}?height={h}"
        #     s_url_api = f"&apiKey={t_api_key}"
        # else:
        #     s_max_height = round(dp(max_height))
        #     s_url_part = (
        #         f"/Comics/{comic_obj.Id}/Pages/{i}?height={s_max_height}"
        #     )
        #     s_url_api = f"&apiKey={t_api_key}"
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
        # proxyImage = Loader.image(comic_page_source,nocache=True)
        # proxyImage.bind(on_load=partial(
        #                                comic_page_image._new_image_downloaded,
        #                                 comic_page_scatter,outer_grid,comic_obj,
        #                                 i,comic_page_source
        #                                 )
        #                 )
        if comic_obj.PageCount - 1 == i:
            self.last_page_done = True
            self.load_user_current_page()

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
        # scroller = self.dynamic_ids['page_thumb_scroll']
        # for grandchild in scroller.walk():
        #             c_page_thumb = f'page_thumb{comic_page}'
        #             c_page_lbl = f'page_thumb_lbl{comic_page}'
        #             if grandchild.id == c_page_thumb:
        #                 target_thumb = grandchild
        #                 self.scroller.scroll_to(
        #                     target_thumb, padd7ing=10, animate=True)
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

    def build_top_nav(self):
        """
        Build the top popup that contains the readnglist comics
        and links via cover image to open
        them
        """
        t_api_key = self.app.config.get("General", "api_key")
        scroll = CommonComicsScroll(
            id="page_thumb_scroll",
            size_hint=(1, 1),
            do_scroll_x=True,
            do_scroll_y=False,
        )
        self.top_pop = MyPopup(
            id="page_pop",
            title="Comics in List",
            title_align="center",
            content=scroll,
            pos_hint={"top": 1},
            size_hint=(1, None),
            height=round(dp(340)),
        )
        self.top_pop
        grid = CommonComicsOuterGrid(
            id="outtergrd",
            size_hint=(None, None),
            spacing=5,
            padding=(5, 5, 5, 5),
        )
        grid.bind(minimum_width=grid.setter("width"))
        if self.current_page is None:
            if self.pag_pagenum == 0:
                page = self.paginator_obj.page(1)
                c_pag_pagenum = page.number
            else:
                page = self.paginator_obj.page(self.pag_pagenum)
            comics_list = page.object_list
            self.current_page = page
            c_pag_pagenum = page.number
            page_num = self.paginator_obj.num_pages()
            c_readinglist_name = self.readinglist_obj.name
            group_str = f" - Page# {page.number} of {page_num}"
            c_title = f"{c_readinglist_name}{group_str}"
            self.top_pop.title = c_title
        else:
            page = self.current_page
            c_pag_pagenum = page.number
            page_num = self.paginator_obj.num_pages()
            c_readinglist_name = self.readinglist_obj.name
            group_str = f" - Page# {page.number} of {page_num}"
            c_title = f"{c_readinglist_name}{group_str}"
            self.top_pop.title = c_title
            comics_list = page.object_list
        if page.has_previous():
            comic_name = "Prev Page"
            src_thumb = "assets/prev_page.jpg"
            inner_grid = CommonComicsCoverInnerGrid(
                id="inner_grid" + str("prev"), padding=(1, 1, 1, 1)
            )
            comic_thumb = CommonComicsCoverImage(
                source=src_thumb, id=str("prev"),
                extra_headers={"Cookie": self.strCookie, }
            )
            if self.view_mode == "FileOpen":
                comic_thumb.mode = "FileOpen"
            elif self.view_mode == "Sync":
                comic_thumb.mode = "Sync"
            comic_thumb.readinglist_obj = self.readinglist_obj
            comic_thumb.paginator_obj = self.paginator_obj
            comic_thumb.new_page_num = page.previous_page_number()
            inner_grid.add_widget(comic_thumb)
            comic_thumb.bind(on_release=self.top_pop.dismiss)
            comic_thumb.bind(on_release=self.load_new_page)
            # smbutton = CommonComicsCoverLabel(text=comic_name)
            smbutton = ThumbPopPagebntlbl(
                text=comic_name,

                padding=(1, 1),
                id=f"comic_lbl_prev",
                comic_slug="Prev Comic",
                font_size=10.5,
                text_color=(0, 0, 0, 1),
            )
            inner_grid.add_widget(smbutton)
            smbutton.bind(on_release=self.top_pop.dismiss)
            smbutton.bind(on_release=self.load_new_page)
            grid.add_widget(inner_grid)
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
                comic_thumb.new_page_num = c_pag_pagenum
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
        if page.has_next():
            comic_name = "Next Page"
            src_thumb = "assets/next_page.jpg"
            inner_grid = CommonComicsCoverInnerGrid(
                id="inner_grid" + str("next")
            )
            comic_thumb = CommonComicsCoverImage(
                source=src_thumb, id=str("next"),
                extra_headers={"Cookie": self.strCookie, }
            )
            comic_thumb.readinglist_obj = self.readinglist_obj
            comic_thumb.new_page_num = page.next_page_number()
            comic_thumb.paginator_obj = self.paginator_obj
            inner_grid.add_widget(comic_thumb)
            comic_thumb.bind(on_release=self.top_pop.dismiss)
            comic_thumb.bind(on_release=self.load_new_page)
            # smbutton = CommonComicsCoverLabel(text=comic_name)
            smbutton = ThumbPopPagebntlbl(
                text=comic_name,

                padding=(1, 1),
                id=f"comic_lbl_next",
                comic_slug="Next Comic",
                font_size=10.5,
                text_color=(0, 0, 0, 1),
            )
            inner_grid.add_widget(smbutton)
            smbutton.bind(on_release=self.top_pop.dismiss)
            smbutton.bind(on_release=self.load_new_page)
            grid.add_widget(inner_grid)
        scroll.add_widget(grid)

    def comicscreen_open_collection_popup(self):
        self.top_pop.open()

    def load_new_page(self, instance):
        new_page = self.paginator_obj.page(instance.new_page_num)
        self.current_page = new_page

        self.build_top_nav()
        self.top_pop.open()

    def load_next_page_comic(self, instance):
        new_page = self.paginator_obj.page(instance.new_page_num)
        self.current_page = new_page
        c_pag_pagenum = new_page.number
        screen = self.app.manager_screens.get_screen("comic book screen")
        screen.setup_screen(
            readinglist_obj=self.readinglist_obj,
            paginator_obj=self.paginator_obj,
            pag_pagenum=c_pag_pagenum,
            comic_obj=self.next_comic,
            view_mode=self.view_mode,
        )
        self.app.manager_screens.current = "comic book screen"

    def load_prev_page_comic(self, instance):
        new_page = self.paginator_obj.page(instance.new_page_num)
        self.current_page = new_page
        c_pag_pagenum = new_page.number
        screen = self.app.manager_screens.get_screen("comic book screen")
        screen.setup_screen(
            readinglist_obj=self.readinglist_obj,
            paginator_obj=self.paginator_obj,
            pag_pagenum=c_pag_pagenum,
            comic_obj=self.prev_comic,
            view_mode=self.view_mode,

        )

    def get_next_comic(self):
        n_paginator = self.paginator_obj
        page = self.current_page
        comic_obj = self.comic_obj
        comics_list = page.object_list
        for x in comics_list:
            if str(x.Id) == str(comic_obj.Id):
                index = comics_list.index(x)
        if comic_obj.Id == comics_list[-1].Id and page.has_next():
            n_page = n_paginator.page(page.next_page_number())
            comics_list = n_page.object_list
            next_comic = comics_list[0]
        else:
            if index >= len(comics_list) - 1:
                if len(comics_list) <= 1 or self.use_sections is True:
                    next_comic = self.comic_obj
                else:
                    next_comic = comics_list[index]
            else:
                if len(comics_list) <= 1 or self.use_sections is True:
                    next_comic = self.comic_obj
                else:
                    next_comic = comics_list[index + 1]
        return next_comic

    # TODO Fix when 1 comic is loaded there should not be a
    # next and prev comic.
    def get_prev_comic(self):
        n_paginator = self.paginator_obj
        page = self.current_page
        comics_list = page.object_list
        comic_obj = self.comic_obj
        for x in comics_list:
            if x.Id == comic_obj.Id:
                index = comics_list.index(x)
        if comic_obj.Id == comics_list[0].Id and page.has_previous():
            n_page = n_paginator.page(page.previous_page_number())
            comics_list = n_page.object_list
            prev_comic = comics_list[-1]
        else:
            if index < len(comics_list):
                if index == 0:
                    if self.section == "Section" or self.section == "Last":
                        prev_comic = self.comic_obj

                    else:
                        prev_comic = comics_list[index]
                else:
                    if self.section == "Section" or self.section == "Last":
                        prev_comic = self.comic_obj
                    else:
                        prev_comic = comics_list[index - 1]
        return prev_comic

    def build_next_comic_dialog(self):
        """ Make popup showing cover for next comic"""
        n_paginator = self.paginator_obj
        page = self.current_page
        comics_list = page.object_list
        comic = self.next_comic
        comic_obj = self.comic_obj
        for x in comics_list:
            if x.Id == comic_obj.Id:
                index = comics_list.index(x)
        if index + 1 == len(comics_list) and page.has_next():
            n_page = n_paginator.page(page.next_page_number())
            comics_list = n_page.object_list
            next_page_number = page.next_page_number()
            c_new_page_num = next_page_number
        else:
            c_new_page_num = page.number
        comic_name = str(comic.__str__)
        s_url_part = f"/api/v1/books/{comic.Id}/pages/1"
        if self.view_mode == "FileOpen" or comic.is_sync:
            src_thumb = get_comic_page(comic, 0)
        else:
            src_thumb = f"{self.app.base_url}{s_url_part}"

        inner_grid = CommonComicsCoverInnerGrid(
            id="inner_grid" + str(comic.Id),
            pos_hint={"top": 0.99, "right": 0.1},
        )

        comic_thumb = CommonComicsCoverImage(
            source=src_thumb, id=str(comic.Id), comic_obj=comic,
            extra_headers={"Cookie": self.strCookie, }
        )
        if self.view_mode == "FileOpen":
            comic_thumb.mode = "FileOpen"
        comic_thumb.readinglist_obj = self.readinglist_obj
        comic_thumb.comic = comic
        comic_thumb.last_load = self.last_load
        if self.use_sections:
            comic_thumb.last_section = self.last_section
        comic_thumb.paginator_obj = self.paginator_obj
        comic_thumb.new_page_num = c_new_page_num
        inner_grid.add_widget(comic_thumb)

        smbutton = ThumbPopPagebntlbl(
            text=comic_name, font_size=12, text_color=(0, 0, 0, 1)
        )
        inner_grid.add_widget(smbutton)
        content = inner_grid
        if index >= len(comics_list) - 1:
            if self.use_sections:
                dialog_title = "Load Next Section"
            else:
                if index + 1 == page.end_index():
                    dialog_title = "Load Next Page"
                else:
                    dialog_title = "On Last Comic"
        else:
            if self.use_sections:
                dialog_title = "Load Next Section"
            else:
                if index + 1 == page.end_index():
                    dialog_title = "Load Next Page"
                else:
                    dialog_title = "Load Next Comic"

        self.next_dialog = MyPopup(
            id="next_pop",
            title=dialog_title,
            content=content,
            pos_hint={0.5: 0.724},
            size_hint=(None, None),
            size=(dp(280), dp(340)),
        )
        self.next_dialog.bind(on_dismiss=self.next_dialog_closed)
        c_padding = self.next_dialog.width / 4
        CommonComicsCoverInnerGrid.padding = (c_padding, 0, 0, 0)
        comic_thumb.bind(on_release=self.close_next_dialog)
        self.next_nav_comic_thumb = comic_thumb
        # if index >= len(comics_list)-1:
        #     if self.use_sections:
        #         comic_thumb.bind(on_release=comic_thumb.open_next_section)
        #     else:
        #         if len(comics_list) >= 1:
        #             comic_thumb.bind(on_release=self.load_next_page_comic)
        #         else:
        #             return
        # else:
        #     if self.use_sections:
        #         comic_thumb.bind(on_release=comic_thumb.open_next_section)
        #     else:
        #         if len(comics_list) >= 1:
        #             comic_thumb.bind(on_release=self.load_next_page_comic)
        #         else:
        #             comic_thumb.bind(on_release=comic_thumb.open_collection)

        if index >= len(comics_list) - 1:
            if self.use_sections:
                comic_thumb.action_do = "open_next_section"
                comic_thumb.bind(on_release=comic_thumb.do_action)
            else:
                if len(comics_list) >= 1:
                    comic_thumb.action_do = "load_next_page_comic"
                    comic_thumb.bind(on_release=self.load_next_page_comic)
                else:
                    return
        else:
            if self.use_sections:
                comic_thumb.action_do = "open_next_section"
                comic_thumb.bind(on_release=comic_thumb.do_action)
            else:
                if len(comics_list) >= 1:
                    comic_thumb.action_do = "load_next_page_comic"
                    comic_thumb.bind(on_release=self.load_next_page_comic)
                else:
                    comic_thumb.action_do = "open_collection"
                    comic_thumb.bind(on_release=comic_thumb.do_action)

    def build_prev_comic_dialog(self):
        t_api_key = self.app.config.get("General", "api_key")
        n_paginator = self.paginator_obj
        page = self.current_page
        comics_list = page.object_list
        comic = self.prev_comic
        comic_obj = self.comic_obj
        for x in comics_list:
            if x.Id == comic_obj.Id:
                index = comics_list.index(x)
        prev_page_number = 1
        if index == 0 and page.has_previous():
            n_page = n_paginator.page(page.previous_page_number())
            comics_list = n_page.object_list
            prev_page_number = page.previous_page_number()
        comic_name = str(comic.__str__)
        s_url_part = f"/api/v1/books/{comic.Id}/pages/1"
        if self.view_mode == "FileOpen" or (
                self.view_mode == "Sync" and comic.is_sync
        ):
            src_thumb = get_comic_page(comic, 0)
        else:
            src_thumb = f"{self.app.base_url}{s_url_part}"
        inner_grid = CommonComicsCoverInnerGrid(
            id="inner_grid" + str(comic.Id),
            pos_hint={"top": 0.99, "right": 0.1},
        )
        comic_thumb = CommonComicsCoverImage(
            source=src_thumb,
            id=str(comic.Id),
            pos_hint={0.5: 0.5},
            comic_obj=comic,
            extra_headers={"Cookie": self.strCookie, }
        )
        if self.view_mode == "FileOpen":
            comic_thumb.mode = "FileOpen"
        elif self.view_mode == "Sync":
            comic_thumb.mode = "Sync"
        comic_thumb.readinglist_obj = self.readinglist_obj
        comic_thumb.comic = comic
        if self.use_sections:
            comic_thumb.last_section = self.last_section
        if index == 0 and page.has_previous():
            comic_thumb.new_page_num = prev_page_number
        else:
            comic_thumb.new_page_num = page.number
        comic_thumb.readinglist_obj = self.readinglist_obj
        inner_grid.add_widget(comic_thumb)

        smbutton = ThumbPopPagebntlbl(
            text=comic_name, font_size=12, text_color=(0, 0, 0, 1)
        )
        inner_grid.add_widget(smbutton)
        content = inner_grid
        if index >= len(comics_list) - 1:
            if len(comics_list) >= 1:
                dialog_title = "Load Prev Page"
            else:
                dialog_title = "On First Comic"
        else:
            if index != 0:
                dialog_title = "Load Prev Page"
            else:
                dialog_title = "On First Comic"
        self.prev_dialog = MyPopup(
            id="prev_pop",
            title=dialog_title,
            content=content,
            pos_hint={0.5: 0.724},
            size_hint=(0.4, 0.34),
        )
        self.prev_dialog.bind(on_dismiss=self.prev_dialog_closed)
        c_padding = self.prev_dialog.width / 4
        CommonComicsCoverInnerGrid.padding = (c_padding, 0, 0, 0)
        comic_thumb.bind(on_release=self.prev_dialog.dismiss)
        self.prev_nav_comic_thumb = comic_thumb
        if index < len(comics_list):
            if index == 0:
                if self.use_sections and self.section != "First":
                    comic_thumb.action_do = "open_prev_section"
                    comic_thumb.bind(on_release=comic_thumb.do_action)
                else:
                    if len(comics_list) > 1:
                        comic_thumb.action_do = "load_prev_page_comic"
                        comic_thumb.bind(on_release=self.load_prev_page_comic)
                    else:
                        return
            else:
                if self.use_sections and self.section != "First":
                    comic_thumb.action_do = "open_prev_section"
                    comic_thumb.bind(on_release=comic_thumb.do_action)
                else:
                    if len(comics_list) > 1:
                        comic_thumb.action_do = "load_prev_page_comic"
                        comic_thumb.bind(on_release=self.load_prev_page_comic)
                    else:
                        comic_thumb.action_do = "open_collection"
                        comic_thumb.bind(on_release=comic_thumb.do_action)

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

    def load_random_comic(self):
        next_screen_name = self.app.manager.next()
        self.app.manager_screens.current = next_screen_name

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
def model_is_changed(self) -> None:
        """
        Called whenever any change has occurred in the data model.
        The view in this method tracks these changes and updates the UI
        according to these changes.
        """
