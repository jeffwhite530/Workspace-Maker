#!/usr/bin/env python3



import os
import sys
import pickle
import datetime
import shutil
import wm



def posix(command_args):
	if command_args.debug_mode is True:
		print("DEBUG: Entering rmworkspace.posix")


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
		workspace_objs = wm.get_workspaces.posix(command_args)


	for workspace_obj in workspace_objs:
		# ** DANGER ** DEBUG ONLY: This will cause workspaces to be deleted immediately by pretending we are in the future
		datetime_now = datetime.datetime.now() + datetime.timedelta(days=1000)

		#datetime_now = datetime.datetime.now()

		if datetime_now > workspace_obj.expiration_datetime:
			print("Workspace", workspace_obj.path, "has expired, removing...")

			# Create a lock directory.
			# We shouldn't use fcntl.flock() as we need to support NFS (which "should" support locking) and other filesystems that may not support it.
			try:
				lock_dir = command_args.storage + os.path.sep + "." + workspace_obj.name + ".lock"

				os.mkdir(lock_dir)

				if command_args.debug_mode is True:
					print("DEBUG: Acquired lock at", lock_dir)

			except OSError as err:
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

