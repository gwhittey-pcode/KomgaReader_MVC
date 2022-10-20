from typing import Union

from kivy.clock import Clock
from kivy.metrics import dp, sp
from kivy.properties import NumericProperty, StringProperty
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton, BaseButton
from kivymd.uix.button.button import ButtonElevationBehaviour, OldButtonIconMixin, ButtonContentsIcon

__all__ = ('MyMDRaisedButton', 'MyMDIconRaisedButton')

from kivymd.uix.label import MDLabel


class MyMDRaisedButton(MDRaisedButton):
    width = NumericProperty(500)  # Same as in Widget class
    height = NumericProperty(500)  # Same as in Widget class

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.set_width)

    def set_width(self, i):
        self.width = dp(40) + (
                self.ids.lbl_txt.texture_size[0] - self.ids.lbl_txt.texture_size[0]
        )


class MyMDIconRaisedButton(BaseButton, ButtonElevationBehaviour, OldButtonIconMixin, ButtonContentsIcon):
    """
    A flat button with (by default) a primary color fill and matching
    color text.
    """

    # FIXME: Move the underlying attributes to the :class:`~BaseButton` class.
    #  This applies to all classes of buttons that have similar attributes.
    _default_md_bg_color = None
    _default_md_bg_color_disabled = None
    _default_theme_text_color = "Custom"
    _default_text_color = "PrimaryHue"
    icon = StringProperty("checkbox-blank-circle")
    """
    Button icon.
    :attr:`icon` is a :class:`~kivy.properties.StringProperty`
    and defaults to `'checkbox-blank-circle'`.
    """

    _min_width = NumericProperty(0)
    _default_icon_pad = max(dp(48) - sp(24), 0)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rounded_button = False
        # FIXME: GraphicException: Invalid width value, must be > 0
        self.line_width = 0.001
        Clock.schedule_once(self.set_size)
        self.shadow_softness = 8
        self.shadow_offset = (0, 2)
        self.shadow_radius = self._radius * 2

    def set_size(self, interval: Union[int, float]) -> None:
        """
        Sets the icon width/height based on the current `icon_size`
        attribute, or the default value if it is zero. The icon size
        is set to `(48, 48)` for an icon with the default font_size 24sp.
        """
        diameter = self._default_icon_pad + (self.icon_size or sp(24))
        self.width = diameter
        self.height = diameter


