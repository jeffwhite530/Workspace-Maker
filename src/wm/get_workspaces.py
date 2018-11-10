#!/usr/bin/env python3



import os
import sys
import pickle
import wm



def posix(command_args):
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

