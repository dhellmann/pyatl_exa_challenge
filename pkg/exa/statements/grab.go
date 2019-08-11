package statements

import (
	"github.com/dhellmann/pyatl_exa_challenge/pkg/exa/interpreter"
)

func init() {
	register("GRAB", newGrab)
}

type grabStatement struct {
	input InputStatement
}

func (s *grabStatement) String() string {
	return s.input.String()
}

func (s *grabStatement) Do(state *interpreter.State) error {
	id, err := state.GetRegOrNum(s.input.Tokens[1])
	if err != nil {
		return err
	}
	state.GrabFile(id)
	state.Counter++
	return nil
}

// New builds an grabStatement from the input statement
func newGrab(input InputStatement) (Statement, error) {
	err := interpreter.CheckSyntax(
		[]string{"R/N"},
		input.Tokens,
		input.LineNum,
	)
	if err != nil {
		return nil, err
	}
	return &grabStatement{
		input: input,
	}, nil
}
