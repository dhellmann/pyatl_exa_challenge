package exa

import (
	"github.com/dhellmann/pyatl_exa_challenge/pkg/exa/interpreter"
	"github.com/dhellmann/pyatl_exa_challenge/pkg/exa/statements"
)

// Program is a bunch of statements
type Program []statements.Statement

// Run executes a program and returns the resulting state or any errors
func (p Program) Run() (interpreter.State, error) {
	state := interpreter.State{}

	for {
		if state.Counter > len(p) {
			break
		}
	}

	return state, nil
}
