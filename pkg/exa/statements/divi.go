package statements

import (
	"github.com/dhellmann/pyatl_exa_challenge/pkg/exa/interpreter"
)

func init() {
	register("DIVI", newDivi)
}

type diviStatement struct {
	input InputStatement
}

func (s *diviStatement) String() string {
	return s.input.String()
}

func (s *diviStatement) Do(state *interpreter.State) error {
	a, err := state.GetRegOrNum(s.input.Tokens[1])
	if err != nil {
		return err
	}
	b, err := state.GetRegOrNum(s.input.Tokens[2])
	if err != nil {
		return err
	}
	state.Store(a/b, s.input.Tokens[3])
	state.Counter++
	return nil
}

// New builds an diviStatement from the input statement
func newDivi(input InputStatement) (Statement, error) {
	err := interpreter.CheckSyntax(
		[]string{"R/N", "R/N", "R"},
		input.Tokens,
		input.LineNum,
	)
	if err != nil {
		return nil, err
	}
	return &diviStatement{
		input: input,
	}, nil
}
