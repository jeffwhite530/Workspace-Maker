#!/usr/bin/env python3



# cython: language_level=3, boundscheck=False
# pylint: disable=line-too-long



import sys
import os
import argparse
import pwd
import grp
import random
import datetime
import pickle
import shutil



WORKSPACE_ROOT_DIR = "/wmtest"
WORKSPACE_LIFETIME_DAYS = 14



class Workspace(object):
	"""This class holds information about a single workspace.
	"""
	def __init__(self):
		self.uid = None
		self.gid = None
		self.user = None
		self.group = None
		self.workspace_name = None
		self.workspace_path = None
		self.expiration_datetime = None
		self.expiration_pretty = None
		self.obj_file_path = None



def get_workspaces():
	"""Get the workspace objects by reading the pickle files.
		Return a list of workspace objects.
	"""
	workspace_objs = list()

	for fs_entry in os.listdir(WORKSPACE_ROOT_DIR):
		entry_path = WORKSPACE_ROOT_DIR + os.path.sep + fs_entry

		if not os.path.isfile(entry_path):
			continue

		if not entry_path.endswith(".pkl"):
			continue

		if command_args.debug_mode is True:
			print("DEBUG: Found workspace object file", entry_path)

		with open(entry_path, "rb") as entry_path_handle:
			workspace_obj = pickle.load(entry_path_handle)

		workspace_objs.append(workspace_obj)

	return workspace_objs



def mkworkspace(command_args):
	if command_args.debug_mode is True:
		print("DEBUG: Entering mkworkspace function")


	workspace_obj = Workspace()


	workspace_obj.uid = os.getuid()
	workspace_obj.gid = pwd.getpwuid(workspace_obj.uid).pw_gid
	workspace_obj.user = pwd.getpwuid(workspace_obj.uid).pw_name
	workspace_obj.group = grp.getgrgid(workspace_obj.gid).gr_name


	# Were we given a workspace name?  If not, make one up.
	if command_args.workspace_name is not None:
		workspace_name = command_args.workspace_name

	else:
		random_int = random.randint(0, 99999)

		random_int_str = str(random_int)

		random_int_str_zeros = random_int_str.zfill(5)

		workspace_obj.name = workspace_obj.user + "_" + random_int_str_zeros

	workspace_obj.path = WORKSPACE_ROOT_DIR + os.path.sep + workspace_obj.name

	if command_args.debug_mode is True:
		print("DEBUG: Workspace path:", workspace_obj.path)


	# Verify the workspace does not already exist
	if os.path.exists(workspace_obj.path):
		print("Workspace path", workspace_obj.path, "already exists, exiting.", file=sys.stderr)

		sys.exit(1)


	# Determine an expiration date for the workspace
	datetime_now = datetime.datetime.now()

	datetime_delta = datetime.timedelta(days=WORKSPACE_LIFETIME_DAYS)

	workspace_obj.expiration_datetime = datetime_now + datetime_delta

	workspace_obj.expiration_pretty = workspace_obj.expiration_datetime.strftime("%Y-%m-%d at %I:%M %p")

	if command_args.debug_mode is True:
		print("DEBUG: Workspace expiration:", workspace_obj.expiration_datetime, "(", workspace_obj.expiration_pretty, ")")


	# Switch to the root user
	os.setuid(0)
	os.setgid(0)
	os.setgroups([0])


	# Create the workspace and set the ownership to the user
	os.mkdir(workspace_obj.path)
	
	os.chown(workspace_obj.path, workspace_obj.uid, workspace_obj.gid)
	
	if command_args.debug_mode is True:
		print("DEBUG: Created workspace")


	# Create the workspace object file
	workspace_obj.obj_file_path = WORKSPACE_ROOT_DIR + os.path.sep + "." + workspace_obj.name + ".pkl"

	with open(workspace_obj.obj_file_path, "wb") as workspace_obj_file_handle:
		pickle.dump(workspace_obj, workspace_obj_file_handle)

	if command_args.debug_mode is True:
		print("DEBUG: Created workspace object file at", workspace_obj.obj_file_path)


	# Done!
	print("Workspace", workspace_obj.path, "created with expiration of", workspace_obj.expiration_pretty)



def lsworkspace(command_args):
	if command_args.debug_mode is True:
		print("DEBUG: Entering lsworkspace function")


	workspace_objs = get_workspaces()
	our_workspace_objs = list()
	current_user_uid = os.getuid()


	# If we are not root and the workspace is not ours, skip it
	for workspace_obj in workspace_objs:
		if current_user_uid != 0 and workspace_obj.uid != current_user_uid:
			if command_args.debug_mode is True:
				print("DEBUG: Skipping workspace as we are not its owner")

			continue

		our_workspace_objs.append(workspace_obj)


	# Show the workspaces, ordered by expiration date
	our_workspace_objs.sort(key=lambda x: x.expiration_datetime, reverse=True)

	for workspace_obj in our_workspace_objs:
		print("Workspace", workspace_obj.path, "will expire on", workspace_obj.expiration_pretty)



def rmworkspace(command_args):
	if command_args.debug_mode is True:
		print("DEBUG: Entering rmworkspace function")


	if os.getuid() != 0:
		print("Only root may remove workspaces, exiting.", file=sys.stderr)

		sys.exit(1)


	workspace_objs = get_workspaces()


	for workspace_obj in workspace_objs:
		datetime_now = datetime.datetime.now()

		if datetime_now > workspace_obj.expiration_datetime:
			print("Workspace", workspace_obj.path, "has expired, removing...")

			# Remove the workspace
			shutil.rmtree(workspace_obj.path)

			# Remove the workspace object file
			os.remove(workspace_obj.obj_file_path)

		else:
			print("Workspace", workspace_obj.path, "has not yet expired, skipping")



if __name__ == "__main__":
	# What options were we called with?
	parser = argparse.ArgumentParser(description="Create and manage storage workspaces.")


	parser.add_argument("workspace_name", metavar="workspace",
							type=str, nargs="?",
                    		help="Name of the workspace to work with")

	parser.add_argument("-d", "--debug", dest="debug_mode",
							default=False, action="store_true",
							help="Enable debug mode")

	# TODO: Add storage option
	# TODO: Add lifetime days option

	command_args = parser.parse_args()



	# What program name were we called with?
	prog_name = os.path.basename(sys.argv[0])

	if prog_name == "mkworkspace":
		mkworkspace(command_args)

	elif prog_name == "lsworkspace":
		lsworkspace(command_args)

	elif prog_name == "rmworkspace":
		rmworkspace(command_args)

	else:
		print("Unable to determine program name.  See installation section of the README.", file=sys.stderr)
		
		sys.exit(1)

