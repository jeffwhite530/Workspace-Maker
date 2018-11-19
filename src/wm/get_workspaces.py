#!/usr/bin/env python3



import os
import sys
import pickle
import boto3
import wm



def amazon_s3(command_args):
	if command_args.debug_mode is True:
		print("DEBUG: Entering get_workspaces.amazon_s3")

	os.environ["AWS_CONFIG_FILE"] = command_args.aws_config_file


	workspace_objs = list()


	s3_resource = boto3.resource("s3")


	for bucket in s3_resource.buckets.all():
		workspace_obj = wm.Workspace()

		bucket_tagging = bucket.Tagging()
		
		for tag in bucket_tagging.tag_set:
			if tag["Key"] == "uid":
				workspace_obj.uid = int(tag["Value"])

			elif tag["Key"] == "gid":
				workspace_obj.gid = int(tag["Value"])

			elif tag["Key"] == "user":
				workspace_obj.user = tag["Value"]

			elif tag["Key"] == "group":
				workspace_obj.group = tag["Value"]

			elif tag["Key"] == "name":
				workspace_obj.name = tag["Value"]

			elif tag["Key"] == "path":
				workspace_obj.path = tag["Value"]

			elif tag["Key"] == "expiration_epoch":
				workspace_obj.expiration_epoch = int(tag["Value"])

			elif tag["Key"] == "expiration_pretty":
				workspace_obj.expiration_pretty = tag["Value"]

		workspace_objs.append(workspace_obj)


	# If we were given a workspace name, only use that one
	if command_args.workspace_name is not None:
		new_workspace_objs = list()

		for workspace_obj in workspace_objs:
			if workspace_obj.name == command_args.workspace_name:
				new_workspace_objs.append(workspace_obj)

		workspace_objs = new_workspace_objs


	return workspace_objs



def posix(command_args):
	"""Get the workspace objects by reading the pickle files.
		Return a list of workspace objects.
	"""
	workspace_objs = list()


	for fs_entry in os.listdir(command_args.posix_storage):
		entry_path = command_args.posix_storage + os.path.sep + fs_entry

		if not os.path.isfile(entry_path):
			continue

		if not entry_path.endswith(".pkl"):
			continue

		if command_args.debug_mode is True:
			print("DEBUG: Found workspace object file", entry_path)

		with open(entry_path, "rb") as entry_path_handle:
			workspace_obj = pickle.load(entry_path_handle)

		workspace_objs.append(workspace_obj)


	# If we were given a workspace name, only use that one
	if command_args.workspace_name is not None:
		new_workspace_objs = list()

		for workspace_obj in workspace_objs:
			if workspace_obj.name == command_args.workspace_name:
				new_workspace_objs.append(workspace_obj)

		workspace_objs = new_workspace_objs


	return workspace_objs

