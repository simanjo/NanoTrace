from typing import Dict, Any, List, Optional, Union
from os import path

import dearpygui.dearpygui as dpg

from experiment import Experiment
import utils
from python_toolbox.util import get_file_hash

# HACK
DEFAULT_SETTINGS = {
    'kde_resolution': 1_000_000,
    'burnin': 350_000
}

DpgItem = Union[int, str]


class Context:

    # Mutable default value {} for exps on purpose.
    # There should only ever be one context at runtime...
    def __init__(
        self, exps={}, settings=DEFAULT_SETTINGS
    ) -> None:

        self.exps: Dict[str, Experiment] = exps
        self.settings: Dict[str, Any] = settings
        self.active_exp: Optional[Experiment] = None

    def update_context(
        self, fpath: str,
        progressbar: Optional[DpgItem] = None
    ) -> None:
        # TODO: add sanity checks for file values
        # calculate hash first and check if experiment is known
        if progressbar is not None:
            dpg.configure_item(
                progressbar, show=True, overlay="Calculating file hash"
            )
            dpg.set_value(progressbar, 0.5)
        hash = get_file_hash(fpath, algo='blake2b')
        if progressbar is not None:
            dpg.configure_item(progressbar, show=False)

        if hash not in self.exps.keys():
            # TODO: add different hash algorithms?
            fname = path.split(fpath)[1]
            properties = utils.parse_exp_name(fname)
            exp = Experiment(fname, fpath, {'blake2b': hash}, properties)
            self.exps[hash] = exp
        else:
            exp = self.exps[hash]
        self.active_exp = exp

    def get_active_channels(self) -> List[int]:
        if (chans := self.active_exp.get_active_channels()) is None:
            details = utils.get_channel_details(
                self.active_exp.path,
                DEFAULT_SETTINGS['burnin']
            )
            chans = list(details.keys())
            self.active_exp.band_distribution = details
        return chans
