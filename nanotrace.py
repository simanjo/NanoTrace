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
    dpg.configure_item("Progress Bar", overlay=f"Checking channel {channel}/126", width=175)
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
    # first thing to happen: button vanishes
    dpg.configure_item("get_active_channels", show=False)

    fpath = dpg.get_value("filepath")
    burnin = 350000
    if not fpath:
        return

    chans = _get_active_channels(fpath, burnin)
    fname = path.splitext(path.split(fpath)[1])[0]
    exp_df[fname]["active_channels"] = chans
    dpg.configure_item("channel", items=chans)
    dpg.configure_item("func_choose", show=True)
    dpg.configure_item("toggle_channels", show=True)


def choose_file(sender, app_data, user_data):
    global exp_df

    try:
        fpath = list(app_data['selections'].values())[0]
        fname = path.splitext(list(app_data['selections'].keys())[0])[0]
    except KeyError:
        return


    dpg.set_value("filename", fname)
    dpg.set_value("filepath", fpath)
    dpg.configure_item("filename", show=True)
    dpg.configure_item("channel_choose", show=True)
    dpg.set_value("channel", "")
    dpg.configure_item("get_active_channels", show=False)
    dpg.configure_item("toggle_channels", show=False)
    dpg.configure_item("func_choose", show=False)

    if fname in exp_df.keys():
        if "active_channels" in exp_df[fname].keys():
            dpg.configure_item("channel", items=exp_df[fname]['active_channels'])
            dpg.configure_item("toggle_channels", show=True)
            dpg.configure_item("func_choose", show=True)
            return
    else:
        dpg.configure_item("Progress Bar", show=True)
        dpg.set_value("Progress Bar", 0.5)
        dpg.configure_item("Progress Bar", overlay=f"Calculating file hash", width=150)
        exp_df[fname] = {'path':fpath, 'md5':md5(fpath)}
        dpg.configure_item("Progress Bar", show=False)

    dpg.configure_item("channel", items=list(range(1,127)))
    dpg.configure_item("get_active_channels", show=True)

def _plot_raw_series(data, name, channel):
    dpg.configure_item("raw_data_window", show=True)

    with dpg.plot(label=f"{name}\nChannel {channel}", height=-1, width=-1, tag="raw_plot", parent="raw_data_window"):
        dpg.add_plot_legend()

        dpg.add_plot_axis(dpg.mvXAxis, label="index", tag="raw_x_axis")#, no_gridlines=True)
        dpg.set_axis_limits(dpg.last_item(), 0, 100000)

        dpg.add_plot_axis(dpg.mvYAxis, label="current [pA]", tag="raw_y_axis")
        dpg.set_axis_limits(dpg.last_item(), -20, 350)

        dpg.add_line_series(list(range(0,len(data))), data, parent=dpg.last_item())
        dpg.set_axis_limits_auto("raw_x_axis")
        dpg.set_axis_limits_auto("raw_y_axis")

    dpg.configure_item("raw_data_window", on_close=lambda:dpg.delete_item("raw_plot"))


def choose_channel(sender, app_data, user_data):
    c = dpg.get_value("channel")
    fpath = dpg.get_value("filepath")
    fname = dpg.get_value("filename")
    if not fpath or not c:
        return

    with BulkFast5(fpath) as fh:
        raw_data = fh.get_raw(c)

    _plot_raw_series(raw_data, fname, c)


def _plot_kde(title, *data):
    dpg.configure_item("kde_window", show=True)

    with dpg.plot(label=title, height=-1, width=-1, tag="kde_plot", parent="kde_window"):
        dpg.add_plot_legend()

        dpg.add_plot_axis(dpg.mvXAxis, label="current [pA]", tag="kde_x_axis")#, no_gridlines=True)
        dpg.set_axis_limits(dpg.last_item(), -20, 350)

        dpg.add_plot_axis(dpg.mvYAxis, label="density", tag="kde_y_axis")
        dpg.set_axis_limits(dpg.last_item(), -0.05, 0.2)

        for kde in data:
            dpg.add_line_series(kde.support, kde.density, parent="kde_y_axis")
        dpg.set_axis_limits_auto("kde_x_axis")
        dpg.set_axis_limits_auto("kde_y_axis")

    dpg.configure_item("kde_window", on_close=lambda:dpg.delete_item("kde_plot"))

def show_kde(sender, app_data, user_data):
    c = dpg.get_value("channel")
    fpath = dpg.get_value("filepath")
    fname = dpg.get_value("filename")
    title = f"{fname}\nChannel {c}"
    if not fpath or not c:
        return

    with BulkFast5(fpath) as fh:
        raw_data = fh.get_raw(c)

    kde = sm.nonparametric.KDEUnivariate(raw_data)
    kde.fit(gridsize=min(1000000,len(raw_data)))
    _plot_kde(title, kde)

def toggle_active_channels(sender, app_data, user_data):
    global exp_df
    if(dpg.get_value(sender)):
        dpg.configure_item("channel", items=list(range(1,127)))
    else:
        fname = dpg.get_value("filename")
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
            dpg.add_text(tag="filename", show=False)
        with dpg.group(horizontal=True, tag="channel_choose", show=False):
            dpg.add_text("Channel:")
            dpg.add_combo(tag="channel", width=60)
            dpg.add_button(label="Get Active Channels", tag="get_active_channels", callback=set_active_channels, show=False)
            dpg.add_checkbox(label="Show All Channels", tag='toggle_channels', callback=toggle_active_channels, show=False)
        with dpg.group(tag="func_choose", show=False):
            dpg.add_button(label="Show Squiggle Plot", callback=choose_channel)
            dpg.add_button(label="Show Density Plot", callback=show_kde)

        dpg.add_progress_bar(tag="Progress Bar", show=False, width=175)


def _add_raw_data_window():
    dpg.add_window(label="Raw Data", width=800, height=600, show=False, tag="raw_data_window")

def _add_kde_window():
    dpg.add_window(label="Kernel Density", width=800, height=600, show=False, tag="kde_window")


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
    _add_raw_data_window()
    _add_kde_window()

    _init_value_registry()

    _start_app()

    dpg.destroy_context()

if __name__ == '__main__':
    main()
