import dearpygui.dearpygui as dpg
from fast5_research.fast5_bulk import BulkFast5
import numpy as np
import statsmodels.api as sm
from themes import custom_theme
from os import path
import hashlib


def _is_active_channel(fname, channel, burnin):
    with BulkFast5(fname) as fh:
        raw_data = fh.get_raw(channel)[burnin:]

    return np.abs(np.mean(raw_data)) > 1 and len(raw_data[np.logical_and(raw_data > 150, raw_data < 350)]) > 0

def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def _update_channel_progress(channel):
    dpg.set_value("Progress Bar", (channel-1)/126)
    dpg.configure_item("Progress Bar", overlay=f"Checking channel {channel}/126")
    return True

def _get_active_channels(fname, burnin=350000):
    dpg.configure_item("Progress Bar", show=True)

    result = [
        c for c in range(1,127) if _update_channel_progress(c) and _is_active_channel(fname, c, burnin)
    ]

    dpg.configure_item("Progress Bar", show=False)
    return result

def set_active_channels():
    global exp_df

    fpath = dpg.get_value("filepath")
    burnin = 350000
    if not fpath:
        return

    chans = _get_active_channels(fpath, burnin)
    fname = path.splitext(path.split(fpath)[1])[0]
    exp_df[fname]["active_channels"] = chans
    dpg.configure_item("channel", items=chans)
    dpg.configure_item("get_active_channels", show=False)
    dpg.configure_item("func_choose", show=True)
    dpg.configure_item("toggle_channels", show=True)


def choose_file(sender, app_data, user_data):
    global exp_df

    try:
        fpath = list(app_data['selections'].values())[0]
        fname = path.splitext(list(app_data['selections'].keys())[0])[0]
    except KeyError:
        return
    if fname in exp_df.keys():
        dpg.set_value("file", fname)
        dpg.set_value("filepath", fpath)
        dpg.configure_item("file", show=True)
        if "active_channels" in exp_df[fname].keys():
            dpg.configure_item("channel", items=exp_df[fname]['active_channels'])
            dpg.configure_item("func_choose", show=True)
        else:
            dpg.configure_item("channel", items=list(range(1,127)))
            dpg.configure_item("get_active_channels", show=True)
            dpg.configure_item("func_choose", show=False)
    else:
        dpg.set_value("file", fname)
        dpg.set_value("filepath", fpath)
        dpg.configure_item("file", show=True)
        dpg.configure_item("channel", items=list(range(1,127)))
        dpg.configure_item("channel_choose", show=True)
        dpg.configure_item("get_active_channels", show=True)
        dpg.configure_item("func_choose", show=False)

        exp_df[fname] = {'path':fpath, 'md5':md5(fpath)}



def choose_channel(sender, app_data, user_data):
    c = dpg.get_value("channel")
    fname = dpg.get_value("filepath")
    if not fname or not c:
        return

    with BulkFast5(fname) as fh:
        raw_data = fh.get_raw(c)

    dpg.configure_item("raw-data", show=True)
    dpg.set_value('raw_series', [list(range(0,len(raw_data))), raw_data])
    dpg.set_axis_limits_auto("raw_x_axis")
    dpg.set_axis_limits_auto("raw_y_axis")

def show_kde(sender, app_data, user_data):
    c = dpg.get_value("channel")
    fname = dpg.get_value("filepath")
    if not fname or not c:
        return

    with BulkFast5(fname) as fh:
        raw_data = fh.get_raw(c)

    dpg.configure_item("kde-data", show=True)
    kdes = sm.nonparametric.KDEUnivariate(raw_data)
    kdes.fit()
    dpg.set_value('raw_density', [kdes.support, kdes.density])
    dpg.set_axis_limits_auto("x_axis")
    dpg.set_axis_limits_auto("y_axis")

def toggle_active_channels(sender, app_data, user_data):
    global exp_df
    if(dpg.get_value(sender)):
        dpg.configure_item("channel", items=list(range(1,127)))
    else:
        fname = dpg.get_value("file")
        if fname in exp_df.keys() and 'active_channels' in exp_df[fname].keys():
            dpg.configure_item("channel", items=exp_df[fname]['active_channels'])



