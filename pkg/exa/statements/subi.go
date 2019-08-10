package statements

import (
	"fmt"
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

func (*subiStatement) Do(state *interpreter.State) error {
	return fmt.Errorf("NotImplemented: SUBI")
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
