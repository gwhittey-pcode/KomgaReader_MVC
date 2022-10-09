import os

from kivy.lang import Builder
from kivy.properties import BooleanProperty, StringProperty, ListProperty,DictProperty, NumericProperty,ObjectProperty
from kivy.utils import get_hex_from_color
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout

from View.ReadingListScreen.components.rlimagelist import RLSmartTile
from kivymd.uix.button import MDIconButton
from kivy.clock import Clock
from functools import partial

with open(
    os.path.join(os.getcwd(), "View","ReadingListScreen","components", "reading_list_image.kv"), encoding="utf-8"
) as kv_file:
    Builder.load_string(kv_file.read())


class ReadingListImage(MDBoxLayout):
    def __init__(self, **kwargs):
        super(ReadingListImage, self).__init__(**kwargs)