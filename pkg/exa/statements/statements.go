package statements

import (
	"fmt"
	"github.com/dhellmann/pyatl_exa_challenge/pkg/exa/interpreter"
)

// Statement is the interface for individual commands
type Statement interface {
	Do(*interpreter.State) error
	String() string
}

// InputStatement holds a read and parsed input line
type InputStatement struct {
	LineNum int
	Line    string
	Tokens  []string
}

func (i InputStatement) String() string {
	return fmt.Sprintf("%3d: %s", i.LineNum, i.Line)
}

// Factory is a function for making a concrete statement from the
// input.
type Factory func(InputStatement) (Statement, error)

var factories = map[string]Factory{}

// Register stores a factory associated with the name of the statement
// it builds.
func register(name string, factory Factory) {
	factories[name] = factory
}

// Build converts an input statement to a concrete statement.
func Build(inStmt InputStatement) (Statement, error) {
	if factory, ok := factories[inStmt.Tokens[0]]; ok {
		return factory(inStmt)
	}
	return nil, fmt.Errorf("Unrecognized statement line %d: %s",
		inStmt.LineNum, inStmt.Tokens[0])
}
