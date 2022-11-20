from kivymd.uix.list import BaseListItem, IRightBodyTouch, \
    OneLineRightIconListItem, TwoLineRightIconListItem
from kivymd.uix.selectioncontrol import MDSwitch


class BaseListItemWithSwitch(BaseListItem):
    """
    Base Class for on and two line items settings type
    """


class RightSwitchContainer(IRightBodyTouch, MDSwitch):
    """
    container used to place switch onm right side
    """


class OneLineListItemWithSwitch(OneLineRightIconListItem, BaseListItemWithSwitch):
    pass


class TwoLineListItemWithSwitch(TwoLineRightIconListItem, BaseListItemWithSwitch):
    pass
