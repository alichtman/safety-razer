from openrazer.client import DeviceManager
from colorama import Fore, Style
from loguru import logger
import subprocess as sp
import platform
import time
import sys
import os

###
# Globals
###

colors = {
    "red"  : (255, 0, 0),   #ff0000
    "blue" : (0, 153, 255)  #0099ff
}

STATIC_EFFECT = "static"
DEBUG = True
LOG_PATH = "~/.safety-razer.log"

logger.add(LOG_PATH,
           format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
           backtrace=True,
           colorize=True)

###
# Functions
###


def print_status(text):
    print(Fore.BLUE + Style.BRIGHT + text + Style.RESET_ALL)


def list_razer_devices(device_manager):
    """
    List detected Razer devices.
    """
    logger.debug("Found {} Razer devices\n".format(len(device_manager.devices)))
    for device in device_manager.devices:
        print_status("{}:".format(device.name))
        print_status("   Type: {}".format(device.type))
        print_status("   Serial: {}".format(device.serial))
        print_status("   Firmware version: {}".format(device.firmware_version))
        print_status("   Driver version: {}".format(device.driver_version))
        print_status("   Supports static lighting effect: {}\n".format(device.fx.has(STATIC_EFFECT)))


def validate_devices(device_list):
    """
    Remove all devices from list that don't have the static effect.
    """
    for device in device_list:
        if not device.fx.has(STATIC_EFFECT):
            logger.debug("Skipping device " + device.name + " (" + device.serial + "). Static not detected.")
            device_list.remove(device)

    return device_list


def compatibility_check():
    """
    If this is not being run on a Linux machine, exit.
    """
    if platform.system() != "Linux":
        logger.exception("Linux not detected.")
        sys.exit(1)


def create_logfile():
    """
    Make sure the LOG_PATH is a file. Create it if it doesn't exist.
    """
    if os.path.isfile(LOG_PATH):
        pass
    elif os.path.isdir(LOG_PATH):
        # This will be printed to stdout, too
        logger.exception("LOG_PATH is set to a directory: {}.".format(LOG_PATH))
        sys.exit()
    else:
        os.mknod(LOG_PATH)
        logger.debug("Created log file: {}.".format(LOG_PATH))


def detect_root():
    """
    Determine if a user is logged in as root.
    :return: True if the user is logged in, False otherwise
    :rtype: Boolean
    """
    if "root" == sp.check_output(['whoami']).strip():
        logger.debug("Detected root.")
        return True
    else:
        logger.debug("Detected user.")
        return False


def main():
    """
    Check if a user is root. If they are, set the keyboard to bright red.
    Otherwise, set the keyboard to bright blue.
    """
    logger.debug("Opening safety-razer.")
    compatibility_check()
    device_manager = DeviceManager()
    if DEBUG:
        list_razer_devices(device_manager)

    already_detected_root = False
    already_detected_user = False

    # Check to update lighting every 5 seconds
    while True:
        for device in validate_devices(device_manager.devices):
            if detect_root():
                already_detected_user = False
                if already_detected_root:
                    print_status("Still root. No color change needed.")
                    continue

                already_detected_root = True
                if device.fx.static(*colors["red"]):
                    logger.debug("Successfully set {} to static red".format(device.name))

            else:
                if already_detected_user:
                    print_status("Still user. No color change needed.")
                    continue

                already_detected_user = True
                already_detected_root = False
                if device.fx.static(*colors["blue"]):
                    logger.debug("Successfully set {} to static blue".format(device.name))

        time.sleep(5)


if __name__ == '__main__':
    main()
