package statements

import (
	"github.com/dhellmann/pyatl_exa_challenge/pkg/exa/interpreter"
)

func init() {
	register("DROP", newDrop)
}

type dropStatement struct {
	input InputStatement
}

func (s *dropStatement) String() string {
	return s.input.String()
}

func (s *dropStatement) Do(state *interpreter.State) error {
	state.DropFile()
	state.Counter++
	return nil
}

// New builds an dropStatement from the input statement
func newDrop(input InputStatement) (Statement, error) {
	err := interpreter.CheckSyntax(
		[]string{},
		input.Tokens,
		input.LineNum,
	)
	if err != nil {
		return nil, err
	}
	return &dropStatement{
		input: input,
	}, nil
}
