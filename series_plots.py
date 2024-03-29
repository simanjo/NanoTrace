from argparse import ArgumentError
from dataclasses import dataclass
import random
from typing import Literal, Optional, Union, Any, Collection, Sequence, List

import dearpygui.dearpygui as dpg
import numpy as np
import statsmodels.api as sm

from fast5_research.fast5_bulk import BulkFast5
from context import Context

DpgItem = Union[int, str]
# TODO: resolve progress bar issue...


# cf. https://www.python.org/dev/peps/pep-0484/#the-numeric-tower
# int is ok where float is required
@dataclass
class SeriesData:
    # implicitly assert len(x_datas) == len(y_datas)
    title: str
    x_label: str
    x_lims: Sequence[float]
    x_datas: List[Collection[float]]
    y_label: str
    y_lims: Sequence[float]
    y_datas: List[Collection[float]]
    h_lines: Optional[Sequence[float]] = None


def _plot_series(target: DpgItem, data: SeriesData) -> None:
    with dpg.plot(label=data.title, height=-1, width=-1, parent=target) as plt:
        x_axis = dpg.add_plot_axis(dpg.mvXAxis, label=data.x_label)
        y_axis = dpg.add_plot_axis(dpg.mvYAxis, label=data.y_label)
        dpg.set_axis_limits(x_axis, *data.x_lims)
        dpg.set_axis_limits(y_axis, *data.y_lims)

        for x_data, y_data in zip(data.x_datas, data.y_datas):
            dpg.add_line_series(x_data, y_data, parent=y_axis)
        # wait a frame to have axis limits registered (some BUG/RACE here?)
        dpg.split_frame()
        dpg.set_axis_limits_auto(x_axis)
        dpg.set_axis_limits_auto(y_axis)
        if data.h_lines:
            dpg.add_hline_series(
                [float(val) for val in data.h_lines], parent=y_axis
            )
    dpg.configure_item(target, on_close=lambda: dpg.delete_item(plt))


def _get_kdes(
    context: Context, channels: List[int]
) -> List[sm.nonparametric.KDEUnivariate]:
    fpath = context.active_exp.path
    burnin = context.settings['burnin']
    kde_resolution = context.settings['kde_resolution']

    progress_bar = "Progress Bar"
    dpg.configure_item(progress_bar, show=True, width=175)
    kdes = []
    for count, chan in enumerate(channels):
        dpg.set_value(progress_bar, count/len(channels))
        dpg.configure_item(
            progress_bar,
            overlay=f"Calculating KDE {count+1}/{len(channels)}"
        )

        with BulkFast5(fpath) as fh:
            raw_data = fh.get_raw(chan)[burnin:]
        kde = sm.nonparametric.KDEUnivariate(raw_data)
        kde.fit(gridsize=min(kde_resolution, len(raw_data)))
        kdes.append(kde)
    dpg.configure_item(progress_bar, show=False)
    return kdes


def _get_series_data(
    context: Context,
    flavour: Literal['raw', 'dens'],
    channels: List[int]
) -> SeriesData:
    fpath = context.active_exp.path
    channel_id = channels[0] if len(channels) == 1 else channels
    title = f"{context.active_exp.name}\nChannel {channel_id}"
    h_lines = None
    if flavour == "raw":

        # TODO: ensure that channels fits as type?
        # assert len(channels) == 1
        channel = channels[0]
        x_axis_scale = 1.0
        x_label = "index"
        with BulkFast5(fpath) as fh:
            y_data = [fh.get_raw(channel)]
            if context.settings['scale_in_seconds']:
                x_axis_scale = fh.sample_rate
                x_label = "time [s]"
        x_lims = (0, int(100_000/x_axis_scale))
        y_label = "current [pA]"
        y_lims = (-20, 350)
        x_data = [np.arange(0, len(y_data[0])) / x_axis_scale]
        if context.settings['plot_event_bands']:
            h_lines = context.get_event_bands(channel)
    elif flavour == 'dens':
        kdes = _get_kdes(context, channels)
        x_data = [kde.support for kde in kdes]
        y_data = [kde.density for kde in kdes]
        x_label = "current [pA]"
        x_lims = (-20, 350)
        y_label = "density"
        y_lims = (-0.05, 0.2)
    else:
        # TODO: find suitable error handling
        msg = [
            f"Flavour {flavour} is no valid series flavour.",
            "Use \'raw\' or \'dens\'"
        ]
        raise ArgumentError(" ".join(msg))
    return SeriesData(
        title, x_label, x_lims, x_data, y_label, y_lims, y_data, h_lines
    )


def show_raw(
    sender: DpgItem,
    app_data: Any,
    user_data: Context
) -> None:
    if not (channel := dpg.get_value("channel")):
        # no channel set, fail silently, TODO: add handling ie message?
        return
    series_data = _get_series_data(user_data, "raw", [int(channel)])
    target = dpg.add_window(label="Raw Data", width=800, height=600)
    _plot_series(target, series_data)


def show_kde(
    sender: DpgItem,
    app_data: Any,
    user_data: Context
) -> None:
    if not (channel := dpg.get_value("channel")):
        # no channel set, fail silently, TODO: add handling ie message?
        return
    series_data = _get_series_data(user_data, "dens", [int(channel)])
    target = dpg.add_window(label="Kernel Density", width=800, height=600)
    _plot_series(target, series_data)


def show_rand_kde(
    sender: DpgItem,
    app_data: Any,
    user_data: Context
) -> None:
    active_chans = user_data.get_active_channels()
    n = user_data.settings['random_kdes']

    if len(active_chans) > n + 1:
        chans = random.sample(active_chans, k=n)
        chans.sort()
    else:
        chans = active_chans

    series_data = _get_series_data(user_data, "dens", chans)
    target = dpg.add_window(label="Kernel Density", width=800, height=600)
    _plot_series(target, series_data)
