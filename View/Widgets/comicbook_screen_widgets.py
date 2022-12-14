from kivy.uix.scatterlayout import ScatterLayout
from kivy.properties import (
    ObjectProperty,
    StringProperty,
    ListProperty,
    NumericProperty,
    DictProperty, BooleanProperty,
)
from kivy.uix.carousel import Carousel
from kivymd.app import MDApp

from Utility.myimage import Image, MyAsyncImage
from kivy.uix.button import Button, ButtonBehavior
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from Utility.komga_server_conn import ComicServerConn
from kivymd.uix.button import MDRaisedButton
from kivy.graphics.transformation import Matrix
from kivy.app import App
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.core.window import Window
from kivy.uix.scatter import Scatter
from kivy.vector import Vector
from math import radians

from kivymd.toast import toast


class MagnifyingGlassScatter(Scatter):
    id = StringProperty()

    def __init__(self, **kwargs):
        super(MagnifyingGlassScatter, self).__init__(**kwargs)
        self.mag_glass_x = int(
            App.get_running_app().config.get("Display", "mag_glass_size")
        )
        self.mag_glass_y = int(
            App.get_running_app().config.get("Display", "mag_glass_size")
        )
        self.page_widget = ""
        self.mag_img = ""

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            touch.grab(self)
            # do whatever else here
        return super(MagnifyingGlassScatter, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        if touch.grab_current is self:
            # get the middle of mag glass
            my_x = self.x + self.mag_glass_x / 2
            m_y = self.y + self.mag_glass_y / 2
            # self.mag_img.texture = self.page_widget.texture.get_region(my_x,
            #                                                            m_y,
            #                                                            my_x,
            #                                                            my_y)
            self.mag_img.texture = self.page_widget.texture.get_region(
                my_x, m_y, self.mag_glass_x, self.mag_glass_y
            )
            # now we only handle moves which we have grabbed
        return super(MagnifyingGlassScatter, self).on_touch_move(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
        return super(MagnifyingGlassScatter, self).on_touch_up(touch)
        # and finish up here


class ComicBookPageScatter(ScatterLayout):
    zoom_state = StringProperty()
    comic_page = NumericProperty()
    id = StringProperty()
    open_this_page = BooleanProperty(False)

    def __init__(self, **kwargs):
        super(ComicBookPageScatter, self).__init__(**kwargs)
        self.zoom_state = "normal"
        self.move_state = "open"

    def on_touch_down(self, touch):
        if touch.is_double_tap:
            self.do_zoom(touch)
        return super(ComicBookPageScatter, self).on_touch_down(touch)

    def on_transform_with_touch(self, touch):
        self.zoom_state = "zoomed"
        return super(ComicBookPageScatter, self).on_transform_with_touch(touch)

    def do_zoom(self, touch):
        if self.zoom_state == "zoomed":
            self.zoom_state = "normal"
            self.do_translation = False
            mat = self.transform_inv
            self.apply_transform(mat, anchor=(0, 0))
        elif self.zoom_state == "normal" and touch is not False:
            self.zoom_state = "zoomed"
            self.do_translation = True
            mat = Matrix().scale(2, 2, 2)
            self.apply_transform(mat, anchor=touch.pos)

    def open_mag_glass(self):
        Logger.debug("my id=%s" % str(self.id))

        mag_glass_setting_x = int(
            App.get_running_app().config.get("Display", "mag_glass_size")
        )
        mag_glass_setting_y = int(
            App.get_running_app().config.get("Display", "mag_glass_size")
        )

        comic_image_id = self.id.replace("comic_scatter", "pi_")
        try:
            for child in self.walk():
                if child.id == comic_image_id:
                    image_w = child
                    Logger.debug(
                        ">>>>>gc named %s this is the image" % comic_image_id
                    )
                elif child.id == "mag_glass":
                    mag_glass_w = child
        except Exception:
            Logger.critical("Some bad happened in _call_mag")
        else:
            if self.move_state == "open":
                self.move_state = "locked"
                self.do_scale = False
                self.do_translation = False
                Logger.debug(
                    "image_w.center = %d,%d"
                    % (image_w.center_x, image_w.center_y)
                )

                mag_glass = MagnifyingGlassScatter(
                    size=(mag_glass_setting_x, mag_glass_setting_y),
                    size_hint=(None, None),
                    do_rotation=False,
                    do_scale=False,
                    pos=(
                        (image_w.center_x - (mag_glass_setting_x / 2)),
                        (image_w.center_y - (mag_glass_setting_y / 2)),
                    ),
                    id="mag_glass",
                )
                mag_glass.page_widget = image_w
                mag_glass_image = Image(
                    size_hint=(None, None),
                    pos_hint={"x": 1, "y": 1},
                    id="mag_image",
                    keep_ratio=True,
                    allow_stretch=False,
                    size=mag_glass.size,
                )
                mag_glass.mag_img = mag_glass_image
                mag_glass_image.texture = image_w.texture.get_region(
                    mag_glass.x,
                    mag_glass.y,
                    mag_glass_setting_x,
                    mag_glass_setting_y,
                )
                mag_glass.add_widget(mag_glass_image)
                self.add_widget(mag_glass)
            else:
                self.move_state = "open"
                self.do_scale = True
                self.do_translation = True

                self.remove_widget(mag_glass_w)

    def check_trans(self, matrix):
        pos_matrix = Matrix().translate(self.pos[0], self.pos[1], 0)
        pos = matrix.multiply(pos_matrix).get()[12:14]
        if pos[0] > 0 or pos[1] > 0:
            return False
        elif (
                pos[0] + self.width * self.scale < Window.size[0]
                or pos[1] + self.height * self.scale < Window.size[1]
        ):
            return False
        return True

    def transform_with_touch(self, touch):
        # just do a simple one finger drag
        changed = False
        if len(self._touches) == self.translation_touches:
            # _last_touch_pos has last pos in correct parent space,
            # just like incoming touch
            dx = (
                         touch.x - self._last_touch_pos[touch][0]
                 ) * self.do_translation_x
            dy = (
                         touch.y - self._last_touch_pos[touch][1]
                 ) * self.do_translation_y
            dx = dx / self.translation_touches
            dy = dy / self.translation_touches
            m = Matrix().translate(dx, dy, 0)
            if self.check_trans(m):
                self.apply_transform(Matrix().translate(dx, dy, 0))
                changed = True
            else:
                pass

        if len(self._touches) == 1:
            return changed

        # we have more than one touch... list of last known pos
        points = [
            Vector(self._last_touch_pos[t])
            for t in self._touches
            if t is not touch
        ]
        # add current touch last
        points.append(Vector(touch.pos))

        # we only want to transform if the touch is part of the two touches
        # farthest apart! So first we find anchor, the point to transform
        # around as another touch farthest away from current touch's pos
        anchor = max(points[:-1], key=lambda p: p.distance(touch.pos))

        # now we find the touch farthest away from anchor, if its not the
        # same as touch. Touch is not one of the two touches used to transform
        farthest = max(points, key=anchor.distance)
        if farthest is not points[-1]:
            return changed

        # ok, so we have touch, and anchor, so we can actually compute the
        # transformation
        old_line = Vector(*touch.ppos) - anchor
        new_line = Vector(*touch.pos) - anchor
        if not old_line.length():  # div by zero
            return changed

        angle = radians(new_line.angle(old_line)) * self.do_rotation
        self.apply_transform(Matrix().rotate(angle, 0, 0, 1), anchor=anchor)

        if self.do_scale:
            scale = new_line.length() / old_line.length()
            new_scale = scale * self.scale
            if new_scale < self.scale_min:
                scale = self.scale_min / self.scale
            elif new_scale > self.scale_max:
                scale = self.scale_max / self.scale
            m = Matrix().scale(scale, scale, scale)
            if self.check_trans(m):
                self.apply_transform(
                    Matrix().scale(scale, scale, scale), anchor=anchor
                )
                changed = True
            else:
                pass
        return changed


class ComicBookPageImage(MyAsyncImage):
    """Fired once the image is downloaded and ready to use"""

    comic_slug = StringProperty()
    comic_page_num = NumericProperty()
    fetch_data = ObjectProperty()
    comic_page = NumericProperty()
    comic_page_type = StringProperty
    proxyImage = ObjectProperty()
    id = StringProperty()
    extra_headers = DictProperty()
    is_place_holder = StringProperty()
    def __init__(self, **kwargs):
        super(ComicBookPageImage, self).__init__(**kwargs)
        extra_headers = kwargs.get('extra_headers')

    def _new_image_downloaded(
            self, scatter, outer_grid, comic_obj, var_i, src_url, proxyImage, open_this_page=False
    ):
        """Fired once the image is downloaded and ready to use"""
        Logger.debug("_new_image_downloaded")
        open_this_page = open_this_page

        def _remove_widget():
            carousel.remove_widget(scatter)

        def _add_parts():
            strech_image = App.get_running_app().config.get(
                "Display", "stretch_image"
            )
            if strech_image == "1":
                s_allow_stretch = True
                s_keep_ratio = False
            else:
                s_allow_stretch = False
                s_keep_ratio = True
            part_1 = ComicBookPageImage(
                comic_slug=comic_obj.slug,
                id="pi_" + str(var_i) + "b",
                comic_page=var_i,
                allow_stretch=s_allow_stretch,
                keep_ratio=s_keep_ratio,
                extra_headers=self.extra_headers
            )
            part_2 = ComicBookPageImage(
                comic_slug=comic_obj.slug,
                id="pi_" + str(var_i) + "b",
                comic_page=var_i,
                allow_stretch=s_allow_stretch,
                keep_ratio=s_keep_ratio,
                extra_headers=self.extra_headers
            )
            scatter_1 = ComicBookPageScatter(
                id="comic_scatter" + str(var_i),
                comic_page=var_i,
                do_rotation=False,
                do_translation=False,
                scale_min=1,
                open_this_page=open_this_page

            )
            scatter_2 = ComicBookPageScatter(
                id="comic_scatter" + str(var_i) + "b",
                comic_page=var_i,
                do_rotation=False,
                do_translation=False,
                scale_min=1,
            )
            part_1.texture = proxyImage.image.texture.get_region(
                0, 0, c_width / 2, c_height
            )
            part_2.texture = proxyImage.image.texture.get_region(
                (c_width / 2 + 1), 0, c_width / 2, c_height
            )
            scatter_1.add_widget(part_1)
            scatter_2.add_widget(part_2)
            if last_page is True:
                carousel.add_widget(scatter_1)
                carousel.add_widget(scatter_2)
            else:
                carousel.add_widget(scatter_1, i)
                carousel.add_widget(scatter_2, i + 1)

        if proxyImage.image.texture:
            split_dbl_page = App.get_running_app().config.get(
                "Display", "dblpagesplit"
            )
            p_width = proxyImage.image.texture.width
            p_height = proxyImage.image.texture.height
            c_width = self.texture.width
            c_height = self.texture.height
            if p_width > p_height and split_dbl_page == "1":
                last_page = False
                app = App.get_running_app()
                carousel = (
                    App.get_running_app()
                    .manager_screens.get_screen("comic book screen")
                    .ids.comic_book_carousel
                )
                i = 0
                for slide in carousel.slides:
                    if slide.id == scatter.id:
                        if slide.comic_page == comic_obj.PageCount - 1:
                            last_page = True
                        _remove_widget()
                        _add_parts()
                    i += 1
                s_screen = MDApp.get_running_app().manager_screens.current_screen
                Clock.schedule_once(s_screen.load_user_current_page)
            else:
                if p_width > p_height:
                    scatter.size_hint = (2, 1)
            if comic_obj.PageCount - 1 == var_i:
                app = App.get_running_app()
                s_screen = app.manager_screens.get_screen("comic book screen")
                Clock.schedule_once(s_screen.load_user_current_page)


class ComicCarousel(Carousel):
    id = StringProperty()

    def on_touch_move(self, touch):  # noqa
        if not self.touch_mode_change:
            if self.ignore_perpendicular_swipes and self.direction in (
                    "top",
                    "bottom",
            ):
                if abs(touch.oy - touch.y) < self.scroll_distance:
                    if abs(touch.ox - touch.x) > self.scroll_distance:
                        self._change_touch_mode()
                        self.touch_mode_change = True
            elif self.ignore_perpendicular_swipes and self.direction in (
                    "right",
                    "left",
            ):
                if abs(touch.ox - touch.x) < self.scroll_distance:
                    if abs(touch.oy - touch.y) > self.scroll_distance:
                        self._change_touch_mode()
                        self.touch_mode_change = True

        if self._get_uid("cavoid") in touch.ud:
            return
        if self._touch is not touch:
            super(ComicCarousel, self).on_touch_move(touch)
            return self._get_uid() in touch.ud
        if touch.grab_current is not self:
            return True
        ud = touch.ud[self._get_uid()]
        direction = self.direction
        if ud["mode"] == "unknown":
            if direction[0] in ("r", "l"):
                distance = abs(touch.ox - touch.x)
            else:
                distance = abs(touch.oy - touch.y)
            if distance > self.scroll_distance:
                if self.index is not None:
                    current_slide = self.current_slide
                    if (
                            current_slide == self.slides[-1]
                            and self.next_slide is None
                    ):
                        app = App.get_running_app()
                        comic_book_screen = app.manager_screens.current_screen
                        comic_book_screen.open_next_dialog()
                    # elif current_slide == self.slides[0] and\
                    #         self.previous_slide is None:
                    #     app = App.get_running_app()
                    #     comic_book_screen = app.manager_screens.current_screen
                    #     comic_book_screen.open_prev_dialog()
                ev = self._change_touch_mode_ev
                if ev is not None:
                    ev.cancel()
                ud["mode"] = "scroll"
        else:
            if direction[0] in ("r", "l"):
                self._offset += touch.dx
            if direction[0] in ("t", "b"):
                self._offset += touch.dy
        return super(ComicCarousel, self).on_touch_move(touch)


# Button for screen tapping control
class ComicBookPageControlButton(Button):
    location = StringProperty()
    id = StringProperty()

    def enable_me(self, instance):
        self.disabled = False

    def on_touch_down(self, touch):
        if touch.is_double_tap:
            if self.collide_point(*touch.pos):
                app = App.get_running_app()
                comic_book_screen = app.manager_screens.current_screen
                comic_book_carousel = comic_book_screen.ids.comic_book_carousel
                current_slide = comic_book_carousel.current_slide
                return current_slide.on_touch_down(touch)
        if self.disabled:
            if self.collide_point(*touch.pos):
                app = App.get_running_app()
                comic_book_screen = app.manager_screens.current_screen
                comic_book_carousel = comic_book_screen.ids.comic_book_carousel
                current_slide = comic_book_carousel.current_slide
                return current_slide.on_touch_down(touch)

        return super(ComicBookPageControlButton, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        if touch.is_double_tap:
            if self.collide_point(*touch.pos):
                app = App.get_running_app()
                comic_book_screen = app.manager_screens.current_screen
                comic_book_carousel = comic_book_screen.ids.comic_book_carousel
                current_slide = comic_book_carousel.current_slide
                return current_slide.on_touch_up(touch)
        else:

            return super(ComicBookPageControlButton, self).on_touch_up(touch)

    def click(btn):
        btn.disabled = True
        Clock.schedule_once(btn.enable_me, 0.5)
        comic_book_screen = App.get_running_app().manager_screens.current_screen
        app = App.get_running_app()
        if btn.location == "":
            return
        tap_option = App.get_running_app().config.get(
            "Screen Tap Control", str(btn.location)
        )
        if tap_option == "Next Page":
            comic_book_screen.load_next_slide()
        elif tap_option == "Prev Page":
            comic_book_screen.load_prev_slide()
        elif tap_option == "Open Page Nav":
            comic_book_screen.page_nav_popup_open()
        elif tap_option == "Open Collection Browser":
            if len(comic_book_screen.comiclist_obj.comics) > 1:
                comic_book_screen.comicscreen_open_collection_popup()
            else:
                return
        elif tap_option == "Prev Comic":
            comic_book_screen.load_prev_comic()
        elif tap_option == "Next Comic":
            comic_book_screen.load_next_comic()
        elif tap_option == "Return to Comic List Screen":
            app.manager_screens.current = "server_readinglists_screen"
        elif tap_option == "Go to List of Reading Lists":
            app.manager_screens.current = "base"
        elif tap_option == "Open NavBar":
            comic_book_screen.toggle_option_bar()
        else:
            return


# <<<<Following are class for popup at bottom page for pressing and going to
# page x


class ThumbPopPagePopup(Popup):
    id = StringProperty()


class ThumbPopPageScroll(ScrollView):
    id = StringProperty()


class ThumbPopPageOutterGrid(GridLayout):
    id = StringProperty()


class ThumbPopPageInnerGrid(GridLayout):
    id = StringProperty()


class ThumbPopPagebntlbl(MDRaisedButton):
    comic_slug = StringProperty()
    fetch_data = ObjectProperty()
    comic_page = NumericProperty()
    id = StringProperty()
    def __init__(self, **kwargs):
        super(ThumbPopPagebntlbl, self).__init__(**kwargs)

    def click(self, instance):
        app = App.get_running_app()
        screen = app.manager_screens.current_screen
        stream_comic_pages = screen.stream_comic_pages
        page_nav_popup = app.manager_screens.current_screen.page_nav_popup
        page_nav_popup.dismiss()
        carousel = app.manager_screens.current_screen.ids.comic_book_carousel
        if screen.stream_comic_pages == '1':
            # toast("Not implemented")
            i = self.comic_page
            comic_car = screen.ids.comic_book_carousel
            s_url_part = f"/api/v1/books/{screen.comic_obj.Id}/pages/{i}?zero_based=true"
            src_img = f"{screen.app.base_url}{s_url_part}"
            for item in screen.comic_page_ids:
                if item["pid"] == i:
                    if item['comic_page_obj'].is_place_holder != "no":
                        item['comic_page_obj'].source = src_img
                        item['comic_page_obj'].is_place_holder = "no"
                    screen.current_comic_page = i
                    for slide in carousel.slides:
                        if slide.comic_page == self.comic_page:
                            use_slide = slide
                            carousel.load_slide(use_slide)
                            return
        else:
            for slide in carousel.slides:
                if slide.comic_page == self.comic_page:
                    use_slide = slide
                    carousel.load_slide(use_slide)
                    return


class ThumbPopPageSmallButton(Button):
    pass


# class ThumbPopPageImage(ButtonBehavior, Image):
#     comic_slug = StringProperty()
#     fetch_data = ObjectProperty()
#     comic_page = NumericProperty()

#     def __init__(self, **kwargs):
#         super(ThumbPopPageImage, self).__init__(**kwargs)
#         base_url = App.get_running_app().config.get('General', 'base_url'')

#     def got_json(self, req, result):
#         img = convert_to_image(result["page"])
#         self.texture = img.texture

#     def click(self, instance):
#         app = App.get_running_app()
#         # app.root.current = 'comic_book_screen'
#         page_nav_popup = app.root.ids.comic_book_screen.page_nav_popup
#         page_nav_popup.dismiss()
#         app = App.get_running_app()
#         carousel = app.manager_screens.current_screen.ids.comic_book_carousel
#         for slide in carousel.slides:
#             if slide.id == self.id:
#                 use_slide = slide
#         carousel.load_slide(use_slide)


class ComicBookPageThumb(ButtonBehavior, MyAsyncImage):
    """Fired once the image is downloaded and ready to use"""

    comic_slug = StringProperty()
    fetch_data = ObjectProperty()
    comic_page = NumericProperty()
    extra_headers = DictProperty()
    id = StringProperty()
    extra_headers = DictProperty()

    def __init__(self, **kwargs):
        super(ComicBookPageThumb, self).__init__(**kwargs)
        extra_headers = kwargs.get('extra_headers')

    def click(self, instance):
        app = App.get_running_app()
        screen = app.manager_screens.current_screen
        stream_comic_pages = screen.stream_comic_pages
        page_nav_popup = app.manager_screens.current_screen.page_nav_popup
        page_nav_popup.dismiss()
        carousel = app.manager_screens.current_screen.ids.comic_book_carousel
        if screen.stream_comic_pages == '1':
            # toast("Not implemented")
            i = self.comic_page
            comic_car = screen.ids.comic_book_carousel
            s_url_part = f"/api/v1/books/{screen.comic_obj.Id}/pages/{i}?zero_based=true"
            src_img = f"{screen.app.base_url}{s_url_part}"
            for item in screen.comic_page_ids:
                if item["pid"] == i:
                    if item['comic_page_obj'].is_place_holder != "no":
                        item['comic_page_obj'].source = src_img
                        item['comic_page_obj'].is_place_holder = "no"
                    screen.current_comic_page = i
                    for slide in carousel.slides:
                        if slide.comic_page == self.comic_page:
                            use_slide = slide
                            carousel.load_slide(use_slide)
                            return
        else:
            for slide in carousel.slides:
                if slide.comic_page == self.comic_page:
                    use_slide = slide
                    carousel.load_slide(use_slide)
                    return


class CommonComicsScroll(ScrollView):
    id = StringProperty()


class CommonComicsOuterGrid(GridLayout):
    id = StringProperty()


class CommonComicsCoverLabel(Label):
    id = StringProperty()


class CommonComicsCoverInnerGrid(GridLayout):
    id = StringProperty()


class CommonComicsCoverImage(ButtonBehavior, MyAsyncImage):
    comic_obj = ObjectProperty()
    comiclist_obj = ObjectProperty()
    paginator_obj = ObjectProperty()
    new_page_num = NumericProperty()
    clock_set = StringProperty()
    last_load = NumericProperty()
    last_section = NumericProperty()
    action_do = StringProperty()
    mode = StringProperty()
    id = StringProperty()
    extra_headers = DictProperty()
    current_page = NumericProperty()
    first = BooleanProperty(False)
    last = BooleanProperty(False)
    totalPages = NumericProperty()
    item_per_page = NumericProperty
    comic_list_type = StringProperty()

    def __init__(self, **kwargs):
        super(CommonComicsCoverImage, self).__init__(**kwargs)
        extra_headers = kwargs.get('extra_headers')

    def enable_me(self, instance):
        self.disabled = False

    # def open_comic(self,*args):
    #     self.disabled = True
    #     app = App.get_running_app()
    #     app.root.current = 'comic_book_screen'
    #     new_reading_list = ComicReadingList()
    #     new_reading_list.add_comic(self.comic)
    #     comic_screen = app.manager_screens.get_screen('comic_book_screen')
    #     comic_screen.load_comic_book(self.comic,new_reading_list)
    #     Clock.schedule_once(self.enable_me, .5)
    def do_action(self, *args):
        if self.action_do == "open_collection":
            self.open_collection(*args)
        elif self.action_do == "open_next_section":
            self.open_next_section(*args)
        elif self.action_do == "open_prev_section":
            self.open_prev_section(*args)

    def open_collection(self, *args):
        self.disabled = True
        app = App.get_running_app()
        if self.mode == "FileOpen":
            view_mode = "FileOpen"
        elif self.mode == "Sync":
            view_mode = "Sync"
        else:
            view_mode = "Server"

        screen = app.manager_screens.get_screen("comic book screen")
        screen.setup_screen(
            comiclist_obj=self.comiclist_obj,
            comic_obj=self.comic_obj,
            paginator_obj=self.paginator_obj,
            pag_pagenum=self.new_page_num,
            view_mode=view_mode,
            current_page=self.current_page,
            first=self.first,
            last=self.last,
            totalPages=self.totalPages,
            item_per_page=self.item_per_page,
            comic_list_type=self.comic_list_type,
        )
        app.manager_screens.current = "comic book screen"

        Clock.schedule_once(self.enable_me, 0.5)

    def open_next_section(self, *args):
        self.disabled = True
        app = App.get_running_app()

        if self.mode == "FileOpen":
            view_mode = "FileOpen"
        elif self.mode == "Sync":
            view_mode = "Sync"
        else:
            view_mode = "Server"
        screen = app.manager_screens.get_screen("comic book screen")
        screen.setup_screen(
            comiclist_obj=self.comiclist_obj,
            comic_obj=self.comic_obj,
            paginator_obj=self.paginator_obj,
            pag_pagenum=self.new_page_num,
            view_mode=view_mode,
            current_page=self.current_page,
            first=self.first,
            last=self.last,
            totalPages=self.totalPages,
            item_per_page=self.item_per_page,
            comic_list_type=self.comic_list_type,
        )
        app.manager_screens.current = "comic book screen"

        Clock.schedule_once(self.enable_me, 0.5)

    def open_prev_section(self, *args):
        app = App.get_running_app()
        if self.mode == "FileOpen":
            view_mode = "FileOpen"
        elif self.mode == "Sync":
            view_mode = "Sync"
        else:
            view_mode = "Server"
        screen = app.manager_screens.get_screen("comic book screen")
        screen.setup_screen(
            comiclist_obj=self.comiclist_obj,
            comic_obj=self.comic_obj,
            paginator_obj=self.paginator_obj,
            pag_pagenum=self.new_page_num,
            view_mode=view_mode,
            current_page=self.current_page,
            first=self.first,
            last=self.last,
            totalPages=self.totalPages,
            item_per_page=self.item_per_page,
            comic_list_type=self.comic_list_type,
        )
        app.manager_screens.current = "comic book screen"

        Clock.schedule_once(self.enable_me, 0.5)
