from openrazer.client import DeviceManager
from colorama import Fore, Style
from collections import deque
from loguru import logger
from pathlib import Path
import platform
import time
import sys
import os

###
# Globals
###

# Colors in RGB
colors = {
	"red"  : (255, 0, 0),
	"blue" : (0, 153, 255)
}

action = {
	"none": None,
	"elevate": 1,
	"de-esecalate": 2
}

DEBUG = True
STATIC_EFFECT = "static"
LOG_PATH = "{}/.safety-razer.log".format(str(Path.home()))


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


def get_history_file_path():
	return os.environ(["HISTFILE"])


def get_file_len(history):
	with open(history, "r") as f:
		return len(f.readlines())


def get_unprocessed_commands(history, last_index):
	with open(history, "r") as f:
		all_lines = f.readlines()
		return [line.strip() for line in all_lines][:last_index], len(all_lines)


def process_commands(commands, status_stack):
	escalate = ["sudo", "su"]
	de_secalate = ["exit"]
	privelege_change_commands = [command for command in commands
								if command.startswith(any(escalate + de_secalate))]

	logger.debug("Found {} privelege change commands".format(len(privelege_change_commands)))
	logger.debug(privelege_change_commands)

	orig_len = len(status_stack)

	if len(privelege_change_commands) == 0:
		return action["none"], status_stack
	else:
		for x in privelege_change_commands:
			for item in escalate:
				if x.startswith(item):
					status_stack.append("root")
			for item in de_secalate:
				if x.startswith(item):
					status_stack.pop()

	if orig_len > len(status_stack):
		return action["elevate"], status_stack
	else:
		return action["de-esecalate"], status_stack


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

	hist_file = get_history_file_path()

	# Track privilege level using a stack
	tracked_privilege = deque()
	tracked_privilege.append("user")

	last_hist_index = get_file_len(hist_file)

	# Check every 5 seconds
	while True:
		commands, last_hist_index = get_unprocessed_commands(hist_file, last_hist_index)
		action, tracked_privilege = process_commands(commands, tracked_privilege)

		if action == action["escalate"]:
			for device in validate_devices(device_manager.devices):
				if device.fx.static(*colors["red"]):
					logger.debug("Successfully set {} to static red".format(device.name))

		elif action == action["de-esecalate"]:
			if device.fx.static(*colors["blue"]):
				logger.debug("Successfully set {} to static blue".format(device.name))

		else:
			logger.debug("No privelege change detected.")

		time.sleep(5)


if __name__ == '__main__':
	main()
