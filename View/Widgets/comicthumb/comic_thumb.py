from kivy.properties import StringProperty, NumericProperty, DictProperty
from kivymd.uix.behaviors import CommonElevationBehavior, TouchBehavior, HoverBehavior
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFillRoundFlatIconButton
from kivy.uix.modalview import ModalView

from ..myimagelist.myimagelist import MyMDSmartTile


class ComicThumbOverlay(MDFillRoundFlatIconButton):
    pass


class ComicThumb(MDBoxLayout, TouchBehavior):
    source = StringProperty()
    str_caption = StringProperty()
    read_progress = NumericProperty()
    percent_read = NumericProperty()
    extra_headers = DictProperty()
    tooltip_text = StringProperty()

    def __init__(self, comic_obj=None, **kwargs):
        super(ComicThumb, self).__init__(**kwargs)
        self.source = ""
        UserLastPageRead = 40
        PageCount = 48

        self.percent_read = round(
            UserLastPageRead
            / PageCount
            * 100
        )

