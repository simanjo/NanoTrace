from typing import Any, List, Literal, Dict, Optional


class Experiment:

    def __init__(
        self, fname, fpath, hashs, active_channels, properties
    ) -> None:
        self.name: str = fname
        self.path: str = fpath
        self.hashs: Dict[Literal['blake2b', 'md5', 'sha3'], str] = hashs
        self.active_channels: Optional[List[int]] = active_channels
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