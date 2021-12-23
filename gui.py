import dearpygui.dearpygui as dpg
from fast5_research.fast5_bulk import BulkFast5
import numpy as np

def main():
    dpg.create_context()

    with dpg.window(label="Raw Data", width=800, height=6000):

        with dpg.plot(label="Squiggle Plot", height=-1, width=-1):
            dpg.add_plot_legend()

            # create x axis
            dpg.add_plot_axis(dpg.mvXAxis, label="index", no_gridlines=True, tag="x_axis")
            dpg.set_axis_limits(dpg.last_item(), 0, 100000)

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
