from typing import Dict, Any, Union

import dearpygui.dearpygui as dpg

from context import Context
from python_toolbox.util import split_string_to_size
from series_plots import show_kde, show_rand_kde, show_raw
from utils import event_density, determine_scaling

DpgItem = Union[int, str]


def add_command_central(tab_tag: DpgItem, context: Context):
    with dpg.tab(label="Command Central", parent=tab_tag) as tab:
        dpg.add_spacer(height=5)
        _add_file_select(context)
        dpg.add_spacer(height=10)
        _add_channel_choose(context)
        dpg.add_spacer(height=5)
        _add_func_choose(context)
        dpg.add_spacer(height=5)
        dpg.add_progress_bar(tag="Progress Bar", show=False, width=175)
        dpg.add_spacer(height=5)
        _add_exp_info(context)
        dpg.add_spacer(height=10)
        dpg.add_button(
            label="Save Experiments and Quit",
            callback=_save_and_quit, user_data=context
        )
    return tab


def _save_and_quit(
    sender: DpgItem,
    app_data: Any,
    user_data: Context
) -> None:
    user_data._dump_exps()
    dpg.stop_dearpygui()


# ################ Setup functions ############################################
# TODO: build OO interface for sounder intialization
def _add_file_dialog(dialog_tag: DpgItem, context: Context):
    with dpg.file_dialog(
        directory_selector=False, show=False, callback=choose_file,
        user_data=context, id=dialog_tag, width=500, height=400
    ):
        dpg.add_file_extension(".*")
        dpg.add_file_extension(
            ".fast5", color=(0, 255, 255, 255), custom_text="[fast5]"
        )


def _add_file_select(context: Context):
    _add_file_dialog("file_dialog", context)

    with dpg.group(horizontal=True,):
        dpg.add_button(
            label="File Selector",
            callback=lambda: dpg.show_item("file_dialog")
        )
        dpg.add_text(tag="filename", show=False)


def _add_channel_choose(context: Context):
    with dpg.group(
        horizontal=True, tag="channel_choose", show=False
    ):
        dpg.add_text("Channel:")
        dpg.add_combo(
            tag="channel", width=60,
            callback=set_channel,
            user_data=context
            )
        dpg.add_button(
            label="Get Active Channels",
            tag="get_active_channels",
            callback=set_active_channels,
            user_data=context, show=False
        )
        dpg.add_button(
            label="Calculate Event Bands",
            tag="get_band_distributions",
            callback=get_band_distributions,
            user_data=context, show=False
        )
        dpg.add_checkbox(
            label="Show All Channels",
            tag='toggle_channels',
            callback=toggle_active_channels,
            user_data=context, show=False
        )


def _add_func_choose(context: Context):
    with dpg.group(tag="func_choose", show=False):
        dpg.add_button(
            label="Show Squiggle Plot",
            callback=show_raw, user_data=context
        )
        dpg.add_button(
            label="Show Density Plot",
            callback=show_kde, user_data=context
        )
        dpg.add_button(
            label="Show Random Densities",
            callback=show_rand_kde, user_data=context
        )


def _add_exp_info(context: Context):
    with dpg.group(tag="exp_info", horizontal=True, show=False):
        with dpg.group(tag="general_info"):
            with dpg.group(horizontal=True):
                dpg.add_text("Active channels:")
                dpg.add_text(tag="active_channels_info")
            with dpg.group(horizontal=True):
                dpg.add_text("Avg event density:")
                with dpg.tooltip(dpg.last_item()):
                    dpg.add_text("[mean (+/- 2*sd)]")
                dpg.add_text(tag="avg_event_info")
            with dpg.group(horizontal=True):
                dpg.add_text("Avg Baseline:")
                with dpg.tooltip(dpg.last_item()):
                    dpg.add_text("[mean (+/- 2*sd)]")
                dpg.add_text(tag="avg_baseline_info")
            with dpg.group(horizontal=True):
                dpg.add_text("Concentration:")
                dpg.add_text(tag="concentration_info")
        with dpg.group(tag="channel_info", show=False):
            with dpg.group(horizontal=True):
                dpg.add_text("Selected channel:")
                dpg.add_text(tag="sel_channel_info")
            with dpg.group(horizontal=True):
                dpg.add_text("Event density:")
                dpg.add_text(tag="sel_event_info")
            with dpg.group(horizontal=True):
                dpg.add_text("Baseline: ")
                dpg.add_text(tag="sel_baseline_info")
            with dpg.group(horizontal=True):
                dpg.add_text("Baseline density:")
                dpg.add_text(tag="sel_baseline_density_info")
            with dpg.group(horizontal=True):
                dpg.add_text("Zeroes density:")
                dpg.add_text(tag="sel_zeroes_info")


