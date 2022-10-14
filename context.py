from typing import Dict, Any, List, Optional, Union
from os import path

import dearpygui.dearpygui as dpg

from experiment import Experiment
from utils import get_active_channels, parse_exp_name
from python_toolbox.util import get_file_hash

## HACK
DEFAULT_SETTINGS = {
    'kde_resolution': 1_000_000,
    'burnin': 350_000
}

DpgItem = Union[int, str]

class Context:

    # Mutable default value {} for exps on purpose.
    # There should only ever be one context at runtime...
    def __init__(
        self, exps = {}, settings = DEFAULT_SETTINGS
    ) -> None:

        self.exps: Dict[str, Experiment] = exps
        self.settings: Dict[str, Any] = settings
        self.active_exp: Optional[Experiment] = None

    def update_context(
        self, fpath: str,
        progressbar: Optional[DpgItem] = None,
        table: Optional[DpgItem] = None
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
            properties = parse_exp_name(fname)
            exp = Experiment(fname, fpath, {'blake2b': hash}, None, properties)
            self.exps[hash] = exp
            if table is not None:
                print(f"adding stuffs to table {table}")
                with dpg.table_row(parent=table):

                    # dpg.add_text(fname)
                    with dpg.table_cell() as cell:
                        dpg.add_text(fname)
                        # dpg.add_item_clicked_handler(parent=cell, callback=lambda:print("click°!"))
                    # with dpg.handler_registry() as click_handler:
                    #     dpg.add_item_clicked_handler(callback=lambda:print("click°!"))
                    # dpg.bind_item_handler_registry(cell, click_handler)
                        # dpg.add_mouse_double_click_handler()
                    dpg.add_text(fpath)
                    dpg.add_text("TODO")
                    dpg.add_text(f"{properties['concentration']} nM")
                    dpg.add_text("---")
        else:
            exp = self.exps[hash]
        self.active_exp = exp
        print(exp)


    # def get_context() -> Dict[str, Any]:


    # def _get_active_exp_props() -> Dict[str, Any]:
    #     return _get_props(_get_active_exp())

    # def _get_context() -> Dict[str, Any]:
    #     context = {**_get_settings(), **_get_active_exp_props()}
    #     return context

    def get_active_channels(self) -> List[int]:
        if (chans := self.active_exp.active_channels) is None:
            chans = get_active_channels(
                self.active_exp.path,
                DEFAULT_SETTINGS['burnin']
            )
            self.active_exp.active_channels = chans
        return chans