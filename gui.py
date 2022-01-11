import dearpygui.dearpygui as dpg
from fast5_research.fast5_bulk import BulkFast5
import numpy as np

def _is_active_channel(fname, channel):
    with BulkFast5(fname) as fh:
        raw_data = fh.get_raw(channel)

    return np.abs(np.mean(raw_data)) > 1 and len(raw_data[np.logical_and(raw_data > 150, raw_data < 350)]) > 0
    # baseline = None



def _get_active_channels(fname):
    result = [
        c for c in range(1,127) if _is_active_channel(fname, c)
    ]
    return result

def set_active_channels():
    fname = dpg.get_value("filepath")
    if not fname:
        return

    chans = _get_active_channels(fname)
    dpg.configure_item("channel", items=chans)



def choose_file(sender, app_data, user_data):
    try:
        fpath = list(app_data['selections'].values())[0]
        fname = list(app_data['selections'].keys())[0]
    except KeyError:
        return
    dpg.set_value("file", fname)
    dpg.set_value("filepath", fpath)
    dpg.configure_item("channel", items=list(range(1,127)))



def choose_channel(sender, app_data, user_data):
    c = dpg.get_value("channel")
    fname = dpg.get_value("filepath")
    if not fname or not c:
        return

    with BulkFast5(fname) as fh:
        raw_data = fh.get_raw(c)

    dpg.set_value('raw_series', [list(range(0,len(raw_data))), raw_data])
    dpg.set_axis_limits_auto("x_axis")
    dpg.set_axis_limits_auto("y_axis")

##############################################################################

def main():
    dpg.create_context()

    with dpg.file_dialog(directory_selector=False, show=False, callback=choose_file, id="file_dialog"):
        dpg.add_file_extension(".*")
        dpg.add_file_extension(".fast5", color=(0, 255, 255, 255), custom_text="[fast5]")

    with dpg.value_registry():
        dpg.add_string_value(tag="filepath")

    with dpg.window(label="Command Central", autosize=True, no_close=True, no_collapse=True):
        with dpg.group(horizontal=True):
            dpg.add_button(label="File Selector", callback=lambda: dpg.show_item("file_dialog"))
            dpg.add_text(tag="file", show=False)
        with dpg.group(horizontal=True):
            dpg.add_text("Channel:")
            dpg.add_combo(tag="channel", width=60)
            dpg.add_button(label="Get active channels", callback=set_active_channels)
        with dpg.group(tag="func_choose"):
            dpg.add_button(label="Show Squiggle Plot", callback=choose_channel)

    with dpg.window(label="Raw Data", width=800, height=600, tag="raw-data"):
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
            dpg.add_line_series([], [], parent="y_axis", tag = "raw_series")

    dpg.create_viewport(title='NanoTrace', width=850, height=800)
    dpg.setup_dearpygui()

    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()

if __name__ == '__main__':
    main()
