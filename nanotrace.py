import sys
from pathlib import Path

import dearpygui.dearpygui as dpg

from context import Context
from themes import custom_theme
from command_central import add_command_central

DpgItem = Union[int, str]

    ):



def _start_app():
    dpg.bind_theme(custom_theme())

    dpg.create_viewport(title='NanoTrace', width=850, height=800)
    dpg.setup_dearpygui()

    dpg.show_viewport()
    dpg.set_primary_window("main_window", True)
    dpg.start_dearpygui()


def _get_main_dir():
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return Path(sys.executable).parent
    else:
        return Path(__file__).parent


##############################################################################

def main():
    dpg.create_context()

    context = Context(cwd=_get_main_dir())
    add_command_central(context)
    _add_file_dialog(context)
    _add_command_central(context)
    # _add_raw_data_window()
    # _add_kde_window()

    # _init_value_registry()

    _start_app()

    dpg.destroy_context()


if __name__ == '__main__':
    main()
