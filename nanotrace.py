from typing import Dict, Any, Union
import dearpygui.dearpygui as dpg
from themes import custom_theme
from os import path

from series_plots import show_kde, show_rand_kde, show_raw
from context import Context

DpgItem = Union[int, str]


def set_active_channels() -> None:
    global context
    # first thing to happen: button vanishes
    dpg.configure_item("get_active_channels", show=False)
    dpg.configure_item("channel", items=context.get_active_channels())
    dpg.configure_item("func_choose", show=True)
    dpg.configure_item("toggle_channels", show=True)


def choose_file(sender: DpgItem, app_data: Dict[str, Any]) -> None:
    global context

    try:
        fpath = list(app_data['selections'].values())[0]
        fname = path.splitext(list(app_data['selections'].keys())[0])[0]
    except KeyError:
        return

    # TODO/HACK: invent state interface to allow for
    #            easier switching of displayed stuff
    context.update_context(
        fpath, progressbar="Progress Bar", table="exp_table"
    )
    dpg.configure_item("experiment_tab", show=True)
    dpg.set_value("filename", context.active_exp.name)
    dpg.configure_item("filename", show=True)
    dpg.configure_item("channel_choose", show=True)
    dpg.set_value("channel", "")
    dpg.configure_item("get_active_channels", show=False)
    dpg.configure_item("toggle_channels", show=False)
    dpg.configure_item("func_choose", show=False)

    if (chans := context.active_exp.active_channels) is not None:
        dpg.configure_item("channel", items=chans)
        dpg.configure_item("toggle_channels", show=True)
        dpg.configure_item("func_choose", show=True)
    else:
        dpg.configure_item("channel", items=list(range(1, 127)))
        dpg.configure_item("get_active_channels", show=True)


def toggle_active_channels(sender: DpgItem) -> None:
    global context

    if dpg.get_value(sender):
        dpg.configure_item("channel", items=list(range(1, 127)))
    else:
        dpg.configure_item("channel", context.active_exp.active_channels)


################# Setup functions ############################################
#TODO: build OO interface for sounder intialization
def _add_file_dialog():
    with dpg.file_dialog(
        directory_selector=False, show=False, callback=choose_file,
        id="file_dialog", width=500, height=400
    ):
        dpg.add_file_extension(".*")
        dpg.add_file_extension(
            ".fast5", color=(0, 255, 255, 255), custom_text="[fast5]"
        )


def _add_command_central():
    global context
    with dpg.window(
        tag="main_window", autosize=True,
        no_close=True, no_collapse=True
    ):
        with dpg.tab_bar():
            with dpg.tab(label="Command Central"):
                with dpg.group(horizontal=True):
                    dpg.add_button(
                        label="File Selector",
                        callback=lambda: dpg.show_item("file_dialog")
                    )
                    dpg.add_text(tag="filename", show=False)
                with dpg.group(
                    horizontal=True, tag="channel_choose", show=False
                ):
                    dpg.add_text("Channel:")
                    dpg.add_combo(tag="channel", width=60)
                    dpg.add_button(
                        label="Get Active Channels",
                        tag="get_active_channels",
                        callback=set_active_channels, show=False
                    )
                    dpg.add_checkbox(
                        label="Show All Channels",
                        tag='toggle_channels',
                        callback=toggle_active_channels, show=False
                    )
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

                dpg.add_progress_bar(tag="Progress Bar", show=False, width=175)
            with dpg.tab(label="Experiments", show=False, tag="exp_tab"):
                with dpg.table(header_row=True, resizable=True, tag="exp_tbl"):
                    dpg.add_table_column(label="Name")
                    dpg.add_table_column(label="Filepath(s)")
                    dpg.add_table_column(label="Analyte")
                    dpg.add_table_column(label="Concentration")
                    dpg.add_table_column(label="# channels")


def _start_app():
    dpg.bind_theme(custom_theme())

    dpg.create_viewport(title='NanoTrace', width=850, height=800)
    dpg.setup_dearpygui()

    dpg.show_viewport()
    dpg.set_primary_window("main_window", True)
    dpg.start_dearpygui()


##############################################################################

def main():
    global context

    dpg.create_context()

    context = Context()
    _add_file_dialog()
    _add_command_central()
    # _add_raw_data_window()
    # _add_kde_window()

    # _init_value_registry()

    _start_app()

    dpg.destroy_context()


if __name__ == '__main__':
    main()