################# Setup functions ############################################
#TODO: build OO interface for sounder intialization
def _add_file_dialog():
    with dpg.file_dialog(directory_selector=False, show=False, callback=choose_file, id="file_dialog", width=500, height=400):
        dpg.add_file_extension(".*")
        dpg.add_file_extension(".fast5", color=(0, 255, 255, 255), custom_text="[fast5]")

def _init_value_registry():
    with dpg.value_registry():
        dpg.add_string_value(tag="filepath")

def _add_command_central():
    with dpg.window(label="Command Central", autosize=True, no_close=True, no_collapse=True):
        with dpg.group(horizontal=True):
            dpg.add_button(label="File Selector", callback=lambda: dpg.show_item("file_dialog"))
            dpg.add_text(tag="file", show=False)
        with dpg.group(horizontal=True, tag="channel_choose", show=False):
            dpg.add_text("Channel:")
            dpg.add_combo(tag="channel", width=60)
            dpg.add_button(label="Get Active Channels", tag="get_active_channels", callback=set_active_channels)
            dpg.add_checkbox(label="Show All Channels", tag='toggle_channels', callback=toggle_active_channels, show=False)
        with dpg.group(tag="func_choose", show=False):
            dpg.add_button(label="Show Squiggle Plot", callback=choose_channel)
            dpg.add_button(label="Show Density Plot", callback=show_kde)

        dpg.add_progress_bar(tag="Progress Bar", show=False, width=175)

def _start_app():
    dpg.bind_theme(custom_theme())

    dpg.create_viewport(title='NanoTrace', width=850, height=800)
    dpg.setup_dearpygui()

    dpg.show_viewport()
    dpg.start_dearpygui()


##############################################################################

def main():
    global exp_df
    exp_df = {}
    dpg.create_context()

    _add_file_dialog()
    _add_command_central()

    _init_value_registry()

    with dpg.window(label="Raw Data", width=800, height=600, show=False, tag="raw-data"):
        with dpg.plot(label="Squiggle Plot", height=-1, width=-1):
            dpg.add_plot_legend()

            # create x axis
            dpg.add_plot_axis(dpg.mvXAxis, label="index", no_gridlines=True, tag="raw_x_axis")
            dpg.set_axis_limits(dpg.last_item(), 0, 100000)
            # dpg.set_axis_ticks(dpg.last_item(), (("S1", 11), ("S2", 21), ("S3", 31)))

            # create y axis
            dpg.add_plot_axis(dpg.mvYAxis, label="current [pA]", tag="raw_y_axis")
            dpg.set_axis_limits(dpg.last_item(), -20, 350)

            # add series to y axis
            dpg.add_line_series([], [], parent=dpg.last_item(), tag = "raw_series")
            # dpg.set_axis_limits_auto("x_axis")
            # dpg.set_axis_limits_auto("y_axis")

    with dpg.window(label="Kernel Density", width=800, height=600, show=False, tag="kde-data"):
        #dpg.add_button(label="Show signal density", callback=show_kde)

        with dpg.plot(label="Density Plot", height=-1, width=-1):
            dpg.add_plot_legend()

            # create x axis
            dpg.add_plot_axis(dpg.mvXAxis, label="current [pA]", no_gridlines=True, tag="x_axis")
            dpg.set_axis_limits(dpg.last_item(), -20, 350)
            # dpg.set_axis_ticks(dpg.last_item(), (("S1", 11), ("S2", 21), ("S3", 31)))

            # create y axis
            dpg.add_plot_axis(dpg.mvYAxis, label="density", tag="y_axis")
            dpg.set_axis_limits("y_axis", -0.05, 0.2)

            # add series to y axis
            dpg.add_line_series([], [], parent="y_axis", tag = "raw_density")
            # dpg.set_axis_limits_auto("x_axis")
            # dpg.set_axis_limits_auto("y_axis")

    _start_app()

    dpg.destroy_context()

if __name__ == '__main__':
    main()
