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



# Which storage spaces are allowed.  The first listed will be the default if none are given.
STORAGE_SPACES = ["/wmtest", "/wmtest2"]

# How long until workspaces expire
DEFAULT_LIFETIME_DAYS = 14
MAX_LIFETIME_DAYS = 14



# DO NOT EDIT BELOW HERE



class Workspace(object):
	"""This class holds information about a single workspace.
	"""
	def __init__(self):
		self.uid = None
		self.gid = None
		self.user = None
		self.group = None
		self.name = None
		self.path = None
		self.expiration_datetime = None
		self.expiration_pretty = None
		self.obj_file_path = None



def get_workspaces():
	"""Get the workspace objects by reading the pickle files.
		Return a list of workspace objects.
	"""
	workspace_objs = list()

	for fs_entry in os.listdir(command_args.storage):
		entry_path = command_args.storage + os.path.sep + fs_entry

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
		workspace_obj.name = command_args.workspace_name

	else:
		random_int = random.randint(0, 99999)

		random_int_str = str(random_int)

		random_int_str_zeros = random_int_str.zfill(5)

		workspace_obj.name = workspace_obj.user + "_" + random_int_str_zeros

	workspace_obj.path = command_args.storage + os.path.sep + workspace_obj.name

	if command_args.debug_mode is True:
		print("DEBUG: Workspace path:", workspace_obj.path)


	# Verify the workspace does not already exist
	if os.path.exists(workspace_obj.path):
		print("Workspace path", workspace_obj.path, "already exists, exiting.", file=sys.stderr)

		sys.exit(1)


	# Determine an expiration date for the workspace
	datetime_now = datetime.datetime.now()

	datetime_delta = datetime.timedelta(days=command_args.lifetime_days)

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
	workspace_obj.obj_file_path = command_args.storage + os.path.sep + "." + workspace_obj.name + ".pkl"

	with open(workspace_obj.obj_file_path, "wb") as workspace_obj_file_handle:
		pickle.dump(workspace_obj, workspace_obj_file_handle)

	if command_args.debug_mode is True:
		print("DEBUG: Created workspace object file at", workspace_obj.obj_file_path)


	# Done!
	print("Workspace", workspace_obj.path, "created with expiration of", workspace_obj.expiration_pretty)



def lsworkspace(command_args):
	if command_args.debug_mode is True:
		print("DEBUG: Entering lsworkspace function")


	workspace_objs = list()


	# If we were given a workspace name, only use that one
	if command_args.workspace_name is not None:
		workspace_obj_file_path = command_args.storage + os.path.sep + "." + command_args.workspace_name + ".pkl"

		if os.path.exists(workspace_obj_file_path):
			with open(workspace_obj_file_path, "rb") as workspace_obj_file_path_handle:
				workspace_obj = pickle.load(workspace_obj_file_path_handle)

			workspace_objs.append(workspace_obj)

		else:
			print("No workspace object file found for workspace", command_args.workspace_name, file=sys.stderr)

			sys.exit(1)

	else:
		workspace_objs = get_workspaces()


	our_workspace_objs = list()
	current_user_uid = os.getuid()


	# If we are not root and the workspace is not ours, skip it
	for workspace_obj in workspace_objs:
		if current_user_uid != 0 and workspace_obj.uid != current_user_uid:
			if command_args.debug_mode is True:
				print("DEBUG: Skipping workspace", workspace_obj.name, "as we are not its owner")

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


	workspace_objs = list()


	# If we were given a workspace name, only use that one
	if command_args.workspace_name is not None:
		workspace_obj_file_path = command_args.storage + os.path.sep + "." + command_args.workspace_name + ".pkl"

		if os.path.exists(workspace_obj_file_path):
			with open(workspace_obj_file_path, "rb") as workspace_obj_file_path_handle:
				workspace_obj = pickle.load(workspace_obj_file_path_handle)

			workspace_objs.append(workspace_obj)

		else:
			print("No workspace object file found for workspace", command_args.workspace_name, file=sys.stderr)

			sys.exit(1)

	else:
		workspace_objs = get_workspaces()


	for workspace_obj in workspace_objs:
		# ** DANGER ** DEBUG ONLY: This will cause workspaces to be deleted immediately by pretending we are in the future
		#datetime_now = datetime.datetime.now() + datetime.timedelta(days=1000)

		datetime_now = datetime.datetime.now()

		if datetime_now > workspace_obj.expiration_datetime:
			print("Workspace", workspace_obj.path, "has expired, removing...")

			# Create a lock directory.
			# We shouldn't use fcntl.flock() as we need to support NFS (which "should" support locking) and other filesystems that may not support it.
			try:
				lock_dir = command_args.storage + os.path.sep + "." + command_args.workspace_name + ".lock"

				os.mkdir(lock_dir)

				if command_args.debug_mode is True:
					print("DEBUG: Acquired lock at", lock_dir)

			except:
				print("Failed to obtain lock, skipping workspace", file=sys.stderr)

				continue

			# Remove the workspace
			shutil.rmtree(workspace_obj.path)

			# Remove the workspace object file
			os.remove(workspace_obj.obj_file_path)

			# Remove the lock
			os.rmdir(lock_dir)

		else:
			print("Workspace", workspace_obj.path, "has not yet expired, skipping")



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
							help="Number of days until the workspace expires (Default: " + str(DEFAULT_LIFETIME_DAYS) + ")")

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
		mkworkspace(command_args)

	elif prog_name == "lsworkspace":
		lsworkspace(command_args)

	elif prog_name == "rmworkspace":
		rmworkspace(command_args)

	else:
		print("Unable to determine program name.  See installation section of the README.", file=sys.stderr)
		
		sys.exit(1)

