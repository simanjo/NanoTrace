import numpy as np
import re
import dearpygui.dearpygui as dpg
from fast5_research.fast5_bulk import BulkFast5

from typing import Any, Dict, Literal, Optional, Tuple, Union


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


def get_channel_details(
    fname: str, burnin: int,
    event_low: Union[float, int], event_high: Union[float, int]
) -> Dict[int, Dict[str, float]]:
    dpg.configure_item("Progress Bar", show=True)

    scaling = determine_scaling(event_low, event_high)
    result = {
        c: band_details for c in range(1, 127)
        if _update_channel_progress(c) and
        _is_active_channel(fname, c, burnin) and
        (
            band_details := _get_band_distribution(
                fname, c, burnin, scaling, event_low, event_high
            )
        ) is not None
    }

    dpg.configure_item("Progress Bar", show=False)
    return result


def determine_scaling(
    event_low: Union[float, int], event_high: Union[float, int]
) -> Literal['none', 'both', 'lower', 'upper']:
    if isinstance(event_low, int):
        if isinstance(event_high, int):
            return 'none'
        else:
            return 'upper'
    elif isinstance(event_high, int):
        return 'lower'
    else:
        return 'both'
    assert False


def get_baseline(raw_data):
    baseline = None

    try:
        if np.abs(np.mean(raw_data)) > 1:
            baseline = int(np.median(
                raw_data[np.logical_and(raw_data > 150, raw_data < 350)]
            ))
    finally:
        return baseline


def _get_band_distribution(
    fname: str, channel: int, burnin: int,
    scaling: Literal['both', 'none', 'lower', 'upper'] = 'both',
    event_low: float = 0.27, event_high: float = 0.48
) -> Optional[Dict[int, Dict[str, Any]]]:
    try:
        with BulkFast5(fname) as fh:
            raw_data = fh.get_raw(channel)[burnin:]
    except Exception as e:
        print(e)
        return None

    if (baseline_val := get_baseline(raw_data)) is None:
        return None
    low_band, high_band = _sanitize_event_bands(
        scaling, event_low, event_high, baseline_val
        )
    low_outs = np.sum(np.logical_and(-100 < raw_data, raw_data < -5))
    zeroes = np.sum(np.logical_and(-5 <= raw_data, raw_data <= 5))
    events = np.sum(np.logical_and(
        low_band < raw_data,
        raw_data < high_band
    ))
    baselines = np.sum(np.logical_and(
        baseline_val - 30 <= raw_data,
        raw_data <= baseline_val + 30
    ))
    high_outs = np.sum(np.logical_and(
        baseline_val + 30 < raw_data,
        raw_data < 350
    ))
    heavy_outs = np.sum(np.logical_or(
        raw_data <= -100,
        max(350, baseline_val + 30) <= raw_data
    ))
    return {
        scaling: {
            (event_low, event_high): (
                baseline_val,
                {
                    'outlier': (low_outs, high_outs, heavy_outs),
                    'zeroes': zeroes,
                    'events': events,
                    'baseline': baselines,
                }
            )
        }
    }


def _sanitize_event_bands(
    scaling: Literal['both', 'none', 'lower', 'upper'],
    event_low: float, event_high: float, baseline_val: int
) -> Tuple[float, float]:
    if scaling == 'both':
        assert not isinstance(event_low, int)
        assert not isinstance(event_high, int)
        return (event_low*baseline_val, event_high*baseline_val)
    elif scaling == 'none':
        assert isinstance(event_low, int)
        assert isinstance(event_high, int)
        return (event_low, event_high)
    elif scaling == 'lower':
        assert not isinstance(event_low, int)
        assert isinstance(event_high, int)
        return (event_low*baseline_val, event_high)
    elif scaling == 'upper':
        assert isinstance(event_low, int)
        assert not isinstance(event_high, int)
        return (event_low, event_high*baseline_val)
    assert False


def event_density(
    band_distr: Dict[
        Literal['outlier', 'zeroes', 'events', 'baseline'],
        Union[Tuple[int, int, int], int]
    ],
    key: Literal['outlier', 'zeroes', 'events', 'baseline'] = 'events'
) -> float:
    run_length = sum(band_distr['outlier']) + band_distr['zeroes'] \
                 + band_distr['events'] + band_distr['baseline']
    # assert zeroes and heavy outliers are equally distributed amongst bands
    length = run_length - band_distr['zeroes'] - band_distr['outlier'][2]
    if key == "outlier":
        return band_distr['outlier'][2] / run_length
    elif key == "zeroes":
        return band_distr['zeroes'] / run_length
    else:
        return band_distr[key] / length


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
            concentration_str = match.group('conc').replace(",", ".")
            expo = 3 if match.group('exp') == "mikro" else 0
            if int(concentration_str[0]) == 0 and concentration_str[1] != ".":
                # handle cases as "05mikromolar <-> 0.5 mikromolar"
                conc = int(float("0." + concentration_str[1:])*(10**expo))
            else:
                conc = int(float(concentration_str)*(10 ** expo))
    except BaseException:
        print(f"Couldn't determine concentration for {name}")
        print(f"Having {match}")
    finally:
        properties["concentration"] = conc

    if "buffer" in name.lower():
        properties["buffer"] = True
        properties["concentration"] = 0
        return properties
    else:
        properties["buffer"] = False

    return properties
