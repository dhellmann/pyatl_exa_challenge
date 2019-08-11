package main

import (
	"flag"
	"fmt"
	"os"

	"github.com/dhellmann/pyatl_exa_challenge/pkg/exa"
	"github.com/dhellmann/pyatl_exa_challenge/pkg/exa/datafile"
)

func main() {
	flag.Parse()

	programName := flag.Arg(0)
	if programName == "" {
		fmt.Fprintf(os.Stderr, "Please specify a program to run\n")
		os.Exit(1)
	}

	fd, err := os.Open(programName)
	defer fd.Close()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Could not open program file: %s\n", err)
		os.Exit(2)
	}

	program, err := exa.Load(fd)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Could not load program: %s\n", err)
		os.Exit(2)
	}

	dataFileNames := []string{}
	for i := 1; i < flag.NArg(); i++ {
		dataFileNames = append(dataFileNames, flag.Arg(i))
	}

	dataFiles, err := datafile.Load(dataFileNames)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Failed to load data file: %s\n", err)
		os.Exit(3)
	}
	fmt.Printf("data files: %v\n", dataFiles)

	results, err := program.Run(dataFiles)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Failed to run program: %s\n", err)
		os.Exit(4)
	}
	fmt.Printf("%v\n", results)
}
