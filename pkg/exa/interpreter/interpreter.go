package interpreter

import (
	"strconv"
)

// State holds the interpreter state
type State struct {
	// T is a register
	T int

	// X is a register
	X int

	// Counter is the program counter
	Counter int
}

// GetRegOrNum returns the contents of a register or converts its
// input to an integer.
func (s *State) GetRegOrNum(regOrNum string) (int, error) {
	switch regOrNum {
	case "T":
		return s.T, nil
	case "X":
		return s.X, nil
	default:
		return strconv.Atoi(regOrNum)
	}
}

// Store saves the value to the specified register
func (s *State) Store(value int, register string) {
	switch register {
	case "T":
		s.T = value
	case "X":
		s.X = value
	}
}
