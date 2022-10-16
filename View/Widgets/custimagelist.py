from kivy.lang import Builder
from kivy.properties import (
    StringProperty,
    BooleanProperty,
    ObjectProperty,
    NumericProperty,
    ListProperty,
    OptionProperty,
    DictProperty
)
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout

from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.behaviors import RectangularRippleBehavior
from kivymd.uix.button import MDIconButton
from kivymd.theming import ThemableBehavior
from kivymd.icon_definitions import md_icons
from Utility.myimage import MyAsyncImage

Builder.load_string(
    """
#:import md_icons kivymd.icon_definitions.md_icons
#:import MyAsyncImage Utility.myimage 


<MySmartTile>
    _img_widget: img
    _img_overlay: img_overlay
    _box_overlay: box

    MyAsyncImage:
        id: img
        allow_stretch: root.allow_stretch
        anim_delay: root.anim_delay
        anim_loop: root.anim_loop
        color: root.img_color
        keep_ratio: root.keep_ratio
        mipmap: root.mipmap
        source: root.source
        extra_headers: root.extra_headers
        size_hint_y: 1 if root.overlap else None
        x: root.x
        y: root.y if root.overlap or root.box_position == 'header' else box.top

    BoxLayout:
        id: img_overlay
        size_hint: img.size_hint
        size: img.size
        pos: img.pos

    BoxLayout:
        canvas:
            Color:
                rgba: root.box_color
            Rectangle:
                pos: self.pos
                size: self.size
        id: box
        size_hint_y: None
        height: dp(68) if root.lines == 2 else dp(48)
        x: root.x
        y: root.y if root.box_position == 'footer'\
            else root.y + root.height - self.height


<ComicTileLabel>
    _img_widget: img
    _img_overlay: img_overlay
    _box_overlay: box
    _box_label: boxlabel
    _box_header: box_header
    _box_icon: boxicon
    MyAsyncImage:
        id: img
        allow_stretch: root.allow_stretch
        anim_delay: root.anim_delay
        anim_loop: root.anim_loop
        keep_ratio: root.keep_ratio
        mipmap: root.mipmap
        source: root.source
        extra_headers: root.extra_headers
        size_hint_y: 1 if root.overlap else None
        x: root.x
        y: root.y if root.overlap or root.box_position == 'header' else box.top

    BoxLayout:
        id: img_overlay
        size_hint: img.size_hint
        size: img.size
        pos: img.pos

    BoxLayout:
        canvas:
            Color:
                rgba: root.box_color 
            Rectangle:
                pos: self.pos
                size: self.size

        id: box#header
        size_hint_y: None
        padding: dp(5), 0, 0, 0
        height: self.minimum_height #dp(68) if root.lines == 2 else dp(48)
        x: root.x
        y: root.y + root.height - self.height

        MDLabel:
            id: boxlabel
            font_style: root.font_style
            #halign: "center"
            size_hint_y: None
            height: self.texture_size[1]
            text: root.text
            color: root.tile_text_color
            markup: True

    BoxLayout:
        canvas:
            Color:
                rgba: root.box_header_color
            Rectangle:
                pos: self.pos
                size: self.size
    
        id: box_header
        size_hint_y: None
        padding: dp(5), 0, 0, 0
        height: self.minimum_height #dp(68) if root.lines == 2 else dp(48)
        x: root.x
        y: root.y
        opacity:1
    
        MDLabel:
            id: boxicon
            #icon_name: 'read'
            #halign: "center"
            size_hint_y: None
            height: self.texture_size[1]
            text: "Read"
            theme_text_color: 'Custom'
            text_color: 1,1,1,1
            opacity: 1 if root.is_read else 0
        MDIcon:
            id: boxicon
            icon_name: 'file-check'
            #halign: "center"
            size_hint_y: None
            height: self.texture_size[1]
            text: md_icons.get(self.icon_name)
            theme_text_color: 'Custom'
            text_color: app.theme_cls.primary_color
            opacity: 1 if root.has_localfile else 0
            font_size: dp(25)
        MDLabel:
            id: boxlabel
            icon_name: 'cloud-sync'
            #halign: "center"
            size_hint_y: None
            height: self.texture_size[1]
            text: str(root.page_count_text)
            theme_text_color: 'Custom'
            text_color: root.page_count_text_color

<RLTileLabel>
    _img_widget: img
    _img_overlay: img_overlay
    _box_overlay: box
    _box_label: boxlabel
    _box_header: box_header
    MyAsyncImage:
        id: img
        allow_stretch: root.allow_stretch
        anim_delay: root.anim_delay
        anim_loop: root.anim_loop
        keep_ratio: root.keep_ratio
        mipmap: root.mipmap
        source: root.source
        extra_headers: root.extra_headers
        size_hint_y: 1 if root.overlap else None
        x: root.x
        y: root.y if root.overlap or root.box_position == 'header' else box.top

    BoxLayout:
        id: img_overlay
        size_hint: img.size_hint
        size: img.size
        pos: img.pos

    BoxLayout:
        canvas:
            Color:
                rgba: root.box_color
            Rectangle:
                pos: self.pos
                size: self.size

        id: box#header
        size_hint_y: None
        padding: dp(5), 0, 0, 0
        height: self.minimum_height #dp(68) if root.lines == 2 else dp(48)
        x: root.x
        y: root.y + root.height - self.height

        MDLabel:
            id: boxlabel
            font_style: root.font_style
            #halign: "center"
            size_hint_y: None
            height: self.texture_size[1]
            text: root.text
            color: root.tile_text_color
            markup: True

    BoxLayout:
        canvas:
            Color:
                rgba: 0, 0, 0, 0.5
            Rectangle:
                pos: self.pos
                size: self.size

        id: box_header
        size_hint_y: None
        padding: dp(5), 0, 0, 0
        height: self.minimum_height #dp(68) if root.lines == 2 else dp(48)
        x: root.x
        y: root.y
        opacity:1
        MDLabel:
            id: boxlabel
            icon_name: 'cloud-sync'
            #halign: "center"
            size_hint_y: None
            height: self.texture_size[1]
            text: str(root.page_count_text)
            #root.page_count_text
            theme_text_color: 'Custom'
            text_color: app.theme_cls.primary_color



"""
)


