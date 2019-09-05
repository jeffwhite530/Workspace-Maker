package main



import (
	"fmt"
	"os"
	"log"
	"github.com/spf13/pflag"
)



func main() {
	// TODO: Make this a config file
	var posix_storage_spaces [2]string
	posix_storage_spaces[0] = "/wmtest"
	posix_storage_spaces[1] = "/wmtest2"


	// What options were we called with?
	// TODO: How to print "Create and manage storage workspaces." with the help text?
	// TODO: How to remove "pflag: help requested" from the output of --help

	debug_flag_ptr := pflag.BoolP("debug", "D", false, "Enable debug mode")
	days_flag_ptr := pflag.IntP("days", "d", 7, "Number of days until the workspace expires")
	posix_storage_flag_ptr := pflag.StringP("storage", "s", posix_storage_spaces[0], "Which storage space to use for the workspace")

	pflag.Parse()

	_ = days_flag_ptr
	_ = posix_storage_flag_ptr
	_ = posix_storage_spaces


	if *debug_flag_ptr == true {
		fmt.Println("Debug mode enabled")
	}


	// Sanity checks
	


	// Get to work
	workspace_name := os.Args[len(os.Args)-1]


	fmt.Println("Working with workspace", workspace_name)


	// What program name were we called with?
	prog_name := os.Args[0]

	if prog_name == "mkworkspace" {
		fmt.Println(prog_name)

	} else if prog_name == "lsworkspace" {
		fmt.Println(prog_name)

	} else if prog_name == "rmworkspace" {
		fmt.Println(prog_name)

	} else {
		 //fmt.Fprintf(os.Stderr, "Unable to determine program name.  See installation section of the README.")
		log.Fatal("Unable to determine program name.  See installation section of the README.")
	}
}

