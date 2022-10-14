import numpy as np
import re
import dearpygui.dearpygui as dpg
from fast5_research.fast5_bulk import BulkFast5


# TODO/HACK introduce seperate progress bar variable
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
    dpg.configure_item(
        "Progress Bar", overlay=f"Checking channel {channel}/126", width=175
    )
    return True


def get_active_channels(fname: str, burnin: int = 350000) -> bool:
    dpg.configure_item("Progress Bar", show=True)

    result = [
        c for c in range(1, 127)
        if _update_channel_progress(c) and
        _is_active_channel(fname, c, burnin)
    ]

    dpg.configure_item("Progress Bar", show=False)
    return result


def parse_exp_name(name):
    properties = dict()

    # try to guess concentration from name if that fails
    # for whatever reason, concentration is NaN
    conc = np.nan
    try:
        match = re.search(
            '\D*(?P<conc>\d*\.?\d*)(?P<exp>mikro|nm|nano)',
            name.lower()
        )
        if match is None:
            print(f"Couldn't determine concentration for {name}")
            conc = np.nan
        else:
            concentration = float(match.group('conc'))
            expo = 1000 if match.group('exp') == "mikro" else 1
            conc = int(concentration*expo)
    except BaseException:
        print(f"Couldn't determine concentration for {name}")
        print(f"Having {match}")
    finally:
        properties["concentration"] = conc

    if "ochratoxin" in name.lower():
        properties["hplc"] = False
        properties["special_run"] = False
        properties["buffer"] = False
        return properties

    if "buffer" in name.lower():
        properties["buffer"] = True
        properties["hplc"] = False
        properties["special_run"] = False
        properties["concentration"] = 0
        return properties
    else:
        properties["buffer"] = False

    if "hplc" in name.lower():
        properties["hplc"] = True
    else:
        properties["hplc"] = False

    special_names = ["glycerol", "polya", "150mv", "denatured", "strepdavidin"]
    if any(part in name.lower() for part in special_names):
        properties["special_run"] = True
    else:
        properties["special_run"] = False

    return properties
