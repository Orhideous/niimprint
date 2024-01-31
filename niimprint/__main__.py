import logging
import re
from typing import Optional

import click
from click_option_group import (
    GroupedOption,
    RequiredMutuallyExclusiveOptionGroup,
    optgroup,
)
from PIL import Image

from niimprint import (
    SUPPORTED_DEVICES,
    BluetoothTransport,
    NiimPrintError,
    PrinterClient,
    SerialTransport,
    SupportedDevice,
    validate_image,
)


def validate_mac(ctx: click.Context, _: GroupedOption, value: str) -> str:
    if ctx.params.get("serial", None) is not None:
        return value
    addr = value.upper()
    if re.fullmatch(r"([0-9A-F]{2}:){5}([0-9A-F]{2})", addr):
        return addr
    raise click.BadParameter("format must be 'aa:bb:cc:dd:ee:ff'")


@click.command("print")
@click.option(
    "-m",
    "--model",
    type=click.Choice(SupportedDevice, case_sensitive=False),
    default=SupportedDevice.D11.name,
    show_default=True,
    help="Niimbot printer model",
)
@optgroup.group("Connection type", cls=RequiredMutuallyExclusiveOptionGroup)
@optgroup.option(
    "-b",
    "--bluetooth",
    type=click.UNPROCESSED,
    callback=validate_mac,
    help="Bluetooth MAC address"
)
@optgroup.option(
    "-s",
    "--serial",
    type=click.Path(exists=True, writable=True, dir_okay=False),
    is_flag=False,
    flag_value="/dev/ttyACM0",
    help="Serial port [default: /dev/ttyACM0]"
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
def print_cmd(
        model: SupportedDevice,
        density: int,
        rotate: int,
        image: str,
        verbose: bool,
        bluetooth: Optional[str],
        serial: Optional[str]
):
    logging.basicConfig(
        level="DEBUG" if verbose else "INFO",
        format="%(levelname)s | %(module)s:%(funcName)s:%(lineno)d - %(message)s",
    )

    match (bluetooth, serial):
        case mac, None:
            transport = BluetoothTransport(mac)
        case None, tty:
            transport = SerialTransport(port=tty)
        case _:
            # Unreachable (guaranteed by click), but still
            logging.exception("Ambiguous transport")
            exit(1)

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