def build_pageination_nav():

    screen = MDApp.get_running_app().manager_screens.current_screen
    grid = screen.ids.page_num_grid
    grid.clear_widgets()
    c = MyMDRaisedButton(opacity=0)
    c.width = dp(500) + (c.ids.lbl_txt.texture_size[0] - c.ids.lbl_txt.texture_size[0])
    screen.ids.page_num_grid.add_widget(c)
    grid.bind(minimum_width=grid.setter("width"))
    ltbutton = MyMDIconRaisedButton(
        icon="less-than",
        icon_color=(1, 1, 1, 1),
        size_hint=(None, None),
        icon_size="13dp",
        width=dp(20),
        height=dp(20),
        text_color=(0, 0, 0, 1)
    )
    if not screen.first:
        ltbutton.bind(on_press=screen.ltgtbutton_press)
    screen.ids.page_num_grid.add_widget(ltbutton)
    if screen.totalPages <= 7:
        for num in range(1, screen.totalPages + 1):
            c = MyMDRaisedButton(text=str(num),
                                 size_hint=(None, None),
                                 height=dp(40),
                                 text_color=(0, 0, 0, 1)
                                 )
            c.width = dp(40) + (c.ids.lbl_txt.texture_size[0] - c.ids.lbl_txt.texture_size[0])
            c.bind(on_press=screen.pag_num_press)
            if num == screen.current_page + 1:
                c.md_bg_color = (1, 1, 1, 1)
            grid.add_widget(c)
    elif screen.current_page + 1 in range(1, 13) and screen.current_page + 1 != screen.totalPages:
        print(
            "###############if self.current_page + 1 in range(1, 13) and self.current_page + 1 != self.totalPages:#################")

        for num in range(screen.current_page + 1, screen.current_page + 7):
            c = MyMDRaisedButton(text=str(num),
                                 size_hint=(None, None),
                                 height=dp(40),
                                 text_color=(0, 0, 0, 1)
                                 )
            c.width = dp(40) + (c.ids.lbl_txt.texture_size[0] - c.ids.lbl_txt.texture_size[0])
            c.bind(on_press=screen.pag_num_press)
            if num == screen.current_page + 1:
                c.md_bg_color = (1, 1, 1, 1)
            grid.add_widget(c)
        screen.ids.page_num_grid.add_widget(
            MDLabel(
                text="...",
                size_hint=(None, None),
                width=dp(20),
                height=dp(20),
            ))
        for num in range(screen.totalPages - 4, screen.totalPages + 1):
            c = MyMDRaisedButton(text=str(num),
                                 size_hint=(None, None),
                                 height=dp(40),

                                 text_color=(0, 0, 0, 1)
                                 )
            c.width = dp(40) + (c.ids.lbl_txt.texture_size[0] - c.ids.lbl_txt.texture_size[0])
            c.bind(on_press=screen.pag_num_press)
            if num == screen.current_page + 1:
                c.md_bg_color = (1, 1, 1, 1)
            grid.add_widget(c)


    elif screen.totalPages - screen.current_page + 1 >= 7 and screen.current_page + 1 not in range(1, 13) and \
            screen.current_page + 1 != screen.totalPages:
        print("#######elif self.totalPages-self.current_page+1 >= 7 and self.current_page+1 not in range(1, 13) and \
                    self.current_page + 1 != self.totalPages:######")
        c = MyMDRaisedButton(text=str("1"),
                             size_hint=(None, None),
                             height=dp(40),
                             text_color=(0, 0, 0, 1)
                             )
        c.width = dp(40) + (c.ids.lbl_txt.texture_size[0] - c.ids.lbl_txt.texture_size[0])
        c.bind(on_press=screen.pag_num_press)
        grid.add_widget(c)
        screen.ids.page_num_grid.add_widget(
            MDLabel(
                text="...",
                size_hint=(None, None),
                width=dp(20),
                height=dp(20),
                text_color=(0, 0, 0, 1)
            ))
        for num in range(screen.current_page + 1 - 6, screen.current_page + 1, ):
            c = MyMDRaisedButton(text=str(num),
                                 size_hint=(None, None),
                                 height=dp(40),

                                 text_color=(0, 0, 0, 1)
                                 )
            c.width = dp(40) + (c.ids.lbl_txt.texture_size[0] - c.ids.lbl_txt.texture_size[0])
            c.bind(on_press=screen.pag_num_press)
            if num == screen.current_page + 1:
                print("#$##$##$#")
                c.md_bg_color = (1, 1, 1, 1)
            grid.add_widget(c)
        for num in range(screen.current_page + 1, screen.current_page + 7, ):
            c = MyMDRaisedButton(text=str(num),
                                 size_hint=(None, None),
                                 height=dp(40),

                                 text_color=(0, 0, 0, 1)
                                 )
            c.width = dp(40) + (c.ids.lbl_txt.texture_size[0] - c.ids.lbl_txt.texture_size[0])
            c.bind(on_press=screen.pag_num_press)
            if num == screen.current_page + 1:
                c.md_bg_color = (1, 1, 1, 1)
            grid.add_widget(c)
        screen.ids.page_num_grid.add_widget(
            MDLabel(
                text="...",
                size_hint=(None, None),
                width=dp(20),
                height=dp(20),
                text_color=(0, 0, 0, 1)
            ))
        c = MyMDRaisedButton(text=str(screen.totalPages),
                             size_hint=(None, None),
                             height=dp(40),
                             text_color=(0, 0, 0, 1)
                             )
        c.width = dp(40) + (c.ids.lbl_txt.texture_size[0] - c.ids.lbl_txt.texture_size[0])
        c.bind(on_press=screen.pag_num_press)
        grid.add_widget(c)
    else:
        for num in range(1, 8):
            c = MyMDRaisedButton(text=str(num),
                                 size_hint=(None, None),
                                 height=dp(40),

                                 text_color=(0, 0, 0, 1)
                                 )
            c.width = dp(40) + (c.ids.lbl_txt.texture_size[0] - c.ids.lbl_txt.texture_size[0])
            c.bind(on_press=screen.pag_num_press)
            if num == screen.current_page + 1:
                c.md_bg_color = (1, 1, 1, 1)
            grid.add_widget(c)
        screen.ids.page_num_grid.add_widget(
            MDLabel(
                text="...",
                size_hint=(None, None),
                width=dp(20),
                height=dp(20),
            ))

        for num in range(screen.totalPages - 6, screen.totalPages + 1):
            c = MyMDRaisedButton(text=str(num),
                                 size_hint=(None, None),
                                 height=dp(40),

                                 text_color=(0, 0, 0, 1)
                                 )
            c.width = dp(40) + (c.ids.lbl_txt.texture_size[0] - c.ids.lbl_txt.texture_size[0])
            c.bind(on_press=screen.pag_num_press)
            if num == screen.current_page + 1:
                c.md_bg_color = (1, 1, 1, 1)
            grid.add_widget(c)
    gtbutton = MyMDIconRaisedButton(
        icon="greater-than",
        icon_color=(1, 1, 1, 1),
        size_hint=(None, None),
        icon_size="13dp",
        width=dp(20),
        height=dp(20),
    )

    if not screen.last:
        gtbutton.bind(on_press=screen.ltgtbutton_press)
    screen.ids.page_num_grid.add_widget(gtbutton)

    # alphabet = ["All", "#"];
    # for i in range(ord('A'), ord('Z') + 1):
    #     alphabet.append(chr(i))
    # print(alphabet)