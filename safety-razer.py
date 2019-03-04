from openrazer.client import DeviceManager
from colorama import Fore, Style
from datetime import datetime
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

sudo_logs = {
	"ubuntu" : "/var/log/auth.log"
}

# Used for changing the light settings
light_change_action = {
	"none": None,
	"elevate": 1,
	"de-esecalate": 2
}

privilege_status = {
	"user": 0,
	"elevated": 1
}

DEBUG = True
STATIC_EFFECT = "static"
LOG_PATH = "{}/.safety-razer.log".format(str(Path.home()))
CHECK_INTERVAL = 3  # in seconds


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


def extract_date_from_log_line(line):
	date_parts = line.split()[:3]
	if len(date_parts[1]) == 1:
		date_parts[1] = "0" + date_parts[1]
	date = " ".join(date_parts)

	# Format: month-abbr day-number HH:MM:SS
	return datetime.strptime(date, '%b %d %:H%M%S')


def get_last_time(history):
	with open(history, "r") as f:
		return extract_date_from_log_line(f.readlines()[-1])


def get_new_privelege_changes(history, last_time):
	start_idx = 0
	with open(history, "r") as f:
		all_lines = f.readlines()
		for line in all_lines:
			if extract_date_from_log_line(line) <= last_time:
				start_idx += 1
			else:
				break

		return [line.strip() for line in all_lines[start_idx:]], extract_date_from_log_line(all_lines[-1])


def process_changes(changes, status_stack):
	orig_len = len(status_stack)
	escalate = "Successful su"
	de_escalate = "Removed session"

	for change in changes:
		if escalate in change:
			logger.debug("Found privilege escalation.")
			status_stack.append(privilege_status["elevated"])
		elif de_escalate in change:
			logger.debug("Found privilege de-escalation.")
			status_stack.pop()

	new_len = len(status_stack)
	if orig_len > new_len:
		return light_change_action["elevate"], status_stack
	elif orig_len < new_len:
		return light_change_action["de-esecalate"], status_stack
	else:
		return light_change_action["none"], status_stack


def main():
	"""
	Check if a user is root. If they are, set the keyboard to bright red.
	Otherwise, set the keyboard to bright blue.
	"""
	create_logfile()
	logger.debug("Opening safety-razer.")
	compatibility_check()
	
	try:
	        device_manager = DeviceManager()
	except Exception as e:
	        logger.exception("Razer DeviceManager error. {}".format(e))
	        sys.exit()

	if DEBUG:
	        list_razer_devices(device_manager)

	# TODO: This demo is just for Ubuntu, but this should be expanded to more Linux distros
	sudo_access_file = sudo_logs["ubuntu"]

	# Track privilege level using a stack.
	# Assume no elevated priveleges at start.
	tracked_privilege = deque()
	tracked_privilege.append(privilege_status["user"])

	last_time = get_last_time(sudo_access_file)

	# Check every 5 seconds
	while True:
		logger.debug("Current privilege stack: {}".format(privilege_status))
		privelege_changes, last_time = get_new_privelege_changes(sudo_access_file, last_time)
		light_change_action, tracked_privilege = process_changes(privelege_changes, tracked_privilege)

		if light_change_action == light_change_action["escalate"]:
			for device in validate_devices(device_manager.devices):
				if device.fx.static(*colors["red"]):
					logger.debug("Successfully set {} to static red".format(device.name))
		elif light_change_action == light_change_action["de-esecalate"]:
			for device in validate_devices(device_manager.devices):
				if device.fx.static(*colors["blue"]):
					logger.debug("Successfully set {} to static blue".format(device.name))
		else:
			logger.debug("No privelege change detected.")

		time.sleep(CHECK_INTERVAL)


if __name__ == '__main__':
	main()
