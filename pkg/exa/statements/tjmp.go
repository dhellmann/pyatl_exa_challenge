package statements

import (
	"fmt"

	"github.com/dhellmann/pyatl_exa_challenge/pkg/exa/interpreter"
)

func init() {
	register("TJMP", newTjmp)
}

type tjmpStatement struct {
	input InputStatement
	label string
}

func (s *tjmpStatement) String() string {
	return s.input.String()
}

func (s *tjmpStatement) Do(state *interpreter.State) error {
	if state.T == 0 {
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

// New builds a tjmpStatement from the input statement
func newTjmp(input InputStatement) (Statement, error) {
	err := interpreter.CheckSyntax(
		[]string{"L"},
		input.Tokens,
		input.LineNum,
	)
	if err != nil {
		return nil, err
	}
	return &tjmpStatement{
		input: input,
		label: input.Tokens[1],
	}, nil
}
