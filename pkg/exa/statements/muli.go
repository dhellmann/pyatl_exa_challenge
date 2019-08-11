package statements

import (
	"github.com/dhellmann/pyatl_exa_challenge/pkg/exa/interpreter"
)

func init() {
	register("MULI", newMuli)
}

type muliStatement struct {
	input InputStatement
}

func (s *muliStatement) String() string {
	return s.input.String()
}

func (s *muliStatement) Do(state *interpreter.State) error {
	a, err := state.GetRegOrNum(s.input.Tokens[1])
	if err != nil {
		return err
	}
	b, err := state.GetRegOrNum(s.input.Tokens[2])
	if err != nil {
		return err
	}
	if err = state.Store(a*b, s.input.Tokens[3]); err != nil {
		return err
	}
	state.Counter++
	return nil
}

// New builds an muliStatement from the input statement
func newMuli(input InputStatement) (Statement, error) {
	err := interpreter.CheckSyntax(
		[]string{"R/N", "R/N", "R"},
		input.Tokens,
		input.LineNum,
	)
	if err != nil {
		return nil, err
	}
	return &muliStatement{
		input: input,
	}, nil
}
