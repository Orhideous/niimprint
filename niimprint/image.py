import math
import struct
from pathlib import Path

from PIL import Image, ImageOps

from niimprint import NiimPrintError
from niimprint.models import Device
from niimprint.packet import NiimbotImage, NiimbotPacket


def _encode_image(image: Image, density: int) -> NiimbotImage:
    img = ImageOps.invert(image.convert("L")).convert("1")
    payload = []
    for y in range(img.height):
        line_data = [img.getpixel((x, y)) for x in range(img.width)]
        line_data = "".join("0" if pix == 0 else "1" for pix in line_data)
        line_data = int(line_data, 2).to_bytes(math.ceil(img.width / 8), "big")
        counts = (0, 0, 0)  # It seems like you can always send zeros
        header = struct.pack(">H3BB", y, *counts, 1)
        payload.append(NiimbotPacket(0x85, header + line_data))

    return NiimbotImage(
        width=image.width,
        height=image.height,
        payload=payload,
        density=density
    )


def prepare_image(image_path: str | Path, density: int, rotate: str) -> NiimbotImage:
    """Prepare image for printing, rotating and/or dithering if necessary"""
    image = Image.open(image_path)
    if rotate != "0":
        # PIL library rotates counter clockwise, so we need to multiply by -1
        image = image.rotate(-int(rotate), expand=True)
    return _encode_image(image, density)


def validate_image(device: Device, image: NiimbotImage):
    """Checks whether given image can be printed in given device"""
    if image.density > device.max_density:
        raise NiimPrintError(
            f"Device {device.name} can't support requested density {image.density}. "
            f"Use any of 1-{device.max_density}"
        )
    if image.width > device.max_width:
        raise NiimPrintError(
            f"Image is too wide for {device.name}. "
            f"It supports only {device.max_width}px wide (got {image.width}px)",
        )
