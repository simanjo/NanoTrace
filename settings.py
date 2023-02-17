from typing import Union, Dict, Any
from pathlib import Path
import time

import dearpygui.dearpygui as dpg
from command_central import _show_experiment_info

from context import Context
from utils import determine_scaling

DpgItem = Union[int, str]


def add_settings(tab_tag: DpgItem, context: Context):
    with dpg.tab(label="Settings", parent=tab_tag):
        dpg.add_spacer(height=5)
        _add_database_select(context)
        _add_event_distribution_settings(context)
    settings = context.settings
    update_event_bands(
        min_ev=settings.get('min_event_band', 0.27),
        max_ev=settings.get('max_event_band', 0.48)
    )


def add_changed_settings_handler(tab_tag: DpgItem, context: Context):
    with dpg.item_handler_registry() as handler:
        dpg.add_item_clicked_handler(
            callback=update_context_with_settings,
            user_data=context)
    dpg.bind_item_handler_registry(tab_tag, handler)


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


def _add_event_distribution_settings(context: Context):
    dpg.add_text("Event Band Settings:")
    with dpg.group(horizontal=True):
        # table like grouping, have labels in first group for auto alignment
        with dpg.group():
            dpg.add_text("Scale with Baseline:")
            dpg.add_text("Lower event band bound:")
            dpg.add_text("Upper event band bound:")
        with dpg.group():
            dpg.add_combo(
                tag="bl_scaling",
                items=["lower bound", "upper bound", "both", "none"],
                default_value="both",
                callback=select_bl_scaling, user_data=context
            )
            dpg.add_slider_float(
                tag="min_event_float", clamped=True, max_value=1.0,
                default_value=0.27, label="[1/100]", format='%.2f',
                callback=set_min_band, user_data=context
            )
            dpg.add_slider_int(
                tag="min_event_int", show=False, max_value=350, label="[pA]",
                callback=set_min_band, user_data=context
            )
            dpg.add_slider_float(
                tag="max_event_float", clamped=True,
                max_value=1.0, default_value=0.48, label="[1/100]",
                callback=set_max_band, user_data=context, format='%.2f'
            )
            dpg.add_slider_int(
                tag="max_event_int", show=False, max_value=350, label="[pA]",
                callback=set_max_band, user_data=context
            )
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


def update_event_bands(
    min_ev: Union[float, int], max_ev: Union[float, int], set_scale_combo=True
):
    scale = None
    if isinstance(min_ev, int):
        if isinstance(max_ev, int):
            scale = "none"
            dpg.configure_item("min_event_float", show=False)
            dpg.configure_item("max_event_float", show=False)
            dpg.configure_item(
                "min_event_int", show=True, default_value=min_ev
            )
            dpg.configure_item(
                "max_event_int", show=True, default_value=max_ev
            )
        else:
            assert isinstance(max_ev, float)
            scale = "upper bound"
            dpg.configure_item("min_event_float", show=False)
            dpg.configure_item(
                "max_event_float", show=True, default_value=max_ev
            )
            dpg.configure_item(
                "min_event_int", show=True, default_value=min_ev
            )
            dpg.configure_item("max_event_int", show=False)
    elif isinstance(max_ev, int):
        assert isinstance(min_ev, float)
        scale = "lower bound"
        dpg.configure_item(
            "min_event_float", show=True, default_value=min_ev
        )
        dpg.configure_item("max_event_float", show=False)
        dpg.configure_item("min_event_int", show=False)
        dpg.configure_item("max_event_int", show=True, default_value=max_ev)
    else:
        assert isinstance(max_ev, float)
        assert isinstance(min_ev, float)
        scale = "both"
        dpg.configure_item(
            "min_event_float", show=True, default_value=min_ev
        )
        dpg.configure_item(
            "max_event_float", show=True, default_value=max_ev
        )
        dpg.configure_item("min_event_int", show=False)
        dpg.configure_item("max_event_int", show=False)
    if set_scale_combo:
        dpg.set_value("bl_scaling", scale)


