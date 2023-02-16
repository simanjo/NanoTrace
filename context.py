from typing import Dict, Any, List, Optional, Union
from os import path
from pathlib import Path
import pickle

import dearpygui.dearpygui as dpg

from experiment import Experiment
import utils
from python_toolbox.util import get_file_hash

# HACK
DEFAULT_SETTINGS = {
    'kde_resolution': 1_000_000,
    'burnin': 350_000,
    'min_event_band': 0.27,
    'max_event_band': 0.48,
}

DpgItem = Union[int, str]


class Context:

    def __init__(
        self, experiment_db, settings=DEFAULT_SETTINGS
    ) -> None:

        self.settings: Dict[str, Any] = settings
        self.experiment_db = experiment_db

        self.exps: Dict[str, Experiment] = self._load_exps()
        self.active_exp: Optional[Experiment] = None

    def update_experiment_db(self, fpath: str, dump_first=True) -> None:
        if dump_first:
            self._dump_exps()
        self.experiment_db = fpath
        self.exps, self.settings = self._load_exps()

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

    def _load_exps(self) -> Dict[str, Experiment]:
        if not Path(self.experiment_db).is_file():
            return {}

        with open(self.experiment_db, 'rb') as fh:
            exp_dict = pickle.load(fh)
        return self._sanitize_exps(exp_dict)

    def _sanitize_exps(self, exp_dict) -> Dict[str, Experiment]:
        # TODO: add version tag and version check
        # and reasoning about settings
        experiments = {}
        settings = self.settings
        try:
            experiments = exp_dict['exps']
            settings = exp_dict['settings']
        finally:
            return experiments, settings

    def _dump_exps(self) -> None:
        dump = {
            'settings': self.settings,
            'exps': self.exps
        }
        with open(self.experiment_db, 'wb') as fh:
            pickle.dump(dump, fh)
