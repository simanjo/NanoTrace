from typing import Any, Literal, Dict, Optional


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
