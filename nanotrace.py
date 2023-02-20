from typing import Union

import dearpygui.dearpygui as dpg

from context import Context
from themes import custom_theme
from command_central import add_command_central
from settings import add_settings, add_changed_settings_handler

DpgItem = Union[int, str]


def _setup_app(window_tag: DpgItem, tab_tag: DpgItem, context: Context):
    _add_main_window(window_tag, tab_tag)
    cmd_tab = add_command_central(tab_tag, context)
    add_settings(tab_tag, context)
    add_changed_settings_handler(cmd_tab, context)


def _start_app(window_tag: DpgItem):
    dpg.bind_theme(custom_theme())

    dpg.create_viewport(title='NanoTrace', width=850, height=650)
    dpg.setup_dearpygui()

    dpg.show_viewport()
    dpg.set_primary_window(window_tag, True)
    dpg.start_dearpygui()


def _add_main_window(window_tag: DpgItem, tab_tag: DpgItem):
    with dpg.window(tag=window_tag, autosize=True, no_collapse=True):
        dpg.add_tab_bar(tag=tab_tag)


##############################################################################

def main():
    dpg.create_context()

    context = Context()

    _setup_app("main_window", "main_tab_bar", context)
    _start_app("main_window")

    dpg.destroy_context()


if __name__ == '__main__':
    main()
