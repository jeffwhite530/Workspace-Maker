#!/bin/bash

export GOPATH=~/gopath

go get github.com/spf13/pflag

go build -o bin/workspace_maker src/workspace_maker.go

rm -f bin/mkworkspace bin/lsworkspace bin/rmworkspace
ln -s workspace_maker bin/mkworkspace
ln -s workspace_maker bin/lsworkspace
ln -s workspace_maker bin/rmworkspace

