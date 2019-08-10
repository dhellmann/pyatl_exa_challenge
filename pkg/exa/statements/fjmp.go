package statements

import (
	"fmt"

	"github.com/dhellmann/pyatl_exa_challenge/pkg/exa/interpreter"
)

func init() {
	register("FJMP", newFjmp)
}

type fjmpStatement struct {
	input InputStatement
	label string
}

func (s *fjmpStatement) String() string {
	return s.input.String()
}

func (s *fjmpStatement) Do(state *interpreter.State) error {
	if state.T != 0 {
		state.Counter++
		return nil
	}

	nextCounter, ok := state.Labels[s.label]
	if !ok {
		return fmt.Errorf("Line %d: Undefined label %s",
			s.input.LineNum, s.label)
	}

	state.Counter = nextCounter
	return nil
}

// New builds a fjmpStatement from the input statement
func newFjmp(input InputStatement) (Statement, error) {
	err := interpreter.CheckSyntax(
		[]string{"L"},
		input.Tokens,
		input.LineNum,
	)
	if err != nil {
		return nil, err
	}
	return &fjmpStatement{
		input: input,
		label: input.Tokens[1],
	}, nil
}