class MySmartTile(
    ThemableBehavior, RectangularRippleBehavior, ButtonBehavior, FloatLayout,
):
    """A tile for more complex needs.

    Includes an image, a container to place overlays and a box that can act
    as a header or a footer, as described in the Material Design specs.
    """

    box_color = ListProperty([0, 0, 0, 0.5])
    """Sets the color and opacity for the information box."""

    box_position = OptionProperty("footer", options=["footer", "header"])
    """Determines wether the information box acts as a header or footer to the
    image.
    """

    lines = OptionProperty(1, options=[1, 2])
    """Number of lines in the header/footer.

    As per Material Design specs, only 1 and 2 are valid values.
    """

    overlap = BooleanProperty(True)
    """Determines if the header/footer overlaps on top of the image or not"""

    # Img properties
    allow_stretch = BooleanProperty(True)
    anim_delay = NumericProperty(0.25)
    anim_loop = NumericProperty(0)
    img_color = ListProperty([1, 1, 1, 1])
    keep_ratio = BooleanProperty(False)
    mipmap = BooleanProperty(False)
    source = StringProperty()
    extra_headers = DictProperty()

    _img_widget = ObjectProperty()
    _img_overlay = ObjectProperty()
    _box_overlay = ObjectProperty()
    _box_label = ObjectProperty()

    def reload(self):
        self._img_widget.reload()

    def add_widget(self, widget, index=0, canvas=None):
        if issubclass(widget.__class__, IOverlay):
            self._img_overlay.add_widget(widget, index, canvas)
        elif issubclass(widget.__class__, IBoxOverlay):
            self._box_overlay.add_widget(widget, index, canvas)
        else:
            super().add_widget(widget, index, canvas)


class ComicTileLabel(MySmartTile):
    _box_label = ObjectProperty()
    _box_header = ObjectProperty()
    _box_icon = ObjectProperty()
    # MDLabel properties
    font_style = StringProperty("Caption")
    theme_text_color = StringProperty("Custom")
    tile_text_color = ListProperty([1, 1, 1, 1])
    text = StringProperty("")
    text_header = StringProperty("Sync")
    icon_name = StringProperty()
    is_read = BooleanProperty(False)
    has_localfile = BooleanProperty(False)
    box_header_opaticty = StringProperty(1)
    page_count_text = StringProperty()
    extra_headers = DictProperty()
    page_count_text_color = ListProperty([1, 1, 1, 1])
    box_header_color = ListProperty([0,0,0,.25])
    def __init__(self, **kwargs):
        super(ComicTileLabel, self).__init__(**kwargs)
        extra_headers = kwargs.get('extra_headers')

    """Determines the text for the box footer/header"""


class RLTileLabel(MySmartTile):
    _box_label = ObjectProperty()
    _box_header = ObjectProperty()
    _box_icon = ObjectProperty()
    # MDLabel properties
    font_style = StringProperty("Caption")
    theme_text_color = StringProperty("Custom")
    tile_text_color = ListProperty([1, 1, 1, 1])
    text = StringProperty("")
    text_header = StringProperty("Sync")
    icon_name = StringProperty()
    is_read = BooleanProperty(False)
    has_localfile = BooleanProperty(False)
    box_header_opaticty = StringProperty(1)
    page_count_text = StringProperty()
    extra_headers = DictProperty()

    def __init__(self, **kwargs):
        super(RLTileLabel, self).__init__(**kwargs)
        extra_headers = kwargs.get('extra_headers')


class SyncIcon(MDIconButton):
    def on_touch_down(self, touch):
        return True


class IBoxOverlay:
    """An interface to specify widgets that belong to to the image overlay
    in the :class:`SmartTile` widget when added as a child.
    """

    pass


class IOverlay:
    """An interface to specify widgets that belong to to the image overlay
    in the :class:`SmartTile` widget when added as a child.
    """

    pass