package statements

import (
	"fmt"
	"github.com/dhellmann/pyatl_exa_challenge/pkg/exa/interpreter"
)

func init() {
	register("COPY", newCopy)
}

type copyStatement struct {
	input InputStatement
}

func (*copyStatement) Do(state *interpreter.State) error {
	return fmt.Errorf("NotImplemented: COPY")
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
