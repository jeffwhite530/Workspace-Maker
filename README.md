Workspace Maker
===============

Workspace Maker is a utility to manage access to a shared storage system and was designed for HPC clusters.  Often an HPC cluster will have a shared storage area, for example: /scratch.  Usually, all researchers using the cluster have write access to it and simply create files and directories wherever they want.  This leads to a few problems:

* What happens when a researcher leaves the company/university and their data is still on it?  Where is it in the filesystem?  How do we know it was that person's data and not someone else's?
* How do we enforce time limits on data stored there?  We can't just run `find /scratch -mtime +14 -exec rm -rf '{}' \;` because the researchers can simply touch their files everyday and keep them forever.  Also, that method can remove parts of a dataset while leaving other files alone.

Workspace Maker solves that problem by forcing each researcher to create a *workspace* to store their data in.  A workspace is simply a directory with an expiration date.


Usage Example
-------------

```
$ mkworkspace -h
usage: mkworkspace [-h] [-D] [-d NUM] [-s PATH] [workspace]

Create and manage storage workspaces.

positional arguments:
  workspace             Name of the workspace to work with

optional arguments:
  -h, --help            show this help message and exit
  -D, --debug           Enable debug mode
  -d NUM, --days NUM    Number of days until the workspace expires (Default:
                        14)
  -s PATH, --storage PATH
                        Which storage space to use for the workspace (Default:
                        /wmtest)


$ mkworkspace
Workspace /wmtest/jeffwhite530_64497 created with expiration of 2018-11-10 at 04:46 PM


$ lsworkspace
Workspace /wmtest/jeffwhite530_64497 will expire on 2018-11-10 at 04:46 PM
Workspace /wmtest/jeffwhite530_99373 will expire on 2018-11-10 at 03:27 PM


$ rmworkspace
Only root may remove workspaces, exiting.


# rmworkspace
Workspace /wmtest/jeffwhite530_99373 has not yet expired, skipping
Workspace /wmtest/jeffwhite530_64497 has not yet expired, skipping
```

Installation
------------

In order to compile and install Workspace Maker you will need:

* Cython
* Python 3 (>=3.4 reccomended)
* gcc (or another C compiler)
* Python 3's development headers (libpython3-dev on Ubuntu systems)
* Ensure time and timezone are in sync across all systems which will use Workspace Maker

Before compiling:

* Edit src/workspace_maker.py3 and set STORAGE_SPACES to be a list of where you want to store workspaces.  Ensure only root can write to these directories.
* Edit src/workspace_maker.py3 and set DEFAULT_LIFETIME_DAYS and MAX_LIFETIME_DAYS to how many days you want each workspace to exist before deletion.

### Automatic Build

* ./build.sh
* Move the files from bin/ to where you want to install it to (e.g. /usr/local/bin).

### Manual Build

Run the following to compile Workspace Maker:

* cython3 -3 --embed src/workspace_maker.py3 -o build/workspace_maker.c
* gcc build/workspace_maker.c $(python3-config --cflags --ldflags) -fPIC -o bin/workspace_maker

This will produce an executable binary named workspace_maker in bin/.  Move that binary to where you want to install it (e.g. /usr/local/bin).

Set the owner to root and set the SETUID bit:

* chown root:root bin/workspace_maker
* chmod u+s bin/workspace_maker

Next, create 3 symlinks to the program.  These are the commands you will use to call the associated functions of Workspace Maker:

* ln -s workspace_maker bin/mkworkspace
* ln -s workspace_maker bin/lsworkspace
* ln -s workspace_maker bin/rmworkspace

That's it!  You should now be able to run the commands mkworkspace, lsworkspace, and rmworkspace in order to invoke each function of Workspace Maker.

Optional: Add rmworkspace to your crontab in order to have them automatically removed.  rmworkspace will only remove expired workspaces.

