package statements

import (
	"github.com/dhellmann/pyatl_exa_challenge/pkg/exa/interpreter"
)

func init() {
	register("SUBI", newSubi)
}

type subiStatement struct {
	input InputStatement
}

func (s *subiStatement) String() string {
	return s.input.String()
}

func (s *subiStatement) Do(state *interpreter.State) error {
	a, err := state.GetRegOrNum(s.input.Tokens[1])
	if err != nil {
		return err
	}
	b, err := state.GetRegOrNum(s.input.Tokens[2])
	if err != nil {
		return err
	}
	state.Store(a-b, s.input.Tokens[3])
	state.Counter++
	return nil
}

// New builds an subiStatement from the input statement
func newSubi(input InputStatement) (Statement, error) {
	err := interpreter.CheckSyntax(
		[]string{"R/N", "R/N", "R"},
		input.Tokens,
		input.LineNum,
	)
	if err != nil {
		return nil, err
	}
	return &subiStatement{
		input: input,
	}, nil
}
