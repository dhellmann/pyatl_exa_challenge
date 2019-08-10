package interpreter

// State holds the interpreter state
type State struct {
	// T is a register
	T int

	// X is a register
	X int

	// Counter is the program counter
	Counter int
}
