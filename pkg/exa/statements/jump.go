package statements

import (
	"fmt"

	"github.com/dhellmann/pyatl_exa_challenge/pkg/exa/interpreter"
)

func init() {
	register("JUMP", newJump)
}

type jumpStatement struct {
	input InputStatement
	label string
}

func (s *jumpStatement) String() string {
	return s.input.String()
}

func (s *jumpStatement) Do(state *interpreter.State) error {
	nextCounter, ok := state.Labels[s.label]
	if !ok {
		return fmt.Errorf("Line %d: Undefined label %s",
			s.input.LineNum, s.label)
	}

	state.Counter = nextCounter
	return nil
}

// New builds a jumpStatement from the input statement
func newJump(input InputStatement) (Statement, error) {
	err := interpreter.CheckSyntax(
		[]string{"L"},
		input.Tokens,
		input.LineNum,
	)
	if err != nil {
		return nil, err
	}
	return &jumpStatement{
		input: input,
		label: input.Tokens[1],
	}, nil
}
