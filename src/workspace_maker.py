#!/usr/bin/env python3



# cython: language_level=3, boundscheck=False
# pylint: disable=line-too-long



import sys
import os
import argparse
import wm



# Which storage spaces are allowed.  The first listed will be the default if none are given.
STORAGE_SPACES = ["/wmtest", "/wmtest2"]

# How long until workspaces expire
DEFAULT_LIFETIME_DAYS = 14
MAX_LIFETIME_DAYS = 14



# DO NOT EDIT BELOW HERE



def launch_mkworkspace(command_args):
	wm.mkworkspace.posix(command_args)



def launch_lsworkspace(command_args):
	wm.lsworkspace.posix(command_args)



def launch_rmworkspace(command_args):
	wm.rmworkspace.posix(command_args)



if __name__ == "__main__":
	# What options were we called with?
	parser = argparse.ArgumentParser(description="Create and manage storage workspaces.")


	parser.add_argument("workspace_name", metavar="workspace",
							type=str, nargs="?",
							help="Name of the workspace to work with")

	parser.add_argument("-D", "--debug", dest="debug_mode",
							default=False, action="store_true",
							help="Enable debug mode")

	parser.add_argument("-d", "--days", dest="lifetime_days", metavar="NUM",
							default=DEFAULT_LIFETIME_DAYS, action="store", type=int,
							help="Number of days until the workspace expires (Default: " + str(DEFAULT_LIFETIME_DAYS) + ", Max: " + str(MAX_LIFETIME_DAYS) + ")")

	parser.add_argument("-s", "--storage", dest="storage", metavar="PATH",
							default=STORAGE_SPACES[0], action="store", type=str,
							help="Which storage space to use for the workspace (Default: " + STORAGE_SPACES[0] + ")")

	command_args = parser.parse_args()



	# Sanity checks
	if not command_args.storage.startswith("/"):
		print("Storage option must be a path beginning with '/', exiting.", file=sys.stderr)

		sys.exit(1)


	if command_args.storage not in STORAGE_SPACES:
		print("Storage spaces must be one of:", STORAGE_SPACES, file=sys.stderr)

		sys.exit(1)


	if command_args.lifetime_days > MAX_LIFETIME_DAYS:
		print("Requested lifetime of", command_args.lifetime_days, "greater than maximum of", MAX_LIFETIME_DAYS, file=sys.stderr)

		sys.exit(1)



	# What program name were we called with?
	prog_name = os.path.basename(sys.argv[0])

	if prog_name == "mkworkspace":
		launch_mkworkspace(command_args)

	elif prog_name == "lsworkspace":
		launch_lsworkspace(command_args)

	elif prog_name == "rmworkspace":
		launch_rmworkspace(command_args)

	else:
		print("Unable to determine program name.  See installation section of the README.", file=sys.stderr)
		
		sys.exit(1)

