import os

from kivy.lang import Builder
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.app import MDApp
from kivy.factory import Factory
register = Factory.register
register("MyToolBar", module="View.Widgets.my_tool_bar")

class MyToolBar(MDTopAppBar):
    pass