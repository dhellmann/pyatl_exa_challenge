package exa

import (
	"fmt"
	"github.com/dhellmann/pyatl_exa_challenge/pkg/exa/interpreter"
	"github.com/dhellmann/pyatl_exa_challenge/pkg/exa/statements"
)

// Program is a bunch of statements
type Program []statements.Statement

// Run executes a program and returns the resulting state or any errors
func (p Program) Run() (*interpreter.State, error) {
	state := &interpreter.State{}

	for {
		if state.Counter > len(p) {
			break
		}
		nextStatement := p[state.Counter]
		fmt.Printf("%-20s ", nextStatement)
		if err := nextStatement.Do(state); err != nil {
			return nil, err
		}
		fmt.Printf("%v\n", state)
	}

	return state, nil
}
