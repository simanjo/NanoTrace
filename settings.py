from typing import Union

import dearpygui.dearpygui as dpg

from context import Context

DpgItem = Union[int, str]


def add_settings(tab_tag: DpgItem, context: Context):
    with dpg.tab(label="Settings", parent=tab_tag):
        dpg.add_text("General Settings:")
