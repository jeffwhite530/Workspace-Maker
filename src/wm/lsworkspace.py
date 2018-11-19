#!/usr/bin/env python3



import os
import sys
import pickle
import boto3
import datetime
import wm



def amazon_s3(command_args):
	if command_args.debug_mode is True:
		print("DEBUG: Entering lsworkspace.amazon_s3")

	os.environ["AWS_CONFIG_FILE"] = command_args.aws_config_file

	workspace_objs = wm.get_workspaces.amazon_s3(command_args)

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
	our_workspace_objs.sort(key=lambda x: x.expiration_epoch, reverse=True)

	for workspace_obj in our_workspace_objs:
		print("Workspace", workspace_obj.path, "will expire on", workspace_obj.expiration_pretty)



def posix(command_args):
	if command_args.debug_mode is True:
		print("DEBUG: Entering lsworkspace.posix")


	workspace_objs = wm.get_workspaces.posix(command_args)


	# If we are not root and the workspace is not ours, skip it
	our_workspace_objs = list()

	current_user_uid = os.getuid()

	for workspace_obj in workspace_objs:
		if current_user_uid != 0 and workspace_obj.uid != current_user_uid:
			if command_args.debug_mode is True:
				print("DEBUG: Skipping workspace", workspace_obj.name, "as we are not its owner")

			continue

		our_workspace_objs.append(workspace_obj)

	workspace_objs = our_workspace_objs


	# Show the workspaces, ordered by expiration date
	workspace_objs.sort(key=lambda x: x.expiration_datetime, reverse=True)

	for workspace_obj in workspace_objs:
		print("Workspace", workspace_obj.path, "will expire on", workspace_obj.expiration_pretty)

