package statements

import (
	"github.com/dhellmann/pyatl_exa_challenge/pkg/exa/interpreter"
)

func init() {
	register("COPY", newCopy)
}

type copyStatement struct {
	input InputStatement
}

func (s *copyStatement) Do(state *interpreter.State) error {
	src, err := state.GetRegOrNum(s.input.Tokens[1])
	if err != nil {
		return err
	}
	state.Store(src, s.input.Tokens[2])
	state.Counter++
	return nil
}

// New builds a copyStatement from the input statement
func newCopy(input InputStatement) (Statement, error) {
	err := interpreter.CheckSyntax(
		[]string{"R/N", "R"},
		input.Tokens,
		input.LineNum,
	)
	if err != nil {
		return nil, err
	}
	return &copyStatement{
		input: input,
	}, nil
}
