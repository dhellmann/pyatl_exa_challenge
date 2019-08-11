package interpreter

import (
	"fmt"
	"strconv"

	"github.com/dhellmann/pyatl_exa_challenge/pkg/exa/datafile"
)

// State holds the interpreter state
type State struct {
	// T is a register
	T int

	// X is a register
	X int

	// Counter is the program counter
	Counter int

	// Labels hold the index values for each label in the program
	// being run
	Labels map[string]int

	// Files holds the known data files
	Files map[int]datafile.File

	// currentFileID is the id of the file we're currently using for
	// read/write operations
	currentFileID int
	currentFile   datafile.File
}

func (s *State) String() string {
	return fmt.Sprintf("T=%4d X=%4d", s.T, s.X)
}

// GetRegOrNum returns the contents of a register or converts its
// input to an integer.
func (s *State) GetRegOrNum(regOrNum string) (int, error) {
	switch regOrNum {
	case "T":
		return s.T, nil
	case "X":
		return s.X, nil
	case "F":
		if s.currentFile == nil {
			return 0, fmt.Errorf("No open file")
		}
		return s.currentFile.Read()
	default:
		return strconv.Atoi(regOrNum)
	}
}

// Store saves the value to the specified register
func (s *State) Store(value int, register string) error {
	switch register {
	case "T":
		s.T = value
	case "X":
		s.X = value
	case "F":
		if s.currentFile == nil {
			return fmt.Errorf("No open file")
		}
		return s.currentFile.Write(value)
	}
	return nil
}

// GrabFile opens an existing file or creates a new one
func (s *State) GrabFile(id int) {
	if _, ok := s.Files[id]; !ok {
		s.Files[id] = datafile.New(id)
	}
	s.currentFileID = id
	s.currentFile = s.Files[id]
}

func (s *State) DropFile() {
	s.currentFile = nil
	s.currentFileID = 0
}

func (s *State) AtEOF() (bool, error) {
	if s.currentFile == nil {
		return false, fmt.Errorf("No open file")
	}
	return s.currentFile.AtEOF(), nil
}