# ################ Callbacks ##################################################
# TODO: build OO interface for sounder intialization


def set_active_channels(
    sender: DpgItem,
    app_data: Any,
    user_data: Context
) -> None:
    # first thing to happen: button vanishes
    dpg.configure_item("get_active_channels", show=False)
    user_data.calculate_band_distributions()
    dpg.configure_item(
        "channel", items=user_data.get_active_channels(), show=True
    )
    dpg.configure_item("toggle_channels", show=True)
    dpg.configure_item("func_choose", show=True)
    _show_experiment_info(user_data)


def get_band_distributions(
    sender: DpgItem,
    app_data: Any,
    user_data: Context
) -> None:
    # first thing to happen: button vanishes
    dpg.configure_item("get_band_distributions", show=False)
    user_data.calculate_band_distributions()
    _show_experiment_info(user_data)


def choose_file(
    sender: DpgItem,
    app_data: Dict[str, Any],
    user_data: Context
) -> None:
    try:
        fpath = list(app_data['selections'].values())[0]
    except KeyError:
        return

    # TODO/HACK: invent state interface to allow for
    #            easier switching of displayed stuff
    dpg.configure_item("channel_choose", show=False)
    dpg.configure_item("func_choose", show=False)
    dpg.configure_item("exp_info", show=False)
    # reset filename first as file loading might take some time
    dpg.configure_item("filename", show=False)
    user_data.update_context(fpath, progressbar="Progress Bar")
    dpg.set_value(
        "filename",
        "\n".join(split_string_to_size(user_data.active_exp.name, 60, sep="_"))
    )
    dpg.configure_item("filename", show=True)
    dpg.configure_item("channel_choose", show=True)
    dpg.set_value("channel", "")

    if (chans := user_data.get_active_channels()) is not None:
        dpg.configure_item("channel", items=chans, show=True)
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


def _show_experiment_info(context: Context) -> None:
    if (exp := context.active_exp) is None:
        return
    ev_low = context.settings['min_event_band']
    ev_high = context.settings['max_event_band']
    dpg.set_value("active_channels_info", len(exp.get_active_channels()))
    mean, sd = exp.get_mean_events(ev_low, ev_high)
    dpg.set_value("avg_event_info", f"{mean} (+/-{2*sd})")
    mean_bl, sd_bl = exp.get_mean_baselines(ev_low, ev_high)
    dpg.set_value("avg_baseline_info", f"{mean_bl} (+/-{2*sd_bl})")
    dpg.set_value("concentration_info", exp.properties['concentration'])
    dpg.configure_item("exp_info", show=True)


def set_channel(
    sender: DpgItem,
    app_data: Any,
    user_data: Context
) -> None:
    channel = int(dpg.get_value(sender))
    if user_data.active_exp.band_distribution == {}:
        dpg.set_value("channel", "")
        return
    try:
        band_dict = user_data.active_exp.band_distribution[channel]
    except KeyError:
        dpg.set_value("channel", "")
        dpg.configure_item("channel_info", show=False)
        return

    ev_low = user_data.settings['min_event_band']
    ev_high = user_data.settings['max_event_band']
    try:
        bl, band = band_dict[
            determine_scaling(ev_low, ev_high)
        ][(ev_low, ev_high)]
    except KeyError:
        dpg.configure_item("channel_info", show=False)
        return

    dpg.set_value("sel_channel_info", channel)
    dpg.set_value("sel_event_info", round(event_density(band), 4))
    dpg.set_value("sel_baseline_info", bl)
    dpg.set_value(
        "sel_baseline_density_info",
        round(event_density(band, 'baseline'), 4))
    zeroes = round(event_density(band, 'zeroes'), 4)
    col = (255, 0, 0, 255) if zeroes > 0.1 else (255, 255, 255, 255)
    dpg.set_value("sel_zeroes_info", zeroes)
    dpg.configure_item("sel_zeroes_info", color=col)
    dpg.configure_item("channel_info", show=True)


def toggle_active_channels(
    sender: DpgItem,
    app_data: Any,
    user_data: Context
) -> None:
    if dpg.get_value(sender):
        dpg.configure_item("channel", items=list(range(1, 127)))
    else:
        if (chans := user_data.active_exp.get_active_channels()) is not None:
            dpg.configure_item("channel", items=chans)
