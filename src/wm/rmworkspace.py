#!/usr/bin/env python3



import os
import sys
import pickle
import datetime
import shutil
import boto3
import wm



def amazon_s3(command_args):
	if command_args.debug_mode is True:
		print("DEBUG: Entering rmworkspace.amazon_s3")


	os.environ["AWS_CONFIG_FILE"] = command_args.aws_config_file

	
	if os.getuid() != 0:
		print("Only root may remove workspaces, exiting.", file=sys.stderr)

		sys.exit(1)


	workspace_objs = wm.get_workspaces.amazon_s3(command_args)

	
	for workspace_obj in workspace_objs:
		datetime_now = datetime.datetime.now().timestamp()

		if datetime_now > workspace_obj.expiration_epoch:
			print("Workspace", workspace_obj.path, "has expired, removing...")

			s3_resource = boto3.resource("s3")

			bucket = s3_resource.Bucket("wm-bucket-" + workspace_obj.name)

			# FIXME: How can we lock the bucket before doing this?
			bucket.objects.all().delete()

			bucket.delete()

		else:
			print("Workspace", workspace_obj.path, "has not yet expired, skipping")


def posix(command_args):
	if command_args.debug_mode is True:
		print("DEBUG: Entering rmworkspace.posix")


	if os.getuid() != 0:
		print("Only root may remove workspaces, exiting.", file=sys.stderr)

		sys.exit(1)


	workspace_objs = wm.get_workspaces.posix(command_args)


	for workspace_obj in workspace_objs:
		datetime_now = datetime.datetime.now()

		if datetime_now > workspace_obj.expiration_datetime:
			print("Workspace", workspace_obj.path, "has expired, removing...")

			# Create a lock directory.
			# We shouldn't use fcntl.flock() as we need to support NFS (which "should" support locking) and other filesystems that may not support it.
			try:
				lock_dir = command_args.posix_storage + os.path.sep + "." + workspace_obj.name + ".lock"

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

