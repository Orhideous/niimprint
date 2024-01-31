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


class NiimPrintError(BaseException):
    pass


def validate_image(device: Device, image_width: int, print_density: int):
    if print_density > device.max_density:
        raise NiimPrintError(
            f"Device {device.name} can't support requested density {print_density}. "
            f"Use any of 1-{device.max_density}"
        )
    if image_width > device.max_width:
        raise NiimPrintError(
            f"Image is too wide for {device.name}. "
            f"It supports only {device.max_width}px wide (got {image_width}px)",
        )
