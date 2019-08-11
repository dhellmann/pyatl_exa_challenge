package statements

import (
	"github.com/dhellmann/pyatl_exa_challenge/pkg/exa/interpreter"
)

func init() {
	register("ADDI", newAddi)
}

type addiStatement struct {
	input InputStatement
}

func (s *addiStatement) String() string {
	return s.input.String()
}

func (s *addiStatement) Do(state *interpreter.State) error {
	a, err := state.GetRegOrNum(s.input.Tokens[1])
	if err != nil {
		return err
	}
	b, err := state.GetRegOrNum(s.input.Tokens[2])
	if err != nil {
		return err
	}
	if err = state.Store(a+b, s.input.Tokens[3]); err != nil {
		return err
	}
	state.Counter++
	return nil
}

// New builds an addiStatement from the input statement
func newAddi(input InputStatement) (Statement, error) {
	err := interpreter.CheckSyntax(
		[]string{"R/N", "R/N", "R"},
		input.Tokens,
		input.LineNum,
	)
	if err != nil {
		return nil, err
	}
	return &addiStatement{
		input: input,
	}, nil
}
