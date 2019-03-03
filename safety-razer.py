from openrazer.client import DeviceManager
import subprocess as sp
import sys
import platform

###
# Globals
###

colors = {
    "red"  : (255, 0, 0),   #ff0000
    "blue" : (0, 153, 255)  #0099ff
}

STATIC_EFFECT = "static"
DEBUG = True

###
# Functions
###

def list_razer_devices(device_manager):
    """
    List detected Razer devices.
    """

    print("Found {} Razer devices\n".format(len(device_manager.devices)))
    for device in device_manager.devices:
        print("{}:".format(device.name))
        print("   Type: {}".format(device.type))
        print("   Serial: {}".format(device.serial))
        print("   Firmware version: {}".format(device.firmware_version))
        print("   Driver version: {}".format(device.driver_version))
        print("   Supports static lighting effect: {}\n".format(device.fx.has(STATIC_EFFECT)))


def compatibility_check():
    """
    If this is not being run on a Linux machine, exit.
    """
    system = platform.system()
    if system != "Linux":
        print("ERROR: Not compatible with {}.".format(system))
        sys.exit(1)


def detect_root():
    """
    Determine if a user is logged in as root.
    :return: True if the user is logged in, False otherwise
    :rtype: Boolean
    """
    if "root" == sp.check_output(['whoami']).strip():
        return True
    else:
        return False


def main():
    """
    Check if a user is root. If they are, set the keyboard to bright red.
    Otherwise, set the keyboard to bright blue.
    """
    compatibility_check()
    device_manager = DeviceManager()
    if DEBUG:
        list_razer_devices(device_manager)

    for device in device_manager.devices:
        if not device.fx.has(STATIC_EFFECT):
            print("ERROR: {} does not support the static light effect.".format())
            continue

        if detect_root():
            print("Detected root. Setting {} to RED {}".format(device.name, STATIC_EFFECT))
            device.fx.static(*colors["red"])
        else:
            print("Not root. Setting {} to BLUE {}".format(device.name, STATIC_EFFECT))
            device.fx.static(*colors["blue"])


if __name__ == '__main__':
    main()
