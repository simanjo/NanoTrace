from typing import Dict, Any, List, Optional

from Experiment import Experiment
from utils import get_active_channels

## HACK
DEFAULT_SETTINGS = {
    'kde_resolution': 1_000_000,
    'burnin': 350_000
}

class Context:

    # Mutable default value {} for exps on purpose.
    # There should only ever be one context at runtime...
    def __init__(
        self, exps = {}, settings = DEFAULT_SETTINGS
    ) -> None:

        self.exps: Dict[str, Experiment] = exps
        self.settings: Dict[str, Any] = settings
        self.active_exp: Optional[Experiment] = None

    def _get_active_exp(self) -> Experiment:
        return self.active_exp

    def get_burnin() -> int:
        return DEFAULT_SETTINGS['burnin']

    def get_active_channels(self) -> List[int]:
        if (chans := self.active_exp.active_channels) is None:
            chans = get_active_channels(
                self.active_exp.path,
                DEFAULT_SETTINGS['burnin']
            )
            self.active_exp.active_channels = chans
        return chans