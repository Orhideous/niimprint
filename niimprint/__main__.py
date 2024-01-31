import logging
import re

import click
from PIL import Image

from niimprint import (
    SUPPORTED_DEVICES,
    BluetoothTransport,
    PrinterClient,
    NiimPrintError,
    SerialTransport,
    SupportedDevice,
    validate_image,
)


@click.command("print")
@click.option(
    "-m",
    "--model",
    type=click.Choice(SupportedDevice, case_sensitive=False),
    default=SupportedDevice.D11.name,
    show_default=True,
    help="Niimbot printer model",
)
@click.option(
    "-c",
    "--conn",
    type=click.Choice(["usb", "bluetooth"]),
    default="usb",
    show_default=True,
    help="Connection type",
)
@click.option(
    "-a",
    "--addr",
    help="Bluetooth MAC address OR serial device path",
)
@click.option(
    "-d",
    "--density",
    type=click.IntRange(1, 5),
    default=5,
    show_default=True,
    help="Print density",
)
@click.option(
    "-r",
    "--rotate",
    type=click.Choice(["0", "90", "180", "270"]),
    default="0",
    show_default=True,
    help="Image rotation (clockwise)",
)
@click.option(
    "-i",
    "--image",
    type=click.Path(exists=True),
    required=True,
    help="Image path",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Enable verbose logging",
)
def print_cmd(model: SupportedDevice, conn: str, addr: str, density: int, rotate, image: str, verbose: bool):
    logging.basicConfig(
        level="DEBUG" if verbose else "INFO",
        format="%(levelname)s | %(module)s:%(funcName)s:%(lineno)d - %(message)s",
    )

    if conn == "bluetooth":
        assert conn is not None, "--addr argument required for bluetooth connection"
        addr = addr.upper()
        assert re.fullmatch(r"([0-9A-F]{2}:){5}([0-9A-F]{2})", addr), "Bad MAC address"
        transport = BluetoothTransport(addr)
    if conn == "usb":
        port = addr if addr is not None else "auto"
        transport = SerialTransport(port=port)

    image = Image.open(image)
    if rotate != "0":
        # PIL library rotates counter clockwise, so we need to multiply by -1
        image = image.rotate(-int(rotate), expand=True)

    device = SUPPORTED_DEVICES[model.name]
    try:
        validate_image(device, image_width=image.width, print_density=density)
    except NiimPrintError:
        logging.exception("Unsupported image")
        exit(1)

    printer = PrinterClient(transport)
    printer.print_image(image, density=density)


if __name__ == "__main__":
    print_cmd()
