from typing import Union, Dict, Any
from pathlib import Path
import time

import dearpygui.dearpygui as dpg

from context import Context

DpgItem = Union[int, str]


def add_settings(tab_tag: DpgItem, context: Context):
    with dpg.tab(label="Settings", parent=tab_tag):
        dpg.add_spacer(height=5)
        _add_database_select(context)


# ################ Setup functions ############################################
# TODO: build OO interface for sounder intialization
def _add_database_dialog(dialog_tag: DpgItem, context: Context):
    with dpg.file_dialog(
        directory_selector=False, show=False, callback=choose_db,
        user_data=context, id=dialog_tag, width=500, height=400
    ):
        dpg.add_file_extension(".*")
        dpg.add_file_extension(
            ".db", color=(0, 255, 255, 255), custom_text="[db]"
        )


def _add_database_select(context: Context):
    _add_database_dialog("db_dialog", context)

    with dpg.group(horizontal=True):
        dpg.add_button(
            label="Select experiment database",
            callback=lambda: dpg.show_item("db_dialog")
        )
        dpg.add_text(tag="exp_db_name", show=False)
    dpg.add_spacer(height=5)
    dpg.add_separator()


# ################ Callbacks ##################################################
# TODO: build OO interface for sounder intialization


def choose_db(
    sender: DpgItem,
    app_data: Dict[str, Any],
    user_data: Context
) -> None:
    try:
        fpath = Path(list(app_data['selections'].values())[0])
    except KeyError:
        return

    dpg.set_value("exp_db_name", fpath)
    dpg.configure_item("exp_db_name", show=True)
    user_data.update_experiment_db(fpath)
    settings = user_data.settings
    update_event_bands(
        min_ev=settings.get('min_event_band', 0.27),
        max_ev=settings.get('max_event_band', 0.48)
    )