def select_bl_scaling(
    sender: DpgItem,
    app_data: Dict[str, Any],
    user_data: Context
) -> None:
    scale = dpg.get_value(sender)
    settings = user_data.settings
    min_ev_set = settings.get('min_event_band', 0.27)
    max_ev_set = settings.get('max_event_band', 0.48)
    if scale == "none":
        min_ev = min_ev_set if isinstance(min_ev_set, int) else 40
        max_ev = max_ev_set if isinstance(max_ev_set, int) else 100
    elif scale == "lower bound":
        min_ev = min_ev_set if not isinstance(min_ev_set, int) else 0.27
        max_ev = max_ev_set if isinstance(max_ev_set, int) else 100
    elif scale == "upper bound":
        min_ev = min_ev_set if isinstance(min_ev_set, int) else 40
        max_ev = max_ev_set if not isinstance(max_ev_set, int) else 0.48
    elif scale == "both":
        min_ev = min_ev_set if not isinstance(min_ev_set, int) else 0.27
        max_ev = max_ev_set if not isinstance(max_ev_set, int) else 0.48
    else:
        # should not happen
        assert False
    settings['min_event_band'] = min_ev
    settings['max_event_band'] = max_ev
    user_data.dirty = True
    update_event_bands(min_ev, max_ev, set_scale_combo=False)


def set_min_band(
    sender: DpgItem,
    app_data: Dict[str, Any],
    user_data: Context
) -> None:
    # wait shortly and check whether the value has changed
    min_ev = dpg.get_value(sender)
    time.sleep(0.1)
    if dpg.get_value(sender) == min_ev:
        max_ev = user_data.settings.get('max_event_band', 0.48)
        update_event_bands(min_ev, max_ev, set_scale_combo=False)
        user_data.settings["min_event_band"] = min_ev
        user_data.dirty = True


def set_max_band(
    sender: DpgItem,
    app_data: Dict[str, Any],
    user_data: Context
) -> None:
    # wait shortly and check whether the value has changed
    max_ev = dpg.get_value(sender)
    time.sleep(0.1)
    if dpg.get_value(sender) == max_ev:
        min_ev = user_data.settings.get('min_event_band', 0.27)
        update_event_bands(min_ev, max_ev, set_scale_combo=False)
        user_data.settings["max_event_band"] = max_ev
        user_data.dirty = True


def update_context_with_settings(
    sender: DpgItem,
    app_data: Dict[str, Any],
    user_data: Context
) -> None:
    if not user_data.dirty or user_data.active_exp is None\
            or user_data.active_exp.get_active_channels() is None:
        return

    min_ev = user_data.settings['min_event_band']
    max_ev = user_data.settings['max_event_band']
    scaling = determine_scaling(min_ev, max_ev)
    bands = user_data.active_exp.band_distribution
    if bands == {}:
        recompute = True
    else:
        try:
            if (min_ev, max_ev) in next(iter(bands.values()))[scaling].keys():
                recompute = False
            else:
                recompute = True
        except (KeyError, StopIteration):
            # KeyError stems from scaling missing as key
            # StopIteration stems from empty bands dict
            recompute = True
            pass
    if recompute:
        dpg.configure_item("func_choose", show=False)
        dpg.configure_item("exp_info", show=False)
        dpg.configure_item("channel_choose", show=True)
        if (chans := user_data.get_active_channels()) is not None:
            dpg.configure_item("channel", items=chans)
            dpg.configure_item("toggle_channels", show=True)
            dpg.configure_item("func_choose", show=True)
            if user_data.has_band_distribution():
                _show_experiment_info(user_data)
            else:
                dpg.configure_item("get_band_distributions", show=True)
        else:
            dpg.configure_item("channel", items=list(range(1, 127)))
            dpg.configure_item("toggle_channels", show=False)
            dpg.configure_item("get_active_channels", show=True)
    user_data.dirty = False
