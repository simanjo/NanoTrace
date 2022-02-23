import numpy as np
import re
import dearpygui.dearpygui as dpg
from fast5_research.fast5_bulk import BulkFast5

#TODO/HACK introduce seperate progress bar variable
#          and simplify handling thereof
def _is_active_channel(fname: str, channel: int, burnin: int) -> bool:
    try:
        with BulkFast5(fname) as fh:
            raw_data = fh.get_raw(channel)[burnin:]
    except Exception as e:
        print(e)
        return False

    return (
        np.abs(np.mean(raw_data)) > 1
        and len(raw_data[np.logical_and(raw_data > 150, raw_data < 350)]) > 0
    )

def _update_channel_progress(channel: int) -> bool:
    dpg.set_value("Progress Bar", (channel-1)/126)
    dpg.configure_item("Progress Bar", overlay=f"Checking channel {channel}/126", width=175)
    return True

def get_active_channels(fname: int, burnin: int = 350000) -> bool:
    dpg.configure_item("Progress Bar", show=True)

    result = [
        c for c in range(1,127) if _update_channel_progress(c) and _is_active_channel(fname, c, burnin)
    ]

    dpg.configure_item("Progress Bar", show=False)
    return result
