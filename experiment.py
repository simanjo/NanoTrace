from typing import Any, Literal, Dict, Optional

from numpy import mean, median, std

from utils import event_density


class Experiment:

    def __init__(
        self, fname, fpath, hashs, properties, band_distribution=None
    ) -> None:
        self.name: str = fname
        self.path: str = fpath
        self.hashs: Dict[Literal['blake2b', 'md5', 'sha3'], str] = hashs
        self.band_distribution: Optional[Dict[int, Any]] = band_distribution
        self.properties: Dict[str, Any] = properties

    def __str__(self) -> str:
        return '\n'.join(
            [
                f"Name: {self.name}",
                f"Path: {self.path}",
                f"Hashs: {list(self.hashs.values())}",
                f"Props: {self.properties}"
            ]
        )

    def get_active_channels(self):
        if self.band_distribution is None:
            return None
        return list(self.band_distribution.keys())

    def get_mean_baselines(self, filter_mad=True):
        if self.band_distribution is None:
            return None

        baselines = [val[0] for val in self.band_distribution.values()]
        if filter_mad:
            bl_median = median(baselines)
            bl_mad = median([abs(bl - bl_median) for bl in baselines])
            baselines = [
                bl for bl in baselines if abs(bl - bl_median) < 3*bl_mad
            ]
        return (round(mean(baselines), 2), round(std(baselines), 3))

    def get_mean_events(self, filter_mad=True):
        if self.band_distribution is None:
            return None

        if filter_mad:
            baselines = {k: v[0] for k, v in self.band_distribution.items()}
            bl_median = median(list(baselines.values()))
            bl_mad = median([abs(bl - bl_median) for bl in baselines.values()])
            indizes = [
                k for k, bl in baselines.items()
                if abs(bl - bl_median) < 3*bl_mad
            ]
            events = [
                event_density(v[1]) for k, v in self.band_distribution.items()
                if k in indizes
            ]
        else:
            events = [
                event_density(v[1]) for v in self.band_distribution.values()
            ]
        return (round(mean(events), 4), round(std(events), 3))
