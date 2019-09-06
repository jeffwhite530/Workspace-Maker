package main



import (
	"fmt"
	"os"
	"log"
	"path"
	"strings"
	"github.com/spf13/pflag"
)



func main() {
	// TODO: Make this a config file
	var posixStorageSpaces [2]string
	posixStorageSpaces[0] = "/wmtest"
	posixStorageSpaces[1] = "/wmtest2"

	maxLifetimeDays := 14


	// What options were we called with?
	// TODO: How to print "Create and manage storage workspaces." with the help text?
	// TODO: How to remove "pflag: help requested" from the output of --help

	debugFlagPtr := pflag.BoolP("debug", "D", false, "Enable debug mode")
	daysFlagPtr := pflag.IntP("days", "d", 14, "Number of days until the workspace expires")
	posixStorageFlagPtr := pflag.StringP("storage", "s", posixStorageSpaces[0], "Which storage space to use for the workspace")

	pflag.Parse()

	_ = daysFlagPtr
	_ = posixStorageFlagPtr
	_ = posixStorageSpaces


	if *debugFlagPtr == true {
		fmt.Println("Debug mode enabled")
	}


	// Sanity checks
	if strings.HasPrefix(*posixStorageFlagPtr, "/") == false {
		log.Fatal("Storage space must be a path beginning with '/', exiting.")
	}

	// FIXME: Ensure the storage space given is one in posix_storage_spaces

	if *daysFlagPtr > maxLifetimeDays {
		log.Fatalf("Requested lifetime of %d is greater than maximum of %d, exiting.\n", maxLifetimeDays, *daysFlagPtr)
	}

	// FIXME: Ensure we have a workspace_name if we need one


	// Get to work
	workspaceName := os.Args[len(os.Args)-1]


	fmt.Println("Working with workspace", workspaceName)


	// What program name were we called with?
	progName := path.Base(os.Args[0])

	if progName == "mkworkspace" {
		fmt.Println(progName)

	} else if progName == "lsworkspace" {
		fmt.Println(progName)

	} else if progName == "rmworkspace" {
		fmt.Println(progName)

	} else {
		 //fmt.Fprintf(os.Stderr, "Unable to determine program name.  See installation section of the README.")
		log.Fatal("Unable to determine program name.  See installation section of the README.")
	}
}

