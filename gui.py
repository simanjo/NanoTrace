import dearpygui.dearpygui as dpg
from fast5_research.fast5_bulk import BulkFast5
import numpy as np

def _is_active_channel(fname, channel):
    with BulkFast5(fname) as fh:
        raw_data = fh.get_raw(channel)
    baseline = None

    try:
        if np.abs(np.mean(raw_data)) > 1:
            baseline = int(np.median(raw_data[np.logical_and(raw_data > 150, raw_data < 350)]))
    finally:
        return (baseline is not None)


def _get_active_channels(fname):
    return [str(c) for c in range(1,127) if _is_active_channel(fname, c)]

def set_active_channels():
    fname = dpg.get_value("file")
    if fname is None:
        return

    chans = _get_active_channels(fname)
    dpg.configure_item("channel", items=chans)



def choose_file(sender, app_data, user_data):
    fname = list(app_data['selections'].values())[0]
    dpg.set_value("file", fname)
    dpg.configure_item("channel", items=[str(c) for c in range(1,127)])


def choose_channel():
    c = int(dpg.get_value("channel"))
    fname = dpg.get_value("file")
    if fname is None or c is None:
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


    with dpg.window(label="Raw Data", width=800, height=600):
        with dpg.group(horizontal=True):
            dpg.add_button(label="File Selector", callback=lambda: dpg.show_item("file_dialog"))
            dpg.add_text("Selected File: ", tag="file")
        with dpg.group(horizontal=True):
            dpg.add_combo(tag="channel", callback=choose_channel)
            dpg.add_button(label="Get active channels", callback=set_active_channels)

        with dpg.plot(label="Squiggle Plot", height=-1, width=-1):
            dpg.add_plot_legend()

            # create x axis
            dpg.add_plot_axis(dpg.mvXAxis, label="index", no_gridlines=True, tag="x_axis")
            dpg.set_axis_limits(dpg.last_item(), 0, 100000)
            # dpg.set_axis_ticks(dpg.last_item(), (("S1", 11), ("S2", 21), ("S3", 31)))

            # create y axis
            dpg.add_plot_axis(dpg.mvYAxis, label="current [pA]", tag="y_axis")
            dpg.set_axis_limits("y_axis", -20, 350)

            # add series to y axis
            dpg.add_line_series([], [], parent="y_axis", tag = "raw_series")

    dpg.create_viewport(title='NanoTrace', width=800, height=1000)
    dpg.setup_dearpygui()

    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()

if __name__ == '__main__':
    main()
