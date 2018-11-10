#!/usr/bin/env python3



import os
import sys
import pwd
import grp
import random
import datetime
import pickle
import wm



def posix(command_args):
	if command_args.debug_mode is True:
		print("DEBUG: Entering mkworkspace.posix")


	workspace_obj = wm.Workspace()


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

	workspace_obj.path = command_args.posix_storage + os.path.sep + workspace_obj.name

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
	workspace_obj.obj_file_path = command_args.posix_storage + os.path.sep + "." + workspace_obj.name + ".pkl"

	with open(workspace_obj.obj_file_path, "wb") as workspace_obj_file_handle:
		pickle.dump(workspace_obj, workspace_obj_file_handle)

	if command_args.debug_mode is True:
		print("DEBUG: Created workspace object file at", workspace_obj.obj_file_path)


	# Done!
	print("Workspace", workspace_obj.path, "created with expiration of", workspace_obj.expiration_pretty)

