from typing import Any, List, Literal, Dict, Optional, Tuple, Union

from numpy import mean, median, std

from utils import event_density, determine_scaling


class Experiment:

    def __init__(
        self, fname, fpath, hashs, properties, band_distribution={}
    ) -> None:
        self.name: str = fname
        self.path: str = fpath
        self.hashs: Dict[Literal['blake2b', 'md5', 'sha3'], str] = hashs
        self.properties: Dict[str, Any] = properties

        # {channel ids ->
        #   {baseline scaling identifier ->
        #      {event boundaries -> (baseline, band distribution)}
        #   }
        # }
        self.band_distribution: Optional[
            Dict[int, Dict[
                Literal['none', 'lower', 'upper', 'both'],
                Dict[(float, float), Any]]
            ]
        ] = band_distribution

    def __str__(self) -> str:
        return '\n'.join(
            [
                f"Name: {self.name}",
                f"Path: {self.path}",
                f"Hashs: {list(self.hashs.values())}",
                f"Props: {self.properties}"
            ]
        )

    def get_active_channels(self) -> Optional[List[int]]:
        if self.band_distribution == {}:
            return None
        return list(self.band_distribution.keys())

    def get_mean_baselines(
        self, event_low: Union[float, int],
        event_high: Union[float, int], filter_mad: bool = True
    ) -> Tuple[float, float]:
        if self.band_distribution == {}:
            return None

        scaling = determine_scaling(event_low, event_high)
        try:
            band_dict = {
                c: val[scaling][(event_low, event_high)]
                for c, val in self.band_distribution.items()
            }
        except KeyError:
            return None
        baselines = [val[0] for val in band_dict.values()]
        if filter_mad:
            bl_median = median(baselines)
            bl_mad = median([abs(bl - bl_median) for bl in baselines])
            baselines = [
                bl for bl in baselines if abs(bl - bl_median) < 3*bl_mad
            ]
        return (round(mean(baselines), 2), round(std(baselines), 3))

    def get_mean_events(
        self, event_low: Union[float, int],
        event_high: Union[float, int], filter_mad=True
    ) -> Tuple[float, float]:
        if self.band_distribution == {}:
            return None

        scaling = determine_scaling(event_low, event_high)
        try:
            band_dict = {
                c: val[scaling][(event_low, event_high)]
                for c, val in self.band_distribution.items()
            }
        except KeyError:
            return None

        if filter_mad:
            baselines = {k: v[0] for k, v in band_dict.items()}
            bl_median = median(list(baselines.values()))
            bl_mad = median([abs(bl - bl_median) for bl in baselines.values()])
            indizes = [
                k for k, bl in baselines.items()
                if abs(bl - bl_median) < 3*bl_mad
            ]
            events = [
                event_density(v[1]) for k, v in band_dict.items()
                if k in indizes
            ]
        else:
            events = [
                event_density(v[1]) for v in band_dict.values()
            ]
        return (round(mean(events), 4), round(std(events), 3))
