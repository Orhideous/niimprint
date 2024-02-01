from dataclasses import dataclass
from enum import StrEnum
from typing import Dict, Final


@dataclass
class Device:
    name: str
    max_density: int
    max_width: int


SUPPORTED_DEVICES: Final[Dict[str, Device]] = {
    "D11": Device("D11", 3, 96),
    "D110": Device("D110", 3, 96),
    "B1": Device("B1", 5, 384),
    "B18": Device("B18", 3, 384),
    "B21": Device("B21", 5, 384),
}

# NOTE: It's a hack for click until it support arbitrary Enum as choice
#       https://github.com/pallets/click/pull/2210
SupportedDevice = StrEnum("SupportedDevice", list(SUPPORTED_DEVICES.keys()))
