#!/usr/bin/env python3



import os
import sys
from wm import mkworkspace
from wm import lsworkspace
from wm import rmworkspace
from wm import get_workspaces



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
		# For Amazon S3 workspaces and others that can't hold a DateTime object
		self.expiration_epoch = None
		self.expiration_pretty = None
		self.obj_file_path = None

