#!/bin/bash

rm -f build/workspace_maker.c
rm -f bin/workspace_maker
rm -f bin/mkworkspace
rm -f bin/lsworkspace
rm -f bin/rmworkspace

mkdir -p build
mkdir -p bin

cython3 -3 --embed src/workspace_maker.py3 -o build/workspace_maker.c || exit $?

gcc build/workspace_maker.c $(python3-config --cflags --ldflags) -fPIC -o bin/workspace_maker || exit $?

sudo chown root:root bin/workspace_maker
sudo chmod u+s bin/workspace_maker

ln -s workspace_maker bin/mkworkspace
ln -s workspace_maker bin/lsworkspace
ln -s workspace_maker bin/rmworkspace

